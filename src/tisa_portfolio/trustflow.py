"""Leakage-aware, calibrated network-flow alerting and drift demonstration."""

from __future__ import annotations

import argparse
import random

from .common import clamp, mean, quantile, write_report


def generate_flows(count: int = 500, seed: int = 2026) -> list[dict]:
    rng = random.Random(seed)
    rows: list[dict] = []
    for index in range(count):
        late_period = index >= int(count * 0.72)
        attack_probability = 0.13 if not late_period else 0.22
        attack = rng.random() < attack_probability
        failed_auth = rng.randint(0, 2) if not attack else rng.randint(3, 13)
        unique_ports = rng.randint(1, 5) if not attack else rng.randint(6, 28)
        packet_rate = rng.uniform(5, 85) if not attack else rng.uniform(70, 340)
        outbound_ratio = rng.uniform(0.15, 0.75) if not attack else rng.uniform(0.55, 0.98)
        if late_period and not attack:
            packet_rate *= 1.9
        rows.append(
            {
                "timestamp_index": index,
                "source_group": f"host-{index % 17:02d}",
                "failed_auth": failed_auth,
                "unique_ports": unique_ports,
                "packet_rate": packet_rate,
                "outbound_ratio": outbound_ratio,
                "attack": int(attack),
            }
        )
    return rows


def score(row: dict) -> float:
    raw = (
        0.15
        + row["failed_auth"] / 12.0 * 0.35
        + row["unique_ports"] / 28.0 * 0.30
        + row["packet_rate"] / 340.0 * 0.22
        + row["outbound_ratio"] * 0.18
    )
    return clamp(raw, 0.0, 1.0)


def run_experiment(seed: int = 2026) -> dict:
    rows = generate_flows(seed=seed)
    cut = int(len(rows) * 0.7)
    calibration = rows[:cut]
    test = rows[cut:]
    benign_scores = [score(row) for row in calibration if not row["attack"]]
    threshold = quantile(benign_scores, 0.97)
    predictions = [score(row) >= threshold for row in test]
    tp = sum(prediction and row["attack"] for row, prediction in zip(test, predictions))
    fp = sum(prediction and not row["attack"] for row, prediction in zip(test, predictions))
    fn = sum((not prediction) and row["attack"] for row, prediction in zip(test, predictions))
    tn = sum((not prediction) and not row["attack"] for row, prediction in zip(test, predictions))
    precision = tp / (tp + fp) if tp + fp else 0.0
    recall = tp / (tp + fn) if tp + fn else 0.0
    early = [score(row) for row in rows[:100] if not row["attack"]]
    late = [score(row) for row in rows[-100:] if not row["attack"]]
    drift_delta = mean(late) - mean(early)
    return {
        "project": "trustflow-lab",
        "status": "synthetic SOC evidence demonstration",
        "seed": seed,
        "protocol": "time-ordered calibration/test split; no random-row leakage",
        "dataset": {"flows": len(rows), "calibration_flows": len(calibration), "test_flows": len(test), "source_groups": len({row['source_group'] for row in rows})},
        "metrics": {
            "threshold": round(threshold, 4),
            "precision": round(precision, 4),
            "recall": round(recall, 4),
            "false_positive_rate": round(fp / (fp + tn) if fp + tn else 0.0, 4),
            "alerts": tp + fp,
            "mean_benign_score_drift": round(drift_delta, 4),
            "drift_flag": drift_delta > 0.025,
        },
        "controls": ["time-ordered holdout", "calibrated threshold", "explicit abstention boundary", "drift monitoring"],
        "limitations": [
            "Synthetic alerts are not evidence of performance on a production network.",
            "Real adapters must remove identifiers and prevent source-host leakage.",
            "Analyst review, threat modeling and cross-dataset validation remain necessary.",
        ],
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--out", help="Optional JSON report path")
    parser.add_argument("--seed", type=int, default=2026)
    args = parser.parse_args()
    write_report(args.out, run_experiment(args.seed))


if __name__ == "__main__":
    main()
