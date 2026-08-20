# Research Package

This document combines the project research protocol, data card, and model card for convenient review.

---

## Research Protocol

### Research objective

Can a learned controller reduce outages and residual error while managing the cost and fatigue of recovery actions under changing operating conditions?

### Scope

The protocol evaluates a compact, deterministic implementation on synthetic data. Its purpose is methodological demonstration and portfolio review, not domain certification.

### Hypotheses

1. The proposed learning method should outperform a non-learning or random baseline on its declared primary reward or utility metric.
2. Evaluation should expose at least one operational or distributional metric beyond aggregate utility.
3. A strong simple baseline must remain visible even when it challenges the learned method.
4. Repeated runs with the default seed must reproduce the shipped headline metrics exactly.

### Method

A five-input ReLU Q-network uses experience replay, online and target networks, and Double-DQN targets. The policy is evaluated against monitor-only, random, and threshold baselines.

### Evaluation contract

- Use held-out simulation episodes or client test partitions.
- Use matched random seeds across policies or model variants where applicable.
- Report aggregate performance and operational/distributional metrics.
- Preserve all baseline results in `results.json`.
- Label every result as synthetic.
- Treat failed hypotheses as informative findings, not numbers to hide.

### Reproducibility

```bash
python demo.py --check --output results.json
python validate.py
```

### Threats to validity

The environment is synthetic and the controller is educational. Results are deterministic simulation outputs, not production performance or safety certification. Additional threats include sensitivity to reward definitions, synthetic-data assumptions, seed choice, limited model scale, and absence of real-world operational constraints.

### Responsible extension plan

A future research version should introduce multiple seeds with confidence intervals, ablation studies, hyperparameter registration, external datasets or simulators, domain-specific safety checks, compute and carbon reporting, and a predeclared stopping rule. Real personal, clinical, or institutional data would require appropriate permissions, de-identification, security controls, and ethics review.

---

## Data Card

### Dataset type

Programmatically generated synthetic observations. No real people, patients, devices, organizations, or proprietary records are included.

### Generation

The generator is embedded in `demo.py` and controlled by a fixed default seed. Distribution shifts and system drift are intentionally simulated to exercise the method.

### Intended use

- Reproducible portfolio demonstration
- Unit-level inspection of a learning pipeline
- Teaching and discussion of evaluation design
- Starting point for a better controlled research benchmark

### Out-of-scope use

- Production decision-making
- Clinical or safety-critical use
- Claims about real populations or institutions
- Privacy, security, fairness, or robustness certification
- Comparison to published state of the art without matched datasets and protocols

### Known limitations

Synthetic data can be easier, cleaner, and more controllable than real data. It may omit confounding variables, long-tail behavior, annotation errors, adversarial behavior, and institutional constraints.

### Governance

No personal data are processed. If the prototype is extended to real records, the data owner must define lawful basis, access controls, retention, auditability, de-identification, and appropriate ethics or institutional review.

---

## Model Card

### Model details

- Topic: Deep Reinforcement Learning
- Implementation: inspectable NumPy/Python reference prototype
- Release: 1.0.0, August 2026
- Author: Tisa Selma, Ph.D.

### Intended purpose

A NumPy Double-DQN controller selects monitoring and recovery actions from throughput, buffer, residual, drift, and cooldown state.

### Training and evaluation

A five-input ReLU Q-network uses experience replay, online and target networks, and Double-DQN targets. The policy is evaluated against monitor-only, random, and threshold baselines.

Shipped headline metrics:

- **mean simulated QoE:** 0.800
- **outage rate:** 0.05%
- **mean residual:** 0.112
- **reward gain vs monitor-only:** +648.7%

### Interpretation

The project connects model monitoring to sequential intervention, reports action distributions and operational outcomes, and preserves competitive non-learning baselines for interpretation.

### Limitations and risks

Results depend on the synthetic generator, reward design, hyperparameters, and default seed. The model should not be used to make consequential decisions.

### Ethical considerations

The prototype should not be presented as established expertise based on publication, real-world validation, clinical effectiveness, privacy protection, or deployment impact. Future work should document stakeholder impact, subgroup performance, failure modes, and escalation procedures.
