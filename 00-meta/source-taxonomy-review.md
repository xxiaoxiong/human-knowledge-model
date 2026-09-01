# 外部知识分类体系比较与取舍

## 1. 结论先行

外部分类体系各自优化的是不同任务：

- UNESCO ISCED-F 优化教育项目统计；
- OECD FORD 优化研发统计；
- DDC/LCC 优化馆藏定位；
- MediaWiki 分类优化协作式内容导航；
- ISIC 优化经济活动统计；
- ISCO 优化职业和技能统计；
- SKOS 优化知识组织系统的交换。

HKM 优化“个人理解、学习、跨域迁移和问题求解”。因此采用**交叉覆盖、概念映射和设计原则借鉴**，不复制任何一套顶层目录。

## 2. 比较表

| 体系 | 原始目的与结构 | 可借鉴 | 不直接采用的原因 |
|---|---|---|---|
| UNESCO ISCED-F 2013 | 以教育与训练项目为对象；11 个 broad fields、29 个 narrow fields、约 80 个 detailed fields | 教育与职业训练覆盖；三层编码；跨国可比 | 分类的是课程/资格而非知识本身；将学术、职业与服务目的混在同一轴 |
| OECD FORD（Frascati 2015） | 研发统计；6 个 broad fields 及二级领域 | 紧凑的现代研究覆盖；识别 R&D 边界 | 过度聚合；弱化形式科学、实践知识、日常生活、规范与设计活动 |
| DDC | 十大类，十进制层级，主要按 discipline 组织 | 稳定浏览入口；可递归扩展；明确同一 subject 可分布于多个 discipline | 为排架设计；历史形成的大类不等权；树难表达证据、因果与跨域模型 |
| LCC | 21 个字母主类，细分大量学术馆藏 | 大型知识覆盖压力测试；识别医学、农业、法律、教育、安全等独立检索需求 | 历史与地域不对称；粒度随馆藏传统变化；不是概念本体 |
| MediaWiki Categories | 协作式页面分类；实际常为图而非纯树 | 多父分类、开放扩展、从内容导航 | 关系语义宽松，无法可靠区分 is-a、part-of、applies-to 等 |
| UN ISIC Rev.5 | 生产活动的四层互斥统计分类；依据投入、过程/技术、产出与用途 | 补足产业、服务、基础设施和实际生产知识；学习其明确分类目的 | 分类单位是生产活动/机构，不是知识节点；互斥性不适合跨域知识 |
| ILO ISCO-08 | 按技能水平和技能专门化组织职业；四层、10 个 major groups | 把程序性技能、工具、材料、任务和服务纳入覆盖检查 | 职业随劳动制度和技术变化；“谁做工作”不等于“知识如何组织” |
| W3C SKOS | ConceptScheme、broader/narrower/related、标签和映射 | 标准标签、概念方案、直接/传递层级和跨方案映射 | 关系集不足以表达证据、解释、因果、实现、应用和学习依赖 |

## 3. 关键证据与设计启示

### UNESCO ISCED-F

[ISCED-F 2013 手册](https://uis.unesco.org/sites/default/files/documents/isced-fields-of-education-and-training-2013-en.pdf)明确其对象是教育项目与相关资格，采用 broad/narrow/detailed 三层结构。其 11 个 broad fields 从通用项目、教育、艺术人文延伸到 ICT、工程、农业、健康和服务。

**HKM 取舍**：用它检查教育、健康、农业、工程、服务和个人技能是否被学术分类遗漏；不把“课程所在领域”当成概念的本体类型。

### OECD FORD

[Frascati Manual 2015 的 Fields of R&D 表](https://www.oecd.org/content/dam/oecd/en/publications/reports/2015/10/frascati-manual-2015_g1g57dcb/9789264239012-en.pdf)列出六类：自然科学、工程与技术、医学与健康科学、农业与兽医科学、社会科学、人文与艺术。

**HKM 取舍**：用作研究领域覆盖基线；拆出数学/形式系统、计算/信息等对个人认知高度关键的入口，并补回规范、实践、生活和问题求解维度。

### DDC

[OCLC 的 DDC 介绍](https://www.oclc.org/content/dam/oclc/dewey/versions/print/intro.pdf)说明 DDC 顶层为十个主类，并明确其基本类主要按 disciplines 而非 subjects 组织，因此同一 subject 可能出现在多个类中。

**HKM 取舍**：保留“主领域视图”，但把现实对象另建分面。同一对象（如衣物、食物、城市）可以从心理、文化、技术、经济、健康等多领域观察，不复制对象身份。

### Library of Congress Classification

[LCC 官方说明](https://www.loc.gov/catdir/cpso/lcc.html)说明该体系为组织美国国会图书馆馆藏而发展，顶层有 21 个基本类；[官方 Outline](https://www.loc.gov/catdir/cpso/lcco/lccowp.html)展示其哲学、历史、社会科学、政治、法律、教育、艺术、语言、科学、医学、农业、技术、军事等入口。

**HKM 取舍**：使用其广覆盖检查检索盲区，但不继承因历史、地域和馆藏规模形成的不对称。

### MediaWiki Categories

[MediaWiki 分类帮助](https://www.mediawiki.org/wiki/Help:Categories)指出分类结构虽可组织为有顶层的层级，但实际更常呈图结构。

**HKM 取舍**：接受多重父级和开放演化；同时用本体约束关系，避免“页面放进分类”同时暗示多种互不兼容语义。

### ISIC 与 ISCO

[ISIC Rev.5 介绍](https://unstats.un.org/unsd/classifications/Econ/Download/In%20Text/ISIC5_Intro_11Mar2024.pdf)把经济活动组织为四层互斥结构，分类准则包括投入、生产过程和技术、产出特征及用途。[ISCO-08](https://isco.ilo.org/en/isco-08/)则以技能水平与技能专门化聚合工作，专门化涉及知识领域、工具机器、材料和产出服务。

**HKM 取舍**：这两套体系揭示“学科目录”最容易遗漏的生产、维护、照护、管理、服务和手工技能。HKM 将它们表示为实践、技能、技术、应用与问题模板，而非一律提升为学科。

### SKOS

[W3C SKOS Reference](https://www.w3.org/TR/skos-reference/)定义 ConceptScheme、概念标签以及 broader、narrower、related 和跨方案 mapping；它还区分直接层级边与用于推理的传递闭包。

**HKM 取舍**：兼容其概念与标签思想；在其上增加证据、解释、因果、依赖、实现、应用和学习关系。

## 4. 从比较中得到的八条约束

1. 先声明分类目的和分类单位；
2. 主导航可以分层，但真实结构必须允许多父与横向边；
3. 领域、现实对象、职业、产业和问题必须是不同轴；
4. 分类要覆盖学术研究，也要覆盖实践技能、照护、服务和日常生活；
5. 不能把制度历史造成的目录不对称当成本体真相；
6. 每个类别需要范围说明、包含/排除规则和映射；
7. 外部体系通过 crosswalk 连接，不为兼容而复制节点；
8. 数据结构需要稳定 ID、版本和来源，支持将来导出为 SKOS/RDF/属性图。

## 5. v0.1 覆盖审计

| 压力测试 | HKM 对应 | 初步判断 |
|---|---|---|
| FORD 六大 R&D 领域 | 自然、生命、健康、工程、社会、人文等 H2 | 已覆盖，并补足形式与计算 |
| ISCED 教育/训练 | 教育、工程、农业、健康、服务性实践 | 已覆盖；服务拆入生活、组织、安全等场景 |
| LCC/DDC 馆藏主题 | 20 个 H2 + 对象/应用分面 | 大类已覆盖；宗教、艺术、历史、法律有可发现入口 |
| ISIC 产业活动 | 技术、农业、经济组织、健康、信息、生活实践 | 能映射，但尚未建立产业 crosswalk 数据 |
| ISCO 职业技能 | `skill`、`practice`、`tool` 类型与生活实践领域 | 本体已覆盖，技能地图待后续阶段 |
| 非学术现实问题 | 问题、行动和学习平面 | 架构已覆盖，实例映射待 Phase 5 |

当前最大的结构风险不在 H2 大类遗漏，而在下一层：跨文化知识传统、原住民/地方知识、照护与维修实践、体育与身体技能等很容易在 H3/H4 展开时被弱化。后续覆盖审计必须将这些列为显式检查项。
