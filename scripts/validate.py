"""Validate the structural invariants of the Human Knowledge Model."""

from __future__ import annotations

import re
import sys
from pathlib import Path

import yaml

from audit_graph import build_audit, generate_audit_markdown
from generate_frameworks import generate_framework_relations, generate_framework_view
from generate_learning import (
    calculate_learning_priorities,
    generate_core_knowledge_view,
    generate_learning_relations,
    generate_learning_roadmap_view,
)

from generate_views import (
    generate_bridge_relations,
    generate_bridge_views,
    generate_cross_model_relations,
    generate_problem_mapping_view,
    generate_problem_relations,
    generate_core_relations,
    generate_core_skeletons,
    generate_crosswalk,
    generate_hierarchy_relations,
    generate_map,
    generate_thinking_model_view,
    generate_universal_model_view,
)


ROOT = Path(__file__).resolve().parents[1]


def load_yaml(relative_path: str) -> dict:
    with (ROOT / relative_path).open(encoding="utf-8") as stream:
        return yaml.safe_load(stream)


def normalize_identity_text(value: str) -> str:
    """Normalize human-facing identity text for exact duplicate checks."""

    return re.sub(r"[^\w]+", "", value.casefold(), flags=re.UNICODE)


def main() -> int:
    schema = load_yaml("08-data/schema.yaml")
    domain_data = load_yaml("08-data/domains.yaml")
    subdomain_data = load_yaml("08-data/subdomains.yaml")
    crosswalk_data = load_yaml("08-data/crosswalks.yaml")
    bridge_data = load_yaml("08-data/bridges.yaml")
    core_data = load_yaml("08-data/core-nodes.yaml")
    thinking_data = load_yaml("08-data/thinking-models.yaml")
    universal_data = load_yaml("08-data/universal-models.yaml")
    problem_data = load_yaml("08-data/problem-templates.yaml")
    priority_data = load_yaml("08-data/learning-priorities.generated.yaml")
    roadmap_data = load_yaml("08-data/learning-roadmap.yaml")
    framework_data = load_yaml("08-data/frameworks.yaml")
    relation_data = load_yaml("08-data/relationships.yaml")
    hierarchy_data = load_yaml("08-data/hierarchy-relationships.generated.yaml")
    bridge_relation_data = load_yaml("08-data/bridge-relationships.generated.yaml")
    core_relation_data = load_yaml("08-data/core-relationships.generated.yaml")
    model_relation_data = load_yaml("08-data/model-relationships.generated.yaml")
    problem_relation_data = load_yaml("08-data/problem-relationships.generated.yaml")
    learning_relation_data = load_yaml("08-data/learning-relationships.generated.yaml")
    framework_relation_data = load_yaml("08-data/framework-relationships.generated.yaml")
    global_audit_data = load_yaml("08-data/global-audit.generated.yaml")
    errors: list[str] = []

    subdomains = subdomain_data["subdomains"]
    bridge_views = bridge_data["bridge_views"]
    core_nodes = core_data["core_nodes"]
    thinking_models = thinking_data["thinking_models"]
    universal_models = universal_data["universal_models"]
    problem_templates = problem_data["problem_templates"]
    learning_path = roadmap_data["learning_path"]
    learning_units = roadmap_data["learning_units"]
    frameworks = framework_data["frameworks"]
    scope_nodes = [
        domain_data["root"],
        *domain_data["superdomains"],
        *domain_data["domains"],
        *subdomains,
    ]
    nodes = [
        *scope_nodes,
        *bridge_views,
        *core_nodes,
        *thinking_models,
        *universal_models,
        *problem_templates,
        learning_path,
        *learning_units,
        *frameworks,
    ]
    node_ids = [node["id"] for node in nodes]
    node_id_set = set(node_ids)

    if len(node_ids) != len(node_id_set):
        errors.append("duplicate node IDs")
    if len(domain_data["superdomains"]) != 5:
        errors.append("the v0.1 map must contain exactly 5 H1 superdomains")
    if len(domain_data["domains"]) != 20:
        errors.append("the v0.1 map must contain exactly 20 H2 domains")
    expected_codes = {f"D{number:02d}" for number in range(1, 21)}
    actual_codes = {domain["code"] for domain in domain_data["domains"]}
    if actual_codes != expected_codes:
        errors.append("domain codes must be exactly D01 through D20")

    domain_code_by_id = {
        domain["id"]: domain["code"] for domain in domain_data["domains"]
    }
    h3_counts = {code: 0 for code in expected_codes}
    seen_h3_codes: set[str] = set()
    allowed_modes = set(schema["facets"]["epistemic_modes"])
    for subdomain in subdomains:
        code = subdomain["code"]
        if code in seen_h3_codes:
            errors.append(f"duplicate H3 code: {code}")
        seen_h3_codes.add(code)
        if subdomain["parent"] not in domain_code_by_id:
            errors.append(f"{code}: H3 parent is not an H2 domain")
            continue
        parent_code = domain_code_by_id[subdomain["parent"]]
        if not code.startswith(f"{parent_code}."):
            errors.append(f"{code}: code does not match parent {parent_code}")
        h3_counts[parent_code] += 1
        invalid_modes = set(subdomain["epistemic_modes"]) - allowed_modes
        if invalid_modes:
            errors.append(f"{code}: invalid epistemic modes {sorted(invalid_modes)}")
        invalid_bridges = set(subdomain["bridge_domains"]) - expected_codes
        if invalid_bridges:
            errors.append(f"{code}: invalid bridge domains {sorted(invalid_bridges)}")
    for code, count in sorted(h3_counts.items()):
        if count < 8:
            errors.append(f"{code}: expected at least 8 H3 subdomains, got {count}")

    required_bridge = set(schema["required_bridge_fields"])
    expected_bridge_codes = {f"B{number:02d}" for number in range(1, 11)}
    actual_bridge_codes = {bridge["code"] for bridge in bridge_views}
    if actual_bridge_codes != expected_bridge_codes:
        errors.append("bridge codes must be exactly B01 through B10 in v0.2-draft")
    subdomains_by_id = {item["id"]: item for item in subdomains}
    seen_bridge_memberships: set[tuple[str, str]] = set()
    for bridge in bridge_views:
        missing = required_bridge - bridge.keys()
        if missing:
            errors.append(f"{bridge.get('id')}: missing bridge fields {sorted(missing)}")
            continue
        if bridge["primary_type"] != "bridge-view":
            errors.append(f"{bridge['id']}: primary_type must be bridge-view")
        invalid_domains = set(bridge["member_domains"]) - expected_codes
        if invalid_domains:
            errors.append(
                f"{bridge['code']}: invalid member domains {sorted(invalid_domains)}"
            )
        if len(set(bridge["member_domains"])) < 3:
            errors.append(f"{bridge['code']}: bridge view must connect at least 3 H2 domains")
        if len(bridge["members"]) != len(set(bridge["members"])):
            errors.append(f"{bridge['code']}: duplicate H3 members")
        if len(bridge["members"]) < 5:
            errors.append(f"{bridge['code']}: bridge view must contain at least 5 H3 members")
        unknown_members = set(bridge["members"]) - set(subdomains_by_id)
        if unknown_members:
            errors.append(f"{bridge['code']}: unknown H3 members {sorted(unknown_members)}")
        represented_domains = {
            domain_code_by_id[subdomains_by_id[member_id]["parent"]]
            for member_id in bridge["members"]
            if member_id in subdomains_by_id
        }
        if represented_domains != set(bridge["member_domains"]):
            errors.append(
                f"{bridge['code']}: member_domains do not match member parents "
                f"({sorted(represented_domains)} != {sorted(bridge['member_domains'])})"
            )
        invalid_modes = set(bridge["epistemic_modes"]) - allowed_modes
        if invalid_modes:
            errors.append(
                f"{bridge['code']}: invalid epistemic modes {sorted(invalid_modes)}"
            )
        for member_id in bridge["members"]:
            membership = (member_id, bridge["id"])
            if membership in seen_bridge_memberships:
                errors.append(f"duplicate bridge membership: {member_id} -> {bridge['id']}")
            seen_bridge_memberships.add(membership)

    coverage_sentinels = {
        "hkm:subdomain:comparative-philosophy-knowledge-traditions": "跨知识传统",
        "hkm:subdomain:social-cultural-anthropology": "社会文化人类学",
        "hkm:subdomain:indigenous-local-cosmologies": "原住民与地方宇宙观",
        "hkm:subdomain:nursing-care-practice": "护理与照护实践",
        "hkm:subdomain:home-household-maintenance-repair": "家庭维护维修",
        "hkm:subdomain:physical-literacy-sport-recreation": "身体素养与运动",
        "hkm:subdomain:craft-making-creative-hobbies": "手工制作",
        "hkm:subdomain:vocational-workplace-professional-learning": "职业与工作场所学习",
    }
    for sentinel_id, description in coverage_sentinels.items():
        if sentinel_id not in node_id_set:
            errors.append(f"coverage sentinel missing: {description} ({sentinel_id})")

    allowed_relations = {
        relation_type
        for group in schema["relation_types"].values()
        for relation_type in group
    }
    allowed_node_types = {
        node_type for group in schema["node_types"].values() for node_type in group
    }
    required_node = set(schema["required_node_fields"])
    required_core = set(schema["required_core_node_fields"])
    allowed_roles = set(schema["facets"]["skeleton_roles"])
    allowed_aims = set(schema["facets"]["aims"])
    allowed_priorities = set(schema["facets"]["learning_priority"])
    core_ids = {node["id"] for node in core_nodes}
    published_domains = set(core_data["published_domains"])
    invalid_published_domains = published_domains - expected_codes
    if invalid_published_domains:
        errors.append(
            f"invalid published core domains: {sorted(invalid_published_domains)}"
        )
    core_counts: dict[str, int] = {code: 0 for code in published_domains}
    core_priorities: dict[str, set[str]] = {
        code: set() for code in published_domains
    }
    seen_core_codes: set[str] = set()
    seen_core_labels: dict[tuple[str, str], str] = {}
    seen_core_definitions: dict[str, str] = {}
    prereq_graph: dict[str, list[str]] = {node_id: [] for node_id in core_ids}
    for node in core_nodes:
        missing = required_core - node.keys()
        if missing:
            errors.append(f"{node.get('id')}: missing core fields {sorted(missing)}")
            continue
        if node["primary_type"] not in allowed_node_types:
            errors.append(f"{node['code']}: invalid primary type {node['primary_type']}")
        invalid_additional_types = set(node.get("additional_types", [])) - allowed_node_types
        if invalid_additional_types:
            errors.append(
                f"{node['code']}: invalid additional types {sorted(invalid_additional_types)}"
            )
        if node["code"] in seen_core_codes:
            errors.append(f"duplicate core code: {node['code']}")
        seen_core_codes.add(node["code"])
        label_locales = set(node["labels"])
        if label_locales != {"zh", "en"}:
            errors.append(
                f"{node['code']}: labels must contain exactly zh and en, "
                f"got {sorted(str(locale) for locale in label_locales)}"
            )
        for locale in ("zh", "en"):
            if locale not in node["labels"]:
                continue
            normalized_label = normalize_identity_text(node["labels"][locale])
            label_key = (locale, normalized_label)
            if label_key in seen_core_labels:
                errors.append(
                    f"duplicate normalized {locale} core label: "
                    f"{seen_core_labels[label_key]} and {node['code']}"
                )
            seen_core_labels[label_key] = node["code"]
        normalized_definition = normalize_identity_text(node["definition"])
        if normalized_definition in seen_core_definitions:
            errors.append(
                "duplicate normalized core definition: "
                f"{seen_core_definitions[normalized_definition]} and {node['code']}"
            )
        seen_core_definitions[normalized_definition] = node["code"]
        if node["primary_domain"] not in domain_code_by_id:
            errors.append(f"{node['code']}: invalid primary domain {node['primary_domain']}")
            continue
        core_domain_code = domain_code_by_id[node["primary_domain"]]
        if core_domain_code not in published_domains:
            errors.append(
                f"{node['code']}: domain {core_domain_code} is not in published_domains"
            )
        expected_prefix = f"K{core_domain_code[1:]}."
        if not node["code"].startswith(expected_prefix):
            errors.append(
                f"{node['code']}: core code does not match domain {core_domain_code}"
            )
        core_counts.setdefault(core_domain_code, 0)
        core_counts[core_domain_code] += 1
        core_priorities.setdefault(core_domain_code, set()).add(node["learning_priority"])
        invalid_scopes = set(node["related_subdomains"]) - set(subdomains_by_id)
        if invalid_scopes:
            errors.append(f"{node['code']}: unknown H3 scopes {sorted(invalid_scopes)}")
        wrong_parent_scopes = [
            subdomain_id
            for subdomain_id in node["related_subdomains"]
            if subdomain_id in subdomains_by_id
            and subdomains_by_id[subdomain_id]["parent"] != node["primary_domain"]
        ]
        if wrong_parent_scopes:
            errors.append(
                f"{node['code']}: H3 scopes outside primary domain "
                f"{sorted(wrong_parent_scopes)}"
            )
        if not node["related_subdomains"]:
            errors.append(f"{node['code']}: expected at least one H3 scope")
        invalid_roles = set(node["roles"]) - allowed_roles
        if invalid_roles:
            errors.append(f"{node['code']}: invalid roles {sorted(invalid_roles)}")
        invalid_aims = set(node["aims"]) - allowed_aims
        if invalid_aims:
            errors.append(f"{node['code']}: invalid aims {sorted(invalid_aims)}")
        invalid_core_modes = set(node["epistemic_modes"]) - allowed_modes
        if invalid_core_modes:
            errors.append(
                f"{node['code']}: invalid epistemic modes {sorted(invalid_core_modes)}"
            )
        if node["learning_priority"] not in allowed_priorities:
            errors.append(
                f"{node['code']}: invalid learning priority {node['learning_priority']}"
            )
        unknown_prerequisites = set(node["prerequisites"]) - core_ids
        if unknown_prerequisites:
            errors.append(
                f"{node['code']}: unknown prerequisites {sorted(unknown_prerequisites)}"
            )
        for prerequisite in node["prerequisites"]:
            if prerequisite in prereq_graph:
                prereq_graph[prerequisite].append(node["id"])
        if not node["connections"]:
            errors.append(f"{node['code']}: expected at least one core connection")
        for connection in node["connections"]:
            if connection.get("type") not in allowed_relations:
                errors.append(
                    f"{node['code']}: invalid connection type {connection.get('type')}"
                )
            if connection.get("target") not in core_ids:
                errors.append(
                    f"{node['code']}: unknown connection target {connection.get('target')}"
                )
            if not connection.get("scope"):
                errors.append(f"{node['code']}: connection missing scope")
    if set(core_counts) != published_domains:
        errors.append("published_domains do not exactly match core node domains")
    for code, count in sorted(core_counts.items()):
        if not 10 <= count <= 30:
            errors.append(f"{code}: core skeleton must contain 10-30 nodes, got {count}")
        if not (core_priorities[code] & {"B", "C", "D"}):
            errors.append(f"{code}: S/A cannot cover every core node")
        domain_id = next(
            domain_id
            for domain_id, domain_code in domain_code_by_id.items()
            if domain_code == code
        )
        expected_h3_scope = {
            subdomain["id"]
            for subdomain in subdomains
            if subdomain["parent"] == domain_id
        }
        covered_h3_scope = {
            subdomain_id
            for node in core_nodes
            if node["primary_domain"] == domain_id
            for subdomain_id in node["related_subdomains"]
        }
        missing_h3_scope = expected_h3_scope - covered_h3_scope
        if missing_h3_scope:
            errors.append(
                f"{code}: core skeleton leaves H3 scopes uncovered "
                f"{sorted(missing_h3_scope)}"
            )

    required_thinking = required_node | set(
        schema["required_thinking_model_fields"]
    )
    required_universal = required_node | set(
        schema["required_universal_model_fields"]
    )
    all_model_nodes = [*thinking_models, *universal_models]
    all_model_ids = {model["id"] for model in all_model_nodes}
    core_by_id = {node["id"]: node for node in core_nodes}
    domain_ids = set(domain_code_by_id)
    domain_parent = {
        domain["id"]: domain["parent"] for domain in domain_data["domains"]
    }
    seen_model_labels: dict[tuple[str, str], str] = {}
    seen_model_definitions: dict[str, str] = {}
    for node in core_nodes:
        for locale in ("zh", "en"):
            seen_model_labels[(locale, normalize_identity_text(node["labels"][locale]))] = (
                node["code"]
            )
        seen_model_definitions[normalize_identity_text(node["definition"])] = node[
            "code"
        ]

    def validate_model_identity(model: dict, required: set[str]) -> None:
        missing = required - model.keys()
        if missing:
            errors.append(f"{model.get('id')}: missing model fields {sorted(missing)}")
            return
        if set(model["labels"]) != {"zh", "en"}:
            errors.append(f"{model['code']}: labels must contain exactly zh and en")
        for locale in ("zh", "en"):
            if locale not in model["labels"]:
                continue
            key = (locale, normalize_identity_text(model["labels"][locale]))
            if key in seen_model_labels:
                errors.append(
                    f"duplicate normalized {locale} model label: "
                    f"{seen_model_labels[key]} and {model['code']}"
                )
            seen_model_labels[key] = model["code"]
        definition_key = normalize_identity_text(model["definition"])
        if definition_key in seen_model_definitions:
            errors.append(
                "duplicate normalized model definition: "
                f"{seen_model_definitions[definition_key]} and {model['code']}"
            )
        seen_model_definitions[definition_key] = model["code"]
        if model["primary_type"] not in allowed_node_types:
            errors.append(
                f"{model['code']}: invalid model primary type {model['primary_type']}"
            )
        if model["learning_priority"] not in allowed_priorities:
            errors.append(
                f"{model['code']}: invalid learning priority {model['learning_priority']}"
            )
        invalid_modes = set(model["epistemic_modes"]) - allowed_modes
        if invalid_modes:
            errors.append(
                f"{model['code']}: invalid epistemic modes {sorted(invalid_modes)}"
            )
        if not model["boundary_notes"]:
            errors.append(f"{model['code']}: model boundary must not be empty")
        for relation in model["related_models"]:
            if relation.get("type") not in allowed_relations:
                errors.append(
                    f"{model['code']}: invalid model relation {relation.get('type')}"
                )
            if relation.get("target") not in all_model_ids:
                errors.append(
                    f"{model['code']}: unknown related model {relation.get('target')}"
                )
            if not relation.get("scope"):
                errors.append(f"{model['code']}: model relation missing scope")

    expected_thinking_codes = {
        f"TM{number:02d}" for number in range(1, len(thinking_models) + 1)
    }
    actual_thinking_codes = {model["code"] for model in thinking_models}
    if actual_thinking_codes != expected_thinking_codes:
        errors.append("thinking model codes must be contiguous from TM01")
    thinking_covered_domains: set[str] = set()
    for model in thinking_models:
        validate_model_identity(model, required_thinking)
        thinking_covered_domains.update(model["source_domains"])
        if len(set(model["source_domains"])) < 2:
            errors.append(f"{model['code']}: expected at least two source H2 domains")
        unknown_domains = set(model["source_domains"]) - domain_ids
        if unknown_domains:
            errors.append(
                f"{model['code']}: unknown source domains {sorted(unknown_domains)}"
            )
        if len(set(model["mechanism_core_nodes"])) < 2:
            errors.append(f"{model['code']}: expected at least two mechanism anchors")
        unknown_anchors = set(model["mechanism_core_nodes"]) - set(core_by_id)
        if unknown_anchors:
            errors.append(
                f"{model['code']}: unknown mechanism anchors {sorted(unknown_anchors)}"
            )
        anchored_domains = {
            core_by_id[anchor]["primary_domain"]
            for anchor in model["mechanism_core_nodes"]
            if anchor in core_by_id
        }
        unanchored_sources = set(model["source_domains"]) - anchored_domains
        if unanchored_sources:
            errors.append(
                f"{model['code']}: source domains without mechanism anchors "
                f"{sorted(unanchored_sources)}"
            )
        if len(model["applicable_problems"]) < 2:
            errors.append(f"{model['code']}: expected multiple applicable problems")
        if not model["typical_cases"] or not model["counterexamples"]:
            errors.append(f"{model['code']}: expected cases and counterexamples")
        if len(model["common_misuses"]) < 2:
            errors.append(f"{model['code']}: expected multiple common misuses")
        if not model["related_models"]:
            errors.append(f"{model['code']}: expected at least one model relation")
    if thinking_covered_domains != domain_ids:
        errors.append(
            "thinking models must collectively touch all H2 domains; missing "
            f"{sorted(domain_ids - thinking_covered_domains)}"
        )

    expected_universal_codes = {
        f"UM{number:02d}" for number in range(1, len(universal_models) + 1)
    }
    actual_universal_codes = {model["code"] for model in universal_models}
    if actual_universal_codes != expected_universal_codes:
        errors.append("universal model codes must be contiguous from UM01")
    universal_covered_domains: set[str] = set()
    for model in universal_models:
        validate_model_identity(model, required_universal)
        manifestation_domains = {
            item["domain"] for item in model["manifestations"]
        }
        universal_covered_domains.update(manifestation_domains)
        if len(manifestation_domains) < 4:
            errors.append(f"{model['code']}: expected manifestations in four H2 domains")
        unknown_domains = manifestation_domains - domain_ids
        if unknown_domains:
            errors.append(
                f"{model['code']}: unknown manifestation domains {sorted(unknown_domains)}"
            )
        superdomains = {
            domain_parent[domain_id]
            for domain_id in manifestation_domains
            if domain_id in domain_parent
        }
        if len(superdomains) < 3:
            errors.append(f"{model['code']}: expected manifestations across three H1s")
        for manifestation in model["manifestations"]:
            if not manifestation.get("expression"):
                errors.append(f"{model['code']}: manifestation missing expression")
            if not manifestation.get("core_nodes"):
                errors.append(f"{model['code']}: manifestation missing core anchors")
            for core_id in manifestation.get("core_nodes", []):
                if core_id not in core_by_id:
                    errors.append(f"{model['code']}: unknown core anchor {core_id}")
                elif core_by_id[core_id]["primary_domain"] != manifestation["domain"]:
                    errors.append(
                        f"{model['code']}: core anchor {core_id} is outside "
                        f"manifestation domain {manifestation['domain']}"
                    )
        if len(model["state_variables"]) < 3 or len(model["dynamics"]) < 3:
            errors.append(f"{model['code']}: expected explicit state and dynamics")
        if len(model["failure_modes"]) < 2:
            errors.append(f"{model['code']}: expected multiple failure modes")
        if not model["related_models"]:
            errors.append(f"{model['code']}: expected at least one model relation")
    if universal_covered_domains != domain_ids:
        errors.append(
            "universal models must collectively manifest in all H2 domains; missing "
            f"{sorted(domain_ids - universal_covered_domains)}"
        )

    required_problem = required_node | set(
        schema["required_problem_template_fields"]
    )
    allowed_problem_families = set(schema["facets"]["problem_families"])
    expected_problem_codes = {
        f"PT{number:02d}" for number in range(1, len(problem_templates) + 1)
    }
    actual_problem_codes = {problem["code"] for problem in problem_templates}
    if len(problem_templates) != 20:
        errors.append(f"phase 5 must contain 20 problem templates, got {len(problem_templates)}")
    if actual_problem_codes != expected_problem_codes:
        errors.append("problem template codes must be contiguous from PT01")
    problem_covered_domains: set[str] = set()
    problem_covered_thinking: set[str] = set()
    problem_covered_universal: set[str] = set()
    family_counts: dict[str, int] = {family: 0 for family in allowed_problem_families}
    expected_scoping_keys = {
        "objects",
        "actors",
        "timescales",
        "scales",
        "values_at_stake",
        "constraints",
    }
    expected_call_keys = {
        "domains",
        "core_nodes",
        "thinking_models",
        "universal_models",
    }
    required_workflow_keys = {"stage", "action", "output", "gate"}
    for problem in problem_templates:
        missing = required_problem - problem.keys()
        if missing:
            errors.append(
                f"{problem.get('id')}: missing problem fields {sorted(missing)}"
            )
            continue
        if problem["primary_type"] != "problem-template":
            errors.append(
                f"{problem['code']}: primary_type must be problem-template"
            )
        if set(problem["labels"]) != {"zh", "en"}:
            errors.append(f"{problem['code']}: labels must contain exactly zh and en")
        for locale in ("zh", "en"):
            if locale not in problem["labels"]:
                continue
            key = (locale, normalize_identity_text(problem["labels"][locale]))
            if key in seen_model_labels:
                errors.append(
                    f"duplicate normalized {locale} problem label: "
                    f"{seen_model_labels[key]} and {problem['code']}"
                )
            seen_model_labels[key] = problem["code"]
        definition_key = normalize_identity_text(problem["definition"])
        if definition_key in seen_model_definitions:
            errors.append(
                "duplicate normalized problem definition: "
                f"{seen_model_definitions[definition_key]} and {problem['code']}"
            )
        seen_model_definitions[definition_key] = problem["code"]
        if problem["problem_family"] not in allowed_problem_families:
            errors.append(
                f"{problem['code']}: invalid problem family {problem['problem_family']}"
            )
        else:
            family_counts[problem["problem_family"]] += 1
        if problem["primary_aim"] not in allowed_aims:
            errors.append(
                f"{problem['code']}: invalid primary aim {problem['primary_aim']}"
            )
        invalid_secondary = set(problem["secondary_aims"]) - allowed_aims
        if invalid_secondary:
            errors.append(
                f"{problem['code']}: invalid secondary aims {sorted(invalid_secondary)}"
            )
        if len(set(problem["secondary_aims"])) < 2:
            errors.append(f"{problem['code']}: expected at least two secondary aims")
        if problem["primary_aim"] in problem["secondary_aims"]:
            errors.append(f"{problem['code']}: primary aim repeated as secondary")
        if problem["learning_priority"] not in allowed_priorities:
            errors.append(
                f"{problem['code']}: invalid learning priority {problem['learning_priority']}"
            )
        if len(problem["trigger_questions"]) < 3:
            errors.append(f"{problem['code']}: expected at least three trigger questions")
        if len(problem["success_criteria"]) < 3:
            errors.append(f"{problem['code']}: expected at least three success criteria")
        if set(problem["scoping_dimensions"]) != expected_scoping_keys:
            errors.append(f"{problem['code']}: incomplete scoping dimensions")
        for key, values in problem["scoping_dimensions"].items():
            if not isinstance(values, list) or len(values) < 2:
                errors.append(f"{problem['code']}: scoping dimension {key} is too thin")
        calls = problem["knowledge_calls"]
        if set(calls) != expected_call_keys:
            errors.append(f"{problem['code']}: knowledge_calls must contain four layers")
            continue
        problem_covered_domains.update(calls["domains"])
        problem_covered_thinking.update(calls["thinking_models"])
        problem_covered_universal.update(calls["universal_models"])
        if len(set(calls["domains"])) < 3:
            errors.append(f"{problem['code']}: expected at least three H2 calls")
        if len(set(calls["core_nodes"])) < 3:
            errors.append(f"{problem['code']}: expected at least three core calls")
        if len(set(calls["thinking_models"])) < 4:
            errors.append(f"{problem['code']}: expected at least four thinking models")
        if len(set(calls["universal_models"])) < 3:
            errors.append(f"{problem['code']}: expected at least three universal models")
        unknown_domains = set(calls["domains"]) - domain_ids
        unknown_cores = set(calls["core_nodes"]) - set(core_by_id)
        unknown_thinking = set(calls["thinking_models"]) - {
            model["id"] for model in thinking_models
        }
        unknown_universal = set(calls["universal_models"]) - {
            model["id"] for model in universal_models
        }
        if unknown_domains:
            errors.append(f"{problem['code']}: unknown domains {sorted(unknown_domains)}")
        if unknown_cores:
            errors.append(f"{problem['code']}: unknown core nodes {sorted(unknown_cores)}")
        if unknown_thinking:
            errors.append(
                f"{problem['code']}: unknown thinking models {sorted(unknown_thinking)}"
            )
        if unknown_universal:
            errors.append(
                f"{problem['code']}: unknown universal models {sorted(unknown_universal)}"
            )
        unscoped_cores = {
            core_id
            for core_id in calls["core_nodes"]
            if core_id in core_by_id
            and core_by_id[core_id]["primary_domain"] not in calls["domains"]
        }
        if unscoped_cores:
            errors.append(
                f"{problem['code']}: core calls outside declared domains "
                f"{sorted(unscoped_cores)}"
            )
        if len(problem["evidence_requirements"]) < 3:
            errors.append(f"{problem['code']}: expected at least three evidence gates")
        if len(problem["workflow"]) < 5:
            errors.append(f"{problem['code']}: workflow must contain at least five stages")
        actual_stages = [step.get("stage") for step in problem["workflow"]]
        expected_stages = [f"{number:02d}" for number in range(1, len(actual_stages) + 1)]
        if actual_stages != expected_stages:
            errors.append(f"{problem['code']}: workflow stages must be contiguous")
        for step in problem["workflow"]:
            if set(step) != required_workflow_keys or any(
                not step.get(key) for key in required_workflow_keys
            ):
                errors.append(f"{problem['code']}: workflow step is incomplete")
        if len(problem["outputs"]) < 3:
            errors.append(f"{problem['code']}: expected at least three outputs")
        if len(problem["failure_modes"]) < 3:
            errors.append(f"{problem['code']}: expected at least three failure modes")
        if len(problem["escalation_conditions"]) < 2:
            errors.append(f"{problem['code']}: expected escalation conditions")
        if len(problem["example_prompts"]) < 2:
            errors.append(f"{problem['code']}: expected at least two example prompts")
        if not problem["boundary_notes"]:
            errors.append(f"{problem['code']}: problem boundary must not be empty")
    if problem_covered_domains != domain_ids:
        errors.append(
            "problem templates must collectively call all H2 domains; missing "
            f"{sorted(domain_ids - problem_covered_domains)}"
        )
    if problem_covered_thinking != {model["id"] for model in thinking_models}:
        errors.append(
            "problem templates must collectively call all thinking models; missing "
            f"{sorted({model['id'] for model in thinking_models} - problem_covered_thinking)}"
        )
    if problem_covered_universal != {model["id"] for model in universal_models}:
        errors.append(
            "problem templates must collectively call all universal models; missing "
            f"{sorted({model['id'] for model in universal_models} - problem_covered_universal)}"
        )
    thin_families = {family: count for family, count in family_counts.items() if count < 2}
    if thin_families:
        errors.append(f"problem families need at least two templates: {thin_families}")
    required_pressure_tests = {
        "hkm:problem-template:assess-company-investment",
        "hkm:problem-template:assess-new-technology-success",
        "hkm:problem-template:assess-social-policy-impact",
    }
    if not required_pressure_tests <= {problem["id"] for problem in problem_templates}:
        errors.append("missing company, technology, or social-policy pressure test")

    expected_priority_data = calculate_learning_priorities(
        domain_data, core_data, thinking_data, universal_data, problem_data
    )
    if priority_data != expected_priority_data:
        errors.append("learning-priorities.generated.yaml is stale; run generate_views.py")
    priority_entries = priority_data["entries"]
    expected_asset_ids = {
        *core_ids,
        *{model["id"] for model in thinking_models},
        *{model["id"] for model in universal_models},
    }
    ranked_asset_ids = [entry["node_id"] for entry in priority_entries]
    if len(priority_entries) != 320:
        errors.append(f"learning ranking must contain 320 assets, got {len(priority_entries)}")
    if set(ranked_asset_ids) != expected_asset_ids:
        errors.append("learning ranking candidates do not exactly match core and model assets")
    if len(ranked_asset_ids) != len(set(ranked_asset_ids)):
        errors.append("learning ranking contains duplicate assets")
    if [entry["rank"] for entry in priority_entries] != list(range(1, 321)):
        errors.append("learning ranks must be contiguous from 1 through 320")
    expected_type_counts = {
        50: {"core-node": 28, "thinking-model": 14, "universal-model": 8},
        100: {"core-node": 60, "thinking-model": 25, "universal-model": 15},
        300: {"core-node": 237, "thinking-model": 41, "universal-model": 22},
    }
    for limit, expected_counts_for_tier in expected_type_counts.items():
        actual_counts_for_tier = {
            asset_type: sum(
                entry["asset_type"] == asset_type for entry in priority_entries[:limit]
            )
            for asset_type in expected_counts_for_tier
        }
        if actual_counts_for_tier != expected_counts_for_tier:
            errors.append(
                f"Top {limit} asset allocation mismatch: {actual_counts_for_tier}"
            )
    top50_core_domains = {
        code
        for entry in priority_entries[:50]
        if entry["asset_type"] == "core-node"
        for code in entry["domains"]
    }
    if top50_core_domains != expected_codes:
        errors.append(
            f"Top 50 core assets must cover all H2 domains; missing "
            f"{sorted(expected_codes - top50_core_domains)}"
        )
    for entry in priority_entries:
        component_total = round(sum(entry["score_components"].values()), 2)
        if component_total != entry["raw_score"]:
            errors.append(f"{entry['code']}: learning score components do not sum")
        expected_tier = (
            "Top50"
            if entry["rank"] <= 50
            else "Top100"
            if entry["rank"] <= 100
            else "Top300"
            if entry["rank"] <= 300
            else "outside-top300"
        )
        if entry["tier"] != expected_tier:
            errors.append(f"{entry['code']}: incorrect learning tier")
        if not entry["selection_reasons"]:
            errors.append(f"{entry['code']}: ranking needs selection reasons")
        if entry["rank"] <= 300 and not entry["selection_basis"]:
            errors.append(f"{entry['code']}: selected tier needs a selection basis")

    required_learning_path = required_node | set(
        schema["required_learning_path_fields"]
    )
    required_learning_unit = required_node | set(
        schema["required_learning_unit_fields"]
    )
    missing_path_fields = required_learning_path - learning_path.keys()
    if missing_path_fields:
        errors.append(
            f"{learning_path.get('id')}: missing learning path fields "
            f"{sorted(missing_path_fields)}"
        )
    if learning_path.get("primary_type") != "learning-path":
        errors.append("LP01 primary_type must be learning-path")
    if learning_path.get("code") != "LP01":
        errors.append("the individual learning path must use code LP01")
    for locale in ("zh", "en"):
        if locale in learning_path.get("labels", {}):
            key = (
                locale,
                normalize_identity_text(learning_path["labels"][locale]),
            )
            if key in seen_model_labels:
                errors.append(
                    f"duplicate normalized {locale} learning label: "
                    f"{seen_model_labels[key]} and LP01"
                )
            seen_model_labels[key] = "LP01"
    path_definition_key = normalize_identity_text(learning_path.get("definition", ""))
    if path_definition_key in seen_model_definitions:
        errors.append("duplicate normalized learning path definition")
    seen_model_definitions[path_definition_key] = "LP01"

    learning_unit_ids = {unit["id"] for unit in learning_units}
    expected_unit_codes = {
        f"LU{number:02d}" for number in range(1, len(learning_units) + 1)
    }
    if len(learning_units) != 8:
        errors.append(f"learning roadmap must contain eight units, got {len(learning_units)}")
    if {unit["code"] for unit in learning_units} != expected_unit_codes:
        errors.append("learning unit codes must be contiguous from LU01")
    ordered_units = sorted(learning_units, key=lambda item: item["sequence"])
    if [unit["sequence"] for unit in ordered_units] != list(range(1, 9)):
        errors.append("learning unit sequences must be contiguous from 1 through 8")
    if learning_path.get("stage_units") != [unit["id"] for unit in ordered_units]:
        errors.append("LP01 stage_units must match learning unit sequence")
    if {cycle.get("tier") for cycle in learning_path.get("tier_cycles", [])} != {
        "Top50",
        "Top100",
        "Top300",
    }:
        errors.append("LP01 tier cycles must describe Top50, Top100, and Top300")
    branch_ids: set[str] = set()
    problem_codes = {problem["code"] for problem in problem_templates}
    for branch in learning_path.get("branch_routes", []):
        if branch.get("id") in branch_ids:
            errors.append(f"duplicate learning branch ID {branch.get('id')}")
        branch_ids.add(branch.get("id"))
        invalid_focus_domains = set(branch.get("focus_domains", [])) - expected_codes
        invalid_anchor_problems = set(branch.get("anchor_problems", [])) - problem_codes
        if invalid_focus_domains:
            errors.append(
                f"learning branch {branch.get('id')}: invalid domains "
                f"{sorted(invalid_focus_domains)}"
            )
        if invalid_anchor_problems:
            errors.append(
                f"learning branch {branch.get('id')}: invalid problems "
                f"{sorted(invalid_anchor_problems)}"
            )
    if len(branch_ids) < 4:
        errors.append("LP01 needs at least four Top100/300 branch routes")

    top50_ids = {entry["node_id"] for entry in priority_entries[:50]}
    focused_assets: set[str] = set()
    problem_ids = {problem["id"] for problem in problem_templates}
    learning_prereq_graph: dict[str, list[str]] = {
        unit_id: [] for unit_id in learning_unit_ids
    }
    unit_by_id = {unit["id"]: unit for unit in learning_units}
    for unit in learning_units:
        missing = required_learning_unit - unit.keys()
        if missing:
            errors.append(f"{unit.get('id')}: missing learning fields {sorted(missing)}")
            continue
        if unit["primary_type"] != "learning-unit":
            errors.append(f"{unit['code']}: primary_type must be learning-unit")
        if set(unit["labels"]) != {"zh", "en"}:
            errors.append(f"{unit['code']}: labels must contain exactly zh and en")
        for locale in ("zh", "en"):
            if locale not in unit["labels"]:
                continue
            key = (locale, normalize_identity_text(unit["labels"][locale]))
            if key in seen_model_labels:
                errors.append(
                    f"duplicate normalized {locale} learning label: "
                    f"{seen_model_labels[key]} and {unit['code']}"
                )
            seen_model_labels[key] = unit["code"]
        definition_key = normalize_identity_text(unit["definition"])
        if definition_key in seen_model_definitions:
            errors.append(
                f"duplicate normalized learning definition: "
                f"{seen_model_definitions[definition_key]} and {unit['code']}"
            )
        seen_model_definitions[definition_key] = unit["code"]
        unknown_unit_prerequisites = set(unit["prerequisites"]) - learning_unit_ids
        if unknown_unit_prerequisites:
            errors.append(
                f"{unit['code']}: unknown learning prerequisites "
                f"{sorted(unknown_unit_prerequisites)}"
            )
        for prerequisite_id in unit["prerequisites"]:
            if prerequisite_id in unit_by_id:
                if unit_by_id[prerequisite_id]["sequence"] >= unit["sequence"]:
                    errors.append(f"{unit['code']}: prerequisite must be earlier")
                learning_prereq_graph[prerequisite_id].append(unit["id"])
        unknown_focus = set(unit["focus_assets"]) - expected_asset_ids
        if unknown_focus:
            errors.append(f"{unit['code']}: unknown focus assets {sorted(unknown_focus)}")
        if len(set(unit["focus_assets"])) < 5:
            errors.append(f"{unit['code']}: expected at least five focus assets")
        focused_assets.update(unit["focus_assets"])
        unknown_practice = set(unit["practice_problems"]) - problem_ids
        if unknown_practice:
            errors.append(
                f"{unit['code']}: unknown practice problems {sorted(unknown_practice)}"
            )
        if len(set(unit["practice_problems"])) < 3:
            errors.append(f"{unit['code']}: expected at least three practice problems")
        for field in ("learning_outcomes", "exercises", "exit_evidence"):
            if len(unit[field]) < 3:
                errors.append(f"{unit['code']}: {field} must contain three items")
        if not unit["estimated_hours"] or not unit["boundary_notes"]:
            errors.append(f"{unit['code']}: missing effort or boundary")
    if focused_assets != top50_ids:
        errors.append(
            "learning units must collectively focus exactly the Top 50 assets; "
            f"missing {sorted(top50_ids - focused_assets)}, "
            f"extra {sorted(focused_assets - top50_ids)}"
        )

    learning_state: dict[str, int] = {}

    def visit_learning_unit(unit_id: str) -> None:
        if learning_state.get(unit_id) == 1:
            errors.append(f"learning prerequisite cycle through {unit_id}")
            return
        if learning_state.get(unit_id) == 2:
            return
        learning_state[unit_id] = 1
        for successor_id in learning_prereq_graph[unit_id]:
            visit_learning_unit(successor_id)
        learning_state[unit_id] = 2

    for unit_id in learning_unit_ids:
        visit_learning_unit(unit_id)

    required_framework = required_node | set(schema["required_framework_fields"])
    framework_by_id = {framework["id"]: framework for framework in frameworks}
    framework_ids = set(framework_by_id)
    expected_framework_codes = {"FM01", "FM02"}
    if {framework["code"] for framework in frameworks} != expected_framework_codes:
        errors.append("framework codes must be exactly FM01 and FM02")
    if {framework["framework_kind"] for framework in frameworks} != {
        "multidimensional-thinking",
        "universal-problem-solving",
    }:
        errors.append("framework kinds must include thinking and problem-solving")
    component_ids: set[tuple[str, str]] = set()
    thinking_ids = {model["id"] for model in thinking_models}
    universal_ids = {model["id"] for model in universal_models}
    for framework in frameworks:
        missing = required_framework - framework.keys()
        if missing:
            errors.append(
                f"{framework.get('id')}: missing framework fields {sorted(missing)}"
            )
            continue
        if framework["primary_type"] != "framework":
            errors.append(f"{framework['code']}: primary_type must be framework")
        if set(framework["labels"]) != {"zh", "en"}:
            errors.append(f"{framework['code']}: labels must contain exactly zh and en")
        for locale in ("zh", "en"):
            if locale not in framework["labels"]:
                continue
            key = (locale, normalize_identity_text(framework["labels"][locale]))
            if key in seen_model_labels:
                errors.append(
                    f"duplicate normalized {locale} framework label: "
                    f"{seen_model_labels[key]} and {framework['code']}"
                )
            seen_model_labels[key] = framework["code"]
        definition_key = normalize_identity_text(framework["definition"])
        if definition_key in seen_model_definitions:
            errors.append(
                f"duplicate normalized framework definition: "
                f"{seen_model_definitions[definition_key]} and {framework['code']}"
            )
        seen_model_definitions[definition_key] = framework["code"]
        if len(framework["components"]) != 10:
            errors.append(f"{framework['code']}: expected exactly ten components")
        expected_sequences = (
            list(range(1, 11))
            if framework["framework_kind"] == "multidimensional-thinking"
            else list(range(0, 10))
        )
        components = sorted(framework["components"], key=lambda item: item["sequence"])
        if [component["sequence"] for component in components] != expected_sequences:
            errors.append(f"{framework['code']}: component sequence is not contiguous")
        called_domains: set[str] = set()
        called_thinking: set[str] = set()
        called_universal: set[str] = set()
        for component in components:
            component_key = (framework["id"], component.get("id", ""))
            if component_key in component_ids:
                errors.append(
                    f"{framework['code']}: duplicate component ID {component.get('id')}"
                )
            component_ids.add(component_key)
            missing_component = {
                "id",
                "sequence",
                "labels",
                "purpose",
                "questions",
                "domains",
                "thinking_models",
                "universal_models",
                "output",
            } - component.keys()
            if missing_component:
                errors.append(
                    f"{framework['code']} {component.get('id')}: missing component fields "
                    f"{sorted(missing_component)}"
                )
                continue
            if set(component["labels"]) != {"zh", "en"}:
                errors.append(
                    f"{framework['code']} {component['id']}: labels need zh and en"
                )
            if len(component["questions"]) < 3:
                errors.append(
                    f"{framework['code']} {component['id']}: needs three questions"
                )
            called_domains.update(component["domains"])
            called_thinking.update(component["thinking_models"])
            called_universal.update(component["universal_models"])
            invalid_domains = set(component["domains"]) - domain_ids
            invalid_thinking = set(component["thinking_models"]) - thinking_ids
            invalid_universal = set(component["universal_models"]) - universal_ids
            if invalid_domains or invalid_thinking or invalid_universal:
                errors.append(
                    f"{framework['code']} {component['id']}: invalid calls "
                    f"domains={sorted(invalid_domains)}, thinking={sorted(invalid_thinking)}, "
                    f"universal={sorted(invalid_universal)}"
                )
        if called_domains != domain_ids:
            errors.append(
                f"{framework['code']}: must cover all H2 domains; "
                f"missing {sorted(domain_ids - called_domains)}"
            )
        if len(called_thinking) < 25 or len(called_universal) < 15:
            errors.append(
                f"{framework['code']}: insufficient cross-model coverage "
                f"({len(called_thinking)} Thinking, {len(called_universal)} Universal)"
            )
        invalid_related = set(framework["related_frameworks"]) - framework_ids
        invalid_problem_calls = (
            set(framework["applies_to_problem_templates"]) - problem_ids
        )
        if invalid_related:
            errors.append(
                f"{framework['code']}: invalid related frameworks {sorted(invalid_related)}"
            )
        if invalid_problem_calls:
            errors.append(
                f"{framework['code']}: invalid problem templates "
                f"{sorted(invalid_problem_calls)}"
            )
        if framework["framework_kind"] == "universal-problem-solving":
            if set(framework["applies_to_problem_templates"]) != problem_ids:
                errors.append("FM02 must apply to all twenty problem templates")
        elif framework["applies_to_problem_templates"]:
            errors.append("FM01 uses lenses and should not duplicate problem mapping edges")
        if len(framework["gates"]) < 5 or len(framework["outputs"]) < 5:
            errors.append(f"{framework['code']}: needs at least five gates and outputs")
        if len(framework["escalation_conditions"]) < 4:
            errors.append(f"{framework['code']}: needs four escalation conditions")

    prereq_state: dict[str, int] = {}

    def visit_prerequisite(node_id: str) -> None:
        if prereq_state.get(node_id) == 1:
            errors.append(f"core prerequisite cycle through {node_id}")
            return
        if prereq_state.get(node_id) == 2:
            return
        prereq_state[node_id] = 1
        for successor in prereq_graph[node_id]:
            visit_prerequisite(successor)
        prereq_state[node_id] = 2

    for core_id in core_ids:
        visit_prerequisite(core_id)

    mapping_semantics = set(crosswalk_data["mapping_semantics"])
    system_ids: set[str] = set()
    crosswalk_rows = 0
    for system in crosswalk_data["systems"]:
        if system["id"] in system_ids:
            errors.append(f"duplicate crosswalk system ID: {system['id']}")
        system_ids.add(system["id"])
        category_codes: set[str] = set()
        for category in system["categories"]:
            crosswalk_rows += 1
            category_code = str(category["code"])
            if category_code in category_codes:
                errors.append(f"{system['id']}: duplicate category code {category_code}")
            category_codes.add(category_code)
            if category["mapping"] not in mapping_semantics:
                errors.append(
                    f"{system['id']} {category_code}: unknown mapping semantic "
                    f"{category['mapping']}"
                )
            invalid_targets = set(category["targets"]) - expected_codes
            if invalid_targets:
                errors.append(
                    f"{system['id']} {category_code}: invalid targets "
                    f"{sorted(invalid_targets)}"
                )

    id_pattern = re.compile(schema["id_policy"]["pattern"])
    required_node = set(schema["required_node_fields"])
    required_scope = set(schema["required_scope_fields"])
    for node in nodes:
        missing_node = required_node - node.keys()
        if missing_node:
            errors.append(f"{node.get('id')}: missing node fields {sorted(missing_node)}")
        if not id_pattern.fullmatch(node["id"]):
            errors.append(f"invalid node ID: {node['id']}")
        if node.get("parent") and node["parent"] not in node_id_set:
            errors.append(f"unknown parent: {node['id']} -> {node['parent']}")
    for node in scope_nodes:
        missing_scope = required_scope - node.keys()
        if missing_scope:
            errors.append(f"{node.get('id')}: missing scope fields {sorted(missing_scope)}")

    relation_ids: list[str] = []
    scope_node_ids = {node["id"] for node in scope_nodes}
    hierarchy: dict[str, list[str]] = {node_id: [] for node_id in scope_node_ids}
    hierarchy_pairs: set[tuple[str, str]] = set()

    all_relations = [
        *relation_data["relationships"],
        *hierarchy_data["relationships"],
        *bridge_relation_data["relationships"],
        *core_relation_data["relationships"],
        *model_relation_data["relationships"],
        *problem_relation_data["relationships"],
        *learning_relation_data["relationships"],
        *framework_relation_data["relationships"],
    ]
    for relation in all_relations:
        relation_ids.append(relation["id"])
        missing = set(schema["required_relation_fields"]) - relation.keys()
        if missing:
            errors.append(f"{relation.get('id')}: missing fields {sorted(missing)}")
            continue
        if not id_pattern.fullmatch(relation["id"]):
            errors.append(f"invalid relation ID: {relation['id']}")
        if relation["type"] not in allowed_relations:
            errors.append(f"invalid relation type: {relation['id']} ({relation['type']})")
        if relation["source"] not in node_id_set:
            errors.append(f"unknown source: {relation['id']} -> {relation['source']}")
        if relation["target"] not in node_id_set:
            errors.append(f"unknown target: {relation['id']} -> {relation['target']}")
        if relation["type"] == "narrower-than":
            if relation["source"] not in scope_node_ids or relation["target"] not in scope_node_ids:
                errors.append(f"narrower-than must connect scope nodes: {relation['id']}")
            else:
                hierarchy[relation["source"]].append(relation["target"])
                hierarchy_pairs.add((relation["source"], relation["target"]))

    if len(relation_ids) != len(set(relation_ids)):
        errors.append("duplicate relation IDs")

    for node in scope_nodes:
        if node.get("parent") and (node["id"], node["parent"]) not in hierarchy_pairs:
            errors.append(f"missing parent edge: {node['id']} -> {node['parent']}")

    state: dict[str, int] = {}

    def visit(node_id: str) -> None:
        if state.get(node_id) == 1:
            errors.append(f"scope hierarchy cycle through {node_id}")
            return
        if state.get(node_id) == 2:
            return
        state[node_id] = 1
        for parent_id in hierarchy[node_id]:
            visit(parent_id)
        state[node_id] = 2

    for node_id in scope_node_ids:
        visit(node_id)

    markdown_link_pattern = re.compile(r"\]\(([^)]+)\)")
    for markdown_file in ROOT.rglob("*.md"):
        text = markdown_file.read_text(encoding="utf-8")
        for target in markdown_link_pattern.findall(text):
            clean_target = target.strip("<>").split("#", 1)[0]
            if not clean_target or re.match(r"^[a-z]+://", clean_target):
                continue
            resolved_target = (markdown_file.parent / clean_target).resolve()
            if not resolved_target.exists():
                errors.append(
                    f"broken Markdown link: {markdown_file.relative_to(ROOT)} -> {target}"
                )

    level_one_map = (ROOT / "01-knowledge-map/level-1-domains.md").read_text(
        encoding="utf-8"
    )
    for code in sorted(expected_codes):
        if f"### {code} " not in level_one_map:
            errors.append(f"missing domain heading in level-1-domains.md: {code}")

    generated_map_path = ROOT / "01-knowledge-map/level-2-3-map.generated.md"
    expected_map = generate_map(domain_data, subdomain_data)
    if generated_map_path.read_text(encoding="utf-8") != expected_map:
        errors.append("level-2-3-map.generated.md is stale; run generate_views.py")
    expected_hierarchy = generate_hierarchy_relations(subdomain_data)
    if hierarchy_data != expected_hierarchy:
        errors.append(
            "hierarchy-relationships.generated.yaml is stale; run generate_views.py"
        )
    crosswalk_path = ROOT / "01-knowledge-map/external-crosswalk.generated.md"
    expected_crosswalk = generate_crosswalk(crosswalk_data)
    if crosswalk_path.read_text(encoding="utf-8") != expected_crosswalk:
        errors.append("external-crosswalk.generated.md is stale; run generate_views.py")
    bridge_path = ROOT / "01-knowledge-map/bridge-views.generated.md"
    expected_bridges = generate_bridge_views(domain_data, subdomain_data, bridge_data)
    if bridge_path.read_text(encoding="utf-8") != expected_bridges:
        errors.append("bridge-views.generated.md is stale; run generate_views.py")
    expected_bridge_relations = generate_bridge_relations(domain_data, bridge_data)
    if bridge_relation_data != expected_bridge_relations:
        errors.append(
            "bridge-relationships.generated.yaml is stale; run generate_views.py"
        )
    core_path = ROOT / "02-domain-skeletons/template-domain-skeletons.generated.md"
    expected_core = generate_core_skeletons(domain_data, subdomain_data, core_data)
    if core_path.read_text(encoding="utf-8") != expected_core:
        errors.append(
            "template-domain-skeletons.generated.md is stale; run generate_views.py"
        )
    expected_core_relations = generate_core_relations(
        domain_data, subdomain_data, core_data
    )
    if core_relation_data != expected_core_relations:
        errors.append("core-relationships.generated.yaml is stale; run generate_views.py")
    thinking_path = ROOT / "03-thinking-models/thinking-models.generated.md"
    expected_thinking = generate_thinking_model_view(
        domain_data, core_data, thinking_data, universal_data
    )
    if thinking_path.read_text(encoding="utf-8") != expected_thinking:
        errors.append("thinking-models.generated.md is stale; run generate_views.py")
    universal_path = ROOT / "04-universal-models/universal-models.generated.md"
    expected_universal = generate_universal_model_view(
        domain_data, core_data, thinking_data, universal_data
    )
    if universal_path.read_text(encoding="utf-8") != expected_universal:
        errors.append("universal-models.generated.md is stale; run generate_views.py")
    expected_model_relations = generate_cross_model_relations(
        domain_data, core_data, thinking_data, universal_data
    )
    if model_relation_data != expected_model_relations:
        errors.append("model-relationships.generated.yaml is stale; run generate_views.py")
    problem_path = ROOT / "05-problem-mapping/problem-templates.generated.md"
    expected_problem_text = generate_problem_mapping_view(
        domain_data, core_data, thinking_data, universal_data, problem_data
    )
    if problem_path.read_text(encoding="utf-8") != expected_problem_text:
        errors.append("problem-templates.generated.md is stale; run generate_views.py")
    expected_problem_relations = generate_problem_relations(
        domain_data, core_data, thinking_data, universal_data, problem_data
    )
    if problem_relation_data != expected_problem_relations:
        errors.append("problem-relationships.generated.yaml is stale; run generate_views.py")
    core_knowledge_path = ROOT / "06-learning/core-knowledge.generated.md"
    expected_core_knowledge = generate_core_knowledge_view(expected_priority_data)
    if core_knowledge_path.read_text(encoding="utf-8") != expected_core_knowledge:
        errors.append("core-knowledge.generated.md is stale; run generate_views.py")
    roadmap_path = ROOT / "06-learning/learning-roadmap.generated.md"
    expected_roadmap = generate_learning_roadmap_view(
        roadmap_data, expected_priority_data, problem_data
    )
    if roadmap_path.read_text(encoding="utf-8") != expected_roadmap:
        errors.append("learning-roadmap.generated.md is stale; run generate_views.py")
    expected_learning_relations = generate_learning_relations(
        roadmap_data, expected_priority_data, problem_data
    )
    if learning_relation_data != expected_learning_relations:
        errors.append("learning-relationships.generated.yaml is stale; run generate_views.py")
    framework_path_by_kind = {
        "multidimensional-thinking": ROOT
        / "07-frameworks/multidimensional-thinking-framework.md",
        "universal-problem-solving": ROOT
        / "07-frameworks/universal-problem-solving-framework.md",
    }
    for framework in frameworks:
        expected_framework_text = generate_framework_view(
            framework, domain_data, thinking_data, universal_data
        )
        framework_path = framework_path_by_kind[framework["framework_kind"]]
        if framework_path.read_text(encoding="utf-8") != expected_framework_text:
            errors.append(
                f"{framework_path.name} is stale; run generate_views.py"
            )
    expected_framework_relations = generate_framework_relations(framework_data)
    if framework_relation_data != expected_framework_relations:
        errors.append("framework-relationships.generated.yaml is stale; run generate_views.py")
    expected_global_audit = build_audit()
    if global_audit_data != expected_global_audit:
        errors.append("global-audit.generated.yaml is stale; run generate_views.py")
    global_audit_path = ROOT / "00-meta/phase-8-global-audit.generated.md"
    expected_global_audit_text = generate_audit_markdown(expected_global_audit)
    if global_audit_path.read_text(encoding="utf-8") != expected_global_audit_text:
        errors.append("phase-8-global-audit.generated.md is stale; run generate_views.py")
    if expected_global_audit["status"] != "pass":
        errors.extend(
            f"global audit: {issue}"
            for issue in expected_global_audit["integrity"]["blocking_issues"]
        )

    if errors:
        print("VALIDATION FAILED")
        for error in errors:
            print(f"- {error}")
        return 1

    print(
        "VALIDATION OK: "
        f"{len(scope_nodes)} scope nodes, {len(bridge_views)} bridge views, "
        f"{len(core_nodes)} core nodes across {len(published_domains)} domains, "
        f"{len(thinking_models)} thinking models, "
        f"{len(universal_models)} universal models, "
        f"{len(problem_templates)} problem templates, "
        f"{len(learning_units)} learning units, "
        f"{len(frameworks)} operating frameworks, "
        f"{len(all_relations)} relations, "
        f"20 H2 domains, {len(subdomains)} H3 subdomains, "
        f"{crosswalk_rows} external crosswalk rows, generated views current, "
        "global audit pass, Markdown links intact"
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
