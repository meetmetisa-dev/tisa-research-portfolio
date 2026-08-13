"""Communication-aware federated QoE learning on non-IID synthetic clients."""

from __future__ import annotations

import argparse
import random

from .common import mean, rmse, write_report


def generate_clients(client_count: int = 8, samples_per_client: int = 45, seed: int = 2026) -> list[list[tuple[list[float], float]]]:
    rng = random.Random(seed)
    clients: list[list[tuple[list[float], float]]] = []
    true_weights = [0.72, -0.58, -0.91]
    for client in range(client_count):
        shift = (client - (client_count - 1) / 2) * 0.06
        rows: list[tuple[list[float], float]] = []
        for _ in range(samples_per_client):
            throughput = rng.uniform(0.2, 1.8) + shift
            latency = rng.uniform(0.1, 1.9) - shift / 2
            rebuffer = max(0.0, rng.gauss(0.45 + shift, 0.3))
            features = [throughput, latency, rebuffer]
            target = 3.15 + sum(w * x for w, x in zip(true_weights, features)) + shift + rng.gauss(0, 0.12)
            rows.append((features, target))
        clients.append(rows)
    return clients


def _predict(weights: list[float], bias: float, features: list[float]) -> float:
    return bias + sum(weight * value for weight, value in zip(weights, features))


def _client_update(rows: list[tuple[list[float], float]], weights: list[float], bias: float, learning_rate: float, epochs: int) -> tuple[list[float], float]:
    local_weights = weights[:]
    local_bias = bias
    for _ in range(epochs):
        grad_w = [0.0] * len(local_weights)
        grad_b = 0.0
        for features, target in rows:
            error = _predict(local_weights, local_bias, features) - target
            for index, value in enumerate(features):
                grad_w[index] += 2 * error * value / len(rows)
            grad_b += 2 * error / len(rows)
        local_weights = [weight - learning_rate * grad for weight, grad in zip(local_weights, grad_w)]
        local_bias -= learning_rate * grad_b
    return local_weights, local_bias


def _evaluate(clients: list[list[tuple[list[float], float]]], weights: list[float], bias: float) -> tuple[float, float]:
    client_errors = []
    for rows in clients:
        actual = [target for _, target in rows]
        predicted = [_predict(weights, bias, features) for features, _ in rows]
        client_errors.append(rmse(actual, predicted))
    return mean(client_errors), max(client_errors)


def run_experiment(seed: int = 2026, rounds: int = 24, quantization_bits: int = 16) -> dict:
    rng = random.Random(seed + 7)
    clients = generate_clients(seed=seed)
    weights = [0.0, 0.0, 0.0]
    bias = 0.0
    initial_rmse, initial_worst = _evaluate(clients, weights, bias)
    communication_bytes = 0
    participation = []
    for round_index in range(rounds):
        active = [index for index in range(len(clients)) if rng.random() > (0.05 + (index % 3) * 0.03)]
        if not active:
            active = [round_index % len(clients)]
        updates = [_client_update(clients[index], weights, bias, learning_rate=0.035, epochs=2) for index in active]
        weights = [mean(update[0][dimension] for update in updates) for dimension in range(len(weights))]
        bias = mean(update[1] for update in updates)
        communication_bytes += len(active) * (len(weights) + 1) * quantization_bits // 8
        participation.append(len(active))
    final_rmse, final_worst = _evaluate(clients, weights, bias)
    uncompressed_bytes = sum(participation) * (len(weights) + 1) * 4
    return {
        "project": "fedqoe-bench",
        "status": "synthetic non-IID federated systems demonstration",
        "seed": seed,
        "scenario": {"clients": len(clients), "rounds": rounds, "quantization_bits": quantization_bits, "mean_clients_per_round": round(mean(participation), 2)},
        "metrics": {
            "initial_client_mean_rmse": round(initial_rmse, 4),
            "final_client_mean_rmse": round(final_rmse, 4),
            "initial_worst_client_rmse": round(initial_worst, 4),
            "final_worst_client_rmse": round(final_worst, 4),
            "communication_bytes": communication_bytes,
            "uncompressed_reference_bytes": uncompressed_bytes,
            "communication_reduction": round(1 - communication_bytes / uncompressed_bytes, 4),
        },
        "learned_parameters": {"weights": [round(value, 4) for value in weights], "bias": round(bias, 4)},
        "limitations": [
            "Federated learning does not provide privacy by itself; gradient leakage remains possible.",
            "This CPU simulation models communication accounting but not real network latency or failures.",
            "Real evaluation needs device-level energy, wall-clock time and fairness metrics.",
        ],
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--out", help="Optional JSON report path")
    parser.add_argument("--seed", type=int, default=2026)
    parser.add_argument("--rounds", type=int, default=24)
    parser.add_argument("--bits", type=int, default=16, choices=(8, 16, 32))
    args = parser.parse_args()
    write_report(args.out, run_experiment(args.seed, args.rounds, args.bits))


if __name__ == "__main__":
    main()
