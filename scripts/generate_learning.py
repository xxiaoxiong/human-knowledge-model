"""Generate auditable individual-learning priorities from the HKM graph."""

from __future__ import annotations

import math
from collections import defaultdict
from pathlib import Path

import yaml


ROOT = Path(__file__).resolve().parents[1]


def load_yaml(relative_path: str) -> dict:
    return yaml.safe_load((ROOT / relative_path).read_text(encoding="utf-8"))


def text_cell(value: object) -> str:
    return str(value).replace("|", "\\|").replace("\n", " ")


def calculate_learning_priorities(
    domain_data: dict,
    core_data: dict,
    thinking_data: dict,
    universal_data: dict,
    problem_data: dict,
) -> dict:
    domains = {item["id"]: item for item in domain_data["domains"]}
    core_nodes = core_data["core_nodes"]
    thinking_models = thinking_data["thinking_models"]
    universal_models = universal_data["universal_models"]
    problems = problem_data["problem_templates"]
    all_assets = [
        *[("core-node", item) for item in core_nodes],
        *[("thinking-model", item) for item in thinking_models],
        *[("universal-model", item) for item in universal_models],
    ]
    asset_by_id = {item["id"]: item for _, item in all_assets}
    core_by_id = {item["id"]: item for item in core_nodes}

    dependents: dict[str, set[str]] = {item["id"]: set() for item in core_nodes}
    for node in core_nodes:
        for prerequisite in node["prerequisites"]:
            dependents[prerequisite].add(node["id"])

    dependent_cache: dict[str, set[str]] = {}

    def transitive_dependents(node_id: str) -> set[str]:
        if node_id in dependent_cache:
            return dependent_cache[node_id]
        result: set[str] = set()
        for child_id in dependents[node_id]:
            result.add(child_id)
            result.update(transitive_dependents(child_id))
        dependent_cache[node_id] = result
        return result

    uses: dict[str, list[dict]] = defaultdict(list)
    for problem in problems:
        calls = problem["knowledge_calls"]
        for group in ("core_nodes", "thinking_models", "universal_models"):
            for asset_id in calls[group]:
                uses[asset_id].append(problem)

    priority_points = {"S": 30.0, "A": 24.0, "B": 16.0, "C": 8.0, "D": 2.0}
    daily_problem_ids = {
        "hkm:problem-template:decide-under-uncertainty",
        "hkm:problem-template:manage-risk-crisis-recovery",
        "hkm:problem-template:make-health-medical-decision",
        "hkm:problem-template:learn-teach-skill",
        "hkm:problem-template:personal-life-career-plan",
    }
    entries: list[dict] = []
    for asset_type, asset in all_assets:
        used_by = {problem["id"]: problem for problem in uses[asset["id"]]}
        problem_value = min(
            32.0,
            sum(4.0 if problem["learning_priority"] == "S" else 2.5 for problem in used_by.values()),
        )
        dependent_count = (
            len(transitive_dependents(asset["id"])) if asset_type == "core-node" else 0
        )
        prerequisite_leverage = min(20.0, 4.0 * math.sqrt(dependent_count))

        if asset_type == "core-node":
            reach_domains = {asset["primary_domain"]}
            for connection in asset["connections"]:
                target = core_by_id.get(connection["target"])
                if target:
                    reach_domains.add(target["primary_domain"])
        elif asset_type == "thinking-model":
            reach_domains = set(asset["source_domains"])
        else:
            reach_domains = {item["domain"] for item in asset["manifestations"]}
        cross_domain_reach = min(18.0, 2.6 * len(reach_domains))

        risk_uses = sum(
            problem["problem_family"] == "risk-response" for problem in used_by.values()
        )
        daily_uses = sum(problem_id in daily_problem_ids for problem_id in used_by)
        everyday_bonus = (
            4.0
            if asset_type == "core-node"
            and asset["primary_domain"] == "hkm:domain:everyday-life-practical-agency"
            else 0.0
        )
        risk_daily_value = min(15.0, risk_uses * 4.0 + daily_uses * 2.0 + everyday_bonus)
        epistemic_breadth = min(8.0, 2.0 * len(asset.get("epistemic_modes", [])))
        components = {
            "foundational_priority": priority_points[asset["learning_priority"]],
            "problem_coverage": problem_value,
            "prerequisite_leverage": round(prerequisite_leverage, 2),
            "cross_domain_reach": round(cross_domain_reach, 2),
            "risk_daily_value": risk_daily_value,
            "epistemic_breadth": epistemic_breadth,
        }
        raw_score = round(sum(components.values()), 2)
        entries.append(
            {
                "node_id": asset["id"],
                "code": asset["code"],
                "labels": asset["labels"],
                "asset_type": asset_type,
                "inherited_priority": asset["learning_priority"],
                "raw_score": raw_score,
                "score_components": components,
                "problem_count": len(used_by),
                "problem_templates": sorted(
                    (problem["code"] for problem in used_by.values())
                ),
                "dependent_count": dependent_count,
                "domain_count": len(reach_domains),
                "domains": sorted(domains[item]["code"] for item in reach_domains),
                "selection_basis": [],
            }
        )

    by_id = {entry["node_id"]: entry for entry in entries}
    raw_order = sorted(entries, key=lambda item: (-item["raw_score"], item["code"]))
    by_type = {
        asset_type: [item for item in raw_order if item["asset_type"] == asset_type]
        for asset_type in ("core-node", "thinking-model", "universal-model")
    }

    def mark(entry: dict, basis: str) -> None:
        if basis not in entry["selection_basis"]:
            entry["selection_basis"].append(basis)

    selected_50: set[str] = set()
    for domain_id in domains:
        candidates = [
            entry
            for entry in by_type["core-node"]
            if core_by_id[entry["node_id"]]["primary_domain"] == domain_id
        ]
        chosen = candidates[0]
        selected_50.add(chosen["node_id"])
        mark(chosen, "top50-domain-coverage")
    for entry in by_type["core-node"]:
        if sum(by_id[item]["asset_type"] == "core-node" for item in selected_50) >= 28:
            break
        selected_50.add(entry["node_id"])
        mark(entry, "top50-core-depth")
    for entry in by_type["thinking-model"][:14]:
        selected_50.add(entry["node_id"])
        mark(entry, "top50-thinking-floor")
    for entry in by_type["universal-model"][:8]:
        selected_50.add(entry["node_id"])
        mark(entry, "top50-universal-floor")

    selected_100 = set(selected_50)
    for domain_id in domains:
        candidates = [
            entry
            for entry in by_type["core-node"]
            if core_by_id[entry["node_id"]]["primary_domain"] == domain_id
        ][:2]
        for entry in candidates:
            selected_100.add(entry["node_id"])
            mark(entry, "top100-two-per-domain")
    for entry in by_type["core-node"]:
        if sum(by_id[item]["asset_type"] == "core-node" for item in selected_100) >= 60:
            break
        selected_100.add(entry["node_id"])
        mark(entry, "top100-core-depth")
    for entry in by_type["thinking-model"][:25]:
        selected_100.add(entry["node_id"])
        mark(entry, "top100-thinking-floor")
    for entry in by_type["universal-model"][:15]:
        selected_100.add(entry["node_id"])
        mark(entry, "top100-universal-floor")

    selected_300 = set(selected_100)
    for entry in raw_order:
        if len(selected_300) >= 300:
            break
        if entry["node_id"] not in selected_300:
            selected_300.add(entry["node_id"])
            mark(entry, "top300-score-fill")

    tranche_50 = sorted(
        (by_id[item] for item in selected_50),
        key=lambda item: (-item["raw_score"], item["code"]),
    )
    tranche_100 = sorted(
        (by_id[item] for item in selected_100 - selected_50),
        key=lambda item: (-item["raw_score"], item["code"]),
    )
    tranche_300 = sorted(
        (by_id[item] for item in selected_300 - selected_100),
        key=lambda item: (-item["raw_score"], item["code"]),
    )
    outside = sorted(
        (entry for entry in entries if entry["node_id"] not in selected_300),
        key=lambda item: (-item["raw_score"], item["code"]),
    )
    ranked = [*tranche_50, *tranche_100, *tranche_300, *outside]
    component_labels = {
        "foundational_priority": "既有优先级",
        "problem_coverage": "问题覆盖",
        "prerequisite_leverage": "前置杠杆",
        "cross_domain_reach": "跨域广度",
        "risk_daily_value": "风险与日常价值",
        "epistemic_breadth": "认识方式广度",
    }
    for rank, entry in enumerate(ranked, start=1):
        entry["rank"] = rank
        entry["tier"] = (
            "Top50"
            if rank <= 50
            else "Top100"
            if rank <= 100
            else "Top300"
            if rank <= 300
            else "outside-top300"
        )
        dominant = sorted(
            entry["score_components"].items(), key=lambda item: (-item[1], item[0])
        )[:2]
        reasons = [f"{component_labels[key]} {value:g}" for key, value in dominant]
        if entry["problem_count"]:
            reasons.append(f"被 {entry['problem_count']} 个问题原型调用")
        if entry["dependent_count"]:
            reasons.append(f"支撑 {entry['dependent_count']} 个后续骨架节点")
        entry["selection_reasons"] = reasons

    return {
        "schema_version": "0.1.0",
        "model_version": "0.6.0",
        "generated_from": [
            "08-data/domains.yaml",
            "08-data/core-nodes.yaml",
            "08-data/thinking-models.yaml",
            "08-data/universal-models.yaml",
            "08-data/problem-templates.yaml",
        ],
        "method": {
            "name": "constrained-portfolio-ranking",
            "candidate_count": len(entries),
            "weights": {
                "foundational_priority": "S=30, A=24, B=16, C=8, D=2",
                "problem_coverage": "S 问题调用 4 分、A 问题调用 2.5 分，上限 32",
                "prerequisite_leverage": "4 × sqrt(传递后继数)，上限 20",
                "cross_domain_reach": "每个内在关联 H2 计 2.6 分，上限 18",
                "risk_daily_value": "风险问题 4 分、日常问题 2 分、D20 骨架加 4 分，上限 15",
                "epistemic_breadth": "每种认识方式 2 分，上限 8",
            },
            "guardrails": {
                "Top50": "28 个领域骨架（每个 H2 至少 1 个）、14 个 Thinking、8 个 Universal",
                "Top100": "60 个领域骨架（每个 H2 至少 2 个）、25 个 Thinking、15 个 Universal",
                "Top300": "保留 Top100 后按原始分补足 300；尾部 20 项仍保留审计",
            },
            "interpretation": "排名是有限学习时间下的覆盖组合，不是真理、学术质量或职业价值等级。",
        },
        "entries": ranked,
    }


def generate_core_knowledge_view(priority_data: dict) -> str:
    entries = priority_data["entries"]
    method = priority_data["method"]
    lines = [
        "# Core Knowledge for Individuals：个人核心知识 Top 50 / 100 / 300",
        "",
        "> 本文件由知识图谱结构和 `scripts/generate_learning.py` 计算生成。",
        "> 排名回答“有限通识时间先学什么”，不表示真理等级、学术地位或具体职业要求。",
        "",
        "## 方法",
        "",
        f"候选集合为 {method['candidate_count']} 项：257 个领域骨架节点、41 个 Thinking Models 与 22 个 Universal Models。",
        "原始分综合既有 S/A/B/C/D、问题覆盖、前置杠杆、跨域广度、风险与日常价值、认识方式广度；分层选择再施加领域与模型覆盖约束。",
        "",
        "| 分层 | 覆盖约束 |",
        "|---|---|",
        *[f"| {tier} | {rule} |" for tier, rule in method["guardrails"].items()],
        "",
        "Top 50 是共同底座；Top 100 在其上扩大各领域和模型深度；Top 300 面向长期通识。每一层包含前一层。",
    ]

    def append_table(title: str, selected: list[dict], note: str) -> None:
        lines.extend(
            [
                "",
                f"## {title}",
                "",
                note,
                "",
                "| 排名 | 代码 | 知识资产 | 类型 | 原优先级 | H2 | 问题 | 前置后继 | 分数 | 主要理由 |",
                "|---:|---|---|---|---:|---:|---:|---:|---:|---|",
            ]
        )
        for entry in selected:
            lines.append(
                f"| {entry['rank']} | {entry['code']} | "
                f"{text_cell(entry['labels']['zh'])}<br>{text_cell(entry['labels']['en'])} | "
                f"{entry['asset_type']} | {entry['inherited_priority']} | "
                f"{entry['domain_count']} | {entry['problem_count']} | "
                f"{entry['dependent_count']} | {entry['raw_score']:.2f} | "
                f"{text_cell('；'.join(entry['selection_reasons']))} |"
            )

    append_table(
        "Top 50：个人共同底座",
        [entry for entry in entries if entry["rank"] <= 50],
        "优先建立判断、证据、系统、风险、沟通、伦理和跨领域定位能力，并保证 20 个 H2 都有入口。",
    )
    append_table(
        "Top 100：可迁移通识核心（新增 51–100）",
        [entry for entry in entries if 51 <= entry["rank"] <= 100],
        "本表列新增 50 项；与 Top 50 合并即完整 Top 100。每个 H2 至少有两个核心骨架入口。",
    )
    append_table(
        "Top 300：长期通识网络（新增 101–300）",
        [entry for entry in entries if 101 <= entry["rank"] <= 300],
        "本表列新增 200 项；与前两层合并即完整 Top 300。它是可持续展开的网络，不建议按排名线性背诵。",
    )
    append_table(
        "Top 300 之外：尾部审计（301–320）",
        [entry for entry in entries if entry["rank"] > 300],
        "这些项目并非不重要，只是在一般个人通识的受约束组合中边际优先级较低；专业、地方或人生目标会改变排序。",
    )
    return "\n".join(lines) + "\n"


def generate_learning_roadmap_view(
    roadmap_data: dict, priority_data: dict, problem_data: dict
) -> str:
    path = roadmap_data["learning_path"]
    units = sorted(roadmap_data["learning_units"], key=lambda item: item["sequence"])
    assets = {item["node_id"]: item for item in priority_data["entries"]}
    problems = {item["id"]: item for item in problem_data["problem_templates"]}
    units_by_id = {item["id"]: item for item in units}
    lines = [
        "# 个人核心知识螺旋学习路线",
        "",
        "> 本文件由 `08-data/learning-roadmap.yaml` 与学习优先级生成数据构建。",
        "> 时间仅是一般成人自学估计；退出证据比小时数更重要。",
        "",
        path["definition"],
        "",
        "## Top 50 / 100 / 300 三轮扩展",
        "",
        "| 层 | 目标 | 选择规则 | 建议节奏 | 退出证据 |",
        "|---|---|---|---|---|",
    ]
    for cycle in path["tier_cycles"]:
        lines.append(
            f"| {cycle['tier']} | {text_cell(cycle['objective'])} | "
            f"{text_cell(cycle['selection_rule'])} | {text_cell(cycle['cadence'])} | "
            f"{text_cell(cycle['evidence'])} |"
        )
    lines.extend(
        [
            "",
            "## Top 50 八阶段共同底座",
            "",
            "| 阶段 | 单元 | 预计投入 | Top 50 资产 | 实践问题 |",
            "|---:|---|---:|---:|---:|",
        ]
    )
    top50_ids = {
        item["node_id"] for item in priority_data["entries"] if item["rank"] <= 50
    }
    for unit in units:
        top50_count = len(set(unit["focus_assets"]) & top50_ids)
        lines.append(
            f"| {unit['sequence']} | {unit['code']} {text_cell(unit['labels']['zh'])} | "
            f"{unit['estimated_hours']} | {top50_count} | {len(unit['practice_problems'])} |"
        )
    for unit in units:
        prerequisites = (
            "；".join(
                f"{units_by_id[item]['code']} {units_by_id[item]['labels']['zh']}"
                for item in unit["prerequisites"]
            )
            or "无"
        )
        focus = "；".join(
            f"#{assets[item]['rank']} {assets[item]['code']} {assets[item]['labels']['zh']}"
            for item in unit["focus_assets"]
        )
        practice = "；".join(
            f"{problems[item]['code']} {problems[item]['labels']['zh']}"
            for item in unit["practice_problems"]
        )
        lines.extend(
            [
                "",
                f"## {unit['code']} {unit['labels']['zh']} / {unit['labels']['en']}",
                "",
                unit["definition"],
                "",
                f"**建议投入：** {unit['estimated_hours']} 小时",
                "",
                f"**前置单元：** {prerequisites}",
                "",
                f"**核心资产：** {focus}",
                "",
                f"**实践问题：** {practice}",
                "",
                f"**学习结果：** {'；'.join(unit['learning_outcomes'])}",
                "",
                f"**练习：** {'；'.join(unit['exercises'])}",
                "",
                f"**退出证据：** {'；'.join(unit['exit_evidence'])}",
                "",
                f"**边界：** {unit['boundary_notes']}",
            ]
        )
    lines.extend(
        [
            "",
            "## Top 100 / 300 分支路线",
            "",
            "| 分支 | 重点 H2 | 锚定问题 |",
            "|---|---|---|",
        ]
    )
    problem_by_code = {item["code"]: item for item in problems.values()}
    for branch in path["branch_routes"]:
        problem_labels = "、".join(
            f"{code} {problem_by_code[code]['labels']['zh']}"
            for code in branch["anchor_problems"]
        )
        lines.append(
            f"| {branch['labels']['zh']}<br>{branch['labels']['en']} | "
            f"{'、'.join(branch['focus_domains'])} | {problem_labels} |"
        )
    lines.extend(
        [
            "",
            "## 路线规则",
            "",
            *[f"{index}. {rule}" for index, rule in enumerate(path["route_rules"], start=1)],
            "",
            f"**总边界：** {path['boundary_notes']}",
            "",
        ]
    )
    return "\n".join(lines)


def generate_learning_relations(
    roadmap_data: dict, priority_data: dict, problem_data: dict
) -> dict:
    path = roadmap_data["learning_path"]
    assets = {item["node_id"]: item for item in priority_data["entries"]}
    problems = {item["id"]: item for item in problem_data["problem_templates"]}
    units = {item["id"]: item for item in roadmap_data["learning_units"]}
    relationships: list[dict] = []

    def add(relation_id: str, source: str, relation_type: str, target: str, scope: str) -> None:
        relationships.append(
            {
                "id": relation_id,
                "source": source,
                "type": relation_type,
                "target": target,
                "scope": scope,
                "confidence": "high",
                "provenance": ["hkm:source:editorial-synthesis-v0-6"],
            }
        )

    for unit in sorted(units.values(), key=lambda item: item["sequence"]):
        prefix = unit["code"].lower()
        add(
            f"hkm:relation:{prefix}-member-lp01",
            unit["id"],
            "member-of",
            path["id"],
            "学习单元属于个人核心知识螺旋路线",
        )
        for prerequisite_id in unit["prerequisites"]:
            prerequisite = units[prerequisite_id]
            add(
                f"hkm:relation:{prerequisite['code'].lower()}-prerequisite-{prefix}",
                prerequisite_id,
                "prerequisite-of",
                unit["id"],
                "完成前置单元的退出证据后再进入后续单元",
            )
        for asset_id in unit["focus_assets"]:
            asset = assets[asset_id]
            add(
                f"hkm:relation:{prefix}-uses-{asset['code'].lower().replace('.', '-')}",
                unit["id"],
                "uses",
                asset_id,
                f"学习单元聚焦排名 {asset['rank']} 的知识资产",
            )
        for problem_id in unit["practice_problems"]:
            problem = problems[problem_id]
            add(
                f"hkm:relation:{prefix}-practice-{problem['code'].lower()}",
                unit["id"],
                "applies-to",
                problem_id,
                "用问题原型组织练习和退出作品",
            )
    return {
        "schema_version": "0.1.0",
        "model_version": roadmap_data["model_version"],
        "generated_from": [
            "08-data/learning-roadmap.yaml",
            "08-data/learning-priorities.generated.yaml",
            "08-data/problem-templates.yaml",
        ],
        "relationships": relationships,
    }


def main() -> None:
    priority_data = calculate_learning_priorities(
        load_yaml("08-data/domains.yaml"),
        load_yaml("08-data/core-nodes.yaml"),
        load_yaml("08-data/thinking-models.yaml"),
        load_yaml("08-data/universal-models.yaml"),
        load_yaml("08-data/problem-templates.yaml"),
    )
    yaml_path = ROOT / "08-data/learning-priorities.generated.yaml"
    yaml_path.write_text(
        yaml.safe_dump(priority_data, allow_unicode=True, sort_keys=False, width=120),
        encoding="utf-8",
        newline="\n",
    )
    markdown_path = ROOT / "06-learning/core-knowledge.generated.md"
    markdown_path.parent.mkdir(parents=True, exist_ok=True)
    markdown_path.write_text(
        generate_core_knowledge_view(priority_data), encoding="utf-8", newline="\n"
    )
    roadmap_data = load_yaml("08-data/learning-roadmap.yaml")
    problem_data = load_yaml("08-data/problem-templates.yaml")
    roadmap_path = ROOT / "06-learning/learning-roadmap.generated.md"
    roadmap_path.write_text(
        generate_learning_roadmap_view(roadmap_data, priority_data, problem_data),
        encoding="utf-8",
        newline="\n",
    )
    relation_data = generate_learning_relations(
        roadmap_data, priority_data, problem_data
    )
    (ROOT / "08-data/learning-relationships.generated.yaml").write_text(
        yaml.safe_dump(relation_data, allow_unicode=True, sort_keys=False, width=120),
        encoding="utf-8",
        newline="\n",
    )
    print(
        "LEARNING PRIORITIES OK: "
        f"{len(priority_data['entries'])} candidates, Top 50/100/300, "
        f"{len(roadmap_data['learning_units'])} learning units, "
        f"{len(relation_data['relationships'])} learning relations generated"
    )


if __name__ == "__main__":
    main()
