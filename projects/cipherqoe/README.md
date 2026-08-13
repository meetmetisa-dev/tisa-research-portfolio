# CipherQoE

> What remains inferable when streaming traffic is encrypted, and how reliable is that inference under domain shift?

## Research question

Can startup delay, rebuffer duration and bitrate class be estimated from timing, direction, size and aggregate flow statistics while inspecting **zero payload bytes**?

## Demonstration

The seeded simulator generates HTTPS/QUIC-like aggregate flow metadata. A transparent estimator produces three QoE outputs and reports MAE/class accuracy together with the privacy boundary.

```bash
PYTHONPATH=src python3 -m tisa_portfolio.cipherqoe --out reports/cipherqoe.json
```

## Credible full testbed

- encrypted DASH origin plus dash.js or Shaka Player;
- Linux `tc/netem` profiles for bandwidth, RTT, loss and jitter;
- capture reduced immediately to timestamps, directions, sizes and aggregates;
- content/device/protocol-version holdouts;
- startup MAE, stall count/duration MAE, bitrate macro-F1, p95 latency and payload-bytes-inspected audit;
- threat model covering metadata sensitivity and retention.

This is a research prototype, not a traffic-decryption product.

See [DATA_CARD.md](DATA_CARD.md), [MODEL_CARD.md](MODEL_CARD.md) and [REPRODUCIBILITY.md](REPRODUCIBILITY.md).
