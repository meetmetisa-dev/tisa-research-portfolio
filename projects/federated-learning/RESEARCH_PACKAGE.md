# Research Package

This document combines the project research protocol, data card, and model card for convenient review.

---

## Research Protocol

### Research objective

How well does weighted federated averaging learn across heterogeneous sites when both global utility and the least-served client are part of the evaluation contract?

### Scope

The protocol evaluates a compact, deterministic implementation on synthetic data. Its purpose is methodological demonstration and portfolio review, not domain certification.

### Hypotheses

1. The proposed learning method should outperform a non-learning or random baseline on its declared primary utility metric.
2. Evaluation should expose operational or distributional metrics beyond aggregate utility.
3. A strong simple baseline must remain visible even when it challenges the learned method.
4. Repeated runs with the default seed must reproduce the shipped headline metrics exactly.

### Method

Client-specific feature shifts, scales, and label biases create non-IID local datasets. Clipped local logistic-regression updates are aggregated by weighted FedAvg and evaluated separately on each held-out client.

### Evaluation contract

- Use held-out client test partitions.
- Report mean, worst-client, best-client, and cross-client dispersion.
- Preserve centralized and local-only baselines.
- Account for simulated model-upload and download bytes.
- Label every result as synthetic.

### Reproducibility

```bash
python demo.py --check --output results.json
python validate.py
```

### Threats to validity

Local data retention in this simulation is not equivalent to formal privacy. The prototype does not implement differential privacy, secure aggregation, poisoning resistance, or a confidentiality guarantee. Additional threats include sensitivity to the synthetic client generator, seed choice, limited model scale, and absence of real institutional data constraints.

### Responsible extension plan

A future research version should add multiple seeds with confidence intervals, secure aggregation, differential-privacy accounting, poisoning and dropout experiments, ablation studies, real multisite datasets under appropriate governance, and predeclared evaluation thresholds.

---

## Data Card

### Dataset type

Programmatically generated synthetic multisite observations. No real people, patients, organizations, or proprietary records are included.

### Generation

Eight clients receive different feature shifts, scales, and label biases. Each client has separate train and held-out test partitions. Heterogeneity is intentional and controlled by a fixed seed.

### Intended use

- Reproducible federated-learning portfolio demonstration
- Inspection of non-IID evaluation and communication accounting
- Teaching and methodological discussion
- Starting point for more rigorous multisite benchmarks

### Out-of-scope use

- Production or clinical decisions
- Claims about real institutions or populations
- Formal privacy or security certification
- Comparison to published state of the art without matched datasets and protocols

### Known limitations

Synthetic data may omit real-world confounding, missingness, coding variation, subgroup imbalance, malicious clients, hardware variability, and governance constraints.

### Governance

No personal data are processed. Any extension to real records requires lawful basis, agreements among sites, access controls, retention and audit rules, de-identification, threat modeling, and appropriate ethics or institutional review.

---

## Model Card

### Model details

- Topic: Federated Learning
- Implementation: inspectable NumPy/Python reference prototype
- Release: 1.0.0, August 2026
- Author: Tisa Selma, Ph.D.

### Intended purpose

Eight heterogeneous synthetic sites collaboratively train a classifier without pooling records, with explicit worst-client and communication reporting.

### Training and evaluation

Clipped local logistic-regression updates are aggregated by weighted FedAvg and evaluated separately on each held-out client. Centralized and local-only comparators remain visible.

Shipped headline metrics:

- **mean client accuracy:** 76.2%
- **worst-client accuracy:** 73.2%
- **cross-client std.:** 0.017
- **simulated communication:** 58.5 KiB

### Interpretation

The benchmark prioritizes per-client results, worst-client accuracy, cross-client dispersion, learning curves, and communication accounting rather than reporting only a global average.

### Limitations and risks

Local data retention is not a formal privacy guarantee. Results depend on the synthetic generator, learning rates, clipping, client weighting, and seed. The model should not be used for consequential decisions.

### Ethical considerations

The prototype should not be represented as clinical effectiveness, deployment impact, or privacy protection. Future work should document stakeholder impact, subgroup performance, failure modes, adversarial risks, and escalation procedures.
