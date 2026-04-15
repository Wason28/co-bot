#!/usr/bin/env python3
"""Generate a canonical evidence bundle from the deterministic stub runtime."""

from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
BENCHMARK_PATH = ROOT / "experiments/benchmarks/m2-benchmark-freeze.json"
MODEL_REGISTRY_PATH = ROOT / "models/runtime/model_registry.template.json"
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from backend.api.app import create_task_submission
from orchestrator.langgraph.stub_runtime import SCENARIO_CATALOG, SCENARIO_DECISIONS, run_stub_scenario


def utc_now() -> datetime:
    return datetime.now(timezone.utc).replace(microsecond=0)


def load_json(path: Path) -> dict:
    return json.loads(path.read_text())


def build_run_id(scenario_id: str, attempt_index: int) -> str:
    stamp = utc_now().strftime("%Y%m%dt%H%M%Sz").lower()
    return f"{scenario_id}-attempt-0{attempt_index}-{stamp}"


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--scenario", required=True, choices=sorted(SCENARIO_DECISIONS))
    parser.add_argument("--attempt-index", type=int, default=1)
    parser.add_argument("--run-id")
    args = parser.parse_args()

    benchmark = load_json(BENCHMARK_PATH)
    models = load_json(MODEL_REGISTRY_PATH)
    run_id = args.run_id or build_run_id(args.scenario, args.attempt_index)
    bundle_dir = ROOT / "experiments/evidence" / args.scenario / run_id
    bundle_dir.mkdir(parents=True, exist_ok=True)

    t_start = utc_now()
    submission = create_task_submission(
        args.scenario,
        SCENARIO_CATALOG[args.scenario].input_text,
        run_id=run_id,
        submitted_at=t_start.isoformat(),
    )
    artifacts = run_stub_scenario(
        submission,
        run_id=run_id,
        attempt_index=args.attempt_index,
        benchmark=benchmark,
        model_registry=models,
        started_at=t_start,
    )

    (bundle_dir / "metadata.json").write_text(json.dumps(artifacts.metadata, indent=2) + "\n")
    with (bundle_dir / "events.jsonl").open("w") as handle:
        for event in artifacts.events:
            handle.write(json.dumps(event) + "\n")
    (bundle_dir / "latency.json").write_text(json.dumps(artifacts.latency, indent=2) + "\n")
    (bundle_dir / "result.json").write_text(json.dumps(artifacts.result, indent=2) + "\n")
    (bundle_dir / "summary.md").write_text(artifacts.summary + "\n")

    if artifacts.checkpoints:
        checkpoint_dir = bundle_dir / "checkpoints"
        checkpoint_dir.mkdir(exist_ok=True)
        for filename, snapshot in artifacts.checkpoints.items():
            (checkpoint_dir / filename).write_text(json.dumps(snapshot, indent=2) + "\n")

    if artifacts.redis_records:
        redis_dir = bundle_dir / "redis"
        redis_dir.mkdir(exist_ok=True)
        for filename, snapshot in artifacts.redis_records.items():
            (redis_dir / filename).write_text(json.dumps(snapshot, indent=2) + "\n")

    print(bundle_dir)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
