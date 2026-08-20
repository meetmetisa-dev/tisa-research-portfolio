#!/usr/bin/env python3
"""Deterministic cooperative multi-agent reinforcement-learning prototype.

This educational portfolio experiment uses centralized joint-action Q-learning
for three cooperative resource agents. It is intentionally small, auditable,
and based on synthetic demand. It does not claim production performance.
"""
from __future__ import annotations

import argparse
import itertools
import json
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Callable

import numpy as np

N_AGENTS = 3
ACTION_LEVELS = np.array([0.35, 0.65, 1.00], dtype=float)
JOINT_ACTIONS = np.array(list(itertools.product(range(3), repeat=N_AGENTS)), dtype=int)
N_STATES = 3 ** N_AGENTS
N_ACTIONS = len(JOINT_ACTIONS)
CAPACITY = 2.15


@dataclass
class EpisodeMetrics:
    reward: float
    qoe: float
    overload_rate: float
    fairness: float
    energy: float


def state_index(demand: np.ndarray) -> int:
    bins = np.digitize(demand, bins=[0.48, 0.72]).astype(int)
    return int(bins[0] * 9 + bins[1] * 3 + bins[2])


def jain_index(values: np.ndarray) -> float:
    numerator = float(values.sum() ** 2)
    denominator = float(len(values) * np.square(values).sum() + 1e-12)
    return numerator / denominator


class CooperativeEdgeEnv:
    """Synthetic correlated-demand resource-allocation environment."""

    def __init__(self, seed: int, horizon: int = 120) -> None:
        self.rng = np.random.default_rng(seed)
        self.horizon = horizon
        self.t = 0
        self.demand = np.zeros(N_AGENTS, dtype=float)

    def reset(self) -> np.ndarray:
        regime = self.rng.choice([0.38, 0.58, 0.78], p=[0.25, 0.50, 0.25])
        self.demand = np.clip(regime + self.rng.normal(0.0, 0.08, N_AGENTS), 0.18, 1.0)
        self.t = 0
        return self.demand.copy()

    def step(self, joint_action_index: int) -> tuple[np.ndarray, float, dict[str, float], bool]:
        levels = ACTION_LEVELS[JOINT_ACTIONS[joint_action_index]]
        satisfaction = np.minimum(levels / np.maximum(self.demand, 0.08), 1.0)
        mean_qoe = float(satisfaction.mean())
        fairness = jain_index(satisfaction)
        overload = max(float(levels.sum() - CAPACITY), 0.0)
        energy = float(np.square(levels).mean())
        reward = mean_qoe - 0.62 * overload - 0.11 * energy - 0.26 * (1.0 - fairness)

        if self.rng.random() < 0.07:
            target = self.rng.choice([0.34, 0.56, 0.82], p=[0.25, 0.50, 0.25])
        else:
            target = float(self.demand.mean())
        common = self.rng.normal(0.0, 0.055)
        local = self.rng.normal(0.0, 0.05, N_AGENTS)
        self.demand = np.clip(0.72 * self.demand + 0.28 * target + common + local, 0.18, 1.0)
        self.t += 1
        done = self.t >= self.horizon
        info = {
            "qoe": mean_qoe,
            "overload": float(overload > 1e-12),
            "fairness": fairness,
            "energy": energy,
        }
        return self.demand.copy(), float(reward), info, done


def train(seed: int = 17, episodes: int = 2600, horizon: int = 120) -> np.ndarray:
    rng = np.random.default_rng(seed)
    q = np.zeros((N_STATES, N_ACTIONS), dtype=float)
    alpha, gamma = 0.10, 0.10
    epsilon_start, epsilon_end = 1.0, 0.04

    for episode in range(episodes):
        env = CooperativeEdgeEnv(seed + episode * 19, horizon=horizon)
        demand = env.reset()
        epsilon = epsilon_end + (epsilon_start - epsilon_end) * np.exp(-4.5 * episode / episodes)
        done = False
        while not done:
            s = state_index(demand)
            if rng.random() < epsilon:
                a = int(rng.integers(N_ACTIONS))
            else:
                best = np.flatnonzero(np.isclose(q[s], q[s].max()))
                a = int(rng.choice(best))
            next_demand, reward, _, done = env.step(a)
            ns = state_index(next_demand)
            target = reward if done else reward + gamma * float(q[ns].max())
            q[s, a] += alpha * (target - q[s, a])
            demand = next_demand
    return q


def learned_policy(q: np.ndarray) -> Callable[[np.ndarray, np.random.Generator], int]:
    def policy(demand: np.ndarray, rng: np.random.Generator) -> int:
        values = q[state_index(demand)]
        best = np.flatnonzero(np.isclose(values, values.max()))
        return int(rng.choice(best))
    return policy


def random_policy(_: np.ndarray, rng: np.random.Generator) -> int:
    return int(rng.integers(N_ACTIONS))


def fixed_balanced_policy(_: np.ndarray, __: np.random.Generator) -> int:
    return int(np.where((JOINT_ACTIONS == np.array([1, 1, 1])).all(axis=1))[0][0])


def demand_aware_policy(demand: np.ndarray, _: np.random.Generator) -> int:
    choices = np.abs(ACTION_LEVELS[:, None] - demand[None, :]).argmin(axis=0)
    while ACTION_LEVELS[choices].sum() > CAPACITY:
        candidates = np.where(choices > 0)[0]
        if not len(candidates):
            break
        idx = candidates[np.argmin(demand[candidates])]
        choices[idx] -= 1
    return int(np.where((JOINT_ACTIONS == choices).all(axis=1))[0][0])


def evaluate(policy: Callable[[np.ndarray, np.random.Generator], int], seed: int, episodes: int = 80, horizon: int = 160) -> EpisodeMetrics:
    episode_rows: list[EpisodeMetrics] = []
    for episode in range(episodes):
        env = CooperativeEdgeEnv(seed + episode * 97, horizon=horizon)
        rng = np.random.default_rng(seed + episode * 131)
        demand = env.reset()
        rewards: list[float] = []
        qoes: list[float] = []
        overloads: list[float] = []
        fairness: list[float] = []
        energy: list[float] = []
        done = False
        while not done:
            action = policy(demand, rng)
            demand, reward, info, done = env.step(action)
            rewards.append(reward)
            qoes.append(info["qoe"])
            overloads.append(info["overload"])
            fairness.append(info["fairness"])
            energy.append(info["energy"])
        episode_rows.append(EpisodeMetrics(
            reward=float(np.mean(rewards)),
            qoe=float(np.mean(qoes)),
            overload_rate=float(np.mean(overloads)),
            fairness=float(np.mean(fairness)),
            energy=float(np.mean(energy)),
        ))
    return EpisodeMetrics(**{
        field: float(np.mean([getattr(row, field) for row in episode_rows]))
        for field in EpisodeMetrics.__dataclass_fields__
    })


def run(seed: int = 17) -> dict:
    q = train(seed=seed)
    policies = {
        "learned_joint_q": learned_policy(q),
        "demand_aware_heuristic": demand_aware_policy,
        "fixed_balanced": fixed_balanced_policy,
        "random": random_policy,
    }
    evaluations = {name: asdict(evaluate(policy, seed=seed + 1000)) for name, policy in policies.items()}
    learned = evaluations["learned_joint_q"]
    random = evaluations["random"]
    fixed = evaluations["fixed_balanced"]
    return {
        "project": "Cooperative Edge QoE Control",
        "topic": "Multi-Agent Reinforcement Learning",
        "evidence_status": "Synthetic reproducible research prototype; not peer-reviewed or production validated.",
        "seed": seed,
        "environment": {
            "agents": N_AGENTS,
            "states": N_STATES,
            "joint_actions": N_ACTIONS,
            "capacity": CAPACITY,
            "training_episodes": 2600,
        },
        "evaluations": evaluations,
        "headline": {
            "learned_mean_reward": learned["reward"],
            "reward_gain_vs_random_percent": 100.0 * (learned["reward"] - random["reward"]) / abs(random["reward"]),
            "reward_gap_vs_fixed_percent": 100.0 * (learned["reward"] - fixed["reward"]) / abs(fixed["reward"]),
            "learned_mean_qoe": learned["qoe"],
            "learned_overload_rate": learned["overload_rate"],
            "learned_fairness": learned["fairness"],
        },
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--seed", type=int, default=17)
    parser.add_argument("--output", type=Path, default=Path("results.json"))
    parser.add_argument("--check", action="store_true", help="Fail if basic scientific sanity checks do not hold.")
    args = parser.parse_args()
    result = run(args.seed)
    args.output.write_text(json.dumps(result, indent=2), encoding="utf-8")
    if args.check:
        learned = result["evaluations"]["learned_joint_q"]
        random = result["evaluations"]["random"]
        assert learned["reward"] > random["reward"], "learned policy must outperform random"
        assert 0.0 <= learned["fairness"] <= 1.0
        assert 0.0 <= learned["overload_rate"] <= 1.0
    print(json.dumps(result["headline"], indent=2))


if __name__ == "__main__":
    main()
