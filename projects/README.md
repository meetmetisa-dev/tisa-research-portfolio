# Research prototype portfolio

These four prototypes are deliberately small, testable and honest. They demonstrate research habits relevant to strong ML, vision and systems teams: grouped validation, explicit privacy boundaries, communication accounting, calibration, drift monitoring, deterministic fixtures and documented limitations.

| Project | Research question | Research relevance | Run |
| --- | --- | --- | --- |
| [`qoe-foresight-repro`](qoe-foresight-repro/) | Does multimodal QoE inference generalize to unseen participants? | Video understanding, trustworthy learning, uncertainty | `python -m tisa_portfolio.qoe_repro` |
| [`cipherqoe`](cipherqoe/) | What QoE signals remain inferable from encrypted-flow metadata without payload inspection? | Network measurement, privacy, cybersecurity | `python -m tisa_portfolio.cipherqoe` |
| [`fedqoe-bench`](fedqoe-bench/) | What is the accuracy–communication–fairness trade space in non-IID federated QoE learning? | Distributed ML, systems, responsible evaluation | `python -m tisa_portfolio.fedqoe` |
| [`trustflow-lab`](trustflow-lab/) | Can a SOC experiment expose leakage, false alarms, calibration and drift—not only accuracy? | Security analytics, drift monitoring, reliability | `python -m tisa_portfolio.trustflow` |

The committed implementation uses only Python's standard library. The synthetic results are pipeline checks, not claims about real-world performance. Each project includes a path to credible real-data validation without bundling restricted or personally identifying data.
