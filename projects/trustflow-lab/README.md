# TrustFlow Lab

> From benchmark accuracy to defensible SOC evidence: leakage-aware splits, calibrated alerts, false-positive rates and drift.

## Research question

Can an intrusion-detection experiment surface operational risks—false alarms, threshold calibration, temporal shift and abstention—instead of marketing a single near-perfect accuracy number?

## Demonstration

The simulator creates a time-ordered stream of benign and attack-like flow aggregates. The first period calibrates a threshold on benign behavior; the later period evaluates alerts and monitors benign-score drift.

```bash
PYTHONPATH=src python3 -m tisa_portfolio.trustflow --out reports/trustflow-lab.json
```

## Real-data adapters

Adapters can target CIC-IDS2017, UNSW-NB15 or TON_IoT without committing the large raw datasets. A defensible experiment must prevent source-host and temporal leakage, document duplicated flows, calibrate on training data only and test cross-dataset transfer.

## Operational deliverables

- PR-AUC, recall and false-positive rate at an explicit threshold;
- time-to-detect, p95 scoring latency and throughput;
- calibrated confidence and abstention;
- explanation and drift panels;
- SOC runbook for analyst review and rollback.

See [DATA_CARD.md](DATA_CARD.md), [MODEL_CARD.md](MODEL_CARD.md) and [REPRODUCIBILITY.md](REPRODUCIBILITY.md).
