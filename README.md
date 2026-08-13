# Tisa Selma — Trustworthy AI for Networked Multimedia

[![Reproducibility](https://github.com/tselma/tisa-research-portfolio/actions/workflows/ci.yml/badge.svg)](https://github.com/tselma/tisa-research-portfolio/actions/workflows/ci.yml)
[![MIT License](https://img.shields.io/badge/license-MIT-0b2545.svg)](LICENSE)

Reproducible research prototypes at the intersection of adaptive video, encrypted-network telemetry, multimodal engagement, distributed learning and trustworthy ML.

**[Open the interactive portfolio](https://tselma.github.io/tisa-research-portfolio/)**

## Research premise

What can a system reliably infer about human experience when media adapts, transport is encrypted, clients are heterogeneous and models drift after deployment?

This repository turns that question into four small, auditable demonstrations. Every project has deterministic code, automated checks, a data card, a model card, reproduction instructions and an explicit limitations statement.

## Projects

| Project | Question | Evaluation contract |
|---|---|---|
| [QoE Foresight Repro](projects/qoe-foresight-repro/) | Does multimodal QoE inference generalize to unseen participants? | Participant-grouped holdout; zero identity overlap; baseline and worst-subject error |
| [CipherQoE](projects/cipherqoe/) | What QoE signal remains in encrypted-flow metadata? | Zero payload bytes; aggregate features only; privacy boundary disclosed |
| [FedQoE Bench](projects/fedqoe-bench/) | What is the accuracy–communication–fairness trade space? | Non-IID clients; dropout; worst-client error; update-byte accounting |
| [TrustFlow Lab](projects/trustflow-lab/) | Can SOC experiments report operationally useful evidence? | Time-ordered split; calibrated threshold; false-positive rate; drift monitoring |

## Reproduce

Requirements: Python 3.10+; no third-party runtime dependencies.

```bash
make test
make demos
```

Expected behavior:

- six deterministic checks pass;
- four JSON reports are written to `reports/`;
- repeated runs with the default seed produce identical outputs.

Preview the static portfolio locally:

```bash
make site
```

Then open `http://localhost:8000`.

## Evidence boundary

The included fixtures are **synthetic**. They validate implementations and evaluation protocols—not production accuracy, clinical validity, security readiness, or performance on real participants. Real-data extensions require dataset-specific licensing, consent/ethics review, de-identification and domain-holdout evaluation.

## Repository map

- `src/tisa_portfolio/` — dependency-free Python implementations
- `tests/` — leakage, metric, communication and drift checks
- `projects/` — research briefs, data/model cards and reproduction notes
- `reports/` — deterministic demonstration outputs
- `website/` — accessible, responsive portfolio and browser-only interactive demos
- `.github/workflows/` — continuous checks and GitHub Pages deployment

## Citation and license

Software is released under the [MIT License](LICENSE). Citation metadata is available in [CITATION.cff](CITATION.cff). Personal biography and publication text remain attributable to Tisa Selma.

