"""Generate human-readable maps and materialized structural edges."""

from __future__ import annotations

from collections import defaultdict
from pathlib import Path

import yaml

from generate_learning import (
    calculate_learning_priorities,
    generate_core_knowledge_view,
    generate_learning_relations,
    generate_learning_roadmap_view,
)


ROOT = Path(__file__).resolve().parents[1]


def load_yaml(relative_path: str) -> dict:
    return yaml.safe_load((ROOT / relative_path).read_text(encoding="utf-8"))


def text_cell(value: object) -> str:
    return str(value).replace("|", "\\|").replace("\n", " ")


def generate_map(domain_data: dict, subdomain_data: dict) -> str:
    superdomains = {item["id"]: item for item in domain_data["superdomains"]}
    domains = {item["id"]: item for item in domain_data["domains"]}
    children: dict[str, list[dict]] = defaultdict(list)
    for item in subdomain_data["subdomains"]:
        children[item["parent"]].append(item)
    for items in children.values():
        items.sort(key=lambda item: item["code"])

    lines = [
        "# H1–H3 人类知识范围地图",
        "",
        "> 本文件由 `08-data/domains.yaml` 与 `08-data/subdomains.yaml` 生成。",
        "> 请修改数据源后运行 `python scripts/generate_views.py`，不要直接维护本文件。",
        "",
        "## 总览",
        "",
        f"- H1 超级领域：{len(superdomains)}",
        f"- H2 一级领域：{len(domains)}",
        f"- H3 子领域：{sum(len(items) for items in children.values())}",
        "- H3 是稳定知识范围，不是理论、模型、方法或工具的固定深度。",
        "",
        "| H1 | H2 数 | H3 数 |",
        "|---|---:|---:|",
    ]

    for superdomain in sorted(superdomains.values(), key=lambda item: item["code"]):
        child_domains = sorted(
            [item for item in domains.values() if item["parent"] == superdomain["id"]],
            key=lambda item: item["code"],
        )
        h3_count = sum(len(children[item["id"]]) for item in child_domains)
        lines.append(
            f"| {superdomain['code']} {superdomain['labels']['zh']} | "
            f"{len(child_domains)} | {h3_count} |"
        )

    for superdomain in sorted(superdomains.values(), key=lambda item: item["code"]):
        lines.extend(
            [
                "",
                f"## {superdomain['code']} {superdomain['labels']['zh']}",
                "",
                superdomain["definition"],
            ]
        )
        child_domains = sorted(
            [item for item in domains.values() if item["parent"] == superdomain["id"]],
            key=lambda item: item["code"],
        )
        for domain in child_domains:
            lines.extend(
                [
                    "",
                    f"### {domain['code']} {domain['labels']['zh']} / {domain['labels']['en']}",
                    "",
                    domain["definition"],
                    "",
                    f"**H2 边界：** {domain['boundary_notes']}",
                    "",
                    "| H3 | 子领域 | 核心问题 | 边界 | 桥接领域 |",
                    "|---|---|---|---|---|",
                ]
            )
            for item in children[domain["id"]]:
                lines.append(
                    f"| {item['code']} | {text_cell(item['labels']['zh'])}<br>"
                    f"{text_cell(item['labels']['en'])} | "
                    f"{text_cell('；'.join(item['core_questions']))} | "
                    f"{text_cell(item['boundary_notes'])} | "
                    f"{text_cell(' / '.join(item['bridge_domains']))} |"
                )

    lines.extend(
        [
            "",
            "## 使用规则",
            "",
            "1. H3 只表示范围缩小；内容节点仍按 Ontology 类型建立。",
            "2. 一个概念只建一个稳定身份，跨 H3 使用 `in-domain` 或有类型关系连接。",
            "3. 桥接领域是检索提示，不表示该 H3 的所有节点都属于这些领域。",
            "4. H3 通过压力测试后才进入 H4 主题和领域骨架；数量不是完成标准。",
            "",
        ]
    )
    return "\n".join(lines)


def generate_hierarchy_relations(subdomain_data: dict) -> dict:
    relations = []
    for item in sorted(subdomain_data["subdomains"], key=lambda value: value["code"]):
        slug = item["id"].rsplit(":", 1)[-1]
        relations.append(
            {
                "id": f"hkm:relation:{slug}-narrower-parent",
                "source": item["id"],
                "type": "narrower-than",
                "target": item["parent"],
                "scope": "H3 到 H2 的直接范围层级；由 subdomains.yaml 的 parent 字段生成",
                "confidence": "high",
                "provenance": ["hkm:source:editorial-synthesis-v0-2"],
            }
        )
    return {
        "schema_version": "0.1.0",
        "model_version": subdomain_data["model_version"],
        "generated_from": "08-data/subdomains.yaml",
        "relationships": relations,
    }


def generate_crosswalk(crosswalk_data: dict) -> str:
    lines = [
        "# 外部分类 Crosswalk",
        "",
        "> 本文件由 `08-data/crosswalks.yaml` 生成。映射用于覆盖审计和导航，不表示概念等价。",
        "",
        "## 映射语义",
        "",
        "| 类型 | 含义 |",
        "|---|---|",
    ]
    for key, value in crosswalk_data["mapping_semantics"].items():
        lines.append(f"| `{key}` | {text_cell(value)} |")

    lines.extend(
        [
            "",
            "## 系统概览",
            "",
            "| 系统 | 原始目的 | 映射层 | 类别数 |",
            "|---|---|---|---:|",
        ]
    )
    for system in crosswalk_data["systems"]:
        lines.append(
            f"| [{text_cell(system['title'])}]({system['source']}) | "
            f"{text_cell(system['purpose'])} | {system['mapping_level']} | "
            f"{len(system['categories'])} |"
        )

    for system in crosswalk_data["systems"]:
        lines.extend(
            [
                "",
                f"## {system['title']}",
                "",
                f"原始目的：{system['purpose']}。映射层：`{system['mapping_level']}`。",
                "",
                "| 代码 | 外部类别 | 映射语义 | HKM H2 | 说明 |",
                "|---|---|---|---|---|",
            ]
        )
        for category in system["categories"]:
            lines.append(
                f"| {text_cell(category['code'])} | {text_cell(category['title'])} | "
                f"`{category['mapping']}` | {' / '.join(category['targets'])} | "
                f"{text_cell(category.get('note', ''))} |"
            )

    lines.extend(["", "## 仅用于架构借鉴的来源", ""])
    for source in crosswalk_data["architecture_only_sources"]:
        lines.append(
            f"- [{source['title']}]({source['source']})：{source['lesson']}"
        )
    lines.extend(
        [
            "",
            "## 解释限制",
            "",
            "- 外部类别的统计单位可能是课程、文献、活动或职业，不是知识概念。",
            "- 一个外部类别映射到多个 H2 是预期行为，不是映射失败。",
            "- 覆盖只证明存在导航入口，不证明 H3/H4 内容已足够深入。",
            "- Crosswalk 需随外部体系版本变化而版本化，不能静默覆盖历史映射。",
            "",
        ]
    )
    return "\n".join(lines)


def generate_bridge_views(
    domain_data: dict, subdomain_data: dict, bridge_data: dict
) -> str:
    domains_by_code = {item["code"]: item for item in domain_data["domains"]}
    subdomains_by_id = {item["id"]: item for item in subdomain_data["subdomains"]}
    lines = [
        "# 跨领域桥接视图",
        "",
        "> 本文件由 `08-data/bridges.yaml` 生成。桥接视图是组织层，不占 H0–H4，也不改变成员的主归属。",
        "",
        "## 总览",
        "",
        "| 代码 | 桥接视图 | H2 数 | H3 成员数 | 共同机制 |",
        "|---|---|---:|---:|---|",
    ]
    for bridge in sorted(bridge_data["bridge_views"], key=lambda item: item["code"]):
        lines.append(
            f"| {bridge['code']} | {text_cell(bridge['labels']['zh'])}<br>"
            f"{text_cell(bridge['labels']['en'])} | {len(bridge['member_domains'])} | "
            f"{len(bridge['members'])} | "
            f"{text_cell(' / '.join(bridge['unifying_mechanisms']))} |"
        )

    for bridge in sorted(bridge_data["bridge_views"], key=lambda item: item["code"]):
        lines.extend(
            [
                "",
                f"## {bridge['code']} {bridge['labels']['zh']} / {bridge['labels']['en']}",
                "",
                bridge["definition"],
                "",
                "**核心问题**",
                "",
            ]
        )
        lines.extend(f"- {question}" for question in bridge["core_questions"])
        lines.extend(
            [
                "",
                "**连接的 H2**："
                + "；".join(
                    f"{code} {domains_by_code[code]['labels']['zh']}"
                    for code in bridge["member_domains"]
                ),
                "",
                "| H3 | 成员 | 主归 H2 |",
                "|---|---|---|",
            ]
        )
        for member_id in bridge["members"]:
            member = subdomains_by_id[member_id]
            parent = next(
                item for item in domain_data["domains"] if item["id"] == member["parent"]
            )
            lines.append(
                f"| {member['code']} | {text_cell(member['labels']['zh'])} | "
                f"{parent['code']} {text_cell(parent['labels']['zh'])} |"
            )
        lines.extend(
            [
                "",
                f"**边界：** {bridge['boundary_notes']}",
                "",
                "**共同机制：** " + " / ".join(bridge["unifying_mechanisms"]),
            ]
        )

    lines.extend(
        [
            "",
            "## 使用限制",
            "",
            "- `member-of` 只表示进入同一导航视图，不表示成员互为子类或组成部分。",
            "- 跨域共同词汇必须继续区分操作定义、尺度、证据和因果机制。",
            "- 桥接视图可重叠；一个 H3 同时进入多个视图是预期行为。",
            "- 若视图只剩一个 H2，或能够无损归入一个父域，应降为域内主题而非保留桥接身份。",
            "",
        ]
    )
    return "\n".join(lines)


def generate_bridge_relations(domain_data: dict, bridge_data: dict) -> dict:
    domain_id_by_code = {item["code"]: item["id"] for item in domain_data["domains"]}
    relationships = []
    for bridge in sorted(bridge_data["bridge_views"], key=lambda item: item["code"]):
        bridge_slug = bridge["id"].rsplit(":", 1)[-1]
        for domain_code in bridge["member_domains"]:
            relationships.append(
                {
                    "id": f"hkm:relation:{bridge_slug}-bridges-{domain_code.lower()}",
                    "source": bridge["id"],
                    "type": "bridges",
                    "target": domain_id_by_code[domain_code],
                    "scope": "桥接视图连接的 H2；由 bridges.yaml 的 member_domains 生成",
                    "confidence": "high",
                    "provenance": ["hkm:source:editorial-synthesis-v0-2"],
                }
            )
        for member_id in bridge["members"]:
            member_slug = member_id.rsplit(":", 1)[-1]
            relationships.append(
                {
                    "id": f"hkm:relation:{member_slug}-member-{bridge_slug}",
                    "source": member_id,
                    "type": "member-of",
                    "target": bridge["id"],
                    "scope": "H3 是跨域导航视图的成员；不表示范围父子或概念等价",
                    "confidence": "high",
                    "provenance": ["hkm:source:editorial-synthesis-v0-2"],
                }
            )
    return {
        "schema_version": "0.1.0",
        "model_version": bridge_data["model_version"],
        "generated_from": "08-data/bridges.yaml",
        "relationships": relationships,
    }


def generate_core_skeletons(
    domain_data: dict, subdomain_data: dict, core_data: dict
) -> str:
    domains_by_id = {item["id"]: item for item in domain_data["domains"]}
    subdomains_by_id = {item["id"]: item for item in subdomain_data["subdomains"]}
    children: dict[str, list[dict]] = defaultdict(list)
    for node in core_data["core_nodes"]:
        children[node["primary_domain"]].append(node)
    for items in children.values():
        items.sort(key=lambda item: item["code"])

    lines = [
        f"# 领域核心骨架：{len(children)} 个已发布域",
        "",
        "> 本文件由 `08-data/core-nodes.yaml` 生成。节点是可复用的本体身份，不是 H4 目录项。",
        "",
        "## 总览",
        "",
        "| H2 | 核心节点 | S | A | B–D | 类型数 |",
        "|---|---:|---:|---:|---:|---:|",
    ]
    for domain_id, items in sorted(
        children.items(), key=lambda item: domains_by_id[item[0]]["code"]
    ):
        domain = domains_by_id[domain_id]
        priorities = defaultdict(int)
        types = set()
        for node in items:
            priorities[node["learning_priority"]] += 1
            types.add(node["primary_type"])
        lines.append(
            f"| {domain['code']} {domain['labels']['zh']} | {len(items)} | "
            f"{priorities['S']} | {priorities['A']} | "
            f"{sum(priorities[p] for p in ['B', 'C', 'D'])} | {len(types)} |"
        )

    for domain_id, items in sorted(
        children.items(), key=lambda item: domains_by_id[item[0]]["code"]
    ):
        domain = domains_by_id[domain_id]
        lines.extend(
            [
                "",
                f"## {domain['code']} {domain['labels']['zh']} / {domain['labels']['en']}",
                "",
                domain["definition"],
                "",
                "| 节点 | 类型 / 角色 | 优先级 | 核心问题 | H3 定位 |",
                "|---|---|:---:|---|---|",
            ]
        )
        for node in items:
            subdomain_codes = [
                subdomains_by_id[item_id]["code"] for item_id in node["related_subdomains"]
            ]
            lines.append(
                f"| {node['code']} {text_cell(node['labels']['zh'])}<br>"
                f"{text_cell(node['labels']['en'])} | `{node['primary_type']}`<br>"
                f"{text_cell(' / '.join(node['roles']))} | **{node['learning_priority']}** | "
                f"{text_cell('；'.join(node['core_questions']))} | "
                f"{text_cell(' / '.join(subdomain_codes))} |"
            )
        for node in items:
            lines.extend(
                [
                    "",
                    f"### {node['code']} {node['labels']['zh']}",
                    "",
                    node["definition"],
                    "",
                    f"- **本体类型：** `{node['primary_type']}`"
                    + (
                        "；附加类型："
                        + ", ".join(f"`{value}`" for value in node["additional_types"])
                        if node.get("additional_types")
                        else ""
                    ),
                    f"- **骨架角色：** {' / '.join(node['roles'])}",
                    f"- **学习优先级：** {node['learning_priority']}",
                    f"- **边界：** {node['boundary_notes']}",
                ]
            )
            if node["prerequisites"]:
                prereq_labels = [
                    next(
                        item["labels"]["zh"]
                        for item in core_data["core_nodes"]
                        if item["id"] == prereq
                    )
                    for prereq in node["prerequisites"]
                ]
                lines.append(f"- **前置：** {'；'.join(prereq_labels)}")

    lines.extend(
        [
            "",
            "## 阅读规则",
            "",
            "- S/A/B 表示一般学习优先级，不表示节点的真理等级或社会地位。",
            "- `prerequisite-of` 是面向骨架掌握目标的学习建议，不等于严格逻辑推导。",
            "- H3 定位表示直接适用范围；跨 H2 的复用继续通过显式关系和桥接视图表达。",
            "- 每个边界说明都是骨架的一部分；只记定义而忽略失效条件不算掌握。",
            "",
        ]
    )
    return "\n".join(lines)


def generate_core_relations(
    domain_data: dict, subdomain_data: dict, core_data: dict
) -> dict:
    domains_by_id = {item["id"]: item for item in domain_data["domains"]}
    relationships = []
    for node in sorted(core_data["core_nodes"], key=lambda item: item["code"]):
        node_slug = node["id"].rsplit(":", 1)[-1]
        domain = domains_by_id[node["primary_domain"]]
        relationships.append(
            {
                "id": f"hkm:relation:{node_slug}-primary-{domain['code'].lower()}",
                "source": node["id"],
                "type": "primary-domain",
                "target": node["primary_domain"],
                "scope": "核心节点的稳定 H2 主导航；由 core-nodes.yaml 生成",
                "confidence": "high",
                "provenance": ["hkm:source:editorial-synthesis-v0-3"],
            }
        )
        for subdomain_id in node["related_subdomains"]:
            subdomain_slug = subdomain_id.rsplit(":", 1)[-1]
            relationships.append(
                {
                    "id": f"hkm:relation:{node_slug}-in-{subdomain_slug}",
                    "source": node["id"],
                    "type": "in-scope",
                    "target": subdomain_id,
                    "scope": "核心节点直接适用的 H3 范围；不改变节点身份",
                    "confidence": "high",
                    "provenance": ["hkm:source:editorial-synthesis-v0-3"],
                }
            )
        for prerequisite_id in node["prerequisites"]:
            prereq_slug = prerequisite_id.rsplit(":", 1)[-1]
            relationships.append(
                {
                    "id": f"hkm:relation:{prereq_slug}-prerequisite-{node_slug}",
                    "source": prerequisite_id,
                    "type": "prerequisite-of",
                    "target": node["id"],
                    "scope": "掌握当前领域骨架的一般学习前置；并非严格逻辑蕴含",
                    "confidence": "medium",
                    "provenance": ["hkm:source:editorial-synthesis-v0-3"],
                }
            )
        for connection in node["connections"]:
            target_slug = connection["target"].rsplit(":", 1)[-1]
            relationships.append(
                {
                    "id": f"hkm:relation:{node_slug}-{connection['type']}-{target_slug}",
                    "source": node["id"],
                    "type": connection["type"],
                    "target": connection["target"],
                    "scope": connection["scope"],
                    "confidence": connection.get("confidence", "medium"),
                    "provenance": ["hkm:source:editorial-synthesis-v0-3"],
                }
            )
    return {
        "schema_version": "0.1.0",
        "model_version": core_data["model_version"],
        "generated_from": "08-data/core-nodes.yaml",
        "relationships": relationships,
    }


def generate_thinking_model_view(
    domain_data: dict, core_data: dict, thinking_data: dict, universal_data: dict
) -> str:
    domains = {item["id"]: item for item in domain_data["domains"]}
    core_nodes = {item["id"]: item for item in core_data["core_nodes"]}
    all_models = {
        item["id"]: item
        for item in [
            *thinking_data["thinking_models"],
            *universal_data["universal_models"],
        ]
    }
    models = sorted(thinking_data["thinking_models"], key=lambda item: item["code"])
    lines = [
        "# Thinking Models：核心思维模型库",
        "",
        "> 本文件由 `08-data/thinking-models.yaml` 生成；请修改数据源后运行 `python scripts/generate_views.py`。",
        "",
        f"共 {len(models)} 个思维模型。它们是可迁移的认知操作，不是脱离领域证据的口号。",
        "",
        "| 代码 | 模型 | 来源 H2 | 优先级 |",
        "|---|---|---:|---:|",
    ]
    for model in models:
        source_labels = "、".join(domains[item]["code"] for item in model["source_domains"])
        lines.append(
            f"| {model['code']} | {text_cell(model['labels']['zh'])}<br>{text_cell(model['labels']['en'])} | "
            f"{source_labels} | {model['learning_priority']} |"
        )
    for model in models:
        source_labels = "、".join(
            f"{domains[item]['code']} {domains[item]['labels']['zh']}"
            for item in model["source_domains"]
        )
        mechanisms = "；".join(
            f"{core_nodes[item]['code']} {core_nodes[item]['labels']['zh']}"
            for item in model["mechanism_core_nodes"]
        )
        related = "；".join(
            f"`{item['type']}` → {all_models[item['target']]['code']} "
            f"{all_models[item['target']]['labels']['zh']}（{item['scope']}）"
            for item in model["related_models"]
        )
        lines.extend(
            [
                "",
                f"## {model['code']} {model['labels']['zh']} / {model['labels']['en']}",
                "",
                model["definition"],
                "",
                f"**核心思想：** {model['core_idea']}",
                "",
                f"**来源领域：** {source_labels}",
                "",
                f"**机制锚点：** {mechanisms}",
                "",
                f"**适用问题：** {'；'.join(model['applicable_problems'])}",
                "",
                f"**典型案例：** {'；'.join(model['typical_cases'])}",
                "",
                f"**反例：** {'；'.join(model['counterexamples'])}",
                "",
                f"**使用边界：** {model['boundary_notes']}",
                "",
                f"**常见误用：** {'；'.join(model['common_misuses'])}",
                "",
                f"**模型关系：** {related}",
            ]
        )
    return "\n".join(lines) + "\n"


def generate_universal_model_view(
    domain_data: dict, core_data: dict, thinking_data: dict, universal_data: dict
) -> str:
    domains = {item["id"]: item for item in domain_data["domains"]}
    core_nodes = {item["id"]: item for item in core_data["core_nodes"]}
    all_models = {
        item["id"]: item
        for item in [
            *thinking_data["thinking_models"],
            *universal_data["universal_models"],
        ]
    }
    models = sorted(universal_data["universal_models"], key=lambda item: item["code"])
    lines = [
        "# Universal Models：通用世界模型",
        "",
        "> 本文件由 `08-data/universal-models.yaml` 生成；请修改数据源后运行 `python scripts/generate_views.py`。",
        "",
        f"共 {len(models)} 个通用模型。每个模型都在至少四个 H2、三个 H1 中给出领域锚点。",
        "",
        "| 代码 | 通用结构 | 跨域表现 | 优先级 |",
        "|---|---|---:|---:|",
    ]
    for model in models:
        lines.append(
            f"| {model['code']} | {text_cell(model['labels']['zh'])}<br>{text_cell(model['labels']['en'])} | "
            f"{len(model['manifestations'])} | {model['learning_priority']} |"
        )
    for model in models:
        related = "；".join(
            f"`{item['type']}` → {all_models[item['target']]['code']} "
            f"{all_models[item['target']]['labels']['zh']}（{item['scope']}）"
            for item in model["related_models"]
        )
        lines.extend(
            [
                "",
                f"## {model['code']} {model['labels']['zh']} / {model['labels']['en']}",
                "",
                model["definition"],
                "",
                f"**核心结构：** {model['core_structure']}",
                "",
                f"**状态变量：** {'、'.join(model['state_variables'])}",
                "",
                f"**典型动力学：** {'、'.join(model['dynamics'])}",
                "",
                "| H2 | 领域表现 | 核心锚点 |",
                "|---|---|---|",
            ]
        )
        for manifestation in model["manifestations"]:
            domain = domains[manifestation["domain"]]
            anchors = "；".join(
                f"{core_nodes[item]['code']} {core_nodes[item]['labels']['zh']}"
                for item in manifestation["core_nodes"]
            )
            lines.append(
                f"| {domain['code']} {domain['labels']['zh']} | "
                f"{text_cell(manifestation['expression'])} | {anchors} |"
            )
        lines.extend(
            [
                "",
                f"**失效模式：** {'；'.join(model['failure_modes'])}",
                "",
                f"**使用边界：** {model['boundary_notes']}",
                "",
                f"**模型关系：** {related}",
            ]
        )
    return "\n".join(lines) + "\n"


def generate_problem_mapping_view(
    domain_data: dict,
    core_data: dict,
    thinking_data: dict,
    universal_data: dict,
    problem_data: dict,
) -> str:
    domains = {item["id"]: item for item in domain_data["domains"]}
    cores = {item["id"]: item for item in core_data["core_nodes"]}
    models = {
        item["id"]: item
        for item in [
            *thinking_data["thinking_models"],
            *universal_data["universal_models"],
        ]
    }
    problems = sorted(problem_data["problem_templates"], key=lambda item: item["code"])
    family_labels = {
        "sensemaking": "理解与诊断",
        "prediction-decision": "预测与决策",
        "design-intervention": "设计与干预",
        "coordination-governance": "协调与治理",
        "risk-response": "风险与响应",
        "learning-meaning": "学习与意义",
    }
    lines = [
        "# Problem → Knowledge Mapping：问题—知识调用体系",
        "",
        "> 本文件由 `08-data/problem-templates.yaml` 生成；请修改数据源后运行 `python scripts/generate_views.py`。",
        "",
        f"共 {len(problems)} 个问题原型。它们是生成知识调用、证据计划和行动工作流的模板，不是固定答案。",
        "",
        "| 代码 | 问题原型 | 家族 | H2 | TM | UM | 优先级 |",
        "|---|---|---|---:|---:|---:|---:|",
    ]
    for problem in problems:
        calls = problem["knowledge_calls"]
        lines.append(
            f"| {problem['code']} | {text_cell(problem['labels']['zh'])}<br>"
            f"{text_cell(problem['labels']['en'])} | "
            f"{family_labels[problem['problem_family']]} | "
            f"{len(calls['domains'])} | {len(calls['thinking_models'])} | "
            f"{len(calls['universal_models'])} | {problem['learning_priority']} |"
        )

    for problem in problems:
        calls = problem["knowledge_calls"]
        domain_labels = "；".join(
            f"{domains[item]['code']} {domains[item]['labels']['zh']}"
            for item in calls["domains"]
        )
        core_labels = "；".join(
            f"{cores[item]['code']} {cores[item]['labels']['zh']}"
            for item in calls["core_nodes"]
        )
        thinking_labels = "；".join(
            f"{models[item]['code']} {models[item]['labels']['zh']}"
            for item in calls["thinking_models"]
        )
        universal_labels = "；".join(
            f"{models[item]['code']} {models[item]['labels']['zh']}"
            for item in calls["universal_models"]
        )
        scoping = problem["scoping_dimensions"]
        lines.extend(
            [
                "",
                f"## {problem['code']} {problem['labels']['zh']} / {problem['labels']['en']}",
                "",
                problem["definition"],
                "",
                f"**家族 / 目标：** {family_labels[problem['problem_family']]} / "
                f"`{problem['primary_aim']}`；次要目标："
                f"{'、'.join(problem['secondary_aims'])}",
                "",
                f"**触发问题：** {'；'.join(problem['trigger_questions'])}",
                "",
                f"**成功标准：** {'；'.join(problem['success_criteria'])}",
                "",
                "### 问题边界",
                "",
                "| 对象 | 主体 | 时间 | 尺度 | 价值 | 约束 |",
                "|---|---|---|---|---|---|",
                f"| {'、'.join(scoping['objects'])} | {'、'.join(scoping['actors'])} | "
                f"{'、'.join(scoping['timescales'])} | {'、'.join(scoping['scales'])} | "
                f"{'、'.join(scoping['values_at_stake'])} | {'、'.join(scoping['constraints'])} |",
                "",
                "### 知识调用栈",
                "",
                f"- **H2：** {domain_labels}",
                f"- **核心骨架：** {core_labels}",
                f"- **Thinking Models：** {thinking_labels}",
                f"- **Universal Models：** {universal_labels}",
                "",
                f"**证据门槛：** {'；'.join(problem['evidence_requirements'])}",
                "",
                "### 工作流",
                "",
                "| 阶段 | 动作 | 产物 | 检查门 |",
                "|---:|---|---|---|",
            ]
        )
        for step in problem["workflow"]:
            lines.append(
                f"| {step['stage']} | {text_cell(step['action'])} | "
                f"{text_cell(step['output'])} | {text_cell(step['gate'])} |"
            )
        lines.extend(
            [
                "",
                f"**最终输出：** {'；'.join(problem['outputs'])}",
                "",
                f"**失效模式：** {'；'.join(problem['failure_modes'])}",
                "",
                f"**升级条件：** {'；'.join(problem['escalation_conditions'])}",
                "",
                f"**使用边界：** {problem['boundary_notes']}",
                "",
                f"**示例问题：** {'；'.join(problem['example_prompts'])}",
            ]
        )
    return "\n".join(lines) + "\n"


def generate_cross_model_relations(
    domain_data: dict, core_data: dict, thinking_data: dict, universal_data: dict
) -> dict:
    domains = {item["id"]: item for item in domain_data["domains"]}
    core_nodes = {item["id"]: item for item in core_data["core_nodes"]}
    relationships: list[dict] = []
    seen_ids: set[str] = set()

    def add(relation: dict) -> None:
        if relation["id"] not in seen_ids:
            relationships.append(relation)
            seen_ids.add(relation["id"])

    for model in sorted(thinking_data["thinking_models"], key=lambda item: item["code"]):
        prefix = model["code"].lower()
        for domain_id in model["source_domains"]:
            domain = domains[domain_id]
            add(
                {
                    "id": f"hkm:relation:{prefix}-source-{domain['code'].lower()}",
                    "source": model["id"],
                    "type": "in-domain",
                    "target": domain_id,
                    "scope": "思维模型的历史或方法来源；不表示排他所有权",
                    "confidence": "high",
                    "provenance": ["hkm:source:editorial-synthesis-v0-4"],
                }
            )
        for core_id in model["mechanism_core_nodes"]:
            core = core_nodes[core_id]
            add(
                {
                    "id": f"hkm:relation:{prefix}-derived-{core['code'].lower().replace('.', '-')}",
                    "source": model["id"],
                    "type": "derived-from",
                    "target": core_id,
                    "scope": "思维模型的领域机制锚点；不把领域理论压缩为启发式",
                    "confidence": "high",
                    "provenance": ["hkm:source:editorial-synthesis-v0-4"],
                }
            )
        for index, relation in enumerate(model["related_models"], start=1):
            add(
                {
                    "id": f"hkm:relation:{prefix}-model-link-{index:02d}",
                    "source": model["id"],
                    "type": relation["type"],
                    "target": relation["target"],
                    "scope": relation["scope"],
                    "confidence": relation.get("confidence", "medium"),
                    "provenance": ["hkm:source:editorial-synthesis-v0-4"],
                }
            )

    for model in sorted(universal_data["universal_models"], key=lambda item: item["code"]):
        prefix = model["code"].lower()
        for manifestation in model["manifestations"]:
            domain = domains[manifestation["domain"]]
            add(
                {
                    "id": f"hkm:relation:{prefix}-applies-{domain['code'].lower()}",
                    "source": model["id"],
                    "type": "applies-to",
                    "target": manifestation["domain"],
                    "scope": manifestation["expression"],
                    "confidence": "high",
                    "provenance": ["hkm:source:editorial-synthesis-v0-4"],
                }
            )
            for core_id in manifestation["core_nodes"]:
                core = core_nodes[core_id]
                add(
                    {
                        "id": f"hkm:relation:{prefix}-explains-{core['code'].lower().replace('.', '-')}",
                        "source": model["id"],
                        "type": "explains",
                        "target": core_id,
                        "scope": manifestation["expression"],
                        "confidence": "medium",
                        "provenance": ["hkm:source:editorial-synthesis-v0-4"],
                    }
                )
        for index, relation in enumerate(model["related_models"], start=1):
            add(
                {
                    "id": f"hkm:relation:{prefix}-model-link-{index:02d}",
                    "source": model["id"],
                    "type": relation["type"],
                    "target": relation["target"],
                    "scope": relation["scope"],
                    "confidence": relation.get("confidence", "medium"),
                    "provenance": ["hkm:source:editorial-synthesis-v0-4"],
                }
            )
    return {
        "schema_version": "0.1.0",
        "model_version": thinking_data["model_version"],
        "generated_from": [
            "08-data/thinking-models.yaml",
            "08-data/universal-models.yaml",
        ],
        "relationships": relationships,
    }


def generate_problem_relations(
    domain_data: dict,
    core_data: dict,
    thinking_data: dict,
    universal_data: dict,
    problem_data: dict,
) -> dict:
    domains = {item["id"]: item for item in domain_data["domains"]}
    cores = {item["id"]: item for item in core_data["core_nodes"]}
    thinking = {item["id"]: item for item in thinking_data["thinking_models"]}
    universal = {item["id"]: item for item in universal_data["universal_models"]}
    relationships: list[dict] = []

    for problem in sorted(problem_data["problem_templates"], key=lambda item: item["code"]):
        prefix = problem["code"].lower()
        calls = problem["knowledge_calls"]
        groups = [
            ("domain", calls["domains"], domains, "问题原型调用的知识领域范围", "high"),
            ("core", calls["core_nodes"], cores, "问题原型调用的领域骨架机制", "high"),
            ("thinking", calls["thinking_models"], thinking, "问题原型调用的认知操作", "high"),
            ("universal", calls["universal_models"], universal, "问题原型调用的跨域结构", "medium"),
        ]
        for group_name, target_ids, index, scope, confidence in groups:
            for target_id in target_ids:
                target = index[target_id]
                code = target["code"].lower().replace(".", "-")
                relationships.append(
                    {
                        "id": f"hkm:relation:{prefix}-uses-{group_name}-{code}",
                        "source": problem["id"],
                        "type": "uses",
                        "target": target_id,
                        "scope": scope,
                        "confidence": confidence,
                        "provenance": ["hkm:source:editorial-synthesis-v0-5"],
                    }
                )
    return {
        "schema_version": "0.1.0",
        "model_version": problem_data["model_version"],
        "generated_from": [
            "08-data/problem-templates.yaml",
            "08-data/core-nodes.yaml",
            "08-data/thinking-models.yaml",
            "08-data/universal-models.yaml",
        ],
        "relationships": relationships,
    }


def main() -> None:
    domain_data = load_yaml("08-data/domains.yaml")
    subdomain_data = load_yaml("08-data/subdomains.yaml")
    crosswalk_data = load_yaml("08-data/crosswalks.yaml")
    bridge_data = load_yaml("08-data/bridges.yaml")
    core_data = load_yaml("08-data/core-nodes.yaml")
    thinking_data = load_yaml("08-data/thinking-models.yaml")
    universal_data = load_yaml("08-data/universal-models.yaml")
    problem_data = load_yaml("08-data/problem-templates.yaml")
    roadmap_data = load_yaml("08-data/learning-roadmap.yaml")
    map_text = generate_map(domain_data, subdomain_data)
    (ROOT / "01-knowledge-map/level-2-3-map.generated.md").write_text(
        map_text, encoding="utf-8", newline="\n"
    )
    hierarchy = generate_hierarchy_relations(subdomain_data)
    yaml_text = yaml.safe_dump(
        hierarchy,
        allow_unicode=True,
        sort_keys=False,
        width=120,
    )
    (ROOT / "08-data/hierarchy-relationships.generated.yaml").write_text(
        yaml_text, encoding="utf-8", newline="\n"
    )
    crosswalk_text = generate_crosswalk(crosswalk_data)
    (ROOT / "01-knowledge-map/external-crosswalk.generated.md").write_text(
        crosswalk_text, encoding="utf-8", newline="\n"
    )
    bridge_text = generate_bridge_views(domain_data, subdomain_data, bridge_data)
    (ROOT / "01-knowledge-map/bridge-views.generated.md").write_text(
        bridge_text, encoding="utf-8", newline="\n"
    )
    bridge_relations = generate_bridge_relations(domain_data, bridge_data)
    bridge_yaml = yaml.safe_dump(
        bridge_relations,
        allow_unicode=True,
        sort_keys=False,
        width=120,
    )
    (ROOT / "08-data/bridge-relationships.generated.yaml").write_text(
        bridge_yaml, encoding="utf-8", newline="\n"
    )
    core_text = generate_core_skeletons(domain_data, subdomain_data, core_data)
    core_path = ROOT / "02-domain-skeletons/template-domain-skeletons.generated.md"
    core_path.parent.mkdir(parents=True, exist_ok=True)
    core_path.write_text(core_text, encoding="utf-8", newline="\n")
    core_relations = generate_core_relations(domain_data, subdomain_data, core_data)
    core_yaml = yaml.safe_dump(
        core_relations,
        allow_unicode=True,
        sort_keys=False,
        width=120,
    )
    (ROOT / "08-data/core-relationships.generated.yaml").write_text(
        core_yaml, encoding="utf-8", newline="\n"
    )
    thinking_text = generate_thinking_model_view(
        domain_data, core_data, thinking_data, universal_data
    )
    thinking_path = ROOT / "03-thinking-models/thinking-models.generated.md"
    thinking_path.parent.mkdir(parents=True, exist_ok=True)
    thinking_path.write_text(thinking_text, encoding="utf-8", newline="\n")
    universal_text = generate_universal_model_view(
        domain_data, core_data, thinking_data, universal_data
    )
    universal_path = ROOT / "04-universal-models/universal-models.generated.md"
    universal_path.parent.mkdir(parents=True, exist_ok=True)
    universal_path.write_text(universal_text, encoding="utf-8", newline="\n")
    model_relations = generate_cross_model_relations(
        domain_data, core_data, thinking_data, universal_data
    )
    model_yaml = yaml.safe_dump(
        model_relations,
        allow_unicode=True,
        sort_keys=False,
        width=120,
    )
    (ROOT / "08-data/model-relationships.generated.yaml").write_text(
        model_yaml, encoding="utf-8", newline="\n"
    )
    problem_text = generate_problem_mapping_view(
        domain_data, core_data, thinking_data, universal_data, problem_data
    )
    problem_path = ROOT / "05-problem-mapping/problem-templates.generated.md"
    problem_path.parent.mkdir(parents=True, exist_ok=True)
    problem_path.write_text(problem_text, encoding="utf-8", newline="\n")
    problem_relations = generate_problem_relations(
        domain_data, core_data, thinking_data, universal_data, problem_data
    )
    problem_yaml = yaml.safe_dump(
        problem_relations,
        allow_unicode=True,
        sort_keys=False,
        width=120,
    )
    (ROOT / "08-data/problem-relationships.generated.yaml").write_text(
        problem_yaml, encoding="utf-8", newline="\n"
    )
    learning_priorities = calculate_learning_priorities(
        domain_data, core_data, thinking_data, universal_data, problem_data
    )
    learning_yaml = yaml.safe_dump(
        learning_priorities,
        allow_unicode=True,
        sort_keys=False,
        width=120,
    )
    (ROOT / "08-data/learning-priorities.generated.yaml").write_text(
        learning_yaml, encoding="utf-8", newline="\n"
    )
    learning_path = ROOT / "06-learning/core-knowledge.generated.md"
    learning_path.parent.mkdir(parents=True, exist_ok=True)
    learning_path.write_text(
        generate_core_knowledge_view(learning_priorities),
        encoding="utf-8",
        newline="\n",
    )
    roadmap_path = ROOT / "06-learning/learning-roadmap.generated.md"
    roadmap_path.write_text(
        generate_learning_roadmap_view(roadmap_data, learning_priorities, problem_data),
        encoding="utf-8",
        newline="\n",
    )
    learning_relations = generate_learning_relations(
        roadmap_data, learning_priorities, problem_data
    )
    learning_relation_yaml = yaml.safe_dump(
        learning_relations,
        allow_unicode=True,
        sort_keys=False,
        width=120,
    )
    (ROOT / "08-data/learning-relationships.generated.yaml").write_text(
        learning_relation_yaml, encoding="utf-8", newline="\n"
    )
    print(
        f"Generated H1-H3 map, {len(hierarchy['relationships'])} hierarchy relations, "
        f"{sum(len(s['categories']) for s in crosswalk_data['systems'])} crosswalk rows, "
        f"{len(bridge_data['bridge_views'])} bridge views, and "
        f"{len(bridge_relations['relationships'])} bridge relations; "
        f"{len(core_data['core_nodes'])} core nodes and "
        f"{len(core_relations['relationships'])} core relations; "
        f"{len(thinking_data['thinking_models'])} thinking models, "
        f"{len(universal_data['universal_models'])} universal models, and "
        f"{len(model_relations['relationships'])} cross-model relations; "
        f"{len(problem_data['problem_templates'])} problem templates and "
        f"{len(problem_relations['relationships'])} problem-call relations; "
        f"{len(learning_priorities['entries'])} learning candidates ranked; "
        f"{len(roadmap_data['learning_units'])} learning units and "
        f"{len(learning_relations['relationships'])} learning relations."
    )


if __name__ == "__main__":
    main()
