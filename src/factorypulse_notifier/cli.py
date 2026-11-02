from __future__ import annotations

import argparse
import json
from pathlib import Path

from .service import process_events, read_jsonl, write_intents


def main() -> None:
    parser = argparse.ArgumentParser(description="Create reviewable FactoryPulse notification intents.")
    parser.add_argument("input", type=Path, help="JSONL anomaly or data-quality events")
    parser.add_argument("--output", type=Path, default=Path("notification_intents.jsonl"))
    args = parser.parse_args()
    intents = process_events(read_jsonl(args.input))
    write_intents(args.output, intents)
    print(json.dumps({"intents": len(intents), "output": str(args.output)}))
