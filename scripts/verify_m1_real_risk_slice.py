#!/usr/bin/env python3
"""Verify the canonical M1 lane-1 real-risk evidence bundle."""

from __future__ import annotations

import argparse
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SCENARIO_ID = "demo-real-risk-slice"
BENCHMARK_PATH = ROOT / "experiments/benchmarks/m2-benchmark-freeze.json"
ROBOT_MANIFEST_PATH = ROOT / "services/robot-mcp/tool_manifest.json"
CAMERA_CONTRACT_PATH = ROOT / "services/perception/camera_contract.json"
ROBOT_DEVICE_PATH = ROOT / "services/robot-mcp/device_config.template.json"
CAMERA_DEVICE_PATH = ROOT / "services/perception/device_config.template.json"


def load_json(path: Path) -> dict:
    return json.loads(path.read_text())


def assert_exists(path: Path) -> None:
    if not path.exists():
        raise FileNotFoundError(path)


def resolve_bundle(args: argparse.Namespace) -> Path:
    if args.bundle_dir:
        return Path(args.bundle_dir)
    if not args.run_id:
        raise ValueError("either --run-id or --bundle-dir is required")
    return ROOT / "experiments/evidence" / SCENARIO_ID / args.run_id


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--run-id")
    parser.add_argument("--bundle-dir")
    args = parser.parse_args()

    benchmark = load_json(BENCHMARK_PATH)
    robot_manifest = load_json(ROBOT_MANIFEST_PATH)
    camera_contract = load_json(CAMERA_CONTRACT_PATH)
    robot_device = load_json(ROBOT_DEVICE_PATH)
    camera_device = load_json(CAMERA_DEVICE_PATH)
    bundle_dir = resolve_bundle(args)

    required_paths = [
      bundle_dir / "metadata.json",
      bundle_dir / "summary.md",
      bundle_dir / "events.jsonl",
      bundle_dir / "latency.json",
      bundle_dir / "result.json",
      bundle_dir / "checkpoints/pre-exec.json",
      bundle_dir / "checkpoints/post-exec.json",
      bundle_dir / "redis/session-context.json",
      bundle_dir / "perception/frame-sources.json",
      bundle_dir / "robot/robot-control.log",
      bundle_dir / "video/run.mp4"
    ]
    for path in required_paths:
        assert_exists(path)

    metadata = load_json(bundle_dir / "metadata.json")
    latency = load_json(bundle_dir / "latency.json")
    result = load_json(bundle_dir / "result.json")
    frame_sources = load_json(bundle_dir / "perception/frame-sources.json")
    redis_context = load_json(bundle_dir / "redis/session-context.json")
    with (bundle_dir / "events.jsonl").open() as handle:
        events = [json.loads(line) for line in handle if line.strip()]

    assert metadata["scenario_id"] == SCENARIO_ID
    assert latency["scenario_id"] == SCENARIO_ID
    assert result["scenario_id"] == SCENARIO_ID
    assert latency["exec_latency_ms"] <= benchmark["latency_threshold_ms"]
    assert result["passed"] is True
    assert robot_manifest["hardware_target"] == robot_device["controller"]
    assert robot_device["log_artifact"] == "robot/robot-control.log"
    assert camera_device["evidence_artifact"] == "perception/frame-sources.json"

    required_camera_ids = set(camera_contract["real_risk_slice"]["required_camera_ids"])
    recorded_camera_ids = {stream["camera_id"] for stream in frame_sources["frame_sources"]}
    assert recorded_camera_ids == required_camera_ids

    modules = {event["module"] for event in events}
    assert {"policy-gate", "robot-mcp", "perception", "checkpoint", "memory"} <= modules
    assert redis_context["confirmation_state"] == "completed"
    assert bundle_dir.joinpath("robot/robot-control.log").read_text().strip()
    assert bundle_dir.joinpath("video/run.mp4").exists()

    print(f"M1 real-risk verification passed: {bundle_dir}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
