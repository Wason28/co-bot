"""Backend contracts for deterministic Co-Bot orchestration demos."""

from __future__ import annotations

import json
import sys
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Mapping


ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

BENCHMARK_PATH = ROOT / "experiments/benchmarks/m2-benchmark-freeze.json"
MODEL_REGISTRY_PATH = ROOT / "models/runtime/model_registry.template.json"


@dataclass(frozen=True)
class TaskSubmission:
    session_id: str
    task_id: str
    turn_id: str
    correlation_id: str
    input_text: str
    scenario_id: str
    submitted_at: str


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text())


def utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def create_task_submission(
    scenario_id: str,
    input_text: str,
    *,
    run_id: str,
    submitted_at: str | None = None,
) -> TaskSubmission:
    return TaskSubmission(
        session_id=f"session-{run_id}",
        task_id=f"task-{run_id}",
        turn_id=f"turn-{run_id}-01",
        correlation_id=f"corr-{run_id}",
        input_text=input_text,
        scenario_id=scenario_id,
        submitted_at=submitted_at or utc_now(),
    )


def build_health_payload() -> dict[str, Any]:
    return {
        "service": "backend-api",
        "mode": "m1-demo",
        "status": "ready",
        "capabilities": [
            "task-submit",
            "langgraph-shared-state",
            "policy-gate",
            "checkpoint-placeholder",
            "redis-placeholder",
            "latency-instrumentation",
        ],
    }


def build_submission_event(submission: TaskSubmission) -> dict[str, Any]:
    return {
        "timestamp": submission.submitted_at,
        "module": "backend-api",
        "event": "task_submitted",
        "session_id": submission.session_id,
        "task_id": submission.task_id,
        "correlation_id": submission.correlation_id,
        "state": "proposed",
        "payload": {
            "scenario_id": submission.scenario_id,
            "turn_id": submission.turn_id,
            "input_text": submission.input_text,
        },
    }


def build_task_status_payload(shared_state: Mapping[str, Any]) -> dict[str, Any]:
    payload = {
        "session_id": shared_state["session_id"],
        "task_id": shared_state["task_id"],
        "turn_id": shared_state.get("turn_id", ""),
        "correlation_id": shared_state["correlation_id"],
        "route_decision": shared_state["route_decision"],
        "risk_level": shared_state["risk_level"],
        "confirmation_state": shared_state["confirmation_state"],
        "execution_state": shared_state["execution_state"],
        "pending_confirmation_prompt": shared_state.get(
            "pending_confirmation_prompt", ""
        ),
        "active_model_ids": dict(shared_state["active_model_ids"]),
        "latency_marks": dict(shared_state["latency_marks"]),
    }
    if "scenario_id" in shared_state:
        payload["scenario_id"] = shared_state["scenario_id"]
    return payload


def process_submission(
    submission: TaskSubmission,
    *,
    run_id: str | None = None,
    attempt_index: int = 1,
) -> dict[str, Any]:
    from orchestrator.langgraph.stub_runtime import run_stub_scenario
    from orchestrator.policy.policy_gate import evaluate_policy

    benchmark = load_json(BENCHMARK_PATH)
    model_registry = load_json(MODEL_REGISTRY_PATH)
    artifacts = run_stub_scenario(
        submission,
        run_id=run_id or submission.task_id.removeprefix("task-"),
        attempt_index=attempt_index,
        benchmark=benchmark,
        model_registry=model_registry,
    )
    policy = evaluate_policy(submission.scenario_id, user_input=submission.input_text)
    redis_context = artifacts.redis_records.get("session-context.json", {})
    if "post-resume.json" in artifacts.checkpoints:
        task_state = dict(artifacts.checkpoints["post-resume.json"])
    elif redis_context:
        task_state = {
            key: value
            for key, value in redis_context.items()
            if key not in {"memory_note", "status_payload"}
        }
    else:
        latest_checkpoint = artifacts.checkpoints[sorted(artifacts.checkpoints)[-1]]
        task_state = dict(latest_checkpoint)
    task_state["scenario_id"] = submission.scenario_id
    task_state["confirmation_state"] = artifacts.result["final_state"]
    task_state["latency_marks"] = {
        "T_start": artifacts.latency["T_start"],
        "T_decision": artifacts.latency["T_decision"],
        "T_exec": artifacts.latency["T_exec"],
    }
    if artifacts.result["final_state"] == "completed":
        task_state["execution_state"] = "completed"
        task_state["last_completed_step"] = "task-completed"
        task_state["pending_confirmation_prompt"] = ""
    elif artifacts.result["final_state"] == "resumed":
        task_state["execution_state"] = "resumed"
        task_state["last_completed_step"] = "resumed-from-checkpoint"
    policy_payload = {
        "scenario_id": policy.scenario_id,
        "risk_level": policy.risk_level,
        "requires_confirmation": policy.requires_confirmation,
        "allowed_next_states": list(policy.allowed_next_states),
        "decision_reason": policy.decision_reason,
        "confirmation_state": policy.confirmation_state,
        "pending_confirmation_prompt": policy.pending_confirmation_prompt,
    }
    return {
        "submission": asdict(submission),
        "task_status": artifacts.result["final_state"],
        "task_state": task_state,
        "shared_state": task_state,
        "policy_gate": policy_payload,
        "policy_decision": policy_payload,
        "checkpoints": artifacts.checkpoints,
        "redis_context": redis_context,
        "events": artifacts.events,
        "latency": artifacts.latency,
        "result": artifacts.result,
        "metadata": artifacts.metadata,
        "summary": artifacts.summary,
    }


def submit_task(
    submission: TaskSubmission,
    *,
    run_id: str | None = None,
    attempt_index: int = 1,
) -> dict[str, Any]:
    return process_submission(
        submission,
        run_id=run_id,
        attempt_index=attempt_index,
    )


def submission_example() -> dict[str, Any]:
    example = create_task_submission(
        scenario_id="demo-full-flow",
        input_text="Wake up, greet me, and pick up the red block.",
        run_id="demo-001",
        submitted_at="2026-04-15T06:30:00+00:00",
    )
    return process_submission(example, run_id="demo-001")


if __name__ == "__main__":
    print(json.dumps(build_health_payload(), indent=2))
    print(json.dumps(submission_example(), indent=2))
