# Reproducibility

The seed, client count, round count and quantization width are written into every report. `make test` verifies that training reduces client-mean RMSE and that communication is accounted for.

When moved to containers, pin image digests, framework versions and orchestration configuration; capture wall-clock time rather than replacing it with simulated rounds.
