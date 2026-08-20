#!/usr/bin/env python3
"""Deterministic non-IID federated-learning benchmark using NumPy.

The experiment implements weighted FedAvg for logistic regression across eight
synthetic sites. It reports mean and worst-client performance, dispersion, and
communication accounting. Local data remain local in the simulation, but this
is not a formal privacy guarantee.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path

import numpy as np

N_CLIENTS = 8
N_FEATURES = 12
TRAIN_PER_CLIENT = 420
TEST_PER_CLIENT = 220
ROUNDS = 36
LOCAL_EPOCHS = 3
LEARNING_RATE = 0.075
CLIP_NORM = 1.25


def sigmoid(z: np.ndarray) -> np.ndarray:
    z = np.clip(z, -30.0, 30.0)
    return 1.0 / (1.0 + np.exp(-z))


def add_bias(x: np.ndarray) -> np.ndarray:
    return np.column_stack([x, np.ones(len(x), dtype=float)])


def make_clients(seed: int) -> tuple[list[tuple[np.ndarray, np.ndarray]], list[tuple[np.ndarray, np.ndarray]]]:
    rng = np.random.default_rng(seed)
    true_w = rng.normal(0.0, 0.95, N_FEATURES)
    train_clients: list[tuple[np.ndarray, np.ndarray]] = []
    test_clients: list[tuple[np.ndarray, np.ndarray]] = []
    for client in range(N_CLIENTS):
        shift = rng.normal(0.0, 0.38, N_FEATURES)
        scale = rng.uniform(0.72, 1.35, N_FEATURES)
        label_bias = np.linspace(-0.50, 0.50, N_CLIENTS)[client]
        rotation = rng.normal(0.0, 0.04, N_FEATURES)

        def sample(n: int) -> tuple[np.ndarray, np.ndarray]:
            x = rng.normal(0.0, 1.0, (n, N_FEATURES)) * scale + shift
            logits = x @ (true_w + rotation) / 1.85 + label_bias
            logits += rng.normal(0.0, 0.28, n)
            y = (rng.random(n) < sigmoid(logits)).astype(float)
            return add_bias(x), y

        train_clients.append(sample(TRAIN_PER_CLIENT))
        test_clients.append(sample(TEST_PER_CLIENT))
    return train_clients, test_clients


def loss_and_grad(w: np.ndarray, x: np.ndarray, y: np.ndarray) -> tuple[float, np.ndarray]:
    p = sigmoid(x @ w)
    eps = 1e-9
    loss = float(-np.mean(y * np.log(p + eps) + (1.0 - y) * np.log(1.0 - p + eps)))
    grad = x.T @ (p - y) / len(y)
    return loss, grad


def local_train(global_w: np.ndarray, x: np.ndarray, y: np.ndarray, rng: np.random.Generator) -> np.ndarray:
    w = global_w.copy()
    batch_size = 64
    for _ in range(LOCAL_EPOCHS):
        order = rng.permutation(len(y))
        for start in range(0, len(y), batch_size):
            idx = order[start:start + batch_size]
            _, grad = loss_and_grad(w, x[idx], y[idx])
            norm = float(np.linalg.norm(grad))
            if norm > CLIP_NORM:
                grad *= CLIP_NORM / (norm + 1e-12)
            w -= LEARNING_RATE * grad
    return w


def client_accuracy(w: np.ndarray, dataset: tuple[np.ndarray, np.ndarray]) -> float:
    x, y = dataset
    pred = (sigmoid(x @ w) >= 0.5).astype(float)
    return float(np.mean(pred == y))


def weighted_fedavg(seed: int, train_clients: list[tuple[np.ndarray, np.ndarray]], test_clients: list[tuple[np.ndarray, np.ndarray]]) -> tuple[np.ndarray, list[dict]]:
    global_w = np.zeros(N_FEATURES + 1, dtype=float)
    history: list[dict] = []
    sizes = np.array([len(y) for _, y in train_clients], dtype=float)
    weights = sizes / sizes.sum()
    for round_idx in range(ROUNDS):
        local_models = []
        for client_idx, (x, y) in enumerate(train_clients):
            rng = np.random.default_rng(seed + round_idx * 1009 + client_idx * 53)
            local_models.append(local_train(global_w, x, y, rng))
        global_w = np.sum(np.stack(local_models) * weights[:, None], axis=0)
        accuracies = [client_accuracy(global_w, ds) for ds in test_clients]
        history.append({
            "round": round_idx + 1,
            "mean_accuracy": float(np.mean(accuracies)),
            "worst_client_accuracy": float(np.min(accuracies)),
            "std_accuracy": float(np.std(accuracies)),
        })
    return global_w, history


def centralized_oracle(train_clients: list[tuple[np.ndarray, np.ndarray]], seed: int) -> np.ndarray:
    x = np.vstack([item[0] for item in train_clients])
    y = np.concatenate([item[1] for item in train_clients])
    w = np.zeros(N_FEATURES + 1, dtype=float)
    rng = np.random.default_rng(seed + 991)
    for _ in range(24):
        order = rng.permutation(len(y))
        for start in range(0, len(y), 128):
            idx = order[start:start + 128]
            _, grad = loss_and_grad(w, x[idx], y[idx])
            w -= LEARNING_RATE * grad
    return w


def local_only_models(train_clients: list[tuple[np.ndarray, np.ndarray]], seed: int) -> list[np.ndarray]:
    models = []
    zero = np.zeros(N_FEATURES + 1, dtype=float)
    for client_idx, (x, y) in enumerate(train_clients):
        models.append(local_train(zero, x, y, np.random.default_rng(seed + 5000 + client_idx)))
    return models


def summarize(w: np.ndarray, test_clients: list[tuple[np.ndarray, np.ndarray]]) -> dict:
    acc = [client_accuracy(w, ds) for ds in test_clients]
    return {
        "client_accuracies": acc,
        "mean_accuracy": float(np.mean(acc)),
        "worst_client_accuracy": float(np.min(acc)),
        "best_client_accuracy": float(np.max(acc)),
        "std_accuracy": float(np.std(acc)),
    }


def run(seed: int = 23) -> dict:
    train_clients, test_clients = make_clients(seed)
    fed_w, history = weighted_fedavg(seed, train_clients, test_clients)
    central_w = centralized_oracle(train_clients, seed)
    local_models = local_only_models(train_clients, seed)

    fed = summarize(fed_w, test_clients)
    central = summarize(central_w, test_clients)
    local_acc = [client_accuracy(local_models[i], test_clients[i]) for i in range(N_CLIENTS)]
    local = {
        "client_accuracies": local_acc,
        "mean_accuracy": float(np.mean(local_acc)),
        "worst_client_accuracy": float(np.min(local_acc)),
        "best_client_accuracy": float(np.max(local_acc)),
        "std_accuracy": float(np.std(local_acc)),
    }
    bytes_per_vector = (N_FEATURES + 1) * 8
    communication_bytes = ROUNDS * N_CLIENTS * bytes_per_vector * 2
    return {
        "project": "Non-IID Multisite FedAvg",
        "topic": "Federated Learning",
        "evidence_status": "Synthetic reproducible research prototype; local simulation is not a formal privacy guarantee.",
        "seed": seed,
        "configuration": {
            "clients": N_CLIENTS,
            "features_plus_bias": N_FEATURES + 1,
            "train_samples_per_client": TRAIN_PER_CLIENT,
            "test_samples_per_client": TEST_PER_CLIENT,
            "rounds": ROUNDS,
            "local_epochs": LOCAL_EPOCHS,
            "clip_norm": CLIP_NORM,
        },
        "fedavg": fed,
        "centralized_oracle": central,
        "local_only": local,
        "history": history,
        "communication": {
            "simulated_total_bytes": communication_bytes,
            "simulated_total_kib": communication_bytes / 1024.0,
            "accounting": "one float64 model upload and one download per client per round",
        },
        "headline": {
            "mean_client_accuracy": fed["mean_accuracy"],
            "worst_client_accuracy": fed["worst_client_accuracy"],
            "cross_client_std": fed["std_accuracy"],
            "simulated_communication_kib": communication_bytes / 1024.0,
            "gap_to_centralized_mean_percentage_points": 100.0 * (central["mean_accuracy"] - fed["mean_accuracy"]),
        },
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--seed", type=int, default=23)
    parser.add_argument("--output", type=Path, default=Path("results.json"))
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    result = run(args.seed)
    args.output.write_text(json.dumps(result, indent=2), encoding="utf-8")
    if args.check:
        assert result["fedavg"]["mean_accuracy"] >= 0.75
        assert result["fedavg"]["worst_client_accuracy"] >= 0.60
        assert result["communication"]["simulated_total_bytes"] > 0
    print(json.dumps(result["headline"], indent=2))


if __name__ == "__main__":
    main()
