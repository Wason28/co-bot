# Co-Bot M0 Workspace

This workspace contains the M0 foundation for the Co-Bot graduation project.
It preserves the thesis-facing architecture from the planning artifacts while
keeping the initial implementation lightweight and deterministic.

## M0 scope

- repo skeleton for backend, orchestrator, services, frontend, training, experiments, docs, thesis, and references
- frozen benchmark artifact for the mandatory M2 scenarios
- evidence-bundle schemas and naming rules
- minimal runnable stub that writes a canonical evidence bundle
- thesis, deployment, development-log, and experiment templates

## Quick start

Run a deterministic smoke pass:

```bash
python3 scripts/run_m0_stub.py --scenario demo-dangerous-action --run-id smoke-001
python3 scripts/verify_m0.py
```

The smoke run writes evidence under
`experiments/evidence/demo-dangerous-action/smoke-001/`.

## Layout

```text
backend/
docs/
experiments/
frontend/
logs/
models/
orchestrator/
references/
scripts/
services/
thesis/
training/
```
