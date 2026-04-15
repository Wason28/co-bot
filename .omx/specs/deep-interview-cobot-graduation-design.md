# Deep Interview Spec: Co-Bot Graduation Design

## Metadata

- Profile: `standard`
- Rounds: `5`
- Final ambiguity: `12.3%`
- Threshold: `20.0%`
- Context type: `greenfield`
- Context snapshot: `.omx/context/cobot-graduation-design-20260415T052854Z.md`
- Transcript: `.omx/interviews/cobot-graduation-design-20260415T055211Z.md`

## Clarity breakdown

| Dimension | Score |
| --- | ---: |
| Intent | 0.86 |
| Outcome | 0.90 |
| Scope | 0.90 |
| Constraints | 0.84 |
| Success | 0.88 |

## Intent

Prove that a low-cost, limited-resource undergraduate project can still realize a complete, working, and academically defensible desktop embodied robot system with an integrated perception-decision-execution loop and a meaningful degree of interaction intelligence.

## Desired outcome

Deliver a desktop multimodal embodied robot prototype (`Co-Bot`) based on `SO-ARM101` and a laptop platform, plus a synchronized thesis package. The minimum acceptable outcome is not a toy demo but an `M2` defense-ready system:
- all mandatory thesis demos are present and stable enough to be shown within the defined retry budget
- multimodal interaction and physical execution are both demonstrable
- there is at least one fine-tuning result and one quantitative evaluation package
- checkpoint/memory capabilities are demonstrable
- the thesis has enough substance to support methods, experiments, and results chapters

## In scope

- `SO-ARM101` robotic-arm prototype integration on a laptop-based setup
- Dual-camera perception:
  - wrist USB camera for fine manipulation
  - laptop built-in camera for global/front view
- LangGraph `StateGraph` orchestration with:
  - a `Supervisor Agent` for intent recognition and routing
  - a social interaction agent using `Ollama` with `Qwen2.5-3B/7B`-class local models and role/persona injection
  - an action execution agent using `SmolVLA` within the `LeRobot` stack
- LangGraph checkpoint-based state handling and Redis-backed long-term memory
- MCP-style robotic-arm control service with standard tools for joint movement, end-effector motion, gripper control, status inspection, and expressive motions
- FastAPI backend with REST + WebSocket interfaces
- React + TypeScript frontend with model management, task console, status monitoring, and camera display
- Model hot-switching and asynchronous task handling when feasible
- Teleoperation data collection and `SmolVLA` fine-tuning, potentially scaled down but not eliminated
- Quantitative evaluation on desktop grasping and mixed interaction tasks
- Deployment documentation, demo video, complete development log, reference collection, and synchronized thesis drafting

## Out of scope / Non-goals

- Proving better performance than SOTA systems
- Matching industrial robots in precision, speed, or reliability
- Achieving 100% task success
- Solving universal object grasping or long-horizon general manipulation
- Providing exhaustive user-study comparisons among persona methods
- Proving robustness across all lighting, background, and object-color conditions
- Arguing that LangGraph or MCP are uniquely correct or optimal choices
- Claiming module-level novelty where the main contribution is system integration feasibility

## Decision boundaries

OMX may decide autonomously, without re-confirmation, to replace or degrade:
- frameworks and middleware
- communication protocols
- exact model variants
- inference/deployment approach
- data-pipeline details
- retry/fault-tolerance mechanics
- observability/logging implementation details
- non-core helper or validation modules

OMX must not change without confirmation if the change touches:
- the thesis core task semantics or input/output boundary
- the existence of at least one intact end-to-end execution path
- the definition or measurement method of the evaluation benchmark
- the existence of key shared state between agents
- the minimum stated safety/confirmation rules
- recognizability of the core architecture components in code
- integrity of any fine-tuning/training claim
- the ability to diagnose failures

Every autonomous degradation of a changeable item must be logged in code comments or experiment records.

## Constraints

- Must remain low-cost and feasible on limited undergraduate resources
- Must preserve the core architecture semantics claimed in the thesis, even if individual implementations are simplified
- Must keep at least one demonstrable end-to-end path from user request through agent processing to robot/system response
- Must keep evaluation definitions stable and reproducible
- Must keep failure paths diagnosable
- Must synchronize engineering progress with thesis writing, reference collection, and process logging

## Testable acceptance criteria

### Mandatory demonstrations

The minimum accepted milestone is `M2`, which requires all of the following:
- Full interaction flow succeeds in a demonstration scenario:
  - wake-up
  - greeting
  - conversation
  - grasp execution
  - sleep
- Simple sorting succeeds on a constrained desktop setup
- The system can recognize a grasp request embedded in user conversation and execute it
- The system can detect a dangerous action and either request confirmation or refuse execution

### Demonstration budget

- Each mandatory demonstration may be attempted once with up to two retries
- If the demonstration still cannot be completed within this budget, it is below the required floor

### Latency

- Input to decision to execution-start latency must be `<= 10s`

### Minimum interaction intelligence

- The robot can identify the user
- On wake-up, it attempts to find the user's face
- It can keep the face within the wrist-camera view during the interaction routine
- It can perform preset state/emotion-linked motions during interaction

### M2 milestone floor

`M2` is the minimum graduation threshold and therefore must include:
- all four mandatory demonstrations at presentation-ready quality
- dual-camera collaboration in the visible system behavior
- user recognition / face-following behavior
- emotional/state-linked expressive motions
- a usable task-control and monitoring interface
- a feasible subset of the planned `50-100` teleoperation samples, sufficient to produce at least one fine-tuning result
- at least one quantitative evaluation package covering success rate and end-to-end latency
- demonstrable interruption recovery and long-term memory behavior
- enough thesis material to support the methods, experiments, and results sections

## Assumptions exposed and resolutions

- Assumption: "能做" might be satisfied by a minimal toy pipeline.
  - Resolution: rejected. The true minimum is `M2`, not `M1`.
- Assumption: specific frameworks/models are fixed and must survive unchanged.
  - Resolution: rejected. Many implementation choices are degradable, but thesis semantics and evidence obligations are fixed.
- Assumption: evaluation can stay qualitative if the demo works.
  - Resolution: rejected. Quantitative metrics and stable measurement definitions are mandatory.

## Pressure-pass findings

The milestone-threshold pressure pass clarified that the project floor is materially higher than a single closed-loop demo. The user requires a defense-ready integrated system with stable multi-demo evidence, quantitative evaluation, and thesis-aligned architecture traceability.

## Technical context findings

- Current repository state is effectively empty aside from `.omx` session metadata
- This should be treated as a greenfield build with synchronized research/thesis operations from day one
- Process logging, literature collection, and thesis drafting are first-class workstreams, not optional documentation chores

## Brownfield evidence vs inference notes

- Evidence: workspace currently contains only `.omx` files and no product code
- Inference: repository structure, implementation modules, and thesis/documentation layout must be created from scratch

## Condensed transcript

See `.omx/interviews/cobot-graduation-design-20260415T055211Z.md` for the interview summary and round-by-round outcome.
