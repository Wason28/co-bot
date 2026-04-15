# Test Spec: Co-Bot 毕业设计验证与验收规范

## Scope

本测试规格覆盖 `M0 -> M2` 的工程验证、系统联调、实验评估与论文证据收集。`M3` 仅做增强项验证，不作为最低毕业门槛。

## Verification Principles

1. 每条论文声明都要对应至少一种可保存证据。
2. 先验证闭环存在，再验证性能与体验。
3. 每个阶段都保留可回放日志、实验记录和失败分析。
4. 单元测试、集成测试、端到端演示、观测性检查要同时存在。
5. `M1` 前必须暴露一次真实跨层风险，不允许只靠 mock 宣布“骨架完成”。

## Benchmark Freeze

- 在 `M0` 冻结以下内容，并写入 `experiments/` 模板：
  - 四类强制演示名称与场景描述
  - 物体集合与桌面区域约束
  - 成功/失败判定字段
  - 延迟埋点字段
  - 降级记录字段
- 冻结后只允许追加说明，不允许破坏性变更定义。

## Canonical Scenario IDs

- `demo-full-flow`
- `demo-sorting`
- `demo-conversation-grasp`
- `demo-dangerous-action`
- `demo-recovery-memory`
- `demo-real-risk-slice`

## Canonical Evidence Bundle

每次关键验证都必须落盘到：

```text
experiments/evidence/<scenario-id>/<run-id>/
```

必备文件：
- `metadata.json`
- `summary.md`
- `events.jsonl`
- `latency.json`
- `result.json`

按需文件：
- `checkpoints/*.json`
- `redis/*.json`
- `screenshots/*`
- `video/*`
- `training/*`

## Acceptance Matrix

| Area | Minimum proof | Evidence artifact |
| --- | --- | --- |
| 机械臂控制 | MCP 工具可调用，状态可回读 | 调用日志、状态快照 |
| 双摄像头 | 两路视频可采集并区分用途 | 帧截图、WebSocket 流日志 |
| 用户识别/跟随 | 唤醒时能找到用户并维持腕部视野跟随 | 人脸检测日志、跟随轨迹、视频片段 |
| 中断恢复/长期记忆 | 中断后可恢复到可解释状态，并能读取会话关键上下文 | checkpoint 快照、Redis 记录、恢复演示日志 |
| LangGraph 编排 | Supervisor 能路由到 social/action | 状态图日志、checkpoint 数据 |
| 策略闸门 | 危险动作可被拦截、确认或拒绝 | policy 判定日志、确认事件 |
| 社交代理 | 能完成唤醒、问候、对话输出和状态动作建议 | 对话记录、前端事件流 |
| 动作代理 | 能基于视觉+指令触发动作执行 | 推理输入输出日志、动作序列记录 |
| 安全约束 | 危险动作需确认或拒绝 | 审批事件日志、拒绝案例 |
| 微调证据 | 至少一轮微调与结果摘要 | 训练配置、loss 曲线、结果表 |
| 定量评估 | 成功率与延迟可重复计算 | `experiments/` 原始记录和汇总表 |
| 论文同步 | 方法/实验/结果章节有可审阅草稿 | `thesis/` 草稿文件 |

## Test Levels

### Unit Tests

- 任务与模型注册表的 schema 校验
- 共享状态 schema、任务类型枚举、策略判定枚举
- MCP 工具参数校验、危险动作策略判断
- LangGraph 节点输入输出契约
- WebSocket 消息 schema
- 实验记录与日志写入工具

### Integration Tests

- `backend <-> orchestrator` 任务提交与状态流转
- `orchestrator <-> policy gate` 危险动作确认/拒绝与混合任务准入
- `orchestrator <-> robot-mcp` 工具调用闭环
- `orchestrator <-> checkpoint/redis` 路由后、确认后、执行前、恢复后的状态一致性
- `orchestrator <-> model runtime` 模型加载、切换、推理调用
- `backend <-> frontend` REST/WebSocket 数据联通
- `training pipeline` 数据集清单、训练配置、评估脚本串联

### End-to-End Tests

#### E2E-1: 完整交互闭环

- 输入：用户唤醒并提出简单抓取请求
- 预期：识别用户 -> 打招呼 -> 简短交谈 -> 执行动作 -> 结束/休眠
- 证据：完整日志、视频、状态轨迹、动作执行记录
- 场景 ID：`demo-full-flow`
- 通过条件：
  - 唤醒后 `5s` 内检测到人脸
  - 交互窗口 `>= 10s`
  - 交互期间人脸保持在腕部相机视野内的成功帧占比 `>= 70%`
  - 至少触发 `2` 个状态动作
  - `T_exec - T_start <= 10s`

#### E2E-2: 简单分拣

- 输入：桌面固定区域内有限类物体
- 预期：识别并分拣到预定位置
- 证据：任务前后照片、动作轨迹、成功/失败统计
- 场景 ID：`demo-sorting`
- 通过条件：
  - 在冻结的物体集和桌面区域内完成一次正确分拣
  - 尝试次数不超过 `3`

#### E2E-3: 混合交互触发抓取

- 输入：自然对话中夹带抓取意图
- 预期：Supervisor 正确路由，社交代理与动作代理协同完成
- 证据：对话记录、路由轨迹、动作执行记录
- 场景 ID：`demo-conversation-grasp`
- 通过条件：
  - 对话中包含隐式抓取请求
  - Supervisor 路由记录存在
  - 动作执行成功开始于 `10s` 门槛内

#### E2E-4: 危险动作确认/拒绝

- 输入：包含风险的动作请求
- 预期：系统要求确认或拒绝执行，不可静默放行
- 证据：前端提示、后端日志、状态转移记录
- 场景 ID：`demo-dangerous-action`
- 通过条件：
  - 必须出现 `awaiting_confirm` 或 `rejected` 状态
  - 不允许无确认直接进入 `executing`

#### E2E-5: 中断恢复与长期记忆

- 输入：在任务执行中途模拟中断，再恢复会话
- 预期：系统能恢复到可解释状态，并保留与当前任务相关的关键上下文
- 证据：checkpoint 对比、Redis 记录、恢复后状态日志
- 场景 ID：`demo-recovery-memory`
- 持久化必需字段：
  - `session_id`
  - `task_id`
  - `correlation_id`
  - `route_decision`
  - `risk_level`
  - `confirmation_state`
  - `last_safe_checkpoint_id`
  - `last_completed_step`
  - `pending_confirmation_prompt`
  - `active_model_ids`
  - `latency_marks`
- 通过条件：
  - 中断前后上述字段均可读取
  - 恢复后状态被标记为 `resumed`
  - 若中断前处于确认阶段，恢复后不得丢失确认状态
- 固定证据包：
  - `checkpoints/pre-interrupt.json`
  - `checkpoints/post-resume.json`
  - `redis/session-context.json`
  - `result.json`

#### E2E-6: M1 真实风险纵切片

- 输入：固定使用 `demo-full-flow` 的真实或 hybrid 版本
- 预期：真实机械臂、双相机、policy gate、checkpoint/Redis、延迟记录全部在同一条链路出现
- 证据：视频、日志、checkpoint、Redis 记录、延迟表
- 场景 ID：`demo-real-risk-slice`
- 固定证据包：
  - `video/run.mp4`
  - `events.jsonl`
  - `latency.json`
  - `checkpoints/*.json`
  - `redis/session-context.json`
  - `result.json`
- 通过条件：
  - 真实机械臂控制日志存在
  - 两路相机帧源记录存在
  - policy gate 决策记录存在
  - checkpoint 与 Redis 记录存在
  - `T_exec - T_start <= 10s`

## Observability Checks

- 所有关键服务具备统一时间戳日志
- 每个任务有唯一 `task_id / session_id`
- 推理、控制、视频流、状态图节点都能关联到同一任务
- 策略闸门判定、共享状态变更、用户确认事件都能关联到同一任务
- 出错时可定位到至少一级根因：设备、模型、编排、API、前端
- 所有证据包都能通过 `scenario-id + run-id` 反查到对应日志与模型配置

## Latency Measurement

### Metric

- `T_start`: 接收用户输入时间
- `T_decision`: Supervisor 完成路由决策时间
- `T_exec`: 机器人开始执行动作时间
- 关键指标：`T_exec - T_start <= 10s`

### Procedure

- 每个强制演示都记录三次以内尝试的时间戳
- 失败尝试不能删，必须纳入实验日志
- 汇总表中同时报告：
  - 单次延迟
  - 平均延迟
  - 最大延迟
  - 是否满足 `<= 10s` 答辩门槛

## Success-Rate Measurement

### Mandatory demos

- 四类强制演示每类允许 `1 + 2` 次尝试
- 若在预算内未成功，则该类演示不达标
- `E2E-5` 中断恢复演示至少成功一次，允许一次重试

### Report fields

- 场景名
- 物体/环境配置
- 指令文本
- 是否首次成功
- 第几次成功
- 失败原因
- 是否满足答辩展示要求

## Training and Fine-Tuning Validation

- 在 `M0/M1` 就建立空的训练配置模板、数据 manifest 模板和结果表头
- 记录数据采集日期、任务类型、样本数、设备状态
- 数据切分与版本号可追踪
- 数据任务覆盖应优先服务四类强制演示，不允许采集与 `M2` 无关的数据先于 `M2` 任务样本
- 在 `M1` 结束前必须至少产出：
  - 一次可复现实验运行记录
  - 一份“最低可接受微调结果”占位摘要
  - 该结果与某个 `M2` 演示任务的映射说明
- “最低可接受微调结果”固定定义为：
  - `training/run-config.json`
  - `training/dataset-manifest.json`
  - `training/metrics.json`
  - `training/summary.md`
  - 其中 `metrics.json` 至少包含一个动作任务相关评估值
- 至少保留：
  - 训练配置
  - 使用模型版本
  - 样本统计
  - 至少一项训练结果摘要
- 若训练规模缩水，必须在实验记录和论文中解释原因与影响

## Thesis Evidence Mapping

| Thesis section | Required engineering evidence |
| --- | --- |
| 绪论 | 课题背景、相关工作笔记、系统目标 |
| 系统设计 | 架构图、模块接口、状态流 |
| 关键实现 | 后端、前端、MCP、LangGraph、双摄像头实现记录 |
| 实验设计 | 任务定义、指标、数据采集方案 |
| 实验结果 | 成功率、延迟、失败案例与分析 |
| 总结与展望 | 降级记录、局限性、后续改进方向 |

## Exit Criteria by Milestone

### M0 Exit

- 目录结构与模板齐备
- 可运行 stub 闭环存在
- 基本日志与文档入口可用
- 基准定义和记录 schema 已冻结

### M1 Exit

- 至少一条真实闭环存在
- 前端可观测任务状态
- 危险动作保护路径存在
- `E2E-6` 真实风险纵切片已完成
- 训练/评估最小结果占位已存在

### M2 Exit

- 四类演示全部达标
- 延迟指标达标
- 用户识别 / 人脸跟随 / 情绪动作证据存在
- 微调结果存在
- 量化评估表存在
- 中断恢复/长期记忆可演示
- 论文方法/实验/结果章节草稿存在
- 所有失败尝试及降级决定都有可审阅记录
- 所有强制演示都有固定目录证据包

## Failure Handling Rules

- 不允许静默失败
- 每次失败必须写入实验记录
- 触及不可改边界的变更必须暂停并上报用户
- 未触及不可改边界的降级可直接执行，但必须留痕

## Recommended Initial Test Backlog

1. 定义日志、任务、模型、设备的 schema 测试
2. 打通任务提交到编排状态更新的集成测试
3. 做一个 mock robot-mcp 的端到端烟囱测试
4. 定义四类强制演示的记录模板与结果表
5. 定义延迟埋点和统计脚本
