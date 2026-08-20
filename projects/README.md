# Research prototype portfolio

These five prototypes are deliberately small, testable, and honest. They demonstrate research habits relevant to ML, adaptive systems, and robotics teams: grouped validation, explicit privacy boundaries, communication accounting, calibration, drift monitoring, paired controller evaluation, deterministic fixtures, and documented limitations.

| Project | Research question | Research relevance | Run |
| --- | --- | --- | --- |
| [`soft-flight-control-lab`](soft-flight-control-lab/) | Can bounded online residual learning improve trajectory tracking under randomized compliant dynamics? | Learning-based control, nonlinear dynamics, sim-to-real methodology | `cd soft-flight-control-lab && python scripts/run_benchmark.py` |
| [`qoe-foresight-repro`](qoe-foresight-repro/) | Does multimodal QoE inference generalize to unseen participants? | Video understanding, trustworthy learning, uncertainty | `python -m tisa_portfolio.qoe_repro` |
| [`cipherqoe`](cipherqoe/) | What QoE signals remain inferable from encrypted-flow metadata without payload inspection? | Network measurement, privacy, cybersecurity | `python -m tisa_portfolio.cipherqoe` |
| [`fedqoe-bench`](fedqoe-bench/) | What is the accuracy–communication–fairness trade space in non-IID federated QoE learning? | Distributed ML, systems, responsible evaluation | `python -m tisa_portfolio.fedqoe` |
| [`trustflow-lab`](trustflow-lab/) | Can a SOC experiment expose leakage, false alarms, calibration, and drift—not only accuracy? | Security analytics, drift monitoring, reliability | `python -m tisa_portfolio.trustflow` |

The committed implementations use only Python's standard library at runtime. The results are synthetic pipeline or simulation evidence, not claims about real-world performance. SoftFlight is explicitly not hardware or flight validation. Each project documents the work required for credible real-data or real-platform evaluation.
