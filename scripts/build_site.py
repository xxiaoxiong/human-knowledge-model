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


def build_payload() -> dict:
    domain_data = load_yaml("08-data/domains.yaml")
    subdomain_data = load_yaml("08-data/subdomains.yaml")
    bridge_data = load_yaml("08-data/bridges.yaml")
    core_data = load_yaml("08-data/core-nodes.yaml")
    relation_files = [
        "08-data/relationships.yaml",
        "08-data/hierarchy-relationships.generated.yaml",
        "08-data/bridge-relationships.generated.yaml",
        "08-data/core-relationships.generated.yaml",
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
    domain_ids = {domain["id"] for domain in domains}
    domain_relations = [
        relation
        for relation in relations
        if relation["source"] in domain_ids and relation["target"] in domain_ids
    ]
    return {
        "meta": {
            "id": "human-knowledge-model",
            "version": core_data["model_version"],
            "generatedFrom": [
                "08-data/domains.yaml",
                "08-data/subdomains.yaml",
                "08-data/bridges.yaml",
                "08-data/core-nodes.yaml",
            ],
            "counts": {
                "superdomains": len(superdomains),
                "domains": len(domains),
                "subdomains": len(subdomains),
                "bridges": len(bridges),
                "coreNodes": len(core_nodes),
                "relations": len(relations),
            },
        },
        "root": compact_scope(domain_data["root"]),
        "superdomains": superdomains,
        "domains": domains,
        "subdomains": subdomains,
        "bridges": bridges,
        "coreNodes": core_nodes,
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
        f"{payload['meta']['counts']['relations']} relations"
    )


if __name__ == "__main__":
    main()
