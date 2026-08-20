#!/usr/bin/env python3
"""Deterministic NumPy Double-DQN prototype for drift-aware QoE recovery.

The controller selects monitoring and recovery actions in a synthetic system.
It is intended for portfolio demonstration and reproducible method inspection,
not deployment or safety certification.
"""
from __future__ import annotations

import argparse
import json
from collections import deque
from dataclasses import dataclass
from pathlib import Path
from typing import Callable

import numpy as np

STATE_DIM = 5
N_ACTIONS = 4
HIDDEN = 32
ACTIONS = ["monitor", "recalibrate", "fast_adapt", "full_recovery"]
ACTION_COST = np.array([0.00, 0.035, 0.095, 0.205], dtype=float)


class RecoveryEnv:
    def __init__(self, seed: int, horizon: int = 100) -> None:
        self.rng = np.random.default_rng(seed)
        self.horizon = horizon
        self.t = 0
        self.regime = 0
        self.throughput = 0.65
        self.buffer = 0.55
        self.residual = 0.18
        self.drift = 0.12
        self.cooldown = 0.0

    def state(self) -> np.ndarray:
        return np.array([self.throughput, self.buffer, self.residual, self.drift, self.cooldown], dtype=float)

    def reset(self) -> np.ndarray:
        self.t = 0
        self.regime = int(self.rng.integers(3))
        self.throughput = float(np.clip(self.rng.normal([0.78, 0.58, 0.40][self.regime], 0.08), 0.08, 1.0))
        self.buffer = float(np.clip(self.rng.normal(0.58, 0.12), 0.05, 1.0))
        self.residual = float(np.clip(self.rng.normal(0.16, 0.06), 0.02, 0.55))
        self.drift = float(np.clip(self.rng.normal(0.10, 0.05), 0.0, 1.0))
        self.cooldown = 0.0
        return self.state()

    def step(self, action: int) -> tuple[np.ndarray, float, dict[str, float], bool]:
        cooldown_before = self.cooldown
        efficiency = 0.32 if cooldown_before > 0.26 and action >= 2 else 1.0
        if action == 1:
            self.residual *= 1.0 - efficiency * (1.0 - 0.79)
            self.drift *= 1.0 - efficiency * (1.0 - 0.83)
            self.cooldown = max(self.cooldown, 0.18)
        elif action == 2:
            self.residual *= 1.0 - efficiency * (1.0 - 0.55)
            self.drift *= 1.0 - efficiency * (1.0 - 0.60)
            self.buffer = min(1.0, self.buffer + 0.06 * efficiency)
            self.cooldown = max(self.cooldown, 0.36)
        elif action == 3:
            self.residual *= 1.0 - efficiency * (1.0 - 0.32)
            self.drift *= 1.0 - efficiency * (1.0 - 0.38)
            self.buffer = min(1.0, self.buffer + 0.13 * efficiency)
            self.cooldown = max(self.cooldown, 0.62)

        if self.rng.random() < 0.085:
            self.regime = int(self.rng.integers(3))
            self.drift = min(1.0, self.drift + self.rng.uniform(0.28, 0.55))
            self.residual = min(0.75, self.residual + self.rng.uniform(0.10, 0.28))

        target_throughput = [0.82, 0.58, 0.34][self.regime]
        self.throughput = float(np.clip(0.73 * self.throughput + 0.27 * target_throughput + self.rng.normal(0.0, 0.055), 0.05, 1.0))
        self.drift = float(np.clip(0.93 * self.drift + self.rng.normal(0.015, 0.025), 0.0, 1.0))
        self.residual = float(np.clip(0.91 * self.residual + 0.085 * self.drift + self.rng.normal(0.0, 0.018), 0.01, 0.9))
        self.buffer = float(np.clip(self.buffer + 0.10 * (self.throughput - 0.46) - 0.05 * self.drift + self.rng.normal(0.0, 0.028), 0.0, 1.0))
        self.cooldown = float(max(0.0, self.cooldown - 0.075))

        qoe = float(np.clip(0.48 * self.throughput + 0.42 * self.buffer + 0.18 * (1.0 - self.residual) - 0.12 * self.drift, 0.0, 1.0))
        outage = float(self.buffer < 0.11 or qoe < 0.34)
        fatigue = float(cooldown_before > 0.26 and action >= 2)
        reward = qoe - 0.78 * outage - ACTION_COST[action] - 0.11 * self.residual - 0.24 * fatigue
        self.t += 1
        done = self.t >= self.horizon
        info = {"qoe": qoe, "outage": outage, "residual": self.residual, "drift": self.drift, "action_cost": float(ACTION_COST[action])}
        return self.state(), float(reward), info, done


class TinyQNetwork:
    def __init__(self, rng: np.random.Generator) -> None:
        self.w1 = rng.normal(0.0, np.sqrt(2.0 / STATE_DIM), (STATE_DIM, HIDDEN))
        self.b1 = np.zeros(HIDDEN)
        self.w2 = rng.normal(0.0, np.sqrt(2.0 / HIDDEN), (HIDDEN, N_ACTIONS))
        self.b2 = np.zeros(N_ACTIONS)

    def copy_from(self, other: "TinyQNetwork") -> None:
        for name in ("w1", "b1", "w2", "b2"):
            setattr(self, name, getattr(other, name).copy())

    def forward(self, x: np.ndarray) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
        z1 = x @ self.w1 + self.b1
        h = np.maximum(z1, 0.0)
        q = h @ self.w2 + self.b2
        return z1, h, q

    def predict(self, x: np.ndarray) -> np.ndarray:
        return self.forward(x)[2]

    def train_batch(self, x: np.ndarray, actions: np.ndarray, targets: np.ndarray, lr: float = 0.0018) -> float:
        z1, h, q = self.forward(x)
        pred = q[np.arange(len(x)), actions]
        error = pred - targets
        grad_pred = np.where(np.abs(error) <= 1.0, error, np.sign(error)) / len(x)
        grad_q = np.zeros_like(q)
        grad_q[np.arange(len(x)), actions] = grad_pred
        grad_w2 = h.T @ grad_q
        grad_b2 = grad_q.sum(axis=0)
        grad_h = grad_q @ self.w2.T
        grad_z1 = grad_h * (z1 > 0.0)
        grad_w1 = x.T @ grad_z1
        grad_b1 = grad_z1.sum(axis=0)
        norm = np.sqrt(sum(float(np.square(g).sum()) for g in (grad_w1, grad_b1, grad_w2, grad_b2)))
        scale = min(1.0, 4.0 / (norm + 1e-12))
        self.w1 -= lr * grad_w1 * scale
        self.b1 -= lr * grad_b1 * scale
        self.w2 -= lr * grad_w2 * scale
        self.b2 -= lr * grad_b2 * scale
        return float(np.mean(np.where(np.abs(error) <= 1.0, 0.5 * np.square(error), np.abs(error) - 0.5)))


@dataclass
class Transition:
    state: np.ndarray
    action: int
    reward: float
    next_state: np.ndarray
    done: bool


def train(seed: int = 31, episodes: int = 420, horizon: int = 100) -> TinyQNetwork:
    rng = np.random.default_rng(seed)
    online = TinyQNetwork(rng)
    target = TinyQNetwork(np.random.default_rng(seed + 1))
    target.copy_from(online)
    replay: deque[Transition] = deque(maxlen=12000)
    gamma = 0.965
    batch_size = 64
    step_count = 0

    for episode in range(episodes):
        env = RecoveryEnv(seed + episode * 43, horizon=horizon)
        state = env.reset()
        epsilon = 0.035 + 0.965 * np.exp(-5.0 * episode / episodes)
        done = False
        while not done:
            if rng.random() < epsilon:
                action = int(rng.integers(N_ACTIONS))
            else:
                action = int(np.argmax(online.predict(state[None, :])[0]))
            next_state, reward, _, done = env.step(action)
            replay.append(Transition(state.copy(), action, reward, next_state.copy(), done))
            state = next_state
            step_count += 1
            if len(replay) >= batch_size:
                idx = rng.choice(len(replay), batch_size, replace=False)
                batch = [replay[int(i)] for i in idx]
                states = np.stack([t.state for t in batch])
                actions = np.array([t.action for t in batch], dtype=int)
                rewards = np.array([t.reward for t in batch], dtype=float)
                next_states = np.stack([t.next_state for t in batch])
                dones = np.array([t.done for t in batch], dtype=float)
                next_online = online.predict(next_states)
                best_actions = np.argmax(next_online, axis=1)
                next_target = target.predict(next_states)
                boot = next_target[np.arange(batch_size), best_actions]
                targets = rewards + gamma * (1.0 - dones) * boot
                online.train_batch(states, actions, targets)
            if step_count % 350 == 0:
                target.copy_from(online)
    return online


def learned_policy(model: TinyQNetwork) -> Callable[[np.ndarray, np.random.Generator], int]:
    return lambda state, _: int(np.argmax(model.predict(state[None, :])[0]))


def monitor_only(_: np.ndarray, __: np.random.Generator) -> int:
    return 0


def random_policy(_: np.ndarray, rng: np.random.Generator) -> int:
    return int(rng.integers(N_ACTIONS))


def threshold_policy(state: np.ndarray, _: np.random.Generator) -> int:
    throughput, buffer, residual, drift, cooldown = state
    if cooldown > 0.44:
        return 0
    if buffer < 0.13 or residual > 0.46 or drift > 0.68:
        return 3
    if residual > 0.30 or drift > 0.43:
        return 2
    if residual > 0.20 or drift > 0.26:
        return 1
    return 0


def evaluate(policy: Callable[[np.ndarray, np.random.Generator], int], seed: int, episodes: int = 90, horizon: int = 130) -> dict:
    rewards: list[float] = []
    qoes: list[float] = []
    outages: list[float] = []
    residuals: list[float] = []
    costs: list[float] = []
    counts = np.zeros(N_ACTIONS, dtype=int)
    for episode in range(episodes):
        env = RecoveryEnv(seed + episode * 79, horizon=horizon)
        rng = np.random.default_rng(seed + episode * 101)
        state = env.reset()
        done = False
        while not done:
            action = policy(state, rng)
            counts[action] += 1
            state, reward, info, done = env.step(action)
            rewards.append(reward)
            qoes.append(info["qoe"])
            outages.append(info["outage"])
            residuals.append(info["residual"])
            costs.append(info["action_cost"])
    total = counts.sum()
    return {
        "mean_reward": float(np.mean(rewards)),
        "mean_qoe": float(np.mean(qoes)),
        "outage_rate": float(np.mean(outages)),
        "mean_residual": float(np.mean(residuals)),
        "mean_action_cost": float(np.mean(costs)),
        "action_distribution": {ACTIONS[i]: float(counts[i] / total) for i in range(N_ACTIONS)},
    }


def run(seed: int = 31) -> dict:
    model = train(seed=seed)
    evaluations = {
        "double_dqn": evaluate(learned_policy(model), seed + 2000),
        "threshold": evaluate(threshold_policy, seed + 2000),
        "monitor_only": evaluate(monitor_only, seed + 2000),
        "random": evaluate(random_policy, seed + 2000),
    }
    learned = evaluations["double_dqn"]
    monitor = evaluations["monitor_only"]
    return {
        "project": "Double DQN for Drift-Aware QoE Recovery",
        "topic": "Deep Reinforcement Learning",
        "evidence_status": "Synthetic reproducible research prototype; not a production or safety-certified controller.",
        "seed": seed,
        "configuration": {
            "state_dim": STATE_DIM,
            "actions": ACTIONS,
            "hidden_units": HIDDEN,
            "training_episodes": 420,
            "algorithm": "Double DQN with replay and target network, implemented in NumPy",
        },
        "evaluations": evaluations,
        "headline": {
            "mean_qoe": learned["mean_qoe"],
            "outage_rate": learned["outage_rate"],
            "mean_residual": learned["mean_residual"],
            "reward_gain_vs_monitor_percent": 100.0 * (learned["mean_reward"] - monitor["mean_reward"]) / abs(monitor["mean_reward"]),
            "mean_action_cost": learned["mean_action_cost"],
        },
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--seed", type=int, default=31)
    parser.add_argument("--output", type=Path, default=Path("results.json"))
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    result = run(args.seed)
    args.output.write_text(json.dumps(result, indent=2), encoding="utf-8")
    if args.check:
        learned = result["evaluations"]["double_dqn"]
        monitor = result["evaluations"]["monitor_only"]
        assert learned["mean_reward"] > monitor["mean_reward"]
        assert learned["mean_reward"] > result["evaluations"]["random"]["mean_reward"]
        assert 0.0 <= learned["outage_rate"] <= 1.0
        assert sum(learned["action_distribution"].values()) > 0.999
    print(json.dumps(result["headline"], indent=2))


if __name__ == "__main__":
    main()
