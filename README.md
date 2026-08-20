# Tisa Selma — Trustworthy AI and Adaptive Systems

[![Reproducibility](https://github.com/meetmetisa-dev/tisa-research-portfolio/actions/workflows/ci.yml/badge.svg)](https://github.com/meetmetisa-dev/tisa-research-portfolio/actions/workflows/ci.yml)
[![SoftFlight CI](https://github.com/meetmetisa-dev/tisa-research-portfolio/actions/workflows/softflight-ci.yml/badge.svg?branch=bonn-soft-flight-control)](https://github.com/meetmetisa-dev/tisa-research-portfolio/actions/workflows/softflight-ci.yml)
[![MIT License](https://img.shields.io/badge/license-MIT-0b2545.svg)](LICENSE)

Reproducible research prototypes spanning adaptive video, encrypted-network telemetry, multimodal engagement, distributed learning, trustworthy ML, and an explicitly simulation-only study of learned residual control for a deformable aerial platform.

**[Open the interactive portfolio](https://meetmetisa-dev.github.io/tisa.github.io/)**

## Research premise

How can an intelligent system remain useful when observations, users, networks, or physical dynamics change after deployment?

This repository turns that question into five small, auditable demonstrations. Every project has deterministic code, automated checks, reproduction instructions, and an explicit evidence boundary. The SoftFlight project is a methodological transfer study; it is not a claim of prior robotics hardware experience.

## Projects

| Project | Question | Evaluation contract |
|---|---|---|
| [SoftFlight Control Lab](projects/soft-flight-control-lab/) | Can bounded online residual learning improve tracking under randomized compliant dynamics? | Paired held-out simulation; identical scenarios; RMSE, worst error, effort, and explicit hardware limitations |
| [QoE Foresight Repro](projects/qoe-foresight-repro/) | Does multimodal QoE inference generalize to unseen participants? | Participant-grouped holdout; zero identity overlap; baseline and worst-subject error |
| [CipherQoE](projects/cipherqoe/) | What QoE signal remains in encrypted-flow metadata? | Zero payload bytes; aggregate features only; privacy boundary disclosed |
| [FedQoE Bench](projects/fedqoe-bench/) | What is the accuracy–communication–fairness trade space? | Non-IID clients; dropout; worst-client error; update-byte accounting |
| [TrustFlow Lab](projects/trustflow-lab/) | Can SOC experiments report operationally useful evidence? | Time-ordered split; calibrated threshold; false-positive rate; drift monitoring |

## Reproduce

Requirements: Python 3.10+; no third-party runtime dependencies.

Run the four original demonstrations:

```bash
make test
make demos
```

Run SoftFlight independently:

```bash
cd projects/soft-flight-control-lab
python -m unittest discover -s tests -v
python scripts/run_benchmark.py
```

Expected behavior:

- six deterministic checks pass for the original demonstrations;
- ten SoftFlight tests pass;
- fixed seeds produce deterministic reports; and
- generated evidence remains traceable to the disclosed synthetic fixtures or simulation.

Preview the static portfolio locally:

```bash
make site
```

Then open `http://localhost:8000`.

## Evidence boundary

The original four projects use **synthetic fixtures**. SoftFlight uses a **reduced-order synthetic simulation**. These artifacts validate implementations and evaluation protocols—not production accuracy, physical-flight performance, clinical validity, security readiness, or performance on real participants. SoftFlight has no hardware, ROS, motion-capture, or field validation. Real-data and real-robot extensions require appropriate datasets, licensing and ethics review, platform system identification, safety filters, and staged experiments.

## Repository map

- `src/tisa_portfolio/` — dependency-free Python implementations for the original projects
- `tests/` — leakage, metric, communication, and drift checks
- `projects/` — project code, research briefs, cards, and reproduction notes
- `reports/` — deterministic demonstration outputs
- `website/` — accessible, responsive portfolio and browser-only interactive demos
- `.github/workflows/` — continuous checks and GitHub Pages deployment

## Citation and license

Software is released under the [MIT License](LICENSE). Citation metadata is available in [CITATION.cff](CITATION.cff). Personal biography and publication text remain attributable to Tisa Selma.
