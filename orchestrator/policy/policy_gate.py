"""Deterministic policy-gate helpers for the stub orchestration runtime."""

from __future__ import annotations

import json
from dataclasses import dataclass
from functools import lru_cache
from pathlib import Path


RULESET_PATH = Path(__file__).with_name("ruleset.json")


@dataclass(frozen=True)
class PolicyDecision:
    scenario_id: str
    risk_level: str
    requires_confirmation: bool
    allowed_next_states: tuple[str, ...]
    decision_reason: str
    confirmation_state: str
    pending_confirmation_prompt: str


@lru_cache(maxsize=1)
def load_ruleset() -> dict[str, dict[str, object]]:
    payload = json.loads(RULESET_PATH.read_text())
    return {rule["scenario_id"]: rule for rule in payload.get("rules", [])}


def evaluate_policy(scenario_id: str, *, user_input: str) -> PolicyDecision:
    rule = load_ruleset().get(scenario_id)
    if rule is None:
        return PolicyDecision(
            scenario_id=scenario_id,
            risk_level="safe",
            requires_confirmation=False,
            allowed_next_states=("approved", "executing", "completed"),
            decision_reason="Scripted demo remains inside the frozen safe workspace.",
            confirmation_state="approved",
            pending_confirmation_prompt="",
        )

    confirmation_prompt = ""
    if bool(rule["requires_confirmation"]):
        confirmation_prompt = (
            "Confirm the motion before the arm leaves the frozen safe workspace."
            if scenario_id == "demo-real-risk-slice"
            else f"Confirm or reject risky request: {user_input}"
        )

    return PolicyDecision(
        scenario_id=scenario_id,
        risk_level=str(rule["risk_level"]),
        requires_confirmation=bool(rule["requires_confirmation"]),
        allowed_next_states=tuple(str(state) for state in rule["allowed_next_states"]),
        decision_reason=str(rule["decision_reason"]),
        confirmation_state="awaiting_confirm" if bool(rule["requires_confirmation"]) else "approved",
        pending_confirmation_prompt=confirmation_prompt,
    )
