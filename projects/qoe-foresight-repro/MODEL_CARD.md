# Model card — QoE Foresight Repro

The demonstration uses a dependency-free ridge regression baseline. It is intentionally interpretable and not presented as a state-of-the-art model.

## Intended use

Validate a leakage-aware evaluation pipeline and establish a transparent baseline before introducing temporal, multimodal or probabilistic models.

## Out-of-scope use

Do not use the model for customer scoring, emotion surveillance, health inference, employment decisions or individualized service changes.

## Evaluation requirements for a real study

- participant/content grouped nested validation;
- calibration and uncertainty intervals;
- worst-group and domain-shift analysis;
- ablation of affective inputs;
- comparison with metadata-only baselines;
- latency, memory and energy measurements.
