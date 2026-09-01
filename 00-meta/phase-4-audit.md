# 阶段 4 冻结审计：跨学科模型层

> 版本：v0.4.0  
> 范围：Thinking Models TM01–TM41；Universal Models UM01–UM22  
> 结论：阶段 4 通过冻结门槛，可作为 Problem → Knowledge Mapping 的稳定模型词表。

## 1. 当前结果

| 层 | 数量 | 领域锚定 | 生成关系 |
|---|---:|---:|---:|
| Thinking Models | 41 | 132 个来源领域引用；143 个机制骨架锚点 | 316 |
| Universal Models | 22 | 96 个跨域表现；96 个领域骨架锚点 | 214 |
| 合计 | 63 | 两层均覆盖全部 20 个 H2 | 530 |

加入模型层后，总图谱由 v0.3.0 的 1,793 条关系增长到 2,323 条。模型不是孤立卡片：Thinking Models 通过 `derived-from` 和 `applies-to` 连接来源领域与机制节点；Universal Models 通过 `applies-to` 和 `explains` 连接跨域表现；模型之间保留 `complements`、`depends-on`、`derived-from` 等有方向关系。

## 2. 冻结门槛检查

- **全域覆盖**：Thinking 与 Universal 两层分别触达 D01–D20，不把跨学科等同于少数学科的模型外推。
- **来源可追踪**：每个 Thinking Model 至少来自两个 H2，且每个来源 H2 至少有一个同域核心节点锚点。
- **跨层可迁移**：每个 Universal Model 至少在四个 H2、三个 H1 中给出具体表现，并连接到相应领域骨架。
- **反例与边界完整**：41 个 Thinking Models 均包含典型案例、反例、边界与常见误用；22 个 Universal Models 均包含失效模式和边界。
- **身份唯一**：代码、稳定 ID、中英文规范化标签和定义无重复；所有领域、核心节点和模型引用目标存在。
- **生成可复现**：模型关系和两份 Markdown 视图由数据源生成，校验器拒绝过期生成物。

## 3. 重叠与主身份审计

Thinking Model 描述“怎样思考或行动”，Universal Model 描述“世界中反复出现什么结构”。名称相近时，只有核心机制和使用方式都相同才应合并；以下配对有意保留为两个身份：

| 配对 | Thinking 层 | Universal 层 | 不合并的理由 |
|---|---|---|---|
| TM06 ↔ UM02 | 识别反馈、选择观测和调节动作的思维操作 | 状态—观测—行动闭环的现实结构 | 操作方法可以失败于错误目标；结构本身不提供正当目标 |
| TM12 ↔ UM04 | 用变异、遗传和选择解释适应的推理框架 | 复制单元在选择环境中改变组成的动力学 | 推理工具要求证据比较；动力学可在生物、文化、技术等载体中表现 |
| TM17 ↔ UM03 | 评估连接规模、结构和外部性的决策工具 | 节点与边构成的拓扑和扩散结构 | 网络效应是部分网络过程，不等同所有网络结构 |
| TM21 ↔ UM19 | 诊断历史顺序、切换成本和锁定的分析步骤 | 历史状态改变未来可达路径的系统性质 | 前者可调用反事实与比较；后者描述路径约束本身 |
| TM38 ↔ UM15 | 用模块、接口与松耦合设计系统 | 层级、嵌套和模块化在多尺度系统中的结构 | 设计操作只覆盖可干预系统的一部分 |
| TM39 ↔ UM11 | 选择增长曲线、识别饱和与衰退的判断工具 | 增长、衰减和承载限制的通用动力学 | 曲线诊断与真实生成机制不能互相替代 |

同层精确标签与定义无重复。相似模型通过有类型的边连接，不使用模糊 `related-to` 掩盖差异。

## 4. 验证证据

```text
VALIDATION OK: 274 scope nodes, 10 bridge views, 257 core nodes across 20 domains,
41 thinking models, 22 universal models, 2323 relations, 20 H2 domains,
248 H3 subdomains, 80 external crosswalk rows, generated views current, Markdown links intact

SITE BUILD OK: 20 domains, 248 subdomains, 10 bridge views, 257 core nodes,
41 thinking models, 22 universal models, 2323 relations

SITE VALIDATION OK: 20 domains, 248 subdomains, 10 bridge views, 257 core nodes,
41 thinking models, 22 universal models, project-relative assets and required interaction surfaces present
```

`node --check site/app.js` 与 `git diff --check` 通过。浏览器验收覆盖默认 41 张 Thinking 卡片、22 张 Universal 卡片的层切换、TM01 详情中的反例/误用/边界、全局搜索中的 TM04，以及 390×844 移动视口；桌面和移动端均无横向溢出，控制台无警告或错误。

## 5. 冻结后的已知风险

1. 当前模型文本是跨领域编辑综合，尚未建立逐条文献引用层；它们是导航和推理结构，不应当作替代原始证据的权威陈述。
2. Universal Models 是可迁移抽象，不是自然定律。跨域同构必须逐案核对状态变量、因果机制、尺度、测量和规范前提。
3. S/A/B 优先级表示一般迁移价值，不是最终学习排名。Top 50/100/300 必须结合问题覆盖、前置中心性、风险与可行动性重新计算。
4. 当前关系表达依赖、解释和应用，不声称量化因果强度。阶段 5–7 新增问题与学习路径后需再次检查中心性偏差、孤立模型与循环前置。

## 6. 下一阶段

阶段 5 将建立 Problem → Knowledge Mapping：先用问题原型表达目标、成功标准、主体、尺度、约束、证据需求和升级阈值，再组合领域节点、Thinking Models 与 Universal Models。问题模板不得把开放情境压缩为固定处方，也不得绕过医学、法律、安全等高风险领域的专业升级边界。
