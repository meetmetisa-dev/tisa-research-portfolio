"""Encrypted-flow metadata simulation for privacy-preserving QoE inference."""

from __future__ import annotations

import argparse
import random

from .common import clamp, mae, mean, write_report

PUBLIC_METADATA_FIELDS = (
    "duration_s",
    "down_bytes",
    "up_bytes",
    "packet_count",
    "mean_packet_bytes",
    "rtt_ms",
    "burstiness",
)


def generate_flows(count: int = 240, seed: int = 2026) -> list[dict]:
    rng = random.Random(seed)
    flows: list[dict] = []
    for _ in range(count):
        bandwidth = rng.uniform(1.0, 28.0)
        rtt = rng.uniform(15.0, 240.0)
        congestion = rng.uniform(0.0, 1.0)
        duration = rng.uniform(25.0, 95.0)
        bitrate = max(0.45, min(bandwidth * (0.48 + rng.uniform(-0.08, 0.08)), 12.0))
        down_bytes = int(bitrate * 1_000_000 / 8 * duration)
        mean_packet = rng.uniform(920.0, 1360.0)
        packet_count = max(1, int(down_bytes / mean_packet))
        up_bytes = int(packet_count * rng.uniform(35.0, 62.0))
        burstiness = clamp(0.18 + congestion * 0.7 + rng.gauss(0, 0.04), 0.0, 1.0)
        startup = clamp(0.55 + 0.012 * rtt + 2.1 / max(bandwidth, 0.5) + congestion * 0.6 + rng.gauss(0, 0.11), 0.25, 6.0)
        stalls = clamp((5.2 - bandwidth) * 0.18 + congestion * 1.7 + rng.gauss(0, 0.18), 0.0, 5.0)
        bitrate_class = 0 if bitrate < 2.0 else 1 if bitrate < 5.0 else 2
        flows.append(
            {
                "duration_s": duration,
                "down_bytes": down_bytes,
                "up_bytes": up_bytes,
                "packet_count": packet_count,
                "mean_packet_bytes": mean_packet,
                "rtt_ms": rtt,
                "burstiness": burstiness,
                "startup_delay_s": startup,
                "stall_seconds": stalls,
                "bitrate_class": bitrate_class,
            }
        )
    return flows


def infer(flow: dict) -> tuple[float, float, int]:
    observed_mbps = flow["down_bytes"] * 8 / flow["duration_s"] / 1_000_000
    estimated_bandwidth = observed_mbps / 0.48
    startup = clamp(0.58 + 0.0115 * flow["rtt_ms"] + 2.0 / max(estimated_bandwidth, 0.5) + flow["burstiness"] * 0.58, 0.25, 6.0)
    stalls = clamp((5.0 - estimated_bandwidth) * 0.17 + flow["burstiness"] * 1.65, 0.0, 5.0)
    # A deployment never observes the encoder's exact bitrate boundary.  The
    # deliberately shifted thresholds make the synthetic evaluation non-trivial.
    adjusted_mbps = observed_mbps * (1.0 - 0.06 * flow["burstiness"])
    bitrate_class = 0 if adjusted_mbps < 2.15 else 1 if adjusted_mbps < 5.25 else 2
    return startup, stalls, bitrate_class


def run_experiment(seed: int = 2026) -> dict:
    flows = generate_flows(seed=seed)
    predictions = [infer(flow) for flow in flows]
    startup_actual = [flow["startup_delay_s"] for flow in flows]
    stall_actual = [flow["stall_seconds"] for flow in flows]
    return {
        "project": "cipherqoe",
        "status": "synthetic encrypted-flow metadata demonstration",
        "seed": seed,
        "dataset": {"flows": len(flows), "payload_bytes_inspected": 0, "fields": list(PUBLIC_METADATA_FIELDS)},
        "metrics": {
            "startup_delay_mae_s": round(mae(startup_actual, [item[0] for item in predictions]), 4),
            "stall_duration_mae_s": round(mae(stall_actual, [item[1] for item in predictions]), 4),
            "bitrate_class_accuracy": round(mean(flow["bitrate_class"] == prediction[2] for flow, prediction in zip(flows, predictions)), 4),
        },
        "privacy_boundary": "Only timestamps, directions, sizes, counts and aggregate flow statistics are modeled; payload inspection is excluded.",
        "limitations": [
            "Synthetic sessions do not reproduce every HTTPS/QUIC implementation or network path.",
            "Real validation should hold out content, device, network and protocol versions.",
            "Metadata can remain sensitive and requires minimization, retention limits and access controls.",
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
