# M1 Verification

M1 is complete when the real-risk slice evidence is reviewable, the minimum
fine-tune placeholder is mapped to `demo-full-flow`, and the thesis experiment
chapter references both artifacts.

## Required commands

```bash
python3 scripts/verify_m0.py
python3 scripts/verify_m1_real_risk_slice.py --run-id hybrid-smoke-001
python3 scripts/verify_m1_exit.py
```

## Exit evidence

- real-risk slice bundle:
  - `experiments/evidence/demo-real-risk-slice/hybrid-smoke-001/metadata.json`
  - `experiments/evidence/demo-real-risk-slice/hybrid-smoke-001/events.jsonl`
  - `experiments/evidence/demo-real-risk-slice/hybrid-smoke-001/latency.json`
  - `experiments/evidence/demo-real-risk-slice/hybrid-smoke-001/result.json`
  - `experiments/evidence/demo-real-risk-slice/hybrid-smoke-001/checkpoints/pre-exec.json`
  - `experiments/evidence/demo-real-risk-slice/hybrid-smoke-001/checkpoints/post-exec.json`
  - `experiments/evidence/demo-real-risk-slice/hybrid-smoke-001/redis/session-context.json`
  - `experiments/evidence/demo-real-risk-slice/hybrid-smoke-001/perception/frame-sources.json`
  - `experiments/evidence/demo-real-risk-slice/hybrid-smoke-001/robot/robot-control.log`
  - `experiments/evidence/demo-real-risk-slice/hybrid-smoke-001/video/run.mp4`
- minimum fine-tune placeholder:
  - `training/run-config.json`
  - `training/dataset-manifest.json`
  - `training/metrics.json`
  - `training/summary.md`
- thesis experiment mapping:
  - `thesis/chapters/03-experiments.md`

## Acceptance mapping

- `E2E-6` real-risk slice: verified by `scripts/verify_m1_real_risk_slice.py`
- minimum fine-tune placeholder: mapped to `demo-full-flow` in `training/metrics.json`
- M1 exit evidence owner: `scripts/verify_m1_exit.py` centralizes the regression checks
- thesis traceability: `thesis/chapters/03-experiments.md` references the same evidence and metric path
