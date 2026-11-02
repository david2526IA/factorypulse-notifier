# FactoryPulse Notifier

`factorypulse-notifier` turns validated FactoryPulse anomaly and data-quality events into deterministic, deduplicated notification intents.

It is intentionally safe by default: it **does not** send messages, operate machinery or contain credentials. Its JSONL output is a reviewable hand-off for an organisation's chosen delivery adapter and escalation process.

## Why it exists

Operational alerting needs provenance and restraint. An alert should retain the input event that justified it, have a stable id for deduplication, and be reviewed before any real-world action. This repository implements that boundary.

## Quick start

```bash
pip install .
factorypulse-notify anomalies.jsonl --output notification_intents.jsonl
```

Each output row includes an id, priority, title, source schema and the complete source event. Re-running it with the same input yields the same ids and no duplicate intents.

## Contract boundary

Only `factorypulse.anomaly` and `factorypulse.data_quality` events from [FactoryPulse Contracts](https://github.com/david2526IA/factorypulse-contracts) are accepted. Input is validated before an intent is produced.

## Validation

```bash
pip install ".[dev]"
pytest -q
```

## Scope

This is a reference component for evaluation, development and internal integration. It is not an emergency, safety-instrumented or production notification system.

## License

MIT
