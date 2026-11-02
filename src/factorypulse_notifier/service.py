"""Turn validated operational events into reviewable notification intents.

This package deliberately creates notification *intents*, rather than directly
controlling equipment or silently sending messages. Delivery adapters can be
added by a deployment that owns its credentials and escalation policy.
"""

from __future__ import annotations

import hashlib
import json
from collections.abc import Iterable
from pathlib import Path
from typing import Any

from factorypulse_contracts import validate_event


def _fingerprint(event: dict[str, Any]) -> str:
    material = "|".join(
        str(event.get(key, ""))
        for key in ("event_type", "asset_id", "pipeline", "severity", "occurred_at")
    )
    return hashlib.sha256(material.encode("utf-8")).hexdigest()[:16]


def _intent(event: dict[str, Any]) -> dict[str, Any]:
    severity = event.get("severity", "warning")
    asset = event.get("asset_id", event.get("pipeline", "data-platform"))
    reason = "; ".join(event.get("reasons", [])) or (
        f"accepted={event.get('accepted_rows', 0)}, rejected={event.get('rejected_rows', 0)}"
    )
    return {
        "id": _fingerprint(event),
        "channel": "review-queue",
        "priority": {"critical": "P1", "warning": "P2"}.get(severity, "P3"),
        "title": f"FactoryPulse {severity}: {asset}",
        "body": str(reason),
        "source_schema": event["event_type"],
        "source_event": event,
        "delivery": "not-sent",
    }


def process_events(events: Iterable[dict[str, Any]]) -> list[dict[str, Any]]:
    """Validate, normalize and deduplicate alerts while preserving provenance."""
    intents: dict[str, dict[str, Any]] = {}
    for event in events:
        event_type = event.get("event_type")
        schema = {
            "factorypulse.anomaly": "anomaly.v1",
            "factorypulse.data_quality": "data-quality.v1",
        }.get(event_type)
        if schema is None:
            raise ValueError(f"Unsupported event type: {event_type!r}")
        validate_event(schema, event)
        intent = _intent(event)
        intents.setdefault(intent["id"], intent)
    return sorted(intents.values(), key=lambda item: (item["priority"], item["id"]))


def read_jsonl(path: Path) -> list[dict[str, Any]]:
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]


def write_intents(path: Path, intents: list[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(json.dumps(item, sort_keys=True) for item in intents) + "\n", encoding="utf-8")
