#!/usr/bin/env python3
"""Validate lane-1 robot and dual-camera scaffolding."""

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

    assert tool_manifest["mode"] == "m2-lane1-hybrid-ready"
    assert tool_manifest["hardware_target"] == device_config["controller"]
    assert {"demo-full-flow", "demo-sorting", "demo-conversation-grasp"} <= set(tool_manifest["supported_scenarios"])
    assert "demo-real-risk-slice" in tool_manifest["supported_scenarios"]
    assert "robot/robot-control.log" in tool_manifest["required_evidence"]
    assert "perception/face-tracks.json" in tool_manifest["required_evidence"]
    assert "perception/object-tracks.json" in tool_manifest["required_evidence"]

    assert device_config["controller"] == "so-arm101"
    assert device_config["mode"] == "hybrid"
    assert device_config["log_artifact"] == "robot/robot-control.log"
    assert {"demo-full-flow", "demo-sorting", "demo-conversation-grasp"} <= set(device_config["supported_scenarios"])
    assert "demo-real-risk-slice" in device_config["confirmation_required_for"]
    assert set(device_config["face_following"]["enabled_for"]) == {"demo-full-flow", "demo-conversation-grasp"}

    required_camera_ids = set(camera_contract["real_risk_slice"]["required_camera_ids"])
    stream_ids = {stream["camera_id"] for stream in camera_contract["streams"]}
    assert stream_ids == required_camera_ids
    assert camera_contract["real_risk_slice"]["evidence_file"] == "perception/frame-sources.json"
    for stream in camera_contract["streams"]:
        assert "demo-real-risk-slice" in stream["required_for"]

    assert camera_device["scenario_id"] == "demo-real-risk-slice"
    assert {"demo-full-flow", "demo-sorting", "demo-conversation-grasp"} <= set(camera_device["supported_scenarios"])
    assert camera_device["sync_mode"] == camera_contract["real_risk_slice"]["sync_mode"]
    assert camera_device["evidence_artifact"] == "perception/frame-sources.json"
    assert {stream["camera_id"] for stream in camera_device["frame_sources"]} == required_camera_ids
    assert set(camera_device["face_tracking"]["enabled_for"]) == {
        "demo-full-flow",
        "demo-conversation-grasp",
        "demo-real-risk-slice",
    }

    assert camera_rig["deployment_mode"] == "hybrid"
    assert {stream["camera_id"] for stream in camera_rig["streams"]} == required_camera_ids
    assert camera_rig["recording"]["video_bundle_dir"] == "experiments/evidence/<scenario-id>/<run-id>/video"
    assert camera_rig["camera_switching"]["preserve_prompt_visibility"] is True

    assert integration_manifest["scenario_id"] == "demo-real-risk-slice"
    assert {"demo-full-flow", "demo-sorting", "demo-conversation-grasp"} <= set(integration_manifest["supported_scenarios"])
    assert integration_manifest["required_real_components"] == benchmark["scenarios"]["demo-real-risk-slice"]["required_real_components"]

    print("Lane-1 device scaffolding verification passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
