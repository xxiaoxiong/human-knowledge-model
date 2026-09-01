"""Generate callable framework views and materialized framework relations."""

from __future__ import annotations

from collections import defaultdict
from pathlib import Path

import yaml


ROOT = Path(__file__).resolve().parents[1]


def load_yaml(relative_path: str) -> dict:
    return yaml.safe_load((ROOT / relative_path).read_text(encoding="utf-8"))


def text_cell(value: object) -> str:
    return str(value).replace("|", "\\|").replace("\n", " ")


def generate_framework_view(
    framework: dict,
    domain_data: dict,
    thinking_data: dict,
    universal_data: dict,
) -> str:
    domains = {item["id"]: item for item in domain_data["domains"]}
    thinking = {item["id"]: item for item in thinking_data["thinking_models"]}
    universal = {item["id"]: item for item in universal_data["universal_models"]}
    components = sorted(framework["components"], key=lambda item: item["sequence"])
    title = framework["labels"]["zh"]
    lines = [
        f"# {title} / {framework['labels']['en']}",
        "",
        "> 本文件由 `08-data/frameworks.yaml` 生成。请修改数据源后运行 `python scripts/generate_views.py`。",
        f"> 版本：v{framework['version']} · 节点：`{framework['id']}`",
        "",
        framework["definition"],
        "",
        "## 进入框架前",
        "",
    ]
    lines.extend(f"{index}. {question}" for index, question in enumerate(framework["entry_questions"], 1))
    lines.extend(["", "## 全局结构", "", "```mermaid", "flowchart LR"])
    for index, component in enumerate(components):
        node_key = f"C{index + 1}"
        lines.append(f'    {node_key}["{component["sequence"]}. {component["labels"]["zh"]}"]')
        if index:
            lines.append(f"    C{index} --> {node_key}")
    if framework["framework_kind"] == "universal-problem-solving":
        lines.append("    C10 -->|结果反馈| C2")
    lines.extend(["```", ""])

    lines.extend(
        [
            "| 序号 | 透镜 / 阶段 | 目的 | 主要产物 |",
            "|---:|---|---|---|",
        ]
    )
    for component in components:
        lines.append(
            f"| {component['sequence']} | {text_cell(component['labels']['zh'])}<br>"
            f"{text_cell(component['labels']['en'])} | {text_cell(component['purpose'])} | "
            f"{text_cell(component['output'])} |"
        )

    if framework["framework_kind"] == "universal-problem-solving":
        lines.extend(
            [
                "",
                "## 按风险缩放，而不是机械走流程",
                "",
                "| 情境 | 建议深度 | 不可删除的检查 |",
                "|---|---|---|",
                "| 低风险、可逆、影响局部 | 合并相邻阶段，保留一页记录 | 安全、目标、证据、不行动选项、监测与复盘 |",
                "| 中等风险或多主体 | 完整十阶段，邀请不同视角审查 | 权限、受影响者、竞争解释、情景、撤销条件 |",
                "| 高风险、不可逆或受监管 | 由合格专业和正式治理流程主导 | 紧急分诊、法定权限、独立审查、冗余、停止与升级 |",
            ]
        )
    else:
        lines.extend(
            [
                "",
                "## 使用方式",
                "",
                "先用十个透镜做宽扫描，再按问题风险和信息价值选择 3–6 个透镜深入。每个被暂缓的透镜都要留下理由；发现高风险、不可逆性、权利冲突或关键未知时，转入通用问题求解框架并提高流程深度。",
            ]
        )

    lines.extend(["", "## 逐项调用", ""])
    for component in components:
        domain_labels = " / ".join(
            f"{domains[item]['code']} {domains[item]['labels']['zh']}"
            for item in component["domains"]
        )
        thinking_labels = " / ".join(
            f"{thinking[item]['code']} {thinking[item]['labels']['zh']}"
            for item in component["thinking_models"]
        )
        universal_labels = " / ".join(
            f"{universal[item]['code']} {universal[item]['labels']['zh']}"
            for item in component["universal_models"]
        )
        lines.extend(
            [
                f"### {component['sequence']}. {component['labels']['zh']} / {component['labels']['en']}",
                "",
                component["purpose"],
                "",
                "**检查问题**",
                "",
                *[f"- {question}" for question in component["questions"]],
                "",
                f"**领域入口：** {domain_labels}",
                "",
                f"**Thinking Models：** {thinking_labels}",
                "",
                f"**Universal Models：** {universal_labels}",
                "",
                f"**退出产物：** {component['output']}",
                "",
            ]
        )

    lines.extend(["## 质量门", ""])
    lines.extend(f"- {gate}" for gate in framework["gates"])
    lines.extend(["", "## 完整输出", ""])
    lines.extend(f"- {output}" for output in framework["outputs"])
    lines.extend(["", "## 停止与升级", ""])
    lines.extend(f"- {condition}" for condition in framework["escalation_conditions"])
    lines.extend(["", "## 边界", "", framework["boundary_notes"], ""])
    return "\n".join(lines)


def generate_framework_relations(framework_data: dict) -> dict:
    frameworks = framework_data["frameworks"]
    relations: list[dict] = []
    relation_keys: set[tuple[str, str, str]] = set()
    code_by_id = {framework["id"]: framework["code"] for framework in frameworks}

    for framework in frameworks:
        calls_by_target: dict[str, list[str]] = defaultdict(list)
        for component in framework["components"]:
            for field in ("domains", "thinking_models", "universal_models"):
                for target in component[field]:
                    calls_by_target[target].append(component["labels"]["zh"])
        for target, scopes in sorted(calls_by_target.items()):
            target_slug = target.removeprefix("hkm:").replace(":", "-")
            relation = {
                "id": f"hkm:relation:{framework['code'].lower()}-uses-{target_slug}",
                "source": framework["id"],
                "type": "uses",
                "target": target,
                "scope": f"{framework['code']} 在 {'、'.join(scopes)} 中调用该知识入口",
                "confidence": "high",
                "provenance": ["hkm:source:framework-synthesis-v0-7"],
            }
            key = (relation["source"], relation["type"], relation["target"])
            if key not in relation_keys:
                relations.append(relation)
                relation_keys.add(key)
        for target in framework["applies_to_problem_templates"]:
            target_slug = target.removeprefix("hkm:").replace(":", "-")
            relation = {
                "id": f"hkm:relation:{framework['code'].lower()}-applies-{target_slug}",
                "source": framework["id"],
                "type": "applies-to",
                "target": target,
                "scope": f"{framework['code']} 为该问题原型提供通用操作闭环",
                "confidence": "high",
                "provenance": ["hkm:source:framework-synthesis-v0-7"],
            }
            key = (relation["source"], relation["type"], relation["target"])
            if key not in relation_keys:
                relations.append(relation)
                relation_keys.add(key)

    seen_pairs: set[tuple[str, str]] = set()
    for framework in frameworks:
        for target in framework["related_frameworks"]:
            pair = tuple(sorted((framework["id"], target)))
            if pair in seen_pairs:
                continue
            seen_pairs.add(pair)
            source_code = code_by_id[framework["id"]].lower()
            target_code = code_by_id[target].lower()
            relations.append(
                {
                    "id": f"hkm:relation:{source_code}-complements-{target_code}",
                    "source": framework["id"],
                    "type": "complements",
                    "target": target,
                    "scope": "多维透镜负责扩展观察空间，问题求解闭环负责生成、授权、监测和更新行动",
                    "confidence": "high",
                    "provenance": ["hkm:source:framework-synthesis-v0-7"],
                }
            )

    return {
        "schema_version": "0.1.0",
        "model_version": framework_data["model_version"],
        "generated_from": [
            "08-data/frameworks.yaml",
            "08-data/domains.yaml",
            "08-data/thinking-models.yaml",
            "08-data/universal-models.yaml",
            "08-data/problem-templates.yaml",
        ],
        "relationships": relations,
    }


def main() -> None:
    framework_data = load_yaml("08-data/frameworks.yaml")
    domain_data = load_yaml("08-data/domains.yaml")
    thinking_data = load_yaml("08-data/thinking-models.yaml")
    universal_data = load_yaml("08-data/universal-models.yaml")
    output_dir = ROOT / "07-frameworks"
    output_dir.mkdir(parents=True, exist_ok=True)
    filenames = {
        "multidimensional-thinking": "multidimensional-thinking-framework.md",
        "universal-problem-solving": "universal-problem-solving-framework.md",
    }
    for framework in framework_data["frameworks"]:
        path = output_dir / filenames[framework["framework_kind"]]
        path.write_text(
            generate_framework_view(framework, domain_data, thinking_data, universal_data),
            encoding="utf-8",
            newline="\n",
        )
    relation_data = generate_framework_relations(framework_data)
    (ROOT / "08-data/framework-relationships.generated.yaml").write_text(
        yaml.safe_dump(relation_data, allow_unicode=True, sort_keys=False, width=120),
        encoding="utf-8",
        newline="\n",
    )
    print(
        f"FRAMEWORK BUILD OK: {len(framework_data['frameworks'])} frameworks, "
        f"{sum(len(item['components']) for item in framework_data['frameworks'])} components, "
        f"{len(relation_data['relationships'])} relations"
    )


if __name__ == "__main__":
    main()
