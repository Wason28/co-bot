#!/usr/bin/env python3
"""Verify M1 exit evidence for the Co-Bot workspace."""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
EVIDENCE_RUN_ID = "hybrid-smoke-001"
EVIDENCE_PATH = ROOT / "experiments/evidence/demo-real-risk-slice" / EVIDENCE_RUN_ID


def load_json(path: Path) -> dict:
    return json.loads(path.read_text())


def assert_exists(path: Path) -> None:
    if not path.exists():
        raise FileNotFoundError(path)


def main() -> int:
    required_paths = [
      ROOT / "docs/ops/m1-verification.md",
      ROOT / "training/run-config.json",
      ROOT / "training/dataset-manifest.json",
      ROOT / "training/metrics.json",
      ROOT / "training/summary.md",
      ROOT / "thesis/chapters/03-experiments.md"
    ]
    for path in required_paths:
        assert_exists(path)

    subprocess.run(
      [sys.executable, str(ROOT / "scripts/verify_m1_real_risk_slice.py"), "--run-id", EVIDENCE_RUN_ID],
      check=True,
    )

    run_config = load_json(ROOT / "training/run-config.json")
    dataset_manifest = load_json(ROOT / "training/dataset-manifest.json")
    metrics = load_json(ROOT / "training/metrics.json")
    summary = (ROOT / "training/summary.md").read_text()
    experiments_chapter = (ROOT / "thesis/chapters/03-experiments.md").read_text()

    assert run_config["target_scenario"] == "demo-full-flow"
    assert run_config["evidence_bundle"] == str(EVIDENCE_PATH.relative_to(ROOT))
    assert dataset_manifest["target_scenarios"] == ["demo-full-flow"]
    assert metrics["target_scenario"] == "demo-full-flow"
    assert metrics["metrics"]["demo_full_flow_completion_rate"] >= 0.34
    assert metrics["metrics"]["demo_full_flow_exec_latency_ms_p95"] <= 10000
    assert str(EVIDENCE_PATH.relative_to(ROOT)) in summary
    assert "demo-real-risk-slice" in experiments_chapter
    assert "demo-full-flow" in experiments_chapter

    print("M1 exit verification passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
