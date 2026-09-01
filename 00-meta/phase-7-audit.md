# Phase 7 认知操作框架冻结审计

> 冻结版本：v0.7.0  
> 审计对象：Multi-dimensional Thinking Framework 与 Universal Problem Solving Framework

## 1. 冻结结论

Phase 7 通过冻结。两套框架不是新的知识清单，而是把既有领域、模型和问题原型编排成可调用操作层：FM01 用十个透镜扩展观察空间；FM02 用十阶段闭环生成、授权、执行、监测并更新行动。

| 检查项 | FM01 多维思考 | FM02 通用问题求解 |
|---|---:|---:|
| 透镜 / 阶段 | 10 | 10 |
| H2 覆盖 | 20 / 20 | 20 / 20 |
| Thinking Models 调用 | 38 / 41 | 25 / 41 |
| Universal Models 调用 | 22 / 22 | 15 / 22 |
| Problem Templates 调用 | 0（避免重复映射） | 20 / 20 |
| 进入问题 | 3 | 3 |
| 停止 / 升级条件 | 4 | 5 |

两套框架共生成 161 条有类型关系，全图关系数由 2,895 增至 3,056。

## 2. 结构判断

- FM01 的十个透镜覆盖框定、证据、机制、系统、主体、资源、时间、网络、意义和风险行动；它回答“还应从哪些维度看”。
- FM02 的十阶段覆盖安全分诊、框定、划界、基线、诊断、选项、压力测试、授权、行动监测和复盘迁移；它回答“如何把判断变成负责任行动”。
- 两者通过 `complements` 连接，不互相包含。宽扫描可进入问题闭环；问题闭环又可按阶段回调相关透镜。
- 嵌入组件不是新的知识节点身份，避免把“证据”或“系统”在框架中重复建点；组件通过 `uses` 调用已有 H2、Thinking 和 Universal 节点。
- FM02 通过 `applies-to` 连接全部 20 个问题原型；每个原型仍保留自己的领域栈、证据门槛和专业升级条件。

## 3. 安全与误用边界

1. 框架不能保证正确答案，也不替代领域证据、专业资格、正式治理或价值判断。
2. 十个透镜不是平均用力的问卷；应按风险和信息价值选择重点，并记录暂缓理由。
3. 十阶段不是低风险事务的官僚流程；可以合并阶段，但安全、证据、反证、责任、监测和更新不可删除。
4. 高风险、不可逆、受监管或影响未被代表群体的问题，应提高流程深度并转交合格专业与正式权限主体。
5. “跨领域调用”表示需要检查，不证明某个模型在当前语境必然成立。

## 4. 自动验证结果

```text
VALIDATION OK: 274 scope nodes, 10 bridge views, 257 core nodes across 20 domains,
41 thinking models, 22 universal models, 20 problem templates, 8 learning units,
2 operating frameworks, 3056 relations, 20 H2 domains, 248 H3 subdomains,
80 external crosswalk rows, generated views current, Markdown links intact

SITE VALIDATION OK: 20 domains, 248 subdomains, 10 bridge views, 257 core nodes,
41 thinking models, 22 universal models, 20 problem templates,
320 learning candidates, 8 learning units, 2 operating frameworks,
project-relative assets and required interaction surfaces present
```

验证器同时检查框架字段、双语身份、十项连续序列、引用完整性、20 个 H2 覆盖、模型覆盖下限、FM02 的 20 个问题原型全覆盖、生成文档一致性和 161 条关系可复现性。

## 5. 浏览器审计结果

- 两个框架标签均唯一可操作，面板各渲染 10 个组件。
- FM02 面板首阶段为“安全分诊与权限”，末阶段为“复盘、更新与迁移”。
- FM02 详情显示 10 个阶段、20 个可下钻问题原型，以及领域和模型调用。
- 通过“安全分诊与权限”可以在全站搜索中定位 FM02。
- 桌面与 390 × 844 手机视口均无页面、框架面板或弹窗横向溢出。
- 手机弹窗宽 352 px，内容结构可滚动；页面控制台无警告或错误。

## 6. 冻结资产

- 机器可读源：`08-data/frameworks.yaml`
- 生成关系：`08-data/framework-relationships.generated.yaml`
- 多维思考视图：`07-frameworks/multidimensional-thinking-framework.md`
- 通用求解视图：`07-frameworks/universal-problem-solving-framework.md`
- 生成器：`scripts/generate_frameworks.py`

后续版本若修改组件、调用或边界，必须重新生成视图与关系并重新执行验证、浏览器和全局结构审计。
