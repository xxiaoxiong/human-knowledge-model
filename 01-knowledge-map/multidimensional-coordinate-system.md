# 多维知识坐标系

## 1. 从目录到坐标

树回答“从哪个入口浏览”，坐标回答“为了当前任务怎样筛选和组合”。每个重要知识节点可表示为：

```text
Node = Identity
     + Scope memberships
     + Object facets
     + Problem/Aim facets
     + Artifact type
     + Epistemic mode
     + Method facets
     + Scale/Context
     + Epistemic status
     + Application facets
     + Learning metadata
```

分面可以多选；ID 和节点类型不能因视图变化而变化。

## 2. 维度 A：知识范围（Where）

```text
H0 语料 → H1 超级领域 → H2 一级领域 → H3 子领域 → H4 主题/问题簇
```

用途：主导航、权限/维护责任、领域覆盖统计。限制：只表达范围，不表达证据、因果或应用。

## 3. 维度 B：现实对象（What）

建议受控词表的第一层：

| 代码 | 对象家族 | 示例 |
|---|---|---|
| O01 | 时空、物质、能量与场 | 粒子、分子、材料、辐射 |
| O02 | 天体、地球与环境系统 | 星系、气候、海洋、土壤 |
| O03 | 生命与生态 | 细胞、个体、物种、生态系统 |
| O04 | 身体、脑与心智 | 器官、认知、情绪、意识 |
| O05 | 人与人际关系 | 个体、家庭、关系、身份 |
| O06 | 群体、网络与组织 | 社区、企业、社群、供应链 |
| O07 | 制度、市场、国家与全球系统 | 法律、货币、政府、国际秩序 |
| O08 | 语言、知识、文化与意义 | 符号、文本、传统、世界观 |
| O09 | 技术、工件与基础设施 | 软件、机器、城市、电网 |
| O10 | 行动、实践与体验 | 技能、照护、工作、创作、生活 |

对象可以多尺度嵌套，但 `part-of` 关系与 `scale` 标签分别记录，不从表格顺序自动推理。

## 4. 维度 C：问题与目的（Why）

| 代码 | 目的 | 典型问法 | 主要输出 |
|---|---|---|---|
| A01 | 识别/分类 | 这是什么？属于哪类？ | 概念、分类、判据 |
| A02 | 描述/测量 | 状态怎样？有多少？ | 数据、指标、分布 |
| A03 | 解释/理解 | 为什么？机制/意义是什么？ | 理论、机制、解释 |
| A04 | 预测/预警 | 将发生什么？概率多大？ | 预测、区间、情景 |
| A05 | 诊断/溯因 | 什么导致了已知结果？ | 候选原因、鉴别证据 |
| A06 | 评价/规范 | 好不好、对不对、公平吗？ | 标准、权衡、论证 |
| A07 | 设计/创造 | 怎样实现期望功能/体验？ | 方案、原型、作品 |
| A08 | 控制/维护 | 怎样稳定、纠偏、修复？ | 反馈、程序、维护策略 |
| A09 | 优化/分配 | 约束下怎样更好？ | 目标函数、方案、权衡 |
| A10 | 决策/协商 | 现在应做什么？如何协调？ | 选择、承诺、规则 |
| A11 | 学习/迁移 | 怎样掌握并用于新情境？ | 路线、练习、反馈 |

## 5. 维度 D：知识形态（Which kind）

使用 Ontology 的 `primary_type`：范围、对象/现象、概念、主张、证据、规律/原则、理论、模型、框架、规范/价值、问题、方法、测量、工具、技术、技能、实践、干预、案例、学习单元。

检索时通常要组合类型。例如“解释问题”优先查理论、模型、证据和替代主张；“行动问题”还需方法、工具、技能、规范和案例。

## 6. 维度 E：认识方式（How we know）

| 模式 | 核心操作 | 典型有效性问题 |
|---|---|---|
| `empirical` 经验 | 观察、测量、实验 | 可靠、有效、可复核吗？ |
| `formal` 形式 | 定义、公理、演绎、计算 | 前提清楚、推导有效吗？ |
| `causal` 因果 | 干预、机制、反事实 | 混杂、选择和替代机制排除了吗？ |
| `historical` 历史 | 来源批判、时序、过程追踪 | 史料、语境和时代错置如何处理？ |
| `interpretive` 诠释 | 意义、文本、体验、视角 | 解释是否忠于材料且能比较？ |
| `comparative` 比较 | 跨案例/制度/物种比较 | 案例可比吗？选择偏差如何？ |
| `normative` 规范 | 价值澄清、一致性、权衡 | 价值前提和受影响者是否显式？ |
| `design` 设计 | 需求、原型、测试、迭代 | 是否有用、可行、安全、可维护？ |
| `embodied` 具身实践 | 示范、练习、反馈、情境判断 | 能否稳定表现并迁移？ |
| `synthetic` 综合 | 系统综述、三角验证、建模 | 异质证据如何加权、矛盾如何保留？ |

一个成熟结论往往依赖多种方式，而非“选择一个正确方法”。

## 7. 维度 F：方法家族

```text
观察与记录       实验与准实验       调查与抽样
测量与仪器       演绎与证明         统计估计与检验
因果推断         计算与算法         建模与仿真
比较研究         历史与档案         田野与民族志
文本/话语解释    案例与过程追踪     设计研究与原型
优化与控制       参与式研究         专业实践与反思
综合评价与复现
```

方法节点通过 `applies-to`、`operationalizes`、`measures`、`uses` 和 `produces` 与问题、概念、工具和证据相连。

## 8. 维度 G：尺度

尺度至少拆成三轴，避免把“微观—宏观”混成一条万能序列：

### 空间/物质尺度

`量子/分子 → 细胞/器官 → 个体 → 局部/区域 → 行星 → 宇宙`

### 社会组织尺度

`个体 → 关系/家庭 → 群体/网络 → 组织 → 社区/城市 → 国家 → 全球`

### 时间尺度

`瞬时 → 日/季节 → 生命周期 → 代际 → 历史 → 演化/地质 → 宇宙`

跨尺度推理必须说明聚合规则、涌现结构和信息丢失，不能把个体关系直接外推到社会或反向套用。

## 9. 维度 H：情境与边界条件

```yaml
context:
  time_period: null
  geography: null
  population: null
  culture_language: []
  institution: []
  environment: []
  technology_regime: []
  assumptions: []
  exclusions: []
```

情境是许多社会、医学、生态和工程结论可迁移性的核心，不是可有可无的注释。

## 10. 维度 I：认识状态与不确定性

### 认识状态

`proposal → hypothesis → active-research → contested → limited-consensus → strong-consensus → deprecated`

状态不是简单线性进步；`contested` 可长期存在，`deprecated` 仍有历史学习价值。

### 不确定性来源

| 类型 | 说明 |
|---|---|
| 随机变异 | 系统本身或抽样的变异 |
| 测量误差 | 工具、操作化与记录误差 |
| 参数不确定性 | 模型参数估计不足 |
| 结构不确定性 | 竞争模型、遗漏机制、边界选择 |
| 情景不确定性 | 未来政策、技术、行为路径未知 |
| 深度不确定性 | 结果集合或概率都难以可靠指定 |
| 价值不确定性 | 目标、权重与可接受风险存在分歧 |

## 11. 维度 J：学习价值

```yaml
learning:
  priority: S            # S | A | B | C | D
  difficulty: 2          # 1..5
  prerequisite_ids: []
  transfer_score: 5      # 1..5
  usage_frequency: 4     # 1..5
  explanatory_power: 5   # 1..5
  decision_value: 5      # 1..5
  risk_protection: 4     # 1..5
  target_profiles: [general]
```

分数是可审计的课程设计判断，不是假装精确的自然测量；必须附评分理由并允许不同学习者画像覆盖默认值。

## 12. 组合检索示例

### “是否投资一家 AI 医疗公司？”

```yaml
aim: [diagnose, predict, evaluate, decide]
objects: [organization, market, ai-system, healthcare-system]
domains: [D02, D06, D09, D10, D12, D13, D14, D17]
methods: [accounting-analysis, causal-inference, scenario-analysis, risk-analysis]
scales: [organization, industry, national-regulation]
uncertainty: [parameter, structural, scenario, value]
```

### “如何改善自己的睡眠？”

```yaml
aim: [diagnose, design, maintain, learn]
objects: [body, mind, habit, living-environment]
domains: [D05, D06, D14, D16, D20]
methods: [measurement, self-experiment, clinical-guideline, habit-design]
scales: [individual, daily, lifecycle]
boundary: [seek-professional-help-when-red-flags]
```

坐标负责找到候选知识；证据质量、适用边界和专业责任决定能否安全使用。
