"""Validate the structural invariants of the Human Knowledge Model."""

from __future__ import annotations

import re
import sys
from pathlib import Path

import yaml

from generate_views import (
    generate_bridge_relations,
    generate_bridge_views,
    generate_core_relations,
    generate_core_skeletons,
    generate_crosswalk,
    generate_hierarchy_relations,
    generate_map,
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
    relation_data = load_yaml("08-data/relationships.yaml")
    hierarchy_data = load_yaml("08-data/hierarchy-relationships.generated.yaml")
    bridge_relation_data = load_yaml("08-data/bridge-relationships.generated.yaml")
    core_relation_data = load_yaml("08-data/core-relationships.generated.yaml")
    errors: list[str] = []

    subdomains = subdomain_data["subdomains"]
    bridge_views = bridge_data["bridge_views"]
    core_nodes = core_data["core_nodes"]
    scope_nodes = [
        domain_data["root"],
        *domain_data["superdomains"],
        *domain_data["domains"],
        *subdomains,
    ]
    nodes = [*scope_nodes, *bridge_views, *core_nodes]
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

    if errors:
        print("VALIDATION FAILED")
        for error in errors:
            print(f"- {error}")
        return 1

    print(
        "VALIDATION OK: "
        f"{len(scope_nodes)} scope nodes, {len(bridge_views)} bridge views, "
        f"{len(core_nodes)} core nodes across {len(published_domains)} domains, "
        f"{len(all_relations)} relations, "
        f"20 H2 domains, {len(subdomains)} H3 subdomains, "
        f"{crosswalk_rows} external crosswalk rows, generated views current, "
        "Markdown links intact"
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
