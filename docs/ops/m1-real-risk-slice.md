# M1 Real-Risk Slice

This lane-1 slice establishes the minimum hybrid hardware scaffolding for
`demo-real-risk-slice` without taking ownership of backend/orchestrator work
assigned to other lanes.

## Scope

- `services/robot-mcp/` owns the SO-ARM101 hybrid device profile and control-log contract.
- `services/perception/` owns the dual-camera capture contract and frame-source evidence contract.
- `scripts/run_m1_real_risk_slice.py` emits a reviewable hybrid evidence bundle.
- `scripts/verify_m1_real_risk_slice.py` checks the canonical files plus the lane-1-specific artifacts.
- `scripts/verify_m1_exit.py` checks the task-4 M1 exit package, including training placeholders and thesis/doc references.

## Run

```bash
python3 scripts/run_m1_real_risk_slice.py --run-id hybrid-smoke-001
python3 scripts/verify_m1_real_risk_slice.py --run-id hybrid-smoke-001
python3 scripts/verify_m1_exit.py
```

## Evidence

The generator writes:

```text
experiments/evidence/demo-real-risk-slice/<run-id>/
  metadata.json
  summary.md
  events.jsonl
  latency.json
  result.json
  checkpoints/pre-exec.json
  checkpoints/post-exec.json
  redis/session-context.json
  perception/frame-sources.json
  robot/robot-control.log
  video/run.mp4
```

`video/run.mp4` is a placeholder artifact for the hybrid slice until a live
capture path is wired. The placeholder is kept explicit in the summary and
result degradations so the evidence remains auditable.

## M1 Exit Package

Task-4 extends the real-risk slice with the minimum reviewable training and
thesis artifacts required by the M1 exit criteria:

- `training/run-config.json`
- `training/dataset-manifest.json`
- `training/metrics.json`
- `training/summary.md`
- `thesis/chapters/03-experiments.md`

These placeholders are intentionally mapped to `demo-full-flow` so the training
floor stays aligned to a mandatory M2 demonstration path.
