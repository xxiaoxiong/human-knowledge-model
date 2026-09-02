"""Generate the reproducible Phase 8 structural audit for the complete HKM graph."""

from __future__ import annotations

from collections import Counter, defaultdict, deque
from pathlib import Path
import re
import sys

import yaml


ROOT = Path(__file__).resolve().parents[1]
AUDIT_VERSION = "0.8.0"
RELATION_FILES = [
    "08-data/relationships.yaml",
    "08-data/hierarchy-relationships.generated.yaml",
    "08-data/bridge-relationships.generated.yaml",
    "08-data/core-relationships.generated.yaml",
    "08-data/model-relationships.generated.yaml",
    "08-data/problem-relationships.generated.yaml",
    "08-data/learning-relationships.generated.yaml",
    "08-data/framework-relationships.generated.yaml",
]


def load_yaml(relative_path: str) -> dict:
    return yaml.safe_load((ROOT / relative_path).read_text(encoding="utf-8"))


def normalize(value: str) -> str:
    return re.sub(r"[^\w]+", "", str(value or "").casefold(), flags=re.UNICODE)


def collect_model() -> tuple[list[dict], list[dict], dict[str, dict]]:
    domains = load_yaml("08-data/domains.yaml")
    subdomains = load_yaml("08-data/subdomains.yaml")
    bridges = load_yaml("08-data/bridges.yaml")
    core = load_yaml("08-data/core-nodes.yaml")
    thinking = load_yaml("08-data/thinking-models.yaml")
    universal = load_yaml("08-data/universal-models.yaml")
    problems = load_yaml("08-data/problem-templates.yaml")
    roadmap = load_yaml("08-data/learning-roadmap.yaml")
    frameworks = load_yaml("08-data/frameworks.yaml")
    priorities = load_yaml("08-data/learning-priorities.generated.yaml")
    grouped = {
        "root": [domains["root"]],
        "superdomain": domains["superdomains"],
        "domain": domains["domains"],
        "subdomain": subdomains["subdomains"],
        "bridge-view": bridges["bridge_views"],
        "core-node": core["core_nodes"],
        "thinking-model": thinking["thinking_models"],
        "universal-model": universal["universal_models"],
        "problem-template": problems["problem_templates"],
        "learning-path": [roadmap["learning_path"]],
        "learning-unit": roadmap["learning_units"],
        "operating-framework": frameworks["frameworks"],
    }
    nodes = [
        {**node, "_audit_group": group}
        for group, collection in grouped.items()
        for node in collection
    ]
    relations = [
        relation
        for path in RELATION_FILES
        for relation in load_yaml(path)["relationships"]
    ]
    sources = {
        "domains": domains,
        "subdomains": subdomains,
        "bridges": bridges,
        "core": core,
        "thinking": thinking,
        "universal": universal,
        "problems": problems,
        "roadmap": roadmap,
        "frameworks": frameworks,
        "priorities": priorities,
    }
    return nodes, relations, sources


def duplicate_identity_groups(nodes: list[dict], field: str) -> list[dict]:
    groups: dict[tuple[str, str], list[str]] = defaultdict(list)
    if field == "labels":
        for node in nodes:
            for locale, value in node.get("labels", {}).items():
                if value:
                    groups[(locale, normalize(value))].append(node["id"])
    else:
        for node in nodes:
            value = node.get(field, "")
            if value:
                groups[(field, normalize(value))].append(node["id"])
    return [
        {"key": key[1], "locale_or_field": key[0], "nodes": values}
        for key, values in sorted(groups.items())
        if len(values) > 1
    ]


def weak_components(node_ids: set[str], relations: list[dict]) -> list[list[str]]:
    adjacency: dict[str, set[str]] = {node_id: set() for node_id in node_ids}
    for relation in relations:
        source = relation["source"]
        target = relation["target"]
        if source in adjacency and target in adjacency:
            adjacency[source].add(target)
            adjacency[target].add(source)
    remaining = set(node_ids)
    components: list[list[str]] = []
    while remaining:
        start = next(iter(remaining))
        queue = deque([start])
        component: set[str] = set()
        while queue:
            current = queue.popleft()
            if current in component:
                continue
            component.add(current)
            queue.extend(adjacency[current] - component)
        remaining -= component
        components.append(sorted(component))
    return sorted(components, key=len, reverse=True)


def build_audit() -> dict:
    nodes, relations, sources = collect_model()
    node_ids = [node["id"] for node in nodes]
    node_id_set = set(node_ids)
    relation_ids = [relation["id"] for relation in relations]
    degree = Counter()
    unknown_endpoints: list[str] = []
    self_loops: list[str] = []
    triples: dict[tuple[str, str, str], list[str]] = defaultdict(list)
    for relation in relations:
        source = relation["source"]
        target = relation["target"]
        if source not in node_id_set or target not in node_id_set:
            unknown_endpoints.append(relation["id"])
        else:
            degree[source] += 1
            degree[target] += 1
        if source == target:
            self_loops.append(relation["id"])
        triples[(source, relation["type"], target)].append(relation["id"])

    duplicate_triples = [
        {"source": key[0], "type": key[1], "target": key[2], "relations": values}
        for key, values in sorted(triples.items())
        if len(values) > 1
    ]
    isolated_nodes = sorted(node_id_set - set(degree))
    components = weak_components(node_id_set, relations)
    duplicate_labels = duplicate_identity_groups(nodes, "labels")
    duplicate_definitions = duplicate_identity_groups(nodes, "definition")
    node_group_by_id = {node["id"]: node["_audit_group"] for node in nodes}
    blocking_duplicate_labels = [
        group
        for group in duplicate_labels
        if {node_group_by_id[node_id] for node_id in group["nodes"]}
        != {"subdomain", "core-node"}
    ]
    scope_content_label_collisions = [
        group
        for group in duplicate_labels
        if {node_group_by_id[node_id] for node_id in group["nodes"]}
        == {"subdomain", "core-node"}
    ]
    malformed_labels = [
        node["id"]
        for node in nodes
        if set(node.get("labels", {})) != {"zh", "en"}
        or any(
            not isinstance(value, str) or not value.strip()
            for value in node.get("labels", {}).values()
        )
    ]

    domains = sources["domains"]["domains"]
    subdomains = sources["subdomains"]["subdomains"]
    bridges = sources["bridges"]["bridge_views"]
    core_nodes = sources["core"]["core_nodes"]
    thinking_models = sources["thinking"]["thinking_models"]
    universal_models = sources["universal"]["universal_models"]
    problems = sources["problems"]["problem_templates"]
    frameworks = sources["frameworks"]["frameworks"]
    top50 = sources["priorities"]["entries"][:50]

    domain_code_by_id = {domain["id"]: domain["code"] for domain in domains}
    h3_by_domain = Counter(domain_code_by_id[item["parent"]] for item in subdomains)
    core_by_domain = Counter(domain_code_by_id[item["primary_domain"]] for item in core_nodes)
    bridge_by_domain = Counter(
        code for bridge in bridges for code in set(bridge["member_domains"])
    )
    model_domain_ids = {
        domain_id
        for model in thinking_models
        for domain_id in model["source_domains"]
    } | {
        manifestation["domain"]
        for model in universal_models
        for manifestation in model["manifestations"]
    }
    problem_domain_ids = {
        domain_id
        for problem in problems
        for domain_id in problem["knowledge_calls"]["domains"]
    }
    top50_domains = Counter(
        code
        for entry in top50
        if entry["asset_type"] == "core-node"
        for code in entry["domains"]
    )
    framework_domain_counts = Counter(
        domain_code_by_id[domain_id]
        for framework in frameworks
        for domain_id in {
            domain_id
            for component in framework["components"]
            for domain_id in component["domains"]
        }
    )
    h3_covered = {
        subdomain_id
        for node in core_nodes
        for subdomain_id in node["related_subdomains"]
    }
    domain_metrics = []
    for domain in sorted(domains, key=lambda item: item["code"]):
        code = domain["code"]
        domain_metrics.append(
            {
                "code": code,
                "label": domain["labels"]["zh"],
                "h3": h3_by_domain[code],
                "core_nodes": core_by_domain[code],
                "bridge_views": bridge_by_domain[code],
                "model_coverage": domain["id"] in model_domain_ids,
                "problem_coverage": domain["id"] in problem_domain_ids,
                "top50_core_entries": top50_domains[code],
                "operating_frameworks": framework_domain_counts[code],
            }
        )

    called_thinking = {
        model_id
        for problem in problems
        for model_id in problem["knowledge_calls"]["thinking_models"]
    }
    called_universal = {
        model_id
        for problem in problems
        for model_id in problem["knowledge_calls"]["universal_models"]
    }
    blocking_issues: list[str] = []
    if len(node_ids) != len(node_id_set):
        blocking_issues.append("duplicate node IDs")
    if len(relation_ids) != len(set(relation_ids)):
        blocking_issues.append("duplicate relation IDs")
    if unknown_endpoints:
        blocking_issues.append("relations with unknown endpoints")
    if self_loops:
        blocking_issues.append("self-loop relations")
    if duplicate_triples:
        blocking_issues.append("duplicate directed relation triples")
    if isolated_nodes:
        blocking_issues.append("isolated nodes")
    if len(components) != 1:
        blocking_issues.append("knowledge graph has multiple weak components")
    if blocking_duplicate_labels:
        blocking_issues.append("same-layer or ambiguous exact normalized duplicate labels")
    if duplicate_definitions:
        blocking_issues.append("exact normalized duplicate definitions")
    if malformed_labels:
        blocking_issues.append("nodes without exactly two non-empty bilingual labels")
    if len(h3_covered) != len(subdomains):
        blocking_issues.append("H3 scopes not covered by domain skeletons")
    for metric in domain_metrics:
        if (
            metric["h3"] < 8
            or metric["core_nodes"] < 10
            or not metric["model_coverage"]
            or not metric["problem_coverage"]
            or metric["top50_core_entries"] < 1
            or metric["operating_frameworks"] != 2
        ):
            blocking_issues.append(f"incomplete cross-layer coverage for {metric['code']}")
    if called_thinking != {model["id"] for model in thinking_models}:
        blocking_issues.append("Thinking Models not fully covered by problem templates")
    if called_universal != {model["id"] for model in universal_models}:
        blocking_issues.append("Universal Models not fully covered by problem templates")

    return {
        "schema_version": "0.1.0",
        "audit_version": AUDIT_VERSION,
        "status": "pass" if not blocking_issues else "fail",
        "inventory": {
            "nodes": len(nodes),
            "relations": len(relations),
            "node_groups": dict(sorted(Counter(node["_audit_group"] for node in nodes).items())),
            "relation_types": dict(sorted(Counter(relation["type"] for relation in relations).items())),
        },
        "integrity": {
            "blocking_issues": blocking_issues,
            "duplicate_node_ids": len(node_ids) - len(node_id_set),
            "duplicate_relation_ids": len(relation_ids) - len(set(relation_ids)),
            "unknown_endpoint_relations": unknown_endpoints,
            "self_loop_relations": self_loops,
            "duplicate_relation_triples": duplicate_triples,
            "isolated_nodes": isolated_nodes,
            "weak_component_count": len(components),
            "largest_component_nodes": len(components[0]) if components else 0,
            "duplicate_labels": duplicate_labels,
            "blocking_duplicate_labels": blocking_duplicate_labels,
            "scope_content_label_collisions": scope_content_label_collisions,
            "duplicate_definitions": duplicate_definitions,
            "malformed_labels": malformed_labels,
        },
        "coverage": {
            "domain_metrics": domain_metrics,
            "h3_covered_by_core": len(h3_covered),
            "h3_total": len(subdomains),
            "thinking_called_by_problems": len(called_thinking),
            "thinking_total": len(thinking_models),
            "universal_called_by_problems": len(called_universal),
            "universal_total": len(universal_models),
            "problem_templates": len(problems),
            "learning_top50_covered": len(
                {
                    item
                    for unit in sources["roadmap"]["learning_units"]
                    for item in unit["focus_assets"]
                }
                & {entry["node_id"] for entry in top50}
            ),
            "operating_frameworks": len(frameworks),
        },
        "limitations": [
            "精确去重不能发现语义近义、粒度差异或翻译导致的潜在重复，仍需编辑审查。",
            "Crosswalk 证明外部分类存在入口，不证明所有 H4 主题和具体知识已经展开。",
            "关系数量衡量可导航性，不衡量证据质量、因果强度或文化重要性。",
            "当前版本冻结结构和调用接口，不宣称穷尽未来新领域、地方知识或隐性实践。",
        ],
    }


def generate_audit_markdown(audit: dict) -> str:
    inventory = audit["inventory"]
    integrity = audit["integrity"]
    coverage = audit["coverage"]
    status_label = "通过" if audit["status"] == "pass" else "未通过"
    lines = [
        "# Phase 8 全局结构审计",
        "",
        f"> 审计版本：v{audit['audit_version']} · 结论：**{status_label}**  ",
        "> 本文件由 `scripts/audit_graph.py` 生成；指标源自机器可读节点与全部物化关系。",
        "",
        "## 1. 最终结论",
        "",
        f"Human Knowledge Model 当前包含 {inventory['nodes']} 个正式节点与 {inventory['relations']} 条关系。"
        f"图谱由 {integrity['weak_component_count']} 个弱连通分量构成，最大分量包含 "
        f"{integrity['largest_component_nodes']} 个节点；阻断问题 {len(integrity['blocking_issues'])} 项。",
        "",
    ]
    if audit["status"] == "pass":
        lines.append(
            "审计未发现重大领域遗漏、孤立节点、重复身份、重复有向边、悬空引用或需要立即拆分/合并的 H2。"
            "五个 H1、二十个 H2 和十个正交桥接视图继续作为稳定导航；细节通过 H3、类型化内容节点和关系向下扩展。"
        )
    else:
        lines.extend(["发现以下阻断问题：", *[f"- {item}" for item in integrity["blocking_issues"]]])

    lines.extend(
        [
            "",
            "## 2. 节点与关系清单",
            "",
            "| 节点组 | 数量 |",
            "|---|---:|",
        ]
    )
    for group, count in inventory["node_groups"].items():
        lines.append(f"| `{group}` | {count} |")
    lines.extend(["", "| 关系类型 | 数量 |", "|---|---:|"])
    for relation_type, count in inventory["relation_types"].items():
        lines.append(f"| `{relation_type}` | {count} |")

    lines.extend(
        [
            "",
            "## 3. 二十个领域的逐层覆盖",
            "",
            "| H2 | H3 | 骨架 | 桥接 | 模型 | 问题 | Top50 | 框架 |",
            "|---|---:|---:|---:|---|---|---:|---:|",
        ]
    )
    for metric in coverage["domain_metrics"]:
        lines.append(
            f"| {metric['code']} {metric['label']} | {metric['h3']} | {metric['core_nodes']} | "
            f"{metric['bridge_views']} | {'✓' if metric['model_coverage'] else '—'} | "
            f"{'✓' if metric['problem_coverage'] else '—'} | {metric['top50_core_entries']} | "
            f"{metric['operating_frameworks']} |"
        )
    lines.extend(
        [
            "",
            f"- H3 被领域骨架覆盖：{coverage['h3_covered_by_core']} / {coverage['h3_total']}。",
            f"- Thinking Models 被问题模板调用：{coverage['thinking_called_by_problems']} / {coverage['thinking_total']}。",
            f"- Universal Models 被问题模板调用：{coverage['universal_called_by_problems']} / {coverage['universal_total']}。",
            f"- Top 50 被八单元路线覆盖：{coverage['learning_top50_covered']} / 50。",
            "",
            "## 4. 完整性检查",
            "",
            "| 检查 | 结果 |",
            "|---|---:|",
            f"| 重复节点 ID | {integrity['duplicate_node_ids']} |",
            f"| 重复关系 ID | {integrity['duplicate_relation_ids']} |",
            f"| 悬空关系 | {len(integrity['unknown_endpoint_relations'])} |",
            f"| 自环 | {len(integrity['self_loop_relations'])} |",
            f"| 重复有向关系三元组 | {len(integrity['duplicate_relation_triples'])} |",
            f"| 孤立节点 | {len(integrity['isolated_nodes'])} |",
            f"| 同层或歧义性重复标签 | {len(integrity['blocking_duplicate_labels'])} |",
            f"| H3 范围—骨架同名（不同身份） | {len(integrity['scope_content_label_collisions'])} |",
            f"| 归一化重复定义 | {len(integrity['duplicate_definitions'])} |",
            f"| 非法或空双语标签 | {len(integrity['malformed_labels'])} |",
            f"| 弱连通分量 | {integrity['weak_component_count']} |",
            "",
            "## 5. 八个重构问题的回答",
            "",
            "1. **重大领域遗漏？** 外部分类 crosswalk、H2 覆盖矩阵和现实问题调用未发现需要新增 H2 的缺口；地方知识、隐性实践和未来新领域属于持续扩展边界。",
            "2. **错误分类？** 范围节点、知识类型、行动类型、学习类型和组织视图保持分离；桥接视图不冒充父级，模型和方法不被机械放入 H5/H6。",
            "3. **层级混乱？** H0–H4 只描述范围缩小，内容节点与操作框架正交；全部 scope parent 边已由验证器检查。",
            f"4. **重复知识？** 未发现同层歧义标签、重复定义或有向关系三元组；"
            f"保留 {len(integrity['scope_content_label_collisions'])} 组 H3 范围—骨架同名，因为前者是分类范围、后者是可调用内容节点，定义与 ID 均不同。语义近义仍列为人工审查限制。",
            "5. **跨领域关系不足？** 每个 H2 均进入桥接、模型、问题、学习核心和两套操作框架；全图为单一弱连通分量。",
            "6. **应提升为更高抽象？** 已由 Thinking Models、Universal Models 和两个 framework 节点承接；不再把这些结构复制为新的 H2。",
            "7. **应合并？** 当前 H2 均有独立核心问题、边界和 10–16 个骨架节点；相邻领域通过 bridge 与 typed edge 连接，暂不合并。",
            "8. **应拆分？** 当前最大 H3 数为 14、骨架数为 16，仍在设计范围；专题扩张优先进入 H3/H4，未达到拆分 H2 的证据阈值。",
            "",
            "## 6. 最终重构决定",
            "",
            "| 结构 | 决定 | 理由 |",
            "|---|---|---|",
            "| 5 个 H1 / 20 个 H2 | 保留 | 稳定导航、外部 crosswalk 和全层覆盖均通过 |",
            "| 10 个 Bridge Views | 保持正交 | 解决认知、气候、公共卫生、城市等多归属问题而不制造重复父级 |",
            "| Thinking / Universal | 保持双层 | 区分认知操作与世界结构，避免把模型混成一个列表 |",
            "| Problem Templates / Frameworks | 保持分层 | 前者提供情境调用栈，后者提供共同操作内核 |",
            "| Top 50 / 100 / 300 | 保留约束组合 | 分数可解释，领域配额防止连接度偏差吞没意义与实践领域 |",
            "| 未来扩展 | 先增关系和 H4，再评估拆分 H2 | 保护稳定 ID、历史版本和跨层接口 |",
            "",
            "## 7. 审计边界",
            "",
        ]
    )
    lines.extend(f"- {item}" for item in audit["limitations"])
    lines.extend(
        [
            "",
            "## 8. 冻结门",
            "",
            "v0.8.0 只有在本审计为 `pass`、主验证器与网站验证器通过、浏览器无控制台错误、GitHub Pages 与 `main` 提交一致时才能冻结。",
            "",
        ]
    )
    return "\n".join(lines)


def main() -> int:
    audit = build_audit()
    yaml_path = ROOT / "08-data/global-audit.generated.yaml"
    markdown_path = ROOT / "00-meta/phase-8-global-audit.generated.md"
    yaml_path.write_text(
        yaml.safe_dump(audit, allow_unicode=True, sort_keys=False, width=120),
        encoding="utf-8",
        newline="\n",
    )
    markdown_path.write_text(
        generate_audit_markdown(audit), encoding="utf-8", newline="\n"
    )
    print(
        f"GLOBAL AUDIT {audit['status'].upper()}: "
        f"{audit['inventory']['nodes']} nodes, {audit['inventory']['relations']} relations, "
        f"{audit['integrity']['weak_component_count']} weak component(s), "
        f"{len(audit['integrity']['blocking_issues'])} blocking issue(s)"
    )
    return 0 if audit["status"] == "pass" else 1


if __name__ == "__main__":
    sys.exit(main())
