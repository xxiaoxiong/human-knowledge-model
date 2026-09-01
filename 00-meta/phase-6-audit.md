# Phase 6 学习体系冻结审计

> 冻结版本：v0.6.0  
> 审计对象：个人核心知识排序、Top 50 / 100 / 300、前置关系、八单元学习路线与交互网站

## 1. 冻结结论

Phase 6 通过冻结。学习层覆盖 257 个领域骨架、41 个 Thinking Models 和 22 个 Universal Models，共 320 项候选；生成 1–320 连续唯一排名、8 个学习单元和 109 条学习关系。完整知识图谱由 2,895 条关系构成。

| 检查项 | 冻结结果 |
|---|---:|
| 排名候选 | 320 / 320 |
| Top 50 类型组合 | 28 个领域骨架、14 个 Thinking、8 个 Universal |
| Top 100 类型组合 | 60 个领域骨架、25 个 Thinking、15 个 Universal |
| Top 300 类型组合 | 237 个领域骨架、41 个 Thinking、22 个 Universal |
| Top 50 H2 覆盖 | 20 / 20，每个领域至少 1 个骨架入口 |
| Top 100 H2 覆盖 | 20 / 20，每个领域至少 2 个骨架入口 |
| 学习路线 | 1 条路线、8 个有序单元、3 个层级循环、4 条分支路线 |
| Top 50 路线覆盖 | 50 / 50，全部进入至少一个学习单元 |
| 学习关系 | 109 |
| 全图关系 | 2,895 |

## 2. 排名与路线完整性

- 原始分六个组成项可复算，分项和等于保存的 `raw_score`。
- Top 50、Top 100、Top 300 互相嵌套，类型配额与领域最低覆盖由生成器确定性执行。
- 所有候选都保留继承优先级、问题调用、前置后继、领域广度、得分组成、入选依据和解释理由。
- 八个学习单元按前置拓扑排序，不引用后续单元；每个单元均有重点知识、练习问题、学习结果、练习、验收证据、投入估计和边界说明。
- Top 50 共同底座由 LU01–LU08 完整覆盖；LU08 有意复用关键模型作为综合项目锚点。
- Top 100 与 Top 300 不要求机械按名次线性学习，而以薄弱领域、现实问题和项目证据滚动扩展。

## 3. 风险、偏差与解释边界

本排名是有限时间下的覆盖组合，不是学术真理、职业回报、文明贡献或个人尊严的等级。它仍有以下结构性偏差：

1. 连接多、被问题模板频繁调用的形式、系统、决策和工程知识更容易获得高分。
2. 历史、艺术、宗教、语言、农业和生活实践的价值较难由图连接度衡量，因此必须用 H2 覆盖约束保护。
3. 问题模板与骨架本身反映当前编辑范围；新增问题、文化语境或用户目标会改变排名。
4. 时间估计面向一般成人自学，只能作为规划区间；已有知识、语言、障碍、照护责任和资源会显著改变节奏。
5. 医疗、工程、安全和危机相关学习不授予专业资格，也不能替代合格监督、诊疗、认证或紧急资源。

因此，名次应当被读作“一个公开假设及其可审计理由”。个体可以修改权重、约束和学习路线，但必须保留变更理由与验证证据。

## 4. 自动验证结果

冻结时执行：

```text
VALIDATION OK: 274 scope nodes, 10 bridge views, 257 core nodes across 20 domains,
41 thinking models, 22 universal models, 20 problem templates, 8 learning units,
2895 relations, 20 H2 domains, 248 H3 subdomains, 80 external crosswalk rows,
generated views current, Markdown links intact

SITE VALIDATION OK: 20 domains, 248 subdomains, 10 bridge views, 257 core nodes,
41 thinking models, 22 universal models, 20 problem templates,
320 learning candidates, 8 learning units,
project-relative assets and required interaction surfaces present
```

验证器同时检查：候选全集与唯一名次、三个层级的类型配额、Top 50 / 100 的 H2 覆盖、分数组成、路线前置方向、Top 50 单元覆盖、生成 Markdown 与关系文件一致性、节点 ID 唯一性和 GitHub Pages 相对资源路径。

## 5. 浏览器审计结果

- Top 50 / 100 / 300 分别渲染 50 / 100 / 300 条排名，类型摘要与冻结配额一致。
- 8 张学习卡片均可打开；LU01 详情正确显示 6 个重点知识、3 个练习问题和完整验收结构。
- 全站搜索可以通过“概率、证据与测量”定位 LU02。
- 桌面视口与 390 × 844 手机视口均无页面或学习区横向溢出。
- 手机详情弹窗宽 352 px，未越过 390 px 视口且内部无横向溢出。
- 页面控制台无警告或错误。

## 6. 冻结资产

- 排名设计：`00-meta/learning-priority-design.md`
- 排名数据：`08-data/learning-priorities.generated.yaml`
- 路线源数据：`08-data/learning-roadmap.yaml`
- 学习关系：`08-data/learning-relationships.generated.yaml`
- 人类可读视图：`06-learning/core-knowledge.generated.md`、`06-learning/learning-roadmap.generated.md`
- 生成器：`scripts/generate_learning.py`

后续版本若修改权重、配额、问题模板、骨架或路线，必须重新生成全部学习资产并通过同一审计链；v0.6.0 文件保留为可复现基线。
