import json

import pytest

from factorypulse_notifier.service import process_events, read_jsonl, write_intents


ANOMALY = {
    "event_id": "123e4567-e89b-12d3-a456-426614174000",
    "event_type": "factorypulse.anomaly",
    "schema_version": "1.0",
    "asset_id": "PUMP-01",
    "occurred_at": "2026-01-01T12:00:00Z",
    "severity": "critical",
    "score": 6.2,
    "reasons": ["temperature robust z-score 6.2"],
}


def test_valid_events_become_deduplicated_review_intents(tmp_path) -> None:
    intents = process_events([ANOMALY, ANOMALY])
    assert len(intents) == 1
    assert intents[0]["priority"] == "P1"
    assert intents[0]["delivery"] == "not-sent"
    target = tmp_path / "intents.jsonl"
    write_intents(target, intents)
    assert read_jsonl(target) == intents


def test_unknown_schema_is_rejected() -> None:
    with pytest.raises(ValueError, match="Unsupported"):
        process_events([{"event_type": "factorypulse.telemetry"}])
