# Model card — CipherQoE

The estimator is a transparent synthetic baseline, not a trained traffic classifier. Its purpose is to make the feature boundary and evaluation contract executable.

Real modeling should compare linear/tree baselines with sequence models, hold out content and devices, test HTTPS versus QUIC versions, publish confusion matrices and include an abstention policy for out-of-distribution flows.

The system must not be represented as payload decryption or deployed for covert user surveillance.
