#!/usr/bin/env python3
"""Validate the lane-1 M2 scenario configs and evidence bundles."""

from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
RUN_ID = "lane1-smoke-001"
SCENARIOS = ("demo-full-flow", "demo-sorting", "demo-conversation-grasp")


def load_json(relative_path: str) -> dict:
    return json.loads((ROOT / relative_path).read_text())


def load_bundle_json(scenario_id: str, suffix: str) -> dict:
    return load_json(f"experiments/evidence/{scenario_id}/{RUN_ID}/{suffix}")


def assert_files(scenario_id: str) -> None:
    bundle = ROOT / "experiments/evidence" / scenario_id / RUN_ID
    required = [
        "metadata.json",
        "events.jsonl",
        "latency.json",
        "result.json",
        "summary.md",
        "checkpoints/pre-exec.json",
        "checkpoints/post-exec.json",
        "redis/session-context.json",
        "perception/frame-sources.json",
        "perception/face-tracks.json",
        "perception/object-tracks.json",
        "robot/robot-control.log",
        "robot/status.jsonl",
        "video/run.mp4",
    ]
    for relative_path in required:
        assert (bundle / relative_path).exists(), f"missing {scenario_id}/{relative_path}"


def assert_config_contracts() -> None:
    tool_manifest = load_json("services/robot-mcp/tool_manifest.json")
    robot_device = load_json("services/robot-mcp/device_config.template.json")
    camera_contract = load_json("services/perception/camera_contract.json")
    camera_device = load_json("services/perception/device_config.template.json")
    camera_rig = load_json("services/perception/camera_rig.template.json")
    integration_manifest = load_json("services/device_integration_manifest.json")

    assert tool_manifest["mode"] == "m2-lane1-hybrid-ready"
    assert set(SCENARIOS).issubset(tool_manifest["supported_scenarios"])
    assert "perception/face-tracks.json" in tool_manifest["required_evidence"]
    assert "perception/object-tracks.json" in tool_manifest["required_evidence"]
    assert any(tool["name"] == "follow_face_anchor" for tool in tool_manifest["tools"])

    assert set(SCENARIOS).issubset(robot_device["supported_scenarios"])
    assert set(robot_device["face_following"]["enabled_for"]) == {
        "demo-full-flow",
        "demo-conversation-grasp",
    }
    assert "grasp_complete" in robot_device["expression_motion_map"]

    assert set(SCENARIOS).issubset(camera_device["supported_scenarios"])
    assert set(camera_device["face_tracking"]["enabled_for"]) == {
        "demo-full-flow",
        "demo-conversation-grasp",
        "demo-real-risk-slice",
    }
    assert set(camera_device["object_tracking"]["enabled_for"]) >= set(SCENARIOS)
    assert camera_rig["camera_switching"]["preserve_prompt_visibility"] is True
    assert set(camera_rig["face_following"]["enabled_for"]) == {
        "demo-full-flow",
        "demo-conversation-grasp",
    }

    assert set(SCENARIOS).issubset(integration_manifest["supported_scenarios"])
    assert set(integration_manifest["lane1_components"]) == {
        "dual-camera-frame-sources",
        "face-tracks",
        "object-tracks",
        "expression-motion-log",
    }

    for scenario_id in SCENARIOS:
        scenario_profile = camera_contract["scenario_profiles"][scenario_id]
        assert set(scenario_profile["required_camera_ids"]) == {"wrist-camera", "laptop-camera"}
        assert scenario_profile["object_tracking"] is True


def assert_scenario_bundle(scenario_id: str) -> None:
    assert_files(scenario_id)

    metadata = load_bundle_json(scenario_id, "metadata.json")
    latency = load_bundle_json(scenario_id, "latency.json")
    result = load_bundle_json(scenario_id, "result.json")
    frame_sources = load_bundle_json(scenario_id, "perception/frame-sources.json")
    face_tracks = load_bundle_json(scenario_id, "perception/face-tracks.json")
    object_tracks = load_bundle_json(scenario_id, "perception/object-tracks.json")
    session_context = load_bundle_json(scenario_id, "redis/session-context.json")

    assert metadata["scenario_id"] == scenario_id
    assert latency["within_threshold"] is True
    assert result["passed"] is True
    assert frame_sources["scenario_id"] == scenario_id
    assert {item["camera_id"] for item in frame_sources["frame_sources"]} == {
        "wrist-camera",
        "laptop-camera",
    }
    assert face_tracks["scenario_id"] == scenario_id
    assert object_tracks["scenario_id"] == scenario_id
    assert session_context["scenario_id"] == scenario_id

    if scenario_id == "demo-sorting":
        assert result["metrics"]["sort_success"] is True
        assert face_tracks["follow_enabled"] is False
    else:
        assert result["metrics"]["face_detected_within_5s"] is True
        assert result["metrics"]["wrist_face_coverage_ratio"] >= 0.7
        assert face_tracks["follow_enabled"] is True

    robot_log = (ROOT / "experiments/evidence" / scenario_id / RUN_ID / "robot/robot-control.log").read_text()
    assert "play_expression_motion" in robot_log
    assert "move_end_effector" in robot_log

    events = [
        json.loads(line)
        for line in (ROOT / "experiments/evidence" / scenario_id / RUN_ID / "events.jsonl").read_text().splitlines()
        if line.strip()
    ]
    event_names = {event["event"] for event in events}
    assert "frame_sources_bound" in event_names
    assert "execution_completed" in event_names
    if scenario_id == "demo-sorting":
        assert "object_target_locked" in event_names
    else:
        assert "face_tracking_locked" in event_names


def main() -> int:
    assert_config_contracts()
    for scenario_id in SCENARIOS:
        assert_scenario_bundle(scenario_id)
    print("M2 lane-1 scenario verification passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
