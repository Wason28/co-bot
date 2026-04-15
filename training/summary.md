# Fine-Tuning Summary

## Run metadata

- run id: `ft-demo-full-flow-placeholder-001`
- base model: `smolvla-placeholder-v1`
- target scenario: `demo-full-flow`

## Dataset snapshot

- sample count: `2`
- object coverage: `red-block`
- capture dates: `2026-04-15`

## Metrics

- `demo_full_flow_completion_rate`: `0.34`
- `demo_full_flow_exec_latency_ms_p95`: `4800`

## Mapping to M2

This placeholder result is mapped to `demo-full-flow` so the M1 verification
lane keeps the minimum acceptable fine-tune artifact aligned with the strongest
mixed interaction demo path rather than a side scenario.

## Evidence link

- `experiments/evidence/demo-real-risk-slice/hybrid-smoke-001`

## Degradations and risks

- degradation: placeholder metrics use the hybrid evidence slice rather than a full live training run
- impact: M1 exit evidence is reviewable now, but M2 still needs a real fine-tuned model result
