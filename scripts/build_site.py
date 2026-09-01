"""Build the dependency-free GitHub Pages site from HKM YAML sources."""

from __future__ import annotations

import json
import shutil
from pathlib import Path

import yaml


ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "site"
OUTPUT = ROOT / "dist-site"


def load_yaml(relative_path: str) -> dict:
    return yaml.safe_load((ROOT / relative_path).read_text(encoding="utf-8"))


def compact_scope(node: dict) -> dict:
    return {
        key: node[key]
        for key in (
            "id",
            "code",
            "level",
            "parent",
            "labels",
            "definition",
            "core_questions",
            "scope_includes",
            "boundary_notes",
            "bridge_domains",
            "epistemic_modes",
            "status",
            "version",
        )
        if key in node
    }


def compact_bridge(node: dict) -> dict:
    return {
        key: node[key]
        for key in (
            "id",
            "code",
            "labels",
            "definition",
            "core_questions",
            "member_domains",
            "members",
            "unifying_mechanisms",
            "boundary_notes",
            "epistemic_modes",
            "status",
            "version",
        )
    }


def compact_core(node: dict) -> dict:
    return {
        key: node[key]
        for key in (
            "id",
            "code",
            "primary_type",
            "additional_types",
            "labels",
            "definition",
            "core_questions",
            "primary_domain",
            "related_subdomains",
            "roles",
            "aims",
            "epistemic_modes",
            "learning_priority",
            "prerequisites",
            "connections",
            "boundary_notes",
            "status",
            "version",
        )
        if key in node
    }


def compact_thinking_model(node: dict) -> dict:
    return {
        key: node[key]
        for key in (
            "id",
            "code",
            "primary_type",
            "labels",
            "definition",
            "core_idea",
            "source_domains",
            "mechanism_core_nodes",
            "applicable_problems",
            "typical_cases",
            "counterexamples",
            "boundary_notes",
            "common_misuses",
            "related_models",
            "learning_priority",
            "epistemic_modes",
            "status",
            "version",
        )
    }


def compact_universal_model(node: dict) -> dict:
    return {
        key: node[key]
        for key in (
            "id",
            "code",
            "primary_type",
            "labels",
            "definition",
            "core_structure",
            "state_variables",
            "dynamics",
            "manifestations",
            "failure_modes",
            "boundary_notes",
            "related_models",
            "learning_priority",
            "epistemic_modes",
            "status",
            "version",
        )
    }


def compact_problem_template(node: dict) -> dict:
    return {
        key: node[key]
        for key in (
            "id",
            "code",
            "primary_type",
            "labels",
            "definition",
            "problem_family",
            "primary_aim",
            "secondary_aims",
            "trigger_questions",
            "success_criteria",
            "scoping_dimensions",
            "knowledge_calls",
            "evidence_requirements",
            "workflow",
            "outputs",
            "failure_modes",
            "escalation_conditions",
            "boundary_notes",
            "example_prompts",
            "learning_priority",
            "status",
            "version",
        )
    }


def compact_learning_path(node: dict) -> dict:
    return {
        key: node[key]
        for key in (
            "id",
            "code",
            "primary_type",
            "labels",
            "definition",
            "stage_units",
            "tier_cycles",
            "branch_routes",
            "route_rules",
            "boundary_notes",
            "status",
            "version",
        )
    }


def compact_learning_unit(node: dict) -> dict:
    return {
        key: node[key]
        for key in (
            "id",
            "code",
            "primary_type",
            "labels",
            "definition",
            "sequence",
            "prerequisites",
            "focus_assets",
            "practice_problems",
            "learning_outcomes",
            "exercises",
            "exit_evidence",
            "estimated_hours",
            "boundary_notes",
            "status",
            "version",
        )
    }


def compact_framework(node: dict) -> dict:
    return {
        key: node[key]
        for key in (
            "id",
            "code",
            "primary_type",
            "framework_kind",
            "labels",
            "definition",
            "entry_questions",
            "components",
            "outputs",
            "gates",
            "escalation_conditions",
            "related_frameworks",
            "applies_to_problem_templates",
            "boundary_notes",
            "status",
            "version",
        )
    }


def build_payload() -> dict:
    domain_data = load_yaml("08-data/domains.yaml")
    subdomain_data = load_yaml("08-data/subdomains.yaml")
    bridge_data = load_yaml("08-data/bridges.yaml")
    core_data = load_yaml("08-data/core-nodes.yaml")
    thinking_data = load_yaml("08-data/thinking-models.yaml")
    universal_data = load_yaml("08-data/universal-models.yaml")
    problem_data = load_yaml("08-data/problem-templates.yaml")
    priority_data = load_yaml("08-data/learning-priorities.generated.yaml")
    roadmap_data = load_yaml("08-data/learning-roadmap.yaml")
    framework_data = load_yaml("08-data/frameworks.yaml")
    relation_files = [
        "08-data/relationships.yaml",
        "08-data/hierarchy-relationships.generated.yaml",
        "08-data/bridge-relationships.generated.yaml",
        "08-data/core-relationships.generated.yaml",
        "08-data/model-relationships.generated.yaml",
        "08-data/problem-relationships.generated.yaml",
        "08-data/learning-relationships.generated.yaml",
        "08-data/framework-relationships.generated.yaml",
    ]
    relations = [
        relation
        for path in relation_files
        for relation in load_yaml(path)["relationships"]
    ]
    superdomains = [compact_scope(node) for node in domain_data["superdomains"]]
    domains = [compact_scope(node) for node in domain_data["domains"]]
    subdomains = [compact_scope(node) for node in subdomain_data["subdomains"]]
    bridges = [compact_bridge(node) for node in bridge_data["bridge_views"]]
    core_nodes = [compact_core(node) for node in core_data["core_nodes"]]
    thinking_models = [
        compact_thinking_model(node) for node in thinking_data["thinking_models"]
    ]
    universal_models = [
        compact_universal_model(node) for node in universal_data["universal_models"]
    ]
    problem_templates = [
        compact_problem_template(node) for node in problem_data["problem_templates"]
    ]
    learning_path = compact_learning_path(roadmap_data["learning_path"])
    learning_units = [
        compact_learning_unit(node) for node in roadmap_data["learning_units"]
    ]
    learning_priorities = priority_data["entries"]
    frameworks = [compact_framework(node) for node in framework_data["frameworks"]]
    domain_ids = {domain["id"] for domain in domains}
    domain_relations = [
        relation
        for relation in relations
        if relation["source"] in domain_ids and relation["target"] in domain_ids
    ]
    return {
        "meta": {
            "id": "human-knowledge-model",
            "version": framework_data["model_version"],
            "generatedFrom": [
                "08-data/domains.yaml",
                "08-data/subdomains.yaml",
                "08-data/bridges.yaml",
                "08-data/core-nodes.yaml",
                "08-data/thinking-models.yaml",
                "08-data/universal-models.yaml",
                "08-data/problem-templates.yaml",
                "08-data/learning-priorities.generated.yaml",
                "08-data/learning-roadmap.yaml",
                "08-data/frameworks.yaml",
            ],
            "counts": {
                "superdomains": len(superdomains),
                "domains": len(domains),
                "subdomains": len(subdomains),
                "bridges": len(bridges),
                "coreNodes": len(core_nodes),
                "thinkingModels": len(thinking_models),
                "universalModels": len(universal_models),
                "problemTemplates": len(problem_templates),
                "learningCandidates": len(learning_priorities),
                "learningUnits": len(learning_units),
                "frameworks": len(frameworks),
                "relations": len(relations),
            },
        },
        "root": compact_scope(domain_data["root"]),
        "superdomains": superdomains,
        "domains": domains,
        "subdomains": subdomains,
        "bridges": bridges,
        "coreNodes": core_nodes,
        "thinkingModels": thinking_models,
        "universalModels": universal_models,
        "problemTemplates": problem_templates,
        "learningPriorities": learning_priorities,
        "learningPath": learning_path,
        "learningUnits": learning_units,
        "frameworks": frameworks,
        "domainRelations": domain_relations,
    }


def main() -> None:
    expected_output = (ROOT / "dist-site").resolve()
    if OUTPUT.resolve() != expected_output or OUTPUT.parent.resolve() != ROOT.resolve():
        raise RuntimeError("Refusing to clean an unexpected output path")
    if OUTPUT.exists():
        shutil.rmtree(OUTPUT)
    shutil.copytree(SOURCE, OUTPUT)
    data_dir = OUTPUT / "data"
    data_dir.mkdir(parents=True, exist_ok=True)
    payload = build_payload()
    (data_dir / "model.json").write_text(
        json.dumps(payload, ensure_ascii=False, separators=(",", ":")),
        encoding="utf-8",
        newline="\n",
    )
    (OUTPUT / ".nojekyll").write_text("", encoding="utf-8")
    print(
        "SITE BUILD OK: "
        f"{payload['meta']['counts']['domains']} domains, "
        f"{payload['meta']['counts']['subdomains']} subdomains, "
        f"{payload['meta']['counts']['bridges']} bridge views, "
        f"{payload['meta']['counts']['coreNodes']} core nodes, "
        f"{payload['meta']['counts']['thinkingModels']} thinking models, "
        f"{payload['meta']['counts']['universalModels']} universal models, "
        f"{payload['meta']['counts']['problemTemplates']} problem templates, "
        f"{payload['meta']['counts']['learningCandidates']} learning candidates, "
        f"{payload['meta']['counts']['learningUnits']} learning units, "
        f"{payload['meta']['counts']['frameworks']} operating frameworks, "
        f"{payload['meta']['counts']['relations']} relations"
    )


if __name__ == "__main__":
    main()
