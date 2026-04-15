#!/usr/bin/env python3
"""Validate M1 lane-1 robot and dual-camera scaffolding."""

from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def load_json(relative_path: str) -> dict:
    return json.loads((ROOT / relative_path).read_text())


def main() -> int:
    benchmark = load_json("experiments/benchmarks/m2-benchmark-freeze.json")
    tool_manifest = load_json("services/robot-mcp/tool_manifest.json")
    device_config = load_json("services/robot-mcp/device_config.template.json")
    camera_contract = load_json("services/perception/camera_contract.json")
    camera_device = load_json("services/perception/device_config.template.json")
    camera_rig = load_json("services/perception/camera_rig.template.json")
    integration_manifest = load_json("services/device_integration_manifest.json")

    assert tool_manifest["mode"] == "m1-hybrid-ready"
    assert tool_manifest["hardware_target"] == device_config["controller"]
    assert "demo-real-risk-slice" in tool_manifest["supported_scenarios"]
    assert "robot/robot-control.log" in tool_manifest["required_evidence"]

    assert device_config["controller"] == "so-arm101"
    assert device_config["mode"] == "hybrid"
    assert device_config["log_artifact"] == "robot/robot-control.log"
    assert "demo-real-risk-slice" in device_config["confirmation_required_for"]

    required_camera_ids = set(camera_contract["real_risk_slice"]["required_camera_ids"])
    stream_ids = {stream["camera_id"] for stream in camera_contract["streams"]}
    assert stream_ids == required_camera_ids
    assert camera_contract["real_risk_slice"]["evidence_file"] == "perception/frame-sources.json"
    for stream in camera_contract["streams"]:
        assert "demo-real-risk-slice" in stream["required_for"]

    assert camera_device["scenario_id"] == "demo-real-risk-slice"
    assert camera_device["sync_mode"] == camera_contract["real_risk_slice"]["sync_mode"]
    assert camera_device["evidence_artifact"] == "perception/frame-sources.json"
    assert {stream["camera_id"] for stream in camera_device["frame_sources"]} == required_camera_ids

    assert camera_rig["deployment_mode"] == "hybrid"
    assert {stream["camera_id"] for stream in camera_rig["streams"]} == required_camera_ids
    assert camera_rig["recording"]["video_bundle_dir"] == "experiments/evidence/<scenario-id>/<run-id>/video"

    assert integration_manifest["scenario_id"] == "demo-real-risk-slice"
    assert integration_manifest["required_real_components"] == benchmark["scenarios"]["demo-real-risk-slice"]["required_real_components"]

    print("M1 lane-1 device scaffolding verification passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
