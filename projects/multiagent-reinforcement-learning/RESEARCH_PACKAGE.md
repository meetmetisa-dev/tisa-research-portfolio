# Research Package

This document combines the project research protocol, data card, and model card for convenient review.

---

## Research Protocol

### Research objective

Can cooperative resource agents adapt joint service levels to time-varying demand while controlling congestion and retaining fair service?

### Scope

The protocol evaluates a compact, deterministic implementation on synthetic data. Its purpose is methodological demonstration and portfolio review, not domain certification.

### Hypotheses

1. The proposed learning method should outperform a non-learning or random baseline on its declared primary reward or utility metric.
2. Evaluation should expose at least one operational or distributional metric beyond aggregate utility.
3. A strong simple baseline must remain visible even when it challenges the learned method.
4. Repeated runs with the default seed must reproduce the shipped headline metrics exactly.

### Method

Centralized joint-action Q-learning over a transparent 27-state, 27-action synthetic environment. The learned policy is evaluated with matched seeds against random, demand-aware, and fixed-balanced baselines.

### Evaluation contract

- Use held-out simulation episodes.
- Use matched random seeds across policies.
- Report reward, QoE, overload, fairness, and energy.
- Preserve every baseline result in `results.json`.
- Label every result as synthetic.
- Treat a strong baseline that outperforms learning as an informative result.

### Reproducibility

```bash
python demo.py --check --output results.json
python validate.py
```

### Threats to validity

Synthetic demand only. The centralized joint-action formulation does not scale to large agent populations, and no latency, safety, or production-deployment claim is made. Additional threats include sensitivity to the reward function, demand generator, seed, and limited agent/action scale.

### Responsible extension plan

A future research version should introduce multiple seeds with confidence intervals, decentralized policies, partial observability, communication constraints, safety constraints, ablation studies, external simulators, compute reporting, and a predeclared stopping rule.

---

## Data Card

### Dataset type

Programmatically generated synthetic demand and system-state observations. No real people, organizations, devices, or proprietary records are included.

### Generation

The environment is embedded in `demo.py` and controlled by fixed seeds. Three resource agents observe discretized demand levels and jointly select service levels. Overload, fairness, QoE, and energy are calculated by the simulator.

### Intended use

- Reproducible MARL portfolio demonstration
- Inspection of joint-action and shared-reward design
- Teaching and methodological discussion
- Starting point for more scalable decentralized benchmarks

### Out-of-scope use

- Production resource allocation
- Safety-critical control
- Claims about real users, networks, or institutions
- Comparison to published state of the art without matched environments and protocols

### Known limitations

The simulator is deliberately small and may omit latency, failures, delayed rewards, adversarial behavior, long-tail demand, nonstationary agent populations, and deployment constraints.

### Governance

No personal data are processed. Any extension using user or network telemetry requires lawful basis, access controls, data minimization, retention rules, security review, and appropriate ethics or institutional review.

---

## Model Card

### Model details

- Topic: Multi-Agent Reinforcement Learning
- Implementation: inspectable NumPy/Python reference prototype
- Release: 1.0.0, August 2026
- Author: Tisa Selma, Ph.D.

### Intended purpose

A cooperative three-agent benchmark for resource allocation under changing demand, with shared reward, fairness, overload, and energy accounting.

### Training and evaluation

Centralized joint-action Q-learning over a transparent 27-state, 27-action synthetic environment. The learned policy is evaluated with matched seeds against random, demand-aware, and fixed-balanced baselines.

Shipped headline metrics:

- **learned mean reward:** 0.886
- **reward gain vs random:** +22.7%
- **mean simulated QoE:** 0.933
- **overload rate:** 0.05%

### Interpretation

The prototype demonstrates multi-agent state/action construction, shared-reward design, fairness-aware evaluation, baseline discipline, and reproducible reporting. A strong fixed baseline is retained even when it slightly outperforms the learned controller.

### Limitations and risks

Results depend on the synthetic demand generator, reward design, hyperparameters, and seed. The centralized formulation is not scalable and the policy should not be used for consequential decisions.

### Ethical considerations

The prototype should not be presented as prior publication, real-world validation, or deployment impact. Future work should document stakeholders, failure modes, safety constraints, subgroup/service disparities, and escalation procedures.
