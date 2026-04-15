# M0 Verification

M0 is complete when the repo skeleton exists, the deterministic benchmark freeze
is checked in, the canonical evidence schemas exist, and the smoke stub can emit
a reviewable evidence bundle.

## Required commands

```bash
python3 scripts/run_m0_stub.py --scenario demo-dangerous-action --run-id smoke-001
python3 scripts/verify_m0.py
```

## Exit evidence

- benchmark freeze: `experiments/benchmarks/m2-benchmark-freeze.json`
- evidence schemas:
  - `experiments/templates/metadata.schema.json`
  - `experiments/templates/events.schema.json`
  - `experiments/templates/latency.schema.json`
  - `experiments/templates/result.schema.json`
- smoke run bundle:
  - `experiments/evidence/demo-dangerous-action/smoke-001/metadata.json`
  - `experiments/evidence/demo-dangerous-action/smoke-001/events.jsonl`
  - `experiments/evidence/demo-dangerous-action/smoke-001/latency.json`
  - `experiments/evidence/demo-dangerous-action/smoke-001/result.json`
  - `experiments/evidence/demo-dangerous-action/smoke-001/summary.md`

## Acceptance mapping

- repo skeleton: directory tree present in root
- runnable stub loop: `scripts/run_m0_stub.py`
- basic logging path: `experiments/evidence/...`
- frozen schemas and benchmark: files above exist and parse as JSON
