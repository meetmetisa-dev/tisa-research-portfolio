# Tisa Selma - Trustworthy AI and Adaptive Systems

[![Reproducibility](https://github.com/meetmetisa-dev/tisa-research-portfolio/actions/workflows/ci.yml/badge.svg)](https://github.com/meetmetisa-dev/tisa-research-portfolio/actions/workflows/ci.yml)
[![Advanced AI validation](https://github.com/meetmetisa-dev/tisa-research-portfolio/actions/workflows/validate-advanced-ai.yml/badge.svg)](https://github.com/meetmetisa-dev/tisa-research-portfolio/actions/workflows/validate-advanced-ai.yml)
[![SoftFlight CI](https://github.com/meetmetisa-dev/tisa-research-portfolio/actions/workflows/softflight-ci.yml/badge.svg?branch=bonn-soft-flight-control)](https://github.com/meetmetisa-dev/tisa-research-portfolio/actions/workflows/softflight-ci.yml)
[![MIT License](https://img.shields.io/badge/license-MIT-0b2545.svg)](LICENSE)

Reproducible research prototypes spanning adaptive video, encrypted-network telemetry, multimodal engagement, distributed learning, trustworthy machine learning, multi-agent reinforcement learning, federated learning, deep reinforcement learning, and a simulation-only study of learned residual control for a deformable aerial platform.

**[Open the interactive portfolio](https://meetmetisa-dev.github.io/tisa-research-portfolio/)**

## Research premise

How can an intelligent system remain useful when observations, users, networks, institutions, or physical dynamics change after deployment?

This repository turns that question into eight small, auditable demonstrations. Every project defines an evaluation contract, deterministic code or fixtures, reproduction instructions, and an explicit evidence boundary. Synthetic and simulation-only projects are not presented as peer-reviewed findings or production deployments.

## Projects

| Project | Question | Evaluation contract |
|---|---|---|
| [SoftFlight Control Lab](projects/soft-flight-control-lab/) | Can bounded online residual learning improve tracking under randomized compliant dynamics? | Paired held-out simulation; identical scenarios; RMSE, worst error, effort, and explicit hardware limitations |
| [QoE Foresight Repro](projects/qoe-foresight-repro/) | Does multimodal QoE inference generalize to unseen participants? | Participant-grouped holdout; zero identity overlap; baseline and worst-subject error |
| [CipherQoE](projects/cipherqoe/) | What QoE signal remains in encrypted-flow metadata? | Zero payload bytes; aggregate features only; privacy boundary disclosed |
| [FedQoE Bench](projects/fedqoe-bench/) | What is the accuracy-communication-fairness trade space? | Non-IID clients; dropout; worst-client error; update-byte accounting |
| [TrustFlow Lab](projects/trustflow-lab/) | Can SOC experiments report operationally useful evidence? | Time-ordered split; calibrated threshold; false-positive rate; drift monitoring |
| [Cooperative Edge QoE Control](projects/multiagent-reinforcement-learning/) | Can cooperative agents learn joint resource allocation under changing demand? | Matched seeds; multiple baselines; reward, QoE, overload, fairness, and energy |
| [Non-IID Multisite FedAvg](projects/federated-learning/) | Can a global model serve heterogeneous sites without pooling records? | Per-client holdouts; worst-client accuracy; dispersion and communication accounting |
| [Double DQN QoE Recovery](projects/deep-reinforcement-learning/) | Can a neural policy recover QoE under drift while controlling intervention cost? | Matched-seed baselines; QoE, outage, residual error, cost, and reward |

## Advanced AI portfolio

The repository now includes dedicated, executable portfolios in:

- **Multi-Agent Reinforcement Learning** - cooperative edge QoE control
- **Federated Learning** - non-IID multisite FedAvg
- **Deep Reinforcement Learning** - Double DQN for drift-aware QoE recovery

Open the [Advanced AI overview](advanced-ai.html) or download the [complete repository source](https://github.com/meetmetisa-dev/tisa-research-portfolio/archive/refs/heads/main.zip).

These three projects are synthetic portfolio prototypes created in August 2026. They are not represented as prior peer-reviewed publications, production deployments, clinical evidence, or formal privacy and safety guarantees.

## Reproduce

Requirements: Python 3.10 or later. The original four demonstrations use the standard library. The three advanced-AI projects require NumPy 2.x. SoftFlight has its own project instructions.

```bash
make test
make demos
python3 -m pip install "numpy>=2.0,<3"
make advanced
```

Run SoftFlight independently:

```bash
cd projects/soft-flight-control-lab
python -m unittest discover -s tests -v
python scripts/run_benchmark.py
```

Expected behavior:

- the original deterministic checks pass;
- each advanced-AI validation script reproduces its committed headline metrics;
- fixed seeds produce deterministic reports; and
- generated evidence remains traceable to disclosed synthetic fixtures or simulation.

## Preview the website

```bash
make site
```

Then open `http://localhost:8000`.

## Evidence boundary

The portfolio prototypes use **synthetic fixtures** or **reduced-order simulation**. They validate implementations and evaluation protocols, not production accuracy, physical-flight performance, clinical validity, security readiness, formal privacy guarantees, or results on real participants. Real-data and real-system extensions require appropriate datasets, licensing, governance, ethics review, system identification, safety constraints, and staged evaluation.

## Repository map

- `index.html`, `styles.css`, `app.js` - responsive dark-theme GitHub Pages portfolio
- `src/tisa_portfolio/` - dependency-free Python implementations for the original projects
- `tests/` - leakage, metric, communication, and drift checks
- `projects/` - eight research prototypes with code, protocols, cards, results, and limitations
- `reports/` - deterministic demonstration outputs
- `website/` - existing browser-only interactive demonstrations
- `.github/workflows/` - reproducibility checks and GitHub Pages deployment

## Academic status

Tisa Selma was awarded the Ph.D. in Computer Science by United Arab Emirates University on **10 July 2026**.

## Citation and license

Software is released under the [MIT License](LICENSE). Citation metadata is available in [CITATION.cff](CITATION.cff). Personal biography and publication descriptions remain attributable to Tisa Selma.
