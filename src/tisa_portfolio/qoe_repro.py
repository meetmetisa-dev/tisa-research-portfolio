"""Leakage-aware synthetic reproduction of multimodal streaming QoE inference."""

from __future__ import annotations

import argparse
import random
from collections import defaultdict

from .common import clamp, fit_ridge, mae, mean, predict_ridge, rmse, write_report

FEATURES = ("throughput_mbps", "rtt_ms", "rebuffer_s", "emotion_valence", "ad_exposure")


def generate_sessions(n_subjects: int = 30, sessions_per_subject: int = 10, seed: int = 2026) -> list[dict]:
    rng = random.Random(seed)
    rows: list[dict] = []
    for subject in range(n_subjects):
        subject_bias = rng.gauss(0.0, 0.28)
        for session in range(sessions_per_subject):
            throughput = rng.uniform(1.2, 24.0)
            rtt = rng.uniform(18.0, 220.0)
            rebuffer = max(0.0, rng.gauss(max(0.0, 2.4 - throughput / 7.0), 0.55))
            valence = clamp(rng.gauss(0.18 - rebuffer * 0.13, 0.43), -1.0, 1.0)
            ad_exposure = 1 if rng.random() < 0.36 else 0
            content_effect = ((session % 4) - 1.5) * 0.08
            mos = clamp(
                2.65
                + 0.085 * throughput
                - 0.0045 * rtt
                - 0.48 * rebuffer
                + 0.45 * valence
                - 0.25 * ad_exposure
                + subject_bias
                + content_effect
                + rng.gauss(0.0, 0.16),
                1.0,
                5.0,
            )
            rows.append(
                {
                    "subject_id": f"P{subject:03d}",
                    "content_id": f"C{session % 4}",
                    "throughput_mbps": throughput,
                    "rtt_ms": rtt,
                    "rebuffer_s": rebuffer,
                    "emotion_valence": valence,
                    "ad_exposure": ad_exposure,
                    "mos": mos,
                }
            )
    return rows


def grouped_split(rows: list[dict], test_fraction: float = 0.2) -> tuple[list[dict], list[dict]]:
    subjects = sorted({row["subject_id"] for row in rows})
    test_count = max(1, round(len(subjects) * test_fraction))
    test_subjects = {subject for index, subject in enumerate(subjects) if index % max(1, len(subjects) // test_count) == 0}
    test_subjects = set(sorted(test_subjects)[:test_count])
    train = [row for row in rows if row["subject_id"] not in test_subjects]
    test = [row for row in rows if row["subject_id"] in test_subjects]
    return train, test


def _feature_rows(rows: list[dict]) -> list[list[float]]:
    return [
        [
            row["throughput_mbps"] / 10.0,
            row["rtt_ms"] / 100.0,
            row["rebuffer_s"],
            row["emotion_valence"],
            float(row["ad_exposure"]),
        ]
        for row in rows
    ]


def run_experiment(seed: int = 2026) -> dict:
    rows = generate_sessions(seed=seed)
    train, test = grouped_split(rows)
    train_subjects = {row["subject_id"] for row in train}
    test_subjects = {row["subject_id"] for row in test}
    weights = fit_ridge(_feature_rows(train), [row["mos"] for row in train], ridge=1.0)
    predictions = [clamp(value, 1.0, 5.0) for value in predict_ridge(weights, _feature_rows(test))]
    actual = [row["mos"] for row in test]
    residuals = [a - p for a, p in zip(actual, predictions)]
    per_subject: dict[str, list[float]] = defaultdict(list)
    for row, residual in zip(test, residuals):
        per_subject[row["subject_id"]].append(abs(residual))
    baseline = [mean(row["mos"] for row in train)] * len(test)
    return {
        "project": "qoe-foresight-repro",
        "status": "synthetic reproducibility demonstration",
        "seed": seed,
        "protocol": "participant-grouped holdout; preprocessing fitted on training rows only",
        "dataset": {
            "sessions": len(rows),
            "train_sessions": len(train),
            "test_sessions": len(test),
            "train_subjects": len(train_subjects),
            "test_subjects": len(test_subjects),
            "subject_overlap": len(train_subjects & test_subjects),
        },
        "metrics": {
            "model_rmse": round(rmse(actual, predictions), 4),
            "baseline_rmse": round(rmse(actual, baseline), 4),
            "model_mae": round(mae(actual, predictions), 4),
            "worst_subject_mae": round(max(mean(values) for values in per_subject.values()), 4),
            "within_half_mos": round(mean(abs(a - p) <= 0.5 for a, p in zip(actual, predictions)), 4),
        },
        "weights": {name: round(weight, 4) for name, weight in zip(("intercept", *FEATURES), weights)},
        "limitations": [
            "Synthetic data validates the evaluation pipeline, not real-world accuracy.",
            "Public release of facial or participant data requires consent and ethics review.",
            "External validation across devices, networks, and content remains required.",
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
