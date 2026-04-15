# Evidence Bundle Spec

## Path rule

Every verification run writes to:

```text
experiments/evidence/<scenario-id>/<run-id>/
```

## Run-id and attempts

- `scenario-id` must match a canonical benchmark id from
  `experiments/benchmarks/m2-benchmark-freeze.json`.
- `run-id` must be lowercase kebab-case.
- Recommended pattern: `<scenario-id>-attempt-0N-<yyyymmddthhmmssz>`.
- `attempt_index` is an integer from `1` to `3`.
- Failed attempts must remain on disk and in summary reporting.

## Required files

- `metadata.json`
- `summary.md`
- `events.jsonl`
- `latency.json`
- `result.json`

## File rules

- `metadata.json` records versions, operator, benchmark version, and attempt id.
- `events.jsonl` stores one JSON event per line following
  `events.schema.json`.
- `latency.json` stores raw timestamps plus derived millisecond values.
- `result.json` stores pass/fail, final state, metric snapshot, degradations,
  and failure reasons.
- `summary.md` is a short narrative verdict tied to the same run id.
