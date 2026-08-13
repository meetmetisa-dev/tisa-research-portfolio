# Data card — QoE Foresight Repro

## Current fixture

The repository generates 300 synthetic sessions across 30 synthetic participants and four content identifiers. Features are throughput, RTT, rebuffer duration, affective valence and advertisement exposure; the target is a bounded 1–5 MOS-like score.

The fixture exists to test split logic, training isolation and report generation. It is not a representative population sample and must not be used to claim human performance.

## Sensitive-data boundary

No faces, audio, payloads, names, device identifiers or raw participant records are included. A real-data release requires documented consent, ethics/IRB clearance, de-identification, retention limits and a review of re-identification risk.

## Known bias risks

- participant response styles;
- content and language effects;
- device/network availability;
- demographic imbalance;
- affect-recognition error and cultural variation;
- label subjectivity.
