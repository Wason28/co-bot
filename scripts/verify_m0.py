#!/usr/bin/env python3
"""Lightweight checks for the M0 repository skeleton."""

from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]

REQUIRED_PATHS = [
    ROOT / "README.md",
    ROOT / "backend/api/app.py",
    ROOT / "backend/api/openapi-stub.json",
    ROOT / "orchestrator/langgraph/state_schema.json",
    ROOT / "orchestrator/policy/policy_gate.schema.json",
    ROOT / "services/robot-mcp/tool_manifest.json",
    ROOT / "services/perception/camera_contract.json",
    ROOT / "frontend/web/index.html",
    ROOT / "experiments/benchmarks/m2-benchmark-freeze.json",
    ROOT / "experiments/templates/metadata.schema.json",
    ROOT / "experiments/templates/events.schema.json",
    ROOT / "experiments/templates/latency.schema.json",
    ROOT / "experiments/templates/result.schema.json",
    ROOT / "training/templates/minimum-finetune-result.spec.json",
    ROOT / "docs/ops/m0-verification.md",
]


def assert_exists(path: Path) -> None:
    if not path.exists():
        raise FileNotFoundError(path)


def main() -> int:
    for path in REQUIRED_PATHS:
        assert_exists(path)

    benchmark = json.loads((ROOT / "experiments/benchmarks/m2-benchmark-freeze.json").read_text())
    assert benchmark["retry_budget"]["max_total_attempts"] == 3
    assert "demo-dangerous-action" in benchmark["scenarios"]

    training_spec = json.loads((ROOT / "training/templates/minimum-finetune-result.spec.json").read_text())
    assert training_spec["primary_metric"]["threshold"] == 0.34

    smoke_bundle = ROOT / "experiments/evidence/demo-dangerous-action/smoke-001"
    if smoke_bundle.exists():
        for name in ["metadata.json", "events.jsonl", "latency.json", "result.json", "summary.md"]:
            assert_exists(smoke_bundle / name)

    print("M0 verification passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
