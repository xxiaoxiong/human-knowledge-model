# 外部分类 Crosswalk

> 本文件由 `08-data/crosswalks.yaml` 生成。映射用于覆盖审计和导航，不表示概念等价。

## 映射语义

| 类型 | 含义 |
|---|---|
| `close-field` | 外部类别与一个 HKM 领域核心范围近似，但边界不完全相同。 |
| `composite-field` | 外部类别把多个 HKM 领域合并在一起。 |
| `navigation-to-knowledge` | 馆藏或内容导航类别到可能知识入口的映射。 |
| `curriculum-to-knowledge` | 教育项目类别到其主要知识与实践领域的映射。 |
| `activity-to-knowledge` | 经济活动需要调用的知识领域，不表示该活动是一种知识。 |
| `occupation-to-knowledge` | 职业组需要的知识与技能领域，不表示职业等于领域。 |

## 系统概览

| 系统 | 原始目的 | 映射层 | 类别数 |
|---|---|---|---:|
| [UNESCO ISCED Fields of Education and Training 2013](https://uis.unesco.org/sites/default/files/documents/isced-fields-of-education-and-training-2013-en.pdf) | 教育项目和资格的国际统计分类 | broad-field | 11 |
| [OECD Fields of Research and Development 2015](https://www.oecd.org/content/dam/oecd/en/publications/reports/2015/10/frascati-manual-2015_g1g57dcb/9789264239012-en.pdf) | 研发活动统计 | broad-field | 6 |
| [Dewey Decimal Classification](https://www.oclc.org/content/dam/oclc/dewey/versions/print/intro.pdf) | 图书馆馆藏按学科排架和浏览 | main-class | 10 |
| [Library of Congress Classification](https://www.loc.gov/catdir/cpso/lcco/lccowp.html) | 大型学术馆藏分类与定位 | main-class | 21 |
| [UN International Standard Industrial Classification Revision 5](https://unstats.un.org/unsd/classifications/Econ/isic/4) | 生产活动和经济统计分类 | section | 22 |
| [ILO International Standard Classification of Occupations 2008](https://isco.ilo.org/en/isco-08/) | 按技能水平和专门化对工作与职业分组 | major-group | 10 |

## UNESCO ISCED Fields of Education and Training 2013

原始目的：教育项目和资格的国际统计分类。映射层：`broad-field`。

| 代码 | 外部类别 | 映射语义 | HKM H2 | 说明 |
|---|---|---|---|---|
| 00 | Generic programmes and qualifications | `curriculum-to-knowledge` | D02 / D11 / D16 / D20 | 通识和个人能力项目按实际内容分流，不建立“通用知识”杂项域。 |
| 01 | Education | `close-field` | D16 |  |
| 02 | Arts and humanities | `composite-field` | D01 / D08 / D11 / D18 / D19 |  |
| 03 | Social sciences | `composite-field` | D06 / D07 / D10 / D11 |  |
| 04 | Business | `composite-field` | D09 / D10 |  |
| 05 | Natural sciences | `composite-field` | D02 / D03 / D04 / D05 |  |
| 06 | Information and Communication Technologies | `close-field` | D12 |  |
| 07 | Engineering | `composite-field` | D13 |  |
| 08 | Agriculture | `close-field` | D15 |  |
| 09 | Health and welfare | `composite-field` | D07 / D14 / D20 | Welfare 不等同医学，需连社会服务与照护实践。 |
| 10 | Services | `composite-field` | D10 / D13 / D17 / D20 | 体育、家政、旅游、安保和运输按实际对象与技能分流。 |

## OECD Fields of Research and Development 2015

原始目的：研发活动统计。映射层：`broad-field`。

| 代码 | 外部类别 | 映射语义 | HKM H2 | 说明 |
|---|---|---|---|---|
| 1 | Natural sciences | `composite-field` | D02 / D03 / D04 / D05 / D12 |  |
| 2 | Engineering and technology | `close-field` | D13 | FORD 将计算的一部分放在自然科学，医学/环境/生物技术又与其他域桥接。 |
| 3 | Medical and health sciences | `close-field` | D14 |  |
| 4 | Agricultural and veterinary sciences | `close-field` | D15 |  |
| 5 | Social sciences | `composite-field` | D06 / D07 / D09 / D10 / D11 / D16 |  |
| 6 | Humanities and the arts | `composite-field` | D01 / D08 / D11 / D18 / D19 |  |

## Dewey Decimal Classification

原始目的：图书馆馆藏按学科排架和浏览。映射层：`main-class`。

| 代码 | 外部类别 | 映射语义 | HKM H2 | 说明 |
|---|---|---|---|---|
| 000 | Computer science | `composite-field` | D01 / D11 / D12 |  |
| 100 | Philosophy and psychology | `composite-field` | D01 / D06 |  |
| 200 | Religion | `close-field` | D19 |  |
| 300 | Social sciences | `composite-field` | D07 / D09 / D10 / D11 / D16 |  |
| 400 | Language | `close-field` | D11 |  |
| 500 | Science | `composite-field` | D02 / D03 / D04 / D05 |  |
| 600 | Technology | `composite-field` | D12 / D13 / D14 / D15 |  |
| 700 | Arts and recreation | `composite-field` | D18 / D20 |  |
| 800 | Literature | `close-field` | D18 |  |
| 900 | History and geography | `composite-field` | D04 / D07 / D08 |  |

## Library of Congress Classification

原始目的：大型学术馆藏分类与定位。映射层：`main-class`。

| 代码 | 外部类别 | 映射语义 | HKM H2 | 说明 |
|---|---|---|---|---|
| A | General Works | `navigation-to-knowledge` | D01 / D11 | 按作品体裁和综合性导航，不对应独立知识域。 |
| B | Philosophy | `composite-field` | D01 / D06 / D19 |  |
| C | Auxiliary Sciences of History | `close-field` | D08 / D11 |  |
| D | History General and Europe | `close-field` | D08 |  |
| E | History America | `close-field` | D08 | 地域独立主类反映馆藏历史，不在 HKM 顶层复制。 |
| F | History America | `close-field` | D08 | 地域独立主类反映馆藏历史，不在 HKM 顶层复制。 |
| G | Geography | `composite-field` | D04 / D07 / D20 |  |
| H | Social Sciences | `composite-field` | D07 / D10 |  |
| J | Political Science | `close-field` | D09 |  |
| K | Law | `close-field` | D09 |  |
| L | Education | `close-field` | D16 |  |
| M | Music and Books on Music | `close-field` | D18 |  |
| N | Fine Arts | `close-field` | D18 |  |
| P | Language and Literature | `composite-field` | D11 / D18 |  |
| Q | Science | `composite-field` | D02 / D03 / D04 / D05 / D12 |  |
| R | Medicine | `close-field` | D14 |  |
| S | Agriculture | `close-field` | D15 |  |
| T | Technology | `composite-field` | D12 / D13 |  |
| U | Military Science | `close-field` | D17 |  |
| V | Naval Science | `close-field` | D17 | HKM 将其作为安全与工程的专业子范围而非 H2。 |
| Z | Bibliography | `composite-field` | D01 / D11 / D12 |  |

## UN International Standard Industrial Classification Revision 5

原始目的：生产活动和经济统计分类。映射层：`section`。

| 代码 | 外部类别 | 映射语义 | HKM H2 | 说明 |
|---|---|---|---|---|
| A | Agriculture forestry and fishing | `activity-to-knowledge` | D04 / D05 / D10 / D13 / D15 |  |
| B | Mining and quarrying | `activity-to-knowledge` | D03 / D04 / D09 / D10 / D13 / D17 |  |
| C | Manufacturing | `activity-to-knowledge` | D03 / D10 / D12 / D13 / D17 |  |
| D | Electricity gas steam and air conditioning supply | `activity-to-knowledge` | D03 / D04 / D09 / D10 / D13 / D17 |  |
| E | Water supply sewerage waste management and remediation | `activity-to-knowledge` | D04 / D09 / D10 / D13 / D14 / D17 |  |
| F | Construction | `activity-to-knowledge` | D09 / D10 / D13 / D17 / D20 |  |
| G | Wholesale and retail trade | `activity-to-knowledge` | D09 / D10 / D11 / D12 / D20 |  |
| H | Transportation and storage | `activity-to-knowledge` | D09 / D10 / D12 / D13 / D17 |  |
| I | Accommodation and food service activities | `activity-to-knowledge` | D10 / D14 / D15 / D20 |  |
| J | Publishing broadcasting and content production and distribution | `activity-to-knowledge` | D09 / D10 / D11 / D12 / D18 |  |
| K | Telecommunications computer programming consulting computing infrastructure and other information services | `activity-to-knowledge` | D09 / D10 / D11 / D12 / D13 / D17 |  |
| L | Financial and insurance activities | `activity-to-knowledge` | D02 / D09 / D10 / D12 / D17 |  |
| M | Real estate activities | `activity-to-knowledge` | D07 / D09 / D10 / D13 |  |
| N | Professional scientific and technical activities | `activity-to-knowledge` | D01 / D02 / D03 / D04 / D05 / D09 / D10 / D12 / D13 / D14 / D15 / D16 |  |
| O | Administrative and support service activities | `activity-to-knowledge` | D09 / D10 / D11 / D12 / D17 / D20 |  |
| P | Public administration and defence compulsory social security | `activity-to-knowledge` | D07 / D09 / D10 / D17 |  |
| Q | Education | `activity-to-knowledge` | D07 / D09 / D10 / D12 / D16 |  |
| R | Human health and social work activities | `activity-to-knowledge` | D06 / D07 / D09 / D10 / D14 / D16 / D20 |  |
| S | Arts sports and recreation | `activity-to-knowledge` | D07 / D10 / D14 / D18 / D20 |  |
| T | Other service activities | `activity-to-knowledge` | D10 / D13 / D14 / D17 / D20 |  |
| U | Activities of households as employers and for own use | `activity-to-knowledge` | D07 / D10 / D14 / D15 / D20 | 家务照护与自给生产是知识实践，不因不在正式学科而消失。 |
| V | Activities of extraterritorial organizations and bodies | `activity-to-knowledge` | D07 / D09 / D10 / D11 / D17 |  |

## ILO International Standard Classification of Occupations 2008

原始目的：按技能水平和专门化对工作与职业分组。映射层：`major-group`。

| 代码 | 外部类别 | 映射语义 | HKM H2 | 说明 |
|---|---|---|---|---|
| 0 | Armed Forces Occupations | `occupation-to-knowledge` | D09 / D13 / D14 / D17 / D20 |  |
| 1 | Managers | `occupation-to-knowledge` | D07 / D09 / D10 / D11 / D16 / D17 |  |
| 2 | Professionals | `occupation-to-knowledge` | D01 / D02 / D03 / D04 / D05 / D06 / D07 / D08 / D09 / D10 / D11 / D12 / D13 / D14 / D15 / D16 / D17 / D18 / D19 |  |
| 3 | Technicians and Associate Professionals | `occupation-to-knowledge` | D10 / D11 / D12 / D13 / D14 / D15 / D16 / D17 / D20 |  |
| 4 | Clerical Support Workers | `occupation-to-knowledge` | D09 / D10 / D11 / D12 / D20 |  |
| 5 | Service and Sales Workers | `occupation-to-knowledge` | D06 / D10 / D11 / D14 / D17 / D20 |  |
| 6 | Skilled Agricultural Forestry and Fishery Workers | `occupation-to-knowledge` | D04 / D05 / D13 / D15 / D17 / D20 |  |
| 7 | Craft and Related Trades Workers | `occupation-to-knowledge` | D03 / D10 / D13 / D17 / D18 / D20 |  |
| 8 | Plant and Machine Operators and Assemblers | `occupation-to-knowledge` | D10 / D12 / D13 / D17 / D20 |  |
| 9 | Elementary Occupations | `occupation-to-knowledge` | D07 / D10 / D13 / D14 / D15 / D17 / D20 | 低技能等级不表示工作没有知识、风险或尊严。 |

## 仅用于架构借鉴的来源

- [MediaWiki Categories](https://www.mediawiki.org/wiki/Help:Categories)：类别结构实际常为多父图；HKM 借鉴多重归属，但增加严格关系语义。
- [W3C Simple Knowledge Organization System](https://www.w3.org/TR/skos-reference/)：借鉴概念方案、标签、broader/narrower/related 与映射；HKM 另扩展证据、因果、实现和学习关系。

## 解释限制

- 外部类别的统计单位可能是课程、文献、活动或职业，不是知识概念。
- 一个外部类别映射到多个 H2 是预期行为，不是映射失败。
- 覆盖只证明存在导航入口，不证明 H3/H4 内容已足够深入。
- Crosswalk 需随外部体系版本变化而版本化，不能静默覆盖历史映射。
