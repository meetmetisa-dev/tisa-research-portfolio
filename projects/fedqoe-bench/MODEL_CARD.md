# Model card — FedQoE Bench

The model is a linear regressor trained with local gradient updates and federated averaging. It is an accounting and protocol baseline.

It does not implement secure aggregation, differential privacy or protection against update inversion. Those properties must never be claimed from federation alone.

Required real-world checks include convergence under heterogeneous compute/network conditions, worst-client error, client participation bias, update leakage, calibration and rollback behavior.
