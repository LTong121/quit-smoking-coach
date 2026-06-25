# Skill Requirements: Easy Way Smoking Cessation Coach

## 0. Purpose

本文件评估 `book_model.yaml` 如何落地为一个可运行的 AI Skill。

目标不是复述书籍内容，而是明确：

1. 哪些能力适合 Skill 自动执行
2. 哪些能力必须长期记忆用户状态
3. 哪些能力需要状态机驱动
4. 哪些能力需要任务系统支持
5. 哪些能力需要复吸修复机制

该 Skill 的核心定位是：一个认知重构型戒烟教练。它先识别并拆除用户对吸烟的错误信念，再通过状态机、任务系统和复吸修复机制，持续帮助用户保持非吸烟者身份。

---

## 1. Scope

### 1.1 In Scope

- 识别用户当前戒烟阶段
- 识别用户表达中的错误信念
- 选择对应的信念转化路径
- 生成对话式认知干预
- 生成短周期行为实验
- 维护用户长期戒烟状态
- 记录触发场景、渴望模式和复吸风险
- 支持最后一支烟仪式
- 支持戒断期每日跟进
- 支持复吸后的无羞耻修复
- 支持亲友/支持者对话指导

### 1.2 Out of Scope

- 不提供医学诊断
- 不替代医生、心理咨询师或戒烟门诊
- 不开具药物或尼古丁替代方案
- 不以恐吓、羞辱、道德审判作为主要干预
- 不承诺固定天数内一定成功

---

## 2. Skill Auto-Execution Requirements

以下部分适合由 Skill 自动执行。它们具有明确输入、规则映射和输出模板，可以在每轮对话中稳定运行。

### 2.1 用户状态分类

Skill 应自动读取用户当前表达，并映射到状态机中的一个状态：

- `unaware`
- `ambivalent`
- `questioning`
- `reframing`
- `preparing`
- `quit_day`
- `withdrawal`
- `trigger_exposure`
- `stable`
- `relapse_risk`
- `relapse`

自动执行逻辑：

- 检测用户是否仍相信吸烟有好处
- 检测用户是否正在拖延
- 检测用户是否准备停止
- 检测用户是否已经停止
- 检测用户是否正在经历戒断
- 检测用户是否出现复吸风险语言
- 检测用户是否已经复吸

输出要求：

- 内部更新状态
- 对用户不必暴露状态标签，除非用于复盘
- 根据状态选择下一步干预

### 2.2 False Belief Detection

Skill 应自动从用户话语中识别错误信念，例如：

- "压力大必须抽一支" -> `FB001`
- "饭后一支最舒服" -> `FB017`
- "就一支没事" -> `FB009`
- "我戒了会胖" -> `FB019`
- "我没意志力" -> `FB021`
- "我可以先减量" -> `FB010`

自动执行逻辑：

- 支持直接匹配
- 支持语义匹配
- 支持多信念并发识别
- 优先处理当前风险最高的信念

输出要求：

- 不直接告诉用户 "你有 FB009"
- 应以自然语言指出其推理结构
- 应匹配对应 `Belief Transformation`

### 2.3 Belief Transformation Selection

Skill 应自动选择 `BT001-BT025` 中最合适的转化路径。

例如：

- 触发 `FB001` 时，调用 `BT001`
- 触发 `FB009` 时，调用 `BT009`
- 触发 `FB024` 时，调用 `BT024`

自动执行逻辑：

- 一个用户输入可能命中多个 false belief
- 优先级：复吸风险 > 戒断误读 > 时机拖延 > 一般认知澄清
- 每次对话最多主攻 1-2 个信念，避免认知负荷过高

输出要求：

- 先承认用户感受
- 再解释机制
- 最后给出一句可执行的替代信念

### 2.4 Intervention Pattern Execution

以下干预模式适合自动执行：

- `INT001` 因果倒置拆解
- `INT002` 非吸烟者对照
- `INT003` 链条视角
- `INT004` 牺牲框架反转
- `INT005` 恐惧命名
- `INT006` 体验再标注
- `INT007` 身份即时切换
- `INT008` 等待陷阱解除
- `INT009` 减量悖论暴露
- `INT010` 替代品去神化
- `INT012` 诱惑预演
- `INT013` 可怜而非羡慕
- `INT014` 时机借口拆除
- `INT016` 失败去人格化
- `INT017` 空虚感游戏化

半自动执行：

- `INT011` 最后一支烟仪式：需要用户明确准备好
- `INT015` 风险现实检验：需要避免过度恐吓
- `INT018` 外部支持者指导：需要先判断用户身份是吸烟者还是支持者

### 2.5 Trigger Detection

Skill 应自动识别触发场景：

- 压力
- 饭后
- 社交
- 饮酒
- 递烟
- 无聊
- 工作挫败
- 情绪低落
- 戒烟几天后自信试探
- 戒烟三周左右测试冲动

输出要求：

- 标注当前触发
- 解释该触发背后的心理机制
- 给出当前场景的回应脚本
- 若触发属于高危复吸，进入 `relapse_risk`

### 2.6 Micro-Coaching Response Generation

每轮自动响应应遵循以下结构：

1. 识别用户当前体验
2. 去羞耻化
3. 重构错误信念
4. 给出下一步行动
5. 用非吸烟者身份收尾

示例结构：

```text
你现在不是需要烟，而是旧回路在把压力解释成吸烟需求。
这不是意志力问题。烟只会暂时解除它自己制造的空虚感。
这一刻要做的不是熬，而是把它识别出来：这是依赖在消退。
现在先不抽，离开递烟场景，喝水或继续当前谈话。
你已经在按非吸烟者的方式处理这个场景。
```

---

## 3. Long-Term Memory Requirements

以下部分必须长期记忆用户状态。原因是戒烟是跨天、跨场景、跨复吸风险的过程，单轮对话无法完成。

### 3.1 User Profile Memory

必须记录：

- 用户是否为吸烟者、已戒烟者、复吸者、支持者
- 当前每日吸烟量或历史吸烟量
- 吸烟年限
- 是否已经设定最后一支烟
- 最后一支烟时间
- 当前戒烟天数
- 是否使用替代品
- 是否保留香烟
- 是否有高风险健康或心理状态

建议字段：

```yaml
user_profile:
  user_role: smoker | ex_smoker | relapsed | supporter
  smoking_history:
    years_smoked:
    daily_amount:
    previous_quit_attempts:
    previous_methods:
  quit_status:
    current_state:
    last_cigarette_at:
    quit_day:
    days_since_quit:
    nicotine_replacement_used:
    cigarettes_accessible:
  safety:
    severe_anxiety:
    severe_depression:
    self_harm_risk:
    medical_referral_needed:
```

### 3.2 Belief State Memory

必须记录每个用户已经暴露出的核心错误信念。

建议字段：

```yaml
belief_state:
  active_false_beliefs:
    - id: FB001
      confidence: high
      evidence: "用户说压力大不抽不行"
      last_seen_at:
  transformed_beliefs:
    - from: FB001
      to: TB001
      stability: partial | stable | fragile
      last_reinforced_at:
  unresolved_beliefs:
    - FB009
    - FB017
```

用途：

- 避免每次从头解释
- 识别反复出现的同一错误信念
- 在复吸时定位根因
- 选择下一轮最该处理的信念

### 3.3 Trigger Memory

必须长期记录用户个人高危触发。

建议字段：

```yaml
trigger_profile:
  high_risk_triggers:
    - trigger_id: TR005
      label: "饭后"
      frequency: high
      relapse_history: false
      coping_script:
  recent_trigger_events:
    - trigger_id:
      occurred_at:
      craving_intensity:
      outcome: no_smoke | smoked | avoided | unknown
```

用途：

- 生成个性化预警
- 自动安排行为实验
- 判断何时进入 `trigger_exposure`
- 复吸后精准修复

### 3.4 Identity Memory

必须记录用户身份转化阶段。

建议字段：

```yaml
identity_state:
  current_identity_label:
  identity_confidence: 0-100
  user_language_markers:
    - "我不能抽"
    - "我不用抽"
  target_identity_adopted: true | false
  last_identity_reinforcement_at:
```

关键判断：

- 用户说 "我不能抽"：仍可能有牺牲框架
- 用户说 "我不用抽"：更接近目标身份
- 用户说 "我已经不抽了，但想试一支"：进入复吸风险

### 3.5 Relapse and Risk Memory

必须记录：

- 是否复吸
- 复吸发生时间
- 复吸前触发
- 复吸前错误推理
- 复吸后情绪
- 修复是否完成

建议字段：

```yaml
relapse_history:
  events:
    - occurred_at:
      amount:
      trigger:
      false_reasoning:
      emotional_aftermath:
      repair_completed:
      repair_plan:
  current_relapse_risk:
    level: low | medium | high | acute
    reasons:
    recommended_intervention:
```

### 3.6 Task Progress Memory

必须记录用户当前任务和完成情况。

建议字段：

```yaml
task_state:
  active_tasks:
    - id:
      type:
      due_at:
      status: pending | completed | skipped | failed
      linked_state:
      linked_trigger:
  completed_experiments:
    - experiment_id:
      result:
      realization:
```

---

## 4. State Machine Requirements

以下部分必须由状态机驱动，而不能只靠自由对话。

### 4.1 Why State Machine Is Required

戒烟 Skill 的风险在于：同一句话在不同阶段含义完全不同。

例如 "我想抽一支"：

- 在 `unaware`：可能只是普通吸烟表达
- 在 `preparing`：说明尚未完成决断
- 在 `withdrawal`：是戒断感再标注场景
- 在 `stable`：可能是复吸风险
- 在 `relapse`：需要修复而非普通劝阻

因此 Skill 必须先判断状态，再选择策略。

### 4.2 Required State Machine Controls

每轮对话必须执行：

1. `classify_state`
2. `detect_state_transition`
3. `select_intervention_by_state`
4. `update_memory`
5. `generate_next_action`

### 4.3 State-Specific Requirements

| State | Primary Goal | Required Skill Behavior |
| --- | --- | --- |
| `unaware` | 建立陷阱模型 | 不强推戒烟，先拆享受/选择幻觉 |
| `ambivalent` | 命名恐惧 | 识别拖延、失败恐惧、生活质量恐惧 |
| `questioning` | 拆收益幻觉 | 匹配 false belief 和 transformation |
| `reframing` | 建立获得框架 | 强化 "不用吸" 而不是 "不能吸" |
| `preparing` | 执行前准备 | 触发预演、移除退路、准备最后一支烟 |
| `quit_day` | 身份切换 | 记录最后一支烟时间，确认非吸烟者身份 |
| `withdrawal` | 戒断重标注 | 把渴望解释为恢复信号，安排短任务 |
| `trigger_exposure` | 场景应对 | 使用预案脚本，记录结果 |
| `stable` | 长期守边界 | 防止试探一支，维护身份 |
| `relapse_risk` | 即时阻断 | 使用链条视角和复吸风险脚本 |
| `relapse` | 修复重启 | 去羞耻化、复盘、立即停止下一支 |

### 4.4 Transition Rules

状态迁移必须保守。

关键规则：

- 不应仅凭用户说 "我想戒" 就进入 `preparing`
- 不应仅凭用户一天没抽就进入 `stable`
- 用户出现 "就一支" 语言时，应立即进入 `relapse_risk`
- 用户吸了一口或一支，应进入 `relapse`
- 用户完成最后一支烟仪式后，应进入 `quit_day`
- 用户已停止但处于前三周高触发期，应优先留在 `withdrawal` 或 `trigger_exposure`

### 4.5 State Persistence

状态必须持久化，不能只在当前对话中存在。

最低字段：

```yaml
state_machine_memory:
  current_state:
  previous_state:
  entered_current_state_at:
  state_transition_reason:
  last_intervention_id:
  next_expected_state:
```

---

## 5. Task System Requirements

以下部分需要任务系统支持。原因是它们不是单轮对话可以完成的，而是需要计划、提醒、执行、复盘。

### 5.1 Behavioral Experiments as Tasks

`EXP001-EXP016` 应转化为可分配任务。

任务字段：

```yaml
task:
  id:
  experiment_id:
  title:
  objective:
  steps:
  due_at:
  check_in_prompt:
  completion_criteria:
  linked_false_belief:
  linked_target_belief:
```

示例：

```yaml
task:
  id: task_observe_after_meal
  experiment_id: EXP002
  title: "饭后观察实验"
  objective: "验证饭后快乐不是香烟创造的"
  steps:
    - "饭后先不吸烟"
    - "观察轻松感是否仍然存在"
    - "记录想吸烟时真正出现的是烟味享受还是旧习惯"
  due_at: "next_after_meal"
  linked_false_belief: FB017
  linked_target_belief: TB017
```

### 5.2 Quit Plan Tasks

进入 `preparing` 后，任务系统应自动创建：

- 核心信念确认任务
- 最后一支烟准备任务
- 移除香烟任务
- 高危触发预演任务
- 戒断期首日跟进任务

建议任务序列：

1. `confirm_no_real_benefit`
2. `identify_top_3_triggers`
3. `write_trigger_scripts`
4. `remove_cigarettes_access`
5. `last_cigarette_ritual`
6. `day_1_check_in`
7. `day_3_check_in`
8. `day_7_check_in`
9. `day_21_boundary_review`

### 5.3 Withdrawal Follow-Up Tasks

进入 `withdrawal` 后，任务系统应支持短周期跟进。

建议节奏：

- Day 0: 身份确认
- Day 1: 戒断感再标注
- Day 3: 高危触发复盘
- Day 5: 等待陷阱提醒
- Day 7: 社交/饭后触发检查
- Day 14: 只一支风险检查
- Day 21: 试探冲动检查

每次跟进应记录：

- 渴望强度
- 触发场景
- 是否吸烟
- 是否使用替代品
- 当前身份语言
- 下一个高风险场景

### 5.4 Trigger Response Tasks

当用户报告未来高危场景，应生成一次性任务：

- 饭局前预演
- 饭局后复盘
- 饮酒场景拒烟脚本
- 工作压力前准备
- 情绪低谷替代行动
- 递烟拒绝脚本练习

任务系统应支持：

- 事件前提醒
- 事件中快速脚本
- 事件后复盘

### 5.5 Relapse Repair Tasks

复吸后应自动创建修复任务，而不是只回复一句安慰。

任务序列：

1. `stop_next_cigarette_now`
2. `remove_access_again`
3. `relapse_event_log`
4. `identify_false_reasoning`
5. `repair_belief_transformation`
6. `restart_identity_statement`
7. `next_24h_trigger_plan`

### 5.6 Supporter Tasks

当用户是亲友/伴侣/支持者时，任务系统应生成：

- 不羞辱沟通任务
- 帮助对方命名恐惧任务
- 戒断期减压任务
- 避免反复提醒任务
- 复吸后支持脚本任务

---

## 6. Relapse Repair Mechanism Requirements

复吸修复必须是 Skill 的一等能力，不应被当成普通失败处理。

### 6.1 Relapse Risk Detection

以下语言应立即判定为 `relapse_risk`：

- "就一支"
- "只吸一口"
- "我想证明自己不会再上瘾"
- "今天特殊"
- "大家都抽"
- "我已经戒了，偶尔没事"
- "我先买一包放着"
- "用电子烟/尼古丁口香糖顶一下"
- "戒这么久了，应该安全了"

触发后必须：

- 不争论道德
- 不长篇恐吓
- 立即使用 `INT003` 链条视角
- 识别对应 `REL001/REL002/REL003/REL005/REL014/REL016`
- 给出 1 个即时阻断动作

### 6.2 Relapse Event Handling

用户已吸烟后，应进入 `relapse`。

必须避免：

- "你失败了"
- "你怎么又抽了"
- "前功尽弃"
- "你太没意志力"

必须执行：

1. 去羞耻化
2. 立即阻断下一支
3. 记录复吸事件
4. 找出触发场景
5. 找出错误推理
6. 调用对应修复转化
7. 重新确认非吸烟者身份
8. 创建 24 小时防护任务

### 6.3 Relapse Repair Flow

推荐流程：

```yaml
relapse_repair_flow:
  - step: stabilize
    action: "先确认用户现在停止继续吸烟"
  - step: de_shame
    action: "说明这不是人格失败，而是旧推理被触发"
  - step: classify_event
    action: "识别复吸类型和触发"
  - step: identify_false_reasoning
    action: "定位复吸前的那句自我说服"
  - step: repair_belief
    action: "调用对应 BT/INT 修复"
  - step: reset_boundary
    action: "确认从现在开始不吸下一支"
  - step: protect_24h
    action: "创建未来24小时触发防护任务"
  - step: memory_update
    action: "写入复吸事件、修复状态和新风险"
```

### 6.4 Relapse Pattern Mapping

| Relapse Pattern | Required Repair |
| --- | --- |
| `REL001` 只一支/一口 | 链条视角 + 下一支阻断 |
| `REL002` 感觉良好后试探 | 稳定状态风险教育 + 不测试原则 |
| `REL003` 等待神奇变化 | 等待陷阱解除 + 身份即时确认 |
| `REL004` 压力事件 | 因果倒置 + 低谷不吸烟计划 |
| `REL005` 社交饮酒 | 社交脚本 + 饮酒限制建议 |
| `REL006` 饭后怀念 | 饭后归因修复 + 饭后任务 |
| `REL007` 羡慕别人吸烟 | 可怜而非羡慕练习 |
| `REL008` 随身留烟 | 移除可得性 + 决断修复 |
| `REL009` 体重焦虑 | 体重信念修复 + 饮食任务 |
| `REL010` 替代品 | 替代品去神化 |
| `REL011` 尼古丁制品 | 尼古丁链条重构 |
| `REL012` 失败记忆 | 失败去人格化 |
| `REL013` 情绪低落 | 安慰剂拆解 + 支持行动 |
| `REL014` 庆祝一支 | 奖励框架修复 |
| `REL015` 秘密吸烟 | 羞耻修复 + 透明记录 |
| `REL016` 轻度吸烟幻想 | 特定场合扩张解释 |
| `REL017` 健康恐惧 | 恐惧命名 + 非吸烟处理恐惧 |
| `REL018` 被劝烟 | 拒烟脚本训练 |

### 6.5 Post-Repair State Transition

复吸后不应直接回到 `stable`。

允许迁移：

- `relapse` -> `reframing`: 用户愿意复盘但信念不稳
- `relapse` -> `quit_day`: 用户完成修复并立即重新停止
- `relapse` -> `withdrawal`: 用户重新停止并进入早期恢复

不允许迁移：

- `relapse` -> `stable`
- `relapse` -> `unaware`，除非用户明确放弃戒烟且重新否认问题

---

## 7. Component Requirements

### 7.1 Belief Engine

职责：

- 检测 false belief
- 选择 transformation
- 记录 belief stability
- 检测旧信念回潮

输入：

- 用户自然语言
- 历史 belief_state
- 当前 state

输出：

- detected_false_beliefs
- recommended_transformations
- belief_update

### 7.2 State Manager

职责：

- 维护当前状态
- 判断状态迁移
- 阻止不合理迁移
- 决定响应优先级

输入：

- 用户输入
- memory
- task results
- relapse risk signals

输出：

- current_state
- transition_reason
- recommended_intervention

### 7.3 Task Manager

职责：

- 创建行为实验任务
- 创建戒断期跟进任务
- 创建触发场景预演任务
- 创建复吸修复任务
- 记录完成结果

输入：

- state
- trigger_profile
- active_false_beliefs
- relapse risk

输出：

- active_tasks
- task prompts
- check-in schedule

### 7.4 Relapse Repair Engine

职责：

- 检测复吸风险语言
- 复吸后去羞耻化
- 复盘触发和错误推理
- 重新建立边界
- 写入长期风险档案

输入：

- user reports craving or smoking
- recent trigger events
- belief_state

输出：

- relapse classification
- repair plan
- updated state
- next 24h task plan

### 7.5 Dialogue Policy

职责：

- 控制语气和对话结构
- 禁止羞辱、恐吓主导和牺牲框架
- 保持 "不用吸" 的身份语言

必须遵守：

- 先承认感觉
- 再解释机制
- 再给具体行动
- 最后确认身份

---

## 8. Data Model Summary

最低可运行数据结构：

```yaml
skill_user_memory:
  user_profile:
    user_role:
    smoking_history:
    quit_status:
    safety:

  state_machine_memory:
    current_state:
    previous_state:
    entered_current_state_at:
    state_transition_reason:

  belief_state:
    active_false_beliefs:
    transformed_beliefs:
    unresolved_beliefs:

  trigger_profile:
    high_risk_triggers:
    recent_trigger_events:

  identity_state:
    current_identity_label:
    identity_confidence:
    user_language_markers:
    target_identity_adopted:

  relapse_history:
    events:
    current_relapse_risk:

  task_state:
    active_tasks:
    completed_experiments:
```

---

## 9. Execution Priority

当多个模块同时触发时，Skill 应按以下优先级执行：

1. Safety risk: 严重心理危机或医疗风险
2. Relapse: 用户已经吸烟
3. Acute relapse risk: 用户即将吸一支
4. Trigger exposure: 用户正在高危场景
5. Withdrawal support: 用户处于早期戒断
6. Belief transformation: 用户仍有错误信念
7. Task follow-up: 用户需要复盘任务
8. Identity reinforcement: 用户状态稳定，需要维护边界

---

## 10. Acceptance Criteria

一个合格的 Skill 实现必须满足：

- 能从用户输入中识别至少 20 类 false belief
- 能将 false belief 映射到 target belief 和 transformation
- 能持久化用户当前戒烟状态
- 能记录最后一支烟时间
- 能区分 `relapse_risk` 和 `relapse`
- 能为高危触发生成预演脚本
- 能将行为实验转成任务
- 能在复吸后完成去羞耻化修复流程
- 能在戒断期持续使用非吸烟者身份语言
- 不鼓励减量、试探一支、保留香烟或使用尼古丁作为默认解决方案
- 不把失败归咎于用户意志薄弱

---

## 11. Implementation Notes

### 11.1 Minimal Viable Skill

MVP 版本必须包含：

- `state_manager`
- `belief_engine`
- `dialogue_policy`
- `relapse_repair_engine`
- 基础长期记忆

可以后置：

- 精细任务调度
- 多轮行为实验统计
- 支持者模式
- 图表化进度

### 11.2 Recommended First Build Order

1. 实现状态机和状态持久化
2. 实现 false belief 检测和 transformation 映射
3. 实现核心对话策略
4. 实现复吸风险检测
5. 实现复吸修复流程
6. 实现行为实验任务系统
7. 实现戒断期跟进任务
8. 实现支持者模式

### 11.3 Key Design Constraint

该 Skill 的核心不是提醒用户 "不要抽烟"，而是持续维护一个模型：

```text
吸烟没有真实收益 -> 戒烟不是牺牲 -> 我已经是非吸烟者 -> 任何一支烟都会重启链条
```

所有自动执行、记忆、状态机、任务系统和复吸修复，都应服务于这个模型。
