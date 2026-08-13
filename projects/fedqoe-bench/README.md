# FedQoE Bench

> A systems benchmark for the accuracy–communication–fairness trade space in distributed QoE learning.

## Research question

How does non-IID client variation affect model quality, worst-client error and communication cost when QoE models are trained collaboratively?

## Demonstration

Eight seeded synthetic clients train a small model with local SGD and federated averaging. Clients have heterogeneous feature distributions and probabilistic dropout. The report includes initial/final mean and worst-client RMSE, participation, bytes transferred and a 32-bit communication reference.

```bash
PYTHONPATH=src python3 -m tisa_portfolio.fedqoe --rounds 24 --bits 16 --out reports/fedqoe-bench.json
```

## Why it matters

The prototype converts Tisa's networked-multimedia background into concrete evidence for distributed-ML systems teams. It also states the crucial limitation that federation alone is **not** a privacy guarantee.

## Full benchmark roadmap

- real Flower/PyTorch or TensorFlow clients in containers;
- fixed IID, non-IID, dropout and slow-client scenarios;
- centralized and local-only baselines;
- bytes, rounds-to-target, p50/p95 time, energy and worst-client metrics;
- secure aggregation and differential privacy only when actually implemented and measured.

See [DATA_CARD.md](DATA_CARD.md), [MODEL_CARD.md](MODEL_CARD.md) and [REPRODUCIBILITY.md](REPRODUCIBILITY.md).
