# PRD: Co-Bot 桌面级多模态具身智能机器人毕业设计

## Metadata

- Plan mode: `ralplan --consensus --deliberate`
- Input spec: `.omx/specs/deep-interview-cobot-graduation-design.md`
- Context snapshot: `.omx/context/cobot-graduation-design-20260415T052854Z.md`
- Owner mode recommendation: `team -> ralph verify`
- Minimum acceptance milestone: `M2`

## RALPLAN-DR Summary

### Principles

1. 先保住答辩闭环，再追求架构完整度和体验完整度。
2. 论文声明的核心语义、评估口径、架构可识别性不可漂移。
3. 工程、实验、日志、论文四条线从第一天并行，不把文档延后到末期。
4. 所有可降级项都允许降级，但必须留痕并且不破坏 `M2` 验收线。
5. 任何“智能”能力都要绑定到可演示、可记录、可复现实验上。

### Decision Drivers

1. `M2` 是最低毕业标准，不是理想目标。
2. 仓库当前为空，必须按 greenfield 项目自顶向下搭建可演化骨架。
3. 系统跨度大，必须把硬件控制、模型集成、前后端、数据/微调、论文资产拆成独立但可汇合的工作流。

### Viable Options

#### Option A: 端到端优先的一体化原始方案

- 优点：尽快接近最终论文叙事；架构最贴近初始愿景。
- 缺点：依赖项太多，任何一个环节卡住都会拖慢所有线；在空仓下风险最高。

#### Option B: 分层骨架 + 逐步替换策略

- 优点：可以先做稳定闭环，再逐步用真实模型/硬件替换 stub；最符合 `M2` 风险控制。
- 缺点：前期会有更多适配层和模拟层，短期看起来“没那么智能”。

#### Option C: 论文资产优先，系统实现收缩

- 优点：对时间风险最友好，容易保证论文材料完整。
- 缺点：很容易掉到 `M1` 以下，不满足用户已明确的最低门槛 `M2`。

### Chosen Direction

选择 `Option B: 分层骨架 + 逐步替换策略`。

### Why Chosen

- 它最符合“证明能做而不是做到最好”的课题定位。
- 它允许在任何时点保住一条完整闭环，并逐步补强到 `M2`。
- 它最适合空仓起步、硬件和模型集成不确定性高的情况。

### Real Tradeoff Tension

- 真正的张力不在“要不要做高级功能”，而在“为了让答辩看起来完整，是否过早投入前端观感、人格化交互和完整双视频体验”，这会直接挤压 `M2` 所需的硬件稳定性、实验采集和微调时间。
- 本计划选择把“可演示的研究证据”优先级始终放在“更好看的体验层”之前；任何 `M3` 功能只有在不挤压 `M2` 关键路径时才能启动。

## Problem Statement

在有限预算和普通笔记本计算资源下，构建一个可复现、可答辩、可量化评估的桌面级具身智能机器人系统，证明感知、决策、执行和社交交互可以在统一架构中形成工作闭环，并同步产出毕业论文所需的实验与过程材料。

## Goals

- 交付一个基于 `SO-ARM101 + Laptop + Dual Camera` 的桌面级机器人原型
- 基于 `LangGraph` 组织 Supervisor / Social / Action 三类能力
- 使用 `LeRobot + SmolVLA` 跑通动作执行链路，并保留微调证据
- 提供 `FastAPI + React/TypeScript` 的前后端分离交互界面
- 通过遥操作数据采集、微调、量化评估支撑论文实验章节
- 持续维护开发日志、参考文献资料库、论文大纲与章节草稿

## Non-Goals

- 不追求 SOTA 性能或工业级控制精度
- 不要求通用开放场景抓取
- 不做大规模人格化方法对比用户实验
- 不论证 `LangGraph` 或 `MCP` 的唯一最优性
- 不承诺所有环境/物体条件下稳定泛化

## Users and Reviewers

- 直接用户：课题作者本人，用于开发、遥操作采集、实验与答辩演示
- 评审用户：毕业设计指导老师与答辩老师
- 间接用户：后续复现者，需要基于仓库文档重建环境并重复关键演示

## Scope

### In Scope

- 机械臂控制服务与工具层
- 双摄像头采集、压缩流、状态推送
- `LangGraph StateGraph` 编排与检查点
- `Ollama + Qwen2.5-3B/7B` 社交交互代理
- `SmolVLA` 动作执行接入与至少一轮微调
- 任务提交、模型管理、系统监控前后端
- 遥操作采集、实验记录、量化评估
- 开发日志、参考资料、论文大纲、章节草稿

### Out of Scope

- 云端大规模训练平台
- 多机械臂或移动机器人扩展
- 高保真 3D 仿真优先实现
- 复杂长时序任务规划 benchmark

## Success Criteria

### Hard Acceptance

- `M2` 全部满足
- 四类强制演示全部可在 `1 + 2` 次尝试预算内完成
- 输入到决策到执行开始延迟 `<= 10s`
- 至少一版微调结果和一组量化评估
- 中断恢复和长期记忆能力可演示
- 论文方法、实验、结果章节具备可写证据

### Quality Indicators

- 双摄像头职责清晰且能在界面中观察到
- 系统出错时能定位到摄像头、模型、编排、控制层哪个环节失败
- 每次重大降级都有实验记录或代码注释留痕

### Explicit M2 Pass Checks

- `presentation-ready quality` 的定义：
  - 每个强制演示都有完整视频记录
  - 每个强制演示都有可回放日志和结果表
  - 在答辩彩排环境下可按脚本复现，不依赖临场手工改代码
- `usable task-control interface` 的定义：
  - 能提交任务
  - 能看到任务状态变化
  - 能看到至少一路实时视频
  - 能看到危险动作确认/拒绝提示
  - 能查看关键日志摘要
- 用户识别 / 人脸跟随通过条件：
  - 唤醒后 `5s` 内检测到用户人脸
  - 在不少于 `10s` 的交互窗口内，腕部相机连续保持用户人脸位于画面内的成功帧占比 `>= 70%`
- 情绪动作通过条件：
  - 至少定义 `3` 种状态动作映射：唤醒、交互中、休眠/结束
  - 在完整交互闭环演示中至少触发其中 `2` 种
- 最低微调结果通过条件：
  - 一次有版本号的训练运行
  - 一份包含模型基线、训练配置、样本统计、至少一个评估数值的结果摘要
  - 该结果明确映射到 `M2` 的一个动作类演示任务

## System Strategy

### Phase 0: 项目骨架与治理基线

- 初始化 monorepo 结构
- 建立 `backend/`, `frontend/`, `services/robot-mcp/`, `training/`, `experiments/`, `docs/`, `thesis/`, `references/`, `logs/`
- 建立开发日志模板、实验记录模板、文献卡片模板、论文章节模板
- 建立统一配置、环境变量、模型注册表、设备注册表
- 定义最小共享状态 schema、任务类型枚举、危险动作策略枚举、延迟埋点字段和实验结果表头
- 冻结 `M2` 基准定义：
  - 四类强制演示场景
  - 限定物体/桌面环境集合
  - 成功/失败记录 schema
  - 延迟时间戳字段
  - 降级记录格式
- 写清 mixed-task 共享状态与确认流契约：
  - source of truth
  - correlation id
  - 必填字段
  - 状态转移
  - checkpoint 边界
  - interrupt/resume 语义
- 提前创建训练/评估空骨架，确保 `M1` 前就能记录数据 manifest、训练配置和结果表头

### Phase 1: 可运行骨架闭环

- 先用 stub / mock 跑通：
  - 双摄像头采集接口
  - 机器人 MCP 工具接口
  - LangGraph 编排流
  - FastAPI REST/WebSocket
  - React 状态监控与控制台
- 形成第一条 “用户输入 -> Supervisor -> Action/Social -> Tool -> 前端反馈” 的闭环
- 同时固定 `M2` 纵切片，只围绕四类强制演示先定义最小任务集、场景集、物体集和日志字段
- 先实现“危险动作策略闸门”与“混合交互任务共享状态”这两个不可改边界的最小版本
- 在 `M1` 前半段就插入一条真实风险纵切片，不允许全部留到 `Phase 2`：
  - 真实机械臂接入
  - 两路真实相机采集
  - policy gate 真确认/拒绝流程
  - checkpoint / Redis 最小恢复链路
  - 延迟埋点真实落库
  - 至少一个强制演示场景用 real-or-hybrid 方式打通
- `M1` 即开始训练/评估最小闭环：
  - 训练配置模板可执行
  - 数据 manifest 可记录真实采样
  - 至少定义一项“算作微调结果”的最低输出形式
  - 明确该结果如何映射到 `M2` 演示任务

### Phase 2: 真实硬件与模型替换

- 接入真实 `SO-ARM101` 控制
- 接入 `Ollama + Qwen2.5`
- 接入 `SmolVLA` 推理
- 实现双摄像头融合输入与任务路由
- 打通人脸检测 / 跟随和情绪动作映射
- 不新增新的论文承诺，只替换 `M2` 纵切片中已经验证过的 stub 能力

### Phase 3: 数据与微调

- 设计遥操作采集协议和标注结构
- 完成 `50-100` 次演示的可行子集采集
- 跑通 `SmolVLA` 微调流程
- 输出数据集说明、训练配置、训练日志、结果摘要
- 若样本规模必须缩减，也要保持与 `M2` 强制演示任务一一对应

### Phase 4: 验证与论文同步

- 固化四类强制演示脚本
- 采集成功率、端到端延迟
- 汇总失败案例和调参记录
- 同步补齐论文方法、实验、结果、系统实现章节

## Execution Guardrails

- 在 `M2` 退出条件满足前，不启动任何纯 `M3` 体验增强项，除非它直接降低 `M2` 风险。
- 每个工作流都要维护一条对应的论文资产输出：
  - 工程实现 -> 系统设计/关键实现草稿
  - 实验与训练 -> 实验设计/结果草稿
  - 风险与降级 -> 局限性/展望草稿
- 共享状态 schema、危险动作策略 schema、指标口径一旦冻结，只允许追加字段，不允许破坏式修改。
- `Redis` 长期记忆与 checkpoint 恢复只要求达到“可演示、可解释、可回放”的程度，不追求复杂生产级容灾语义。
- 若 `M1` 真实风险纵切片暴露出架构瓶颈，优先回收 mock 层复杂度，不允许通过继续堆抽象回避真实问题。

## Architecture

### Core Components

- `frontend/web`: 模型管理面板、任务控制台、状态监控、视频切换、可选 3D
- `backend/api`: REST API、WebSocket、任务队列、会话管理、日志汇总
- `orchestrator/langgraph`: Supervisor、Social Agent、Action Agent、checkpoint 管理
- `orchestrator/policy`: 危险动作确认/拒绝策略、任务准入、共享状态一致性校验
- `services/robot-mcp`: 机械臂 MCP 服务，暴露标准动作工具
- `services/perception`: 双摄像头采集、帧预处理、人脸检测、压缩推流
- `models/runtime`: 模型注册、加载、热切换、推理适配
- `training/pipeline`: 数据采集、清洗、切分、微调、评估
- `docs/ops`: 部署、调试、实验与演示手册
- `thesis/`: 大纲、章节草稿、参考文献与图表清单

### Data Flow

1. 用户通过前端或语音/文本接口发出请求
2. 后端接收任务并写入编排上下文
3. Supervisor 判断是社交、动作还是混合任务
4. Supervisor 将任务写入共享状态，并通过策略层判定是否允许直接执行、需要确认、或必须拒绝
5. Social Agent 生成互动文本与状态动作建议
6. Action Agent 获取双摄像头图像 + 文本指令并输出动作序列
7. MCP 控制服务执行机械臂动作并回传状态
8. WebSocket 推送日志、状态、视频流到前端
9. LangGraph checkpoint 与 Redis 记录全局状态

### Shared State And Confirmation Contract

- Source of truth: `LangGraph` 当前工作状态 + checkpoint 快照，`Redis` 持久化跨会话上下文
- Required IDs:
  - `session_id`
  - `task_id`
  - `turn_id`
  - `correlation_id`
- Required shared fields:
  - 用户输入
  - 任务类型
  - 路由决策
  - 危险等级
  - 确认状态
  - 当前感知摘要
  - 动作计划摘要
  - 执行状态
  - 恢复指针
  - `last_safe_checkpoint_id`
  - `last_completed_step`
  - `pending_confirmation_prompt`
  - `active_model_ids`
  - `latency_marks`
- Confirmation flow:
  - `proposed -> gated -> awaiting_confirm -> approved/rejected -> executing -> completed/aborted`
- Checkpoint boundary:
  - 路由完成后
  - 策略闸门判定后
  - 动作执行前
  - 中断恢复后
- Interrupt / resume semantics:
  - 中断时必须保存最近一次可解释状态
  - 恢复时必须重建当前任务上下文并标记为 resumed
  - 不允许恢复后丢失危险动作确认状态

## Milestones

### M0: 基础骨架

- 仓库结构、文档模板、日志模板、配置系统完成
- 后端/前端/编排/工具层都有最小 runnable stub
- 共享状态 schema、危险动作策略 schema、实验记录表与延迟埋点字段冻结

### M1: 端到端原型

- 至少一条从输入到动作执行反馈的闭环完成
- 前端能看到状态与至少一路视频
- 机械臂基础控制与安全拒绝路径可验证
- 至少一个 `M2` 强制演示场景已有可重复的 mock/real 混合纵切片
- 至少一条“真实风险纵切片”已经经过真实机械臂、双相机、确认流、checkpoint/Redis 和延迟记录验证
- 训练/评估骨架已产生第一版可审阅结果占位，且字段与 `M2` 演示任务一致

### M2: 最低毕业标准

- 四类答辩演示全部可运行
- 双摄像头、用户识别、人脸跟随、情绪动作齐备
- 至少一版微调结果和一组量化评估完成
- 中断恢复和长期记忆可演示
- 论文主体章节达到可提交草稿级别
- 不允许通过删除社交代理、危险动作策略层、共享状态机制来换取短期稳定性
- 每类演示都产出规范化证据包并落盘到固定目录

### M3: 完整目标

- 热切换、异步队列、双视频流、可选 3D、完整演示视频、完整部署复现全部完善

## Deliverables

- 可运行代码仓库
- 可复现部署文档
- 演示脚本与演示视频
- 实验记录、训练记录、评估结果
- 文献资料库与技术笔记
- 毕业论文大纲、章节草稿、终稿

## Canonical Evidence Layout

每个强制演示和关键验证项都写入：

```text
experiments/evidence/<scenario-id>/<run-id>/
  metadata.json
  summary.md
  events.jsonl
  latency.json
  result.json
  checkpoints/
  screenshots/
  video/
```

最小要求：
- `metadata.json`: 场景、日期、模型版本、设备版本、操作者
- `summary.md`: 成败结论、失败原因、降级说明
- `events.jsonl`: 关键状态转移和 confirmation 事件
- `latency.json`: `T_start`, `T_decision`, `T_exec`
- `result.json`: 是否通过、尝试次数、指标摘要

## Workstreams

### WS1: 平台与工程基线

- 仓库结构、依赖管理、CI、本地开发工具、环境配置

### WS2: 硬件与工具控制

- `SO-ARM101` 驱动、MCP 服务、安全策略、状态回传

### WS3: 感知与多模态输入

- 双摄像头采集、帧缓存、人脸检测、视频流转发

### WS4: 决策编排与智能体

- LangGraph 状态图、Supervisor、Social/Action Agent 边界与共享状态
- 危险动作策略层和确认/拒绝流程

### WS5: 模型接入与训练

- Ollama 模型管理、SmolVLA 推理适配、遥操作数据、微调与评估
- 评估埋点、结果汇总脚本、数据版本约束从本工作流起始阶段即建立
- 在 `M1` 结束前定义“最低可接受微调结果”：
  - 一次可追踪训练运行
  - 一份结果摘要
  - 与至少一个 `M2` 动作演示场景的映射说明

### WS6: 前端与演示体验

- 实时状态面板、模型控制、视频切换、日志可视化、可选 3D

### WS7: 论文与研究资产

- 开发日志、参考文献、章节草稿、图表、实验表格、结论迭代

## Repo Proposal

```text
.omx/
backend/
frontend/
services/
  robot-mcp/
  perception/
orchestrator/
models/
training/
experiments/
docs/
  deployment/
  development-log/
  experiment-log/
  references/
thesis/
  outline/
  chapters/
  figures/
scripts/
```

## Risks and Mitigations

### Risk 1: 真实硬件控制不稳定

- 缓解：先完成 mock MCP；所有动作先支持 dry-run / safe mode；关键演示提前脚本化

### Risk 2: `SmolVLA` 本地推理性能不足

- 缓解：降低分辨率/帧率；减少动作频率；允许改用更小推理配置，但保留微调与动作模型语义

### Risk 3: 遥操作数据采集效率过低

- 缓解：优先采集直接服务 `M2` 演示的任务；先做少类物体与固定桌面区域

### Risk 4: 论文材料滞后

- 缓解：每个工作流必须同步产出对应的日志、图表、参考文献和章节草稿占位

### Risk 5: `M2` 定义被体验项稀释

- 缓解：每周按 `M2` 验收矩阵复盘一次；任何新增功能都要标记为 `M2-required` 或 `M3-optional`

## Pre-Mortem

### Scenario A: 到中期只完成了零散模块，没有答辩闭环

- 预防：从 `M0 -> M1 -> M2` 强制按闭环优先推进，不允许长时间只做单模块打磨

### Scenario B: 微调与评估一直拖延到后期，论文实验章节无法成文

- 预防：在架构跑通前就先建立训练流水线空壳、实验记录模板和评估脚本

### Scenario C: 前端/可视化投入过多，挤压硬件与实验时间

- 预防：前端先满足 `M2` 监控与演示需要，`Three.js` 放在 `M3` 可选层

## Critic Verdict Integration

### Principle-Option Consistency

- 已确认：所选 `Option B` 与“闭环优先、证据优先、可降级但不破边界”的原则一致。

### Antithesis Considered

- 最强反方观点：如果 `M2` 同时包含双摄像头、用户跟随、社交人格、微调结果、长期记忆和四类演示，系统很可能因为目标过密而在后期陷入“样样都有一点，但没有一项真正稳”的状态。
- 计划回应：通过 `M0/M1` 提前冻结 schema、日志口径和四类演示纵切片，并明确禁止在 `M2` 前抢跑纯体验增强项。

### Final Planning Verdict

- `APPROVE WITH GUARDRAILS`
- 该计划可进入执行，但必须严格执行 `M2` 优先级、指标冻结和降级留痕规则。

## ADR

### Decision

采用“分层骨架 + 逐步替换”的 greenfield 交付策略，以 `M2` 为最低毕业线组织整个课题。

### Drivers

- `M2` 是最低门槛
- 空仓起步且集成不确定性高
- 论文与系统必须同步推进

### Alternatives Considered

- 一次性端到端实现原始愿景
- 论文优先、系统实现压缩

### Why Chosen

- 最能控制进度和集成风险，同时保住答辩所需闭环

### Consequences

- 需要设计清晰的替换接口、mock 策略、日志规范和里程碑门槛
- 某些“高级感”能力会被延后到 `M3`

### Follow-ups

- 创建 monorepo 骨架
- 定义模型/设备/任务注册表
- 写演示脚本和实验模板
- 启动参考文献与论文大纲工作流

## Available Agent Types Roster

- `architect`: 系统分层、接口边界、状态管理
- `executor`: 后端、前端、编排、训练与文档实现
- `debugger`: 硬件联调、推理链路、延迟问题
- `test-engineer`: 测试计划、评估脚本、验收流程
- `researcher`: 文献整理、技术路线比对、论文引用素材
- `writer`: 部署文档、实验记录模板、论文草稿
- `verifier`: 里程碑验收与证据收集

## Execution Staffing Guidance

### If using `ralph`

- 适合单主线、强顺序依赖的阶段：`M0`、`M1`、最终 `M2` 验收收口
- 推荐 lane 顺序：
  1. 工程骨架与文档模板
  2. 后端 + 编排最小闭环
  3. 机器人工具服务
  4. 前端监控与视频
  5. 数据/训练/评估
  6. 论文与部署文档补齐

### If using `team`

- 适合并行工作流：
  - Lane A: `backend + orchestrator`
  - Lane B: `frontend + websocket/video`
  - Lane C: `robot-mcp + perception`
  - Lane D: `training + experiments + thesis assets`

## Suggested Reasoning by Lane

- `architect`: `high`
- `executor` for backend/orchestrator: `high`
- `executor` for frontend/docs: `medium`
- `researcher`: `high`
- `test-engineer`: `medium`
- `verifier`: `high`

## Team Launch Hints

- Sequential owner path:
  - `$ralph .omx/plans/prd-cobot-graduation-design.md`
- Parallel path:
  - `$team .omx/plans/prd-cobot-graduation-design.md`

## Team Verification Path

1. `M0` 骨架验收：结构、模板、可运行 stub、文档入口
2. `M1` 闭环验收：单条端到端路径跑通
3. `M2` 答辩验收：四类演示、延迟、微调结果、记忆恢复、论文草稿
4. `M3` 增强验收：体验与可视化增强项

每次验收都要沉淀：
- 演示记录
- 日志与故障说明
- 指标表
- 论文素材更新
