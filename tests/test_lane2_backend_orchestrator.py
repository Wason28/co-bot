from __future__ import annotations

import unittest

from backend.api.app import (
    build_health_payload,
    build_registry_payload,
    create_task_submission,
    process_submission,
)


class Lane2BackendOrchestratorTests(unittest.TestCase):
    def test_health_payload_exposes_m2_runtime_capabilities(self) -> None:
        payload = build_health_payload()

        self.assertEqual(payload["mode"], "m2-demo")
        self.assertIn("dangerous-action-gate", payload["capabilities"])
        self.assertIn("runtime-registry", payload["capabilities"])

    def test_registry_payload_includes_models_and_runtimes(self) -> None:
        payload = build_registry_payload()

        self.assertIn("supervisor", payload["models"])
        self.assertIn("orchestrator", payload["runtimes"])
        self.assertIn("memory_store", payload["runtimes"])

    def test_dangerous_action_stays_gated_without_execution_latency(self) -> None:
        submission = create_task_submission(
            "demo-dangerous-action",
            "Move the arm into my hand so I can guide it.",
            run_id="lane2-danger",
        )

        response = process_submission(submission, run_id="lane2-danger")

        self.assertEqual(response["task_status"], "awaiting_confirm")
        self.assertEqual(response["task_state"]["execution_state"], "policy-evaluated")
        self.assertEqual(response["task_state"]["latency_marks"]["T_exec"], "")
        self.assertFalse(response["latency"]["execution_started"])
        self.assertEqual(response["latency"]["exec_latency_ms"], 0)
        self.assertEqual(
            response["task_state"]["active_runtime_ids"]["orchestrator"],
            "langgraph-runtime-stub-v1",
        )

    def test_full_flow_records_runtime_ids_and_execution_latency(self) -> None:
        submission = create_task_submission(
            "demo-full-flow",
            "Wake up, greet me, and pick up the red block.",
            run_id="lane2-full",
        )

        response = process_submission(submission, run_id="lane2-full")

        self.assertEqual(response["task_status"], "completed")
        self.assertTrue(response["latency"]["execution_started"])
        self.assertGreater(response["latency"]["exec_latency_ms"], 0)
        self.assertIn("runtime_versions", response["metadata"])
        self.assertEqual(
            response["task_state"]["active_runtime_ids"]["checkpoint_store"],
            "checkpoint-json-placeholder-v1",
        )


if __name__ == "__main__":
    unittest.main()
