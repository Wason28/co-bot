"""Deterministic orchestration helpers for the Co-Bot demo flows."""

from __future__ import annotations

import json
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from typing import Any

from backend.api.app import (
    TaskSubmission,
    build_submission_event,
    build_task_status_payload,
)
from orchestrator.policy.policy_gate import evaluate_policy


@dataclass(frozen=True)
class StubDecision:
    scenario_id: str
    route_decision: str
    risk_level: str
    confirmation_state: str
    outcome: str


@dataclass(frozen=True)
class ScenarioProfile:
    scenario_id: str
    task_type: str
    route_decision: str
    risk_level: str
    confirmation_state: str
    outcome: str
    input_text: str
    perception_summary: str
    action_plan_summary: str


@dataclass(frozen=True)
class RunArtifacts:
    metadata: dict[str, Any]
    events: list[dict[str, Any]]
    latency: dict[str, Any]
    result: dict[str, Any]
    summary: str
    checkpoints: dict[str, dict[str, Any]]
    redis_records: dict[str, dict[str, Any]]


SCENARIO_CATALOG = {
    "demo-full-flow": ScenarioProfile(
        scenario_id="demo-full-flow",
        task_type="mixed",
        route_decision="mixed",
        risk_level="safe",
        confirmation_state="completed",
        outcome="completed",
        input_text="Wake up, greet me, and pick up the red block before resting again.",
        perception_summary="Dual-camera placeholders ready for face and tabletop tracking.",
        action_plan_summary="Wake, greet, converse, align, grasp the red block, and return to idle.",
    ),
    "demo-sorting": ScenarioProfile(
        scenario_id="demo-sorting",
        task_type="action",
        route_decision="action",
        risk_level="safe",
        confirmation_state="completed",
        outcome="completed",
        input_text="Sort the red block into target bin A.",
        perception_summary="Tabletop object map prepared from the wrist camera placeholder.",
        action_plan_summary="Detect the red block, align the gripper, and place it into target bin A.",
    ),
    "demo-conversation-grasp": ScenarioProfile(
        scenario_id="demo-conversation-grasp",
        task_type="mixed",
        route_decision="mixed",
        risk_level="safe",
        confirmation_state="completed",
        outcome="completed",
        input_text="Before you rest, could you also pick up the red block for me?",
        perception_summary="Conversation context and tabletop perception are both active.",
        action_plan_summary="Handle the social reply, then execute a single grasp plan for the red block.",
    ),
    "demo-dangerous-action": ScenarioProfile(
        scenario_id="demo-dangerous-action",
        task_type="action",
        route_decision="action",
        risk_level="dangerous",
        confirmation_state="awaiting_confirm",
        outcome="gated",
        input_text="Move the arm into my hand so I can guide it.",
        perception_summary="Human-safe zone detected inside the frozen workspace boundary.",
        action_plan_summary="No execution plan may start until the risky request is confirmed or rejected.",
    ),
    "demo-recovery-memory": ScenarioProfile(
        scenario_id="demo-recovery-memory",
        task_type="mixed",
        route_decision="mixed",
        risk_level="confirm",
        confirmation_state="resumed",
        outcome="resumed",
        input_text="Resume the interrupted conversation-and-grasp session.",
        perception_summary="Last known user and tabletop context restored from placeholder memory.",
        action_plan_summary="Resume from the last safe checkpoint after reloading the session context.",
    ),
    "demo-real-risk-slice": ScenarioProfile(
        scenario_id="demo-real-risk-slice",
        task_type="mixed",
        route_decision="mixed",
        risk_level="confirm",
        confirmation_state="completed",
        outcome="completed",
        input_text="Run the real-risk slice with dual cameras, confirmation, and the red-block grasp flow.",
        perception_summary="Dual-camera placeholders bound for user-facing and wrist-facing streams.",
        action_plan_summary="Hold at the confirmation checkpoint, then execute the red-block grasp flow.",
    ),
}

SCENARIO_DECISIONS = {
    scenario_id: StubDecision(
        scenario_id=profile.scenario_id,
        route_decision=profile.route_decision,
        risk_level=profile.risk_level,
        confirmation_state=profile.confirmation_state,
        outcome=profile.outcome,
    )
    for scenario_id, profile in SCENARIO_CATALOG.items()
}


def utc_now() -> datetime:
    return datetime.now(timezone.utc).replace(microsecond=0)


def _clone_state(state: dict[str, Any]) -> dict[str, Any]:
    return json.loads(json.dumps(state))


def _checkpoint_snapshot(state: dict[str, Any], checkpoint_id: str) -> dict[str, Any]:
    snapshot = _clone_state(state)
    snapshot["last_safe_checkpoint_id"] = checkpoint_id
    return snapshot


def _base_state(
    submission: TaskSubmission,
    profile: ScenarioProfile,
    *,
    model_ids: dict[str, str],
    runtime_ids: dict[str, str],
    started_at: datetime,
) -> dict[str, Any]:
    return {
        "session_id": submission.session_id,
        "task_id": submission.task_id,
        "turn_id": submission.turn_id,
        "correlation_id": submission.correlation_id,
        "user_input": submission.input_text,
        "task_type": profile.task_type,
        "route_decision": "blocked",
        "risk_level": profile.risk_level,
        "confirmation_state": "proposed",
        "perception_summary": "Perception not initialized yet.",
        "action_plan_summary": "Waiting for routing decision.",
        "execution_state": "submitted",
        "recovery_pointer": "",
        "last_safe_checkpoint_id": "ckpt-submitted-001",
        "last_completed_step": "task-submitted",
        "pending_confirmation_prompt": "",
        "active_model_ids": dict(model_ids),
        "active_runtime_ids": dict(runtime_ids),
        "latency_marks": {
            "T_start": started_at.isoformat(),
            "T_decision": "",
            "T_exec": "",
        },
    }


def _record_checkpoint(
    checkpoints: dict[str, dict[str, Any]],
    events: list[dict[str, Any]],
    state: dict[str, Any],
    *,
    filename: str,
    checkpoint_id: str,
    timestamp: datetime,
    note: str,
) -> None:
    checkpoints[filename] = _checkpoint_snapshot(state, checkpoint_id)
    state["last_safe_checkpoint_id"] = checkpoint_id
    events.append(
        {
            "timestamp": timestamp.isoformat(),
            "module": "checkpoint",
            "event": "checkpoint_saved",
            "session_id": state["session_id"],
            "task_id": state["task_id"],
            "correlation_id": state["correlation_id"],
            "state": state["confirmation_state"],
            "payload": {
                "checkpoint_id": checkpoint_id,
                "filename": filename,
                "note": note,
            },
        }
    )


def _record_memory(state: dict[str, Any], note: str) -> dict[str, Any]:
    record = _clone_state(state)
    record["memory_note"] = note
    record["status_payload"] = build_task_status_payload(state)
    return record


def _build_metrics(scenario_id: str, *, exec_latency_ms: int) -> dict[str, Any]:
    metrics: dict[str, Any] = {"exec_latency_ms": exec_latency_ms}
    if scenario_id in {"demo-full-flow", "demo-real-risk-slice"}:
        metrics.update(
            {
                "face_detected_within_5s": True,
                "wrist_face_coverage_ratio": 0.75,
                "expression_motion_count": 2,
                "confirmation_shown": scenario_id == "demo-real-risk-slice",
            }
        )
    elif scenario_id == "demo-sorting":
        metrics["sort_success"] = True
    elif scenario_id == "demo-dangerous-action":
        metrics["confirmation_shown"] = True
    elif scenario_id == "demo-recovery-memory":
        metrics["recovery_fields_preserved"] = True

    return metrics


def run_stub_scenario(
    submission: TaskSubmission,
    *,
    run_id: str,
    attempt_index: int,
    benchmark: dict[str, Any],
    model_registry: dict[str, Any],
    runtime_registry: dict[str, Any] | None = None,
    started_at: datetime | None = None,
) -> RunArtifacts:
    profile = SCENARIO_CATALOG[submission.scenario_id]
    started_at = started_at or utc_now()
    t_route = started_at + timedelta(milliseconds=1400)
    t_policy = t_route + timedelta(milliseconds=300)
    t_confirm = t_policy + timedelta(milliseconds=350)
    t_exec = started_at + timedelta(milliseconds=3200)
    t_complete = t_exec + timedelta(milliseconds=600)
    model_ids = {
        "supervisor": model_registry["supervisor"]["id"],
        "social": model_registry["social"]["id"],
        "action": model_registry["action"]["id"],
    }
    runtime_registry = runtime_registry or {}
    runtime_ids = {
        "orchestrator": runtime_registry.get("orchestrator", {}).get(
            "id", "langgraph-runtime-stub-v1"
        ),
        "checkpoint_store": runtime_registry.get("checkpoint_store", {}).get(
            "id", "checkpoint-json-placeholder-v1"
        ),
        "memory_store": runtime_registry.get("memory_store", {}).get(
            "id", "redis-session-placeholder-v1"
        ),
        "latency_recorder": runtime_registry.get("latency_recorder", {}).get(
            "id", "latency-markers-v1"
        ),
    }

    metadata = {
        "scenario_id": submission.scenario_id,
        "run_id": run_id,
        "attempt_index": attempt_index,
        "benchmark_version": benchmark["version"],
        "operator": runtime_ids["orchestrator"],
        "created_at": started_at.isoformat(),
        "model_versions": dict(model_ids),
        "runtime_versions": dict(runtime_ids),
        "device_versions": {
            "robot_arm": "so-arm101-placeholder-v1",
            "wrist_camera": "usb-cam-placeholder-v1",
            "laptop_camera": "builtin-cam-placeholder-v1",
        },
        "shared_state_contract": "orchestrator/langgraph/state_schema.json",
    }

    state = _base_state(
        submission,
        profile,
        model_ids=model_ids,
        runtime_ids=runtime_ids,
        started_at=started_at,
    )
    events = [build_submission_event(submission)]
    checkpoints: dict[str, dict[str, Any]] = {}
    redis_records: dict[str, dict[str, Any]] = {}

    state["route_decision"] = profile.route_decision
    state["execution_state"] = "routed"
    state["perception_summary"] = profile.perception_summary
    state["action_plan_summary"] = profile.action_plan_summary
    state["last_completed_step"] = "route-decided"
    state["latency_marks"]["T_decision"] = t_route.isoformat()
    events.append(
        {
            "timestamp": t_route.isoformat(),
            "module": "supervisor",
            "event": "route_decided",
            "session_id": submission.session_id,
            "task_id": submission.task_id,
            "correlation_id": submission.correlation_id,
            "state": profile.route_decision,
            "payload": {
                "task_type": profile.task_type,
                "risk_level": profile.risk_level,
            },
        }
    )
    _record_checkpoint(
        checkpoints,
        events,
        state,
        filename="post-route.json",
        checkpoint_id="ckpt-route-001",
        timestamp=t_route,
        note="checkpoint after supervisor routing",
    )

    policy = evaluate_policy(submission.scenario_id, user_input=submission.input_text)
    state["risk_level"] = policy.risk_level
    state["confirmation_state"] = policy.confirmation_state
    state["pending_confirmation_prompt"] = policy.pending_confirmation_prompt
    state["execution_state"] = "policy-evaluated"
    state["last_completed_step"] = "policy-evaluated"
    events.append(
        {
            "timestamp": t_policy.isoformat(),
            "module": "policy-gate",
            "event": "policy_evaluated",
            "session_id": submission.session_id,
            "task_id": submission.task_id,
            "correlation_id": submission.correlation_id,
            "state": state["confirmation_state"],
            "payload": {
                "risk_level": policy.risk_level,
                "requires_confirmation": policy.requires_confirmation,
                "decision_reason": policy.decision_reason,
                "allowed_next_states": list(policy.allowed_next_states),
            },
        }
    )
    _record_checkpoint(
        checkpoints,
        events,
        state,
        filename="post-policy.json",
        checkpoint_id="ckpt-policy-001",
        timestamp=t_policy,
        note="checkpoint after policy gate evaluation",
    )

    if submission.scenario_id == "demo-real-risk-slice":
        events.append(
            {
                "timestamp": t_confirm.isoformat(),
                "module": "policy-gate",
                "event": "confirmation_recorded",
                "session_id": submission.session_id,
                "task_id": submission.task_id,
                "correlation_id": submission.correlation_id,
                "state": "approved",
                "payload": {
                    "confirmation_source": "human-visible-placeholder",
                    "prompt": policy.pending_confirmation_prompt,
                },
            }
        )
        state["confirmation_state"] = "approved"
        state["pending_confirmation_prompt"] = ""
        state["execution_state"] = "approved"
        state["last_completed_step"] = "confirmation-approved"

    if profile.task_type == "mixed":
        events.append(
            {
                "timestamp": (t_route + timedelta(milliseconds=100)).isoformat(),
                "module": "social-agent",
                "event": "social_response_prepared",
                "session_id": submission.session_id,
                "task_id": submission.task_id,
                "correlation_id": submission.correlation_id,
                "state": state["confirmation_state"],
                "payload": {
                    "summary": "Greeting and short conversation prepared.",
                },
            }
        )

    if submission.scenario_id in {"demo-full-flow", "demo-real-risk-slice"}:
        events.append(
            {
                "timestamp": (t_route + timedelta(milliseconds=180)).isoformat(),
                "module": "perception",
                "event": "dual_camera_sources_attached",
                "session_id": submission.session_id,
                "task_id": submission.task_id,
                "correlation_id": submission.correlation_id,
                "state": "ready",
                "payload": {
                    "sources": ["laptop_camera", "wrist_camera"],
                },
            }
        )

    if submission.scenario_id == "demo-recovery-memory":
        _record_checkpoint(
            checkpoints,
            events,
            state,
            filename="pre-interrupt.json",
            checkpoint_id="ckpt-pre-interrupt-001",
            timestamp=t_exec,
            note="checkpoint before simulated interrupt",
        )
        redis_records["session-context.json"] = _record_memory(
            state,
            "placeholder redis context before simulated recovery",
        )
        events.append(
            {
                "timestamp": (t_exec + timedelta(milliseconds=150)).isoformat(),
                "module": "memory",
                "event": "session_context_saved",
                "session_id": submission.session_id,
                "task_id": submission.task_id,
                "correlation_id": submission.correlation_id,
                "state": state["confirmation_state"],
                "payload": {
                    "record": "redis/session-context.json",
                },
            }
        )
        state["confirmation_state"] = "resumed"
        state["execution_state"] = "resumed"
        state["recovery_pointer"] = "redis/session-context.json"
        state["last_completed_step"] = "resumed-from-checkpoint"
        state["latency_marks"]["T_exec"] = t_exec.isoformat()
        events.append(
            {
                "timestamp": (t_exec + timedelta(milliseconds=300)).isoformat(),
                "module": "memory",
                "event": "session_context_restored",
                "session_id": submission.session_id,
                "task_id": submission.task_id,
                "correlation_id": submission.correlation_id,
                "state": "resumed",
                "payload": {
                    "recovery_pointer": state["recovery_pointer"],
                },
            }
        )
        _record_checkpoint(
            checkpoints,
            events,
            state,
            filename="post-resume.json",
            checkpoint_id="ckpt-post-resume-001",
            timestamp=(t_exec + timedelta(milliseconds=300)),
            note="checkpoint after restoring the placeholder session context",
        )
    elif submission.scenario_id != "demo-dangerous-action":
        events.append(
            {
                "timestamp": (t_exec - timedelta(milliseconds=250)).isoformat(),
                "module": "action-agent",
                "event": "plan_ready",
                "session_id": submission.session_id,
                "task_id": submission.task_id,
                "correlation_id": submission.correlation_id,
                "state": state["confirmation_state"],
                "payload": {
                    "plan_summary": profile.action_plan_summary,
                },
            }
        )
        _record_checkpoint(
            checkpoints,
            events,
            state,
            filename="pre-execution.json",
            checkpoint_id="ckpt-pre-execution-001",
            timestamp=(t_exec - timedelta(milliseconds=200)),
            note="checkpoint right before robot execution",
        )
        redis_records["session-context.json"] = _record_memory(
            state,
            "placeholder redis context for the active task",
        )
        events.append(
            {
                "timestamp": (t_exec - timedelta(milliseconds=100)).isoformat(),
                "module": "memory",
                "event": "session_context_saved",
                "session_id": submission.session_id,
                "task_id": submission.task_id,
                "correlation_id": submission.correlation_id,
                "state": state["confirmation_state"],
                "payload": {
                    "record": "redis/session-context.json",
                },
            }
        )
        state["latency_marks"]["T_exec"] = t_exec.isoformat()
        state["confirmation_state"] = "executing"
        state["execution_state"] = "executing"
        state["last_completed_step"] = "execution-started"
        events.append(
            {
                "timestamp": t_exec.isoformat(),
                "module": "robot-mcp",
                "event": "execution_started",
                "session_id": submission.session_id,
                "task_id": submission.task_id,
                "correlation_id": submission.correlation_id,
                "state": "executing",
                "payload": {
                    "tool": "move_end_effector",
                },
            }
        )
        state["confirmation_state"] = profile.confirmation_state
        state["execution_state"] = "completed"
        state["last_completed_step"] = "task-completed"
        events.append(
            {
                "timestamp": t_complete.isoformat(),
                "module": "robot-mcp",
                "event": "execution_completed",
                "session_id": submission.session_id,
                "task_id": submission.task_id,
                "correlation_id": submission.correlation_id,
                "state": state["confirmation_state"],
                "payload": {
                    "outcome": profile.outcome,
                },
            }
        )
    else:
        redis_records["session-context.json"] = _record_memory(
            state,
            "placeholder redis context captured at the confirmation boundary",
        )
        events.append(
            {
                "timestamp": (t_policy + timedelta(milliseconds=100)).isoformat(),
                "module": "memory",
                "event": "session_context_saved",
                "session_id": submission.session_id,
                "task_id": submission.task_id,
                "correlation_id": submission.correlation_id,
                "state": state["confirmation_state"],
                "payload": {
                    "record": "redis/session-context.json",
                },
            }
        )

    execution_started = bool(state["latency_marks"]["T_exec"])
    exec_latency_ms = (
        int((t_exec - started_at).total_seconds() * 1000) if execution_started else 0
    )
    latency = {
        "scenario_id": submission.scenario_id,
        "run_id": run_id,
        "attempt_index": attempt_index,
        "T_start": started_at.isoformat(),
        "T_decision": t_route.isoformat(),
        "T_exec": state["latency_marks"]["T_exec"],
        "decision_latency_ms": int((t_route - started_at).total_seconds() * 1000),
        "exec_latency_ms": exec_latency_ms,
        "execution_started": execution_started,
        "within_threshold": exec_latency_ms <= benchmark["latency_threshold_ms"],
    }

    failure_reasons: list[str] = []
    if execution_started and not latency["within_threshold"]:
        failure_reasons.append("execution exceeded frozen benchmark latency threshold")
    if submission.scenario_id == "demo-dangerous-action" and (
        state["confirmation_state"] not in {"awaiting_confirm", "rejected"}
        or execution_started
    ):
        failure_reasons.append("dangerous action was not held at the confirmation boundary")
    if submission.scenario_id == "demo-recovery-memory":
        required_fields = benchmark["scenarios"]["demo-recovery-memory"]["required_fields"]
        redis_state = redis_records["session-context.json"]
        missing_fields = [field for field in required_fields if field not in redis_state]
        if missing_fields:
            failure_reasons.append(
                "recovery context is missing required fields: " + ", ".join(sorted(missing_fields))
            )

    result = {
        "scenario_id": submission.scenario_id,
        "run_id": run_id,
        "attempt_index": attempt_index,
        "passed": not failure_reasons,
        "final_state": state["confirmation_state"],
        "metrics": _build_metrics(submission.scenario_id, exec_latency_ms=exec_latency_ms),
        "degradations": [
            "stub-runtime-no-live-hardware",
            "stub-runtime-no-live-models",
            "placeholder-checkpoint-redis",
        ],
        "failure_reasons": failure_reasons,
    }

    summary = "\n".join(
        [
            f"# Summary - {submission.scenario_id}",
            "",
            f"- run id: `{run_id}`",
            f"- attempt: `{attempt_index}`",
            f"- final state: `{result['final_state']}`",
            f"- passed: `{result['passed']}`",
            f"- exec latency ms: `{exec_latency_ms}`",
            f"- checkpoints: `{', '.join(sorted(checkpoints))}`",
            f"- redis records: `{', '.join(sorted(redis_records))}`",
        ]
    )

    return RunArtifacts(
        metadata=metadata,
        events=events,
        latency=latency,
        result=result,
        summary=summary,
        checkpoints=checkpoints,
        redis_records=redis_records,
    )
