# Reproducibility

- Runtime: Python 3.10+.
- Dependencies: standard library only.
- Seed: `2026` by default; override with `--seed`.
- Command: `make demos` from the repository root.
- Test gate: `make test` verifies zero participant overlap and a baseline comparison.

Generated numbers may change only when the implementation, parameters or seed changes. Commit the command, seed and environment together with any result used in an application.
