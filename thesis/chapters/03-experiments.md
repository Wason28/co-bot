# Chapter 3 - Experiments

## Benchmark and evidence baseline

- benchmark freeze: `experiments/benchmarks/m2-benchmark-freeze.json`
- mandatory M1 evidence bundle:
  `experiments/evidence/demo-real-risk-slice/hybrid-smoke-001`
- exit verification guide: `docs/ops/m1-verification.md`

## M1 real-risk slice

The `demo-real-risk-slice` bundle is the main cross-layer experiment artifact
for M1. It records robot control, dual-camera frame-source binding, policy-gate
events, checkpoints, Redis export, and the latency record for the mixed
interaction path.

## Minimum fine-tune placeholder

The current minimum fine-tune placeholder is mapped to `demo-full-flow` instead
of a side scenario so the first reviewable training artifact stays aligned with
the most demanding M1 mixed task.

- config: `training/run-config.json`
- dataset: `training/dataset-manifest.json`
- metrics: `training/metrics.json`
- summary: `training/summary.md`

## Metrics to carry forward

- `demo_full_flow_completion_rate`
- `demo_full_flow_exec_latency_ms_p95`
- `demo-real-risk-slice` bundle completeness

## Remaining risks

- `video/run.mp4` is still a placeholder artifact in the hybrid bundle
- the fine-tune result is reviewable but not yet backed by a live training run
