# QoE Foresight Repro

> A leakage-safe, uncertainty-aware reproduction and stress test of multimodal streaming Quality of Experience inference.

## Research question

Can a QoE model trained on network, playback and affective signals generalize to **unseen participants**, rather than memorize participant-specific response patterns through a random-row split?

## What the demonstration implements

- seeded, schema-compatible synthetic streaming sessions;
- participant-grouped train/test partitioning with a hard zero-overlap assertion;
- a small ridge baseline trained only on training rows;
- RMSE, MAE, worst-participant MAE and within-0.5-MOS coverage;
- comparison against a constant training-mean baseline;
- explicit disclosure of data, consent and external-validity limits.

```bash
PYTHONPATH=src python3 -m tisa_portfolio.qoe_repro --out reports/qoe-foresight-repro.json
```

## Real-data extension

1. Publish only derived, de-identified features when participant consent and the relevant ethics approval permit it.
2. Fit feature selection, scaling, resampling and calibration **inside** each training fold.
3. Hold out participants and content together; add device/network domain holdouts.
4. Report macro-F1 or ordinal MAE as appropriate, Brier score/ECE, bootstrap confidence intervals, worst-group performance and inference latency.
5. Preserve unrelated datasets as separate adapters; do not imply that Puffer, DAiSEE and private AELIX sessions share a joint ground truth.

## Role relevance

The project bridges Tisa Selma's published QoE and multimodal work to teams working on video understanding, trustworthy learning, uncertainty and networked systems.

See [DATA_CARD.md](DATA_CARD.md), [MODEL_CARD.md](MODEL_CARD.md) and [REPRODUCIBILITY.md](REPRODUCIBILITY.md).
