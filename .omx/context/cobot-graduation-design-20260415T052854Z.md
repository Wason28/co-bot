# Context Snapshot: cobot-graduation-design

- Timestamp (UTC): 20260415T052854Z
- Task slug: `cobot-graduation-design`
- Context type: `greenfield`

## Task statement

Design and implement a desktop multimodal embodied intelligence robot prototype system (`Co-Bot`) for an undergraduate thesis. The system is based on the `SO-ARM101` six-axis robotic arm and a laptop compute platform, uses the `LeRobot` framework with `SmolVLA` as the vision-language-action model, and builds an integrated perception-decision-execution closed loop.

## Desired outcome

Deliver a reproducible prototype system, complete source repository, deployment documentation, demo video, development logs, reference-material corpus, and a thesis that advances in parallel with implementation until final submission.

## Stated solution

The user proposes:
- dual-camera perception: wrist USB camera + laptop built-in camera
- LangGraph `StateGraph` orchestration with a `Supervisor Agent`
- social interaction agent via `Ollama` + `Qwen2.5-3B/7B`
- action execution agent via `SmolVLA`
- LangGraph checkpoints + Redis long-term memory
- MCP-based `SO-ARM101` control service
- FastAPI backend + React/TypeScript frontend + optional `Three.js`
- hot model switching + async task queue
- teleoperation data collection (50-100 demos) + SmolVLA fine-tuning
- quantitative evaluation on grasping and mixed interaction tasks
- synchronized engineering and thesis-writing workflow

## Probable intent hypothesis

The user needs a graduation-project-grade system plan and execution path that balances research rigor, demonstrable system value, reproducibility, and paper/thesis deliverables under undergraduate time/resource constraints.

## Known facts / evidence

- Workspace currently contains `.omx` metadata only; no application code exists yet.
- The requested system spans hardware integration, multimodal inference, agent orchestration, web application, data collection/fine-tuning, evaluation, and thesis production.
- The user explicitly wants the full development process logged, references collected, and thesis materials drafted alongside implementation.

## Constraints

- Must stay low-cost and modular.
- Must support two cameras and a laptop-based setup.
- Must use the specified architectural ingredients unless clarified otherwise.
- Must support interruption recovery and long-term memory.
- Must provide both software artifacts and academic deliverables.

## Unknowns / open questions

- Which outcome is primary: research demonstration, engineering completeness, or thesis defensibility?
- What level of prototype realism is required for the first milestone?
- Which parts are hard requirements versus negotiable defaults?
- What exact acceptance criteria define success for system, demo, and thesis?
- What schedule, hardware readiness, and compute budget constraints exist?

## Decision-boundary unknowns

- Which architecture/tooling decisions may be made autonomously during implementation?
- Which components must remain fixed for the thesis proposal/defense?
- What tradeoffs are unacceptable if schedule or hardware limits appear?

## Likely touchpoints

- `.omx/context/`
- `.omx/interviews/`
- `.omx/specs/`
- future backend, frontend, robotics control, training, docs, thesis, and experiment directories
