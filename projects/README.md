# Research prototype portfolio

These eight prototypes are deliberately small, executable, testable, and explicit about their evidence boundaries. Together they demonstrate grouped validation, privacy-aware feature design, communication accounting, calibration, drift monitoring, federated optimization, cooperative control, deep reinforcement learning, and simulation-only residual control.

| Project | Research question | Evaluation contract | Run |
| --- | --- | --- | --- |
| [`soft-flight-control-lab`](soft-flight-control-lab/) | Can bounded online residual learning improve tracking under randomized compliant dynamics? | Paired held-out simulation; identical scenarios; RMSE, worst error, effort, explicit hardware limitations | See project README |
| [`qoe-foresight-repro`](qoe-foresight-repro/) | Does multimodal QoE inference generalize to unseen participants? | Participant-grouped holdout; zero identity overlap; baseline and worst-subject error | `python -m tisa_portfolio.qoe_repro` |
| [`cipherqoe`](cipherqoe/) | What QoE signals remain inferable from encrypted-flow metadata without payload inspection? | Zero payload bytes; aggregate features only; privacy boundary disclosed | `python -m tisa_portfolio.cipherqoe` |
| [`fedqoe-bench`](fedqoe-bench/) | What is the accuracy-communication-fairness trade space in non-IID federated QoE learning? | Non-IID clients; dropout; worst-client error; update-byte accounting | `python -m tisa_portfolio.fedqoe` |
| [`trustflow-lab`](trustflow-lab/) | Can a SOC experiment expose leakage, false alarms, calibration, and drift-not only accuracy? | Time-ordered split; calibrated threshold; false-positive rate; drift monitoring | `python -m tisa_portfolio.trustflow` |
| [`multiagent-reinforcement-learning`](multiagent-reinforcement-learning/) | Can cooperative resource agents adapt service levels under changing demand? | Matched seeds; random, demand-aware, and fixed baselines; QoE, overload, fairness, and reward | `python projects/multiagent-reinforcement-learning/validate.py` |
| [`federated-learning`](federated-learning/) | How well does FedAvg learn across heterogeneous sites when the least-served client is part of the contract? | Non-IID client holdouts; mean and worst-client accuracy; dispersion and communication accounting | `python projects/federated-learning/validate.py` |
| [`deep-reinforcement-learning`](deep-reinforcement-learning/) | Can Double DQN select recovery actions under drift while accounting for intervention costs? | Matched-seed comparison with threshold, random, and monitor-only policies | `python projects/deep-reinforcement-learning/validate.py` |

## Evidence boundary

All included fixtures are synthetic or simulation-based. They test implementations and evaluation protocols; they do not establish production performance, physical-system performance, clinical validity, safety certification, formal privacy guarantees, or results on real participants. The three advanced-AI projects were created as reproducible portfolio demonstrations in August 2026 and are not represented as prior peer-reviewed publications.
