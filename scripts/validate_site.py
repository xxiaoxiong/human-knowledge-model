"""Validate the built static site and its generated model payload."""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SITE = ROOT / "dist-site"


def main() -> int:
    errors: list[str] = []
    required = [
        SITE / "index.html",
        SITE / "styles.css",
        SITE / "app.js",
        SITE / "og-v2.png",
        SITE / "data/model.json",
        SITE / ".nojekyll",
    ]
    for path in required:
        if not path.exists():
            errors.append(f"missing site artifact: {path.relative_to(ROOT)}")
    if errors:
        print("SITE VALIDATION FAILED")
        for error in errors:
            print(f"- {error}")
        return 1

    html = (SITE / "index.html").read_text(encoding="utf-8")
    for required_id in (
        "main",
        "map",
        "bridges",
        "skeletons",
        "models",
        "problems",
        "learning",
        "frameworks",
        "method",
        "problem-workbench",
        "problem-input",
        "problem-analyze",
        "problem-examples",
        "problem-suggestions",
        "problem-suggestion-list",
        "problem-route",
        "knowledge-network",
        "detail-dialog",
        "detail-back",
        "detail-breadcrumbs",
    ):
        if f'id="{required_id}"' not in html:
            errors.append(f"missing required site element: #{required_id}")
    if "<svg" in html.lower() or "<svg" in (SITE / "styles.css").read_text(
        encoding="utf-8"
    ).lower():
        errors.append("finished site must not contain model-authored SVG")
    if re.search(r'(?:src|href)="/(?!/)', html):
        errors.append("root-relative asset URL would break GitHub project Pages")

    app_source = (SITE / "app.js").read_text(encoding="utf-8")
    for required_contract in (
        "detailHistory",
        "navigateDetailBack",
        "renderDetailNavigation",
        "renderTopicProfile",
        "renderScopeGuide",
        "renderRelationshipNavigator",
        "MODE_GUIDES",
        "PROBLEM_KEYWORDS",
        "recommendProblems",
        "renderProblemSuggestions",
        "renderProblemRoute",
        "renderKnowledgeCallGroup",
        "renderModelPairs",
        "buildProblemBrief",
        "downloadProblemBrief",
    ):
        if required_contract not in app_source:
            errors.append(f"site app is missing detail-navigation contract: {required_contract}")
    for scope_kind in ("domain", "subdomain"):
        if f'renderScopeGuide("{scope_kind}", node, idx)' not in app_source:
            errors.append(f"site app does not attach expanded guides to every {scope_kind} detail")
    styles_source = (SITE / "styles.css").read_text(encoding="utf-8")
    for class_name in (
        "topic-guide",
        "inquiry-mode-grid",
        "knowledge-anchor-grid",
        "study-route",
        "journey-ribbon",
        "problem-intake-card",
        "problem-suggestion-card",
        "knowledge-call-card",
        "model-pair-card",
        "evidence-checklist",
        "problem-brief-card",
    ):
        if f".{class_name}" not in styles_source:
            errors.append(f"site styles are missing expanded-guide surface: .{class_name}")
    for detail_kind in (
        "root",
        "superdomain",
        "domain",
        "subdomain",
        "bridge",
        "core",
        "thinking",
        "universal",
        "problem",
        "learningPath",
        "learning",
        "framework",
    ):
        if f'kind === "{detail_kind}"' not in app_source:
            errors.append(f"site app cannot render rich details for node kind: {detail_kind}")

    payload = json.loads((SITE / "data/model.json").read_text(encoding="utf-8"))
    counts = payload["meta"]["counts"]
    if payload["meta"].get("version") != "0.8.0":
        errors.append("site payload must expose the frozen v0.8.0 model")
    if payload["meta"].get("audit") != {
        "status": "pass",
        "weakComponents": 1,
        "blockingIssues": 0,
    }:
        errors.append("site payload must expose a passing single-component global audit")
    expected_counts = {
        "superdomains": len(payload["superdomains"]),
        "domains": len(payload["domains"]),
        "subdomains": len(payload["subdomains"]),
        "bridges": len(payload["bridges"]),
        "coreNodes": len(payload["coreNodes"]),
        "thinkingModels": len(payload["thinkingModels"]),
        "universalModels": len(payload["universalModels"]),
        "problemTemplates": len(payload["problemTemplates"]),
        "learningCandidates": len(payload["learningPriorities"]),
        "learningUnits": len(payload["learningUnits"]),
        "frameworks": len(payload["frameworks"]),
        "topicGuides": len(payload["topicGuides"]),
    }
    for key, expected in expected_counts.items():
        if counts.get(key) != expected:
            errors.append(f"payload count mismatch: {key} ({counts.get(key)} != {expected})")
    if counts["domains"] != 20 or counts["subdomains"] != 248:
        errors.append("site payload must expose the complete frozen H2/H3 map")
    if counts.get("topicGuides") != 268:
        errors.append("site payload must expose expanded guides for all 20 H2 and 248 H3 topics")
    if counts["bridges"] < 10 or counts["coreNodes"] < 40:
        errors.append("site payload is missing bridge views or template skeletons")
    if counts["thinkingModels"] < 30 or counts["universalModels"] < 15:
        errors.append("site payload is missing the cross-disciplinary model layers")
    if counts["problemTemplates"] != 20:
        errors.append("site payload must expose all twenty problem templates")
    if counts["learningCandidates"] != 320:
        errors.append("site payload must expose all 320 ranked learning candidates")
    if counts["learningUnits"] != 8:
        errors.append("site payload must expose all eight learning roadmap units")
    if counts["frameworks"] != 2:
        errors.append("site payload must expose both operating frameworks")
    if counts.get("relations") != 3056:
        errors.append("site payload must expose all 3,056 frozen graph relations")
    if len(payload.get("relations", [])) != counts.get("relations"):
        errors.append("site payload must materialize every frozen graph relation for detail navigation")
    ranks = [entry["rank"] for entry in payload["learningPriorities"]]
    if sorted(ranks) != list(range(1, 321)):
        errors.append("site payload learning ranks must be unique and contiguous from 1 to 320")

    node_collections = (
        [payload["root"]],
        payload["superdomains"],
        payload["domains"],
        payload["subdomains"],
        payload["bridges"],
        payload["coreNodes"],
        payload["thinkingModels"],
        payload["universalModels"],
        payload["problemTemplates"],
        payload["learningUnits"],
        [payload["learningPath"]],
        payload["frameworks"],
    )
    ids = {
        node["id"]
        for collection in node_collections
        for node in collection
    }
    expected_total = sum(len(collection) for collection in node_collections)
    if len(ids) != expected_total:
        errors.append("site payload contains duplicate node IDs")
    relation_endpoints = {
        endpoint
        for relation in payload.get("relations", [])
        for endpoint in (relation.get("source"), relation.get("target"))
    }
    unknown_endpoints = sorted(endpoint for endpoint in relation_endpoints if endpoint not in ids)
    if unknown_endpoints:
        errors.append(f"site relation navigator has unknown endpoints: {unknown_endpoints[:5]}")
    unconnected_nodes = sorted(node_id for node_id in ids if node_id not in relation_endpoints)
    if unconnected_nodes:
        errors.append(f"site detail nodes lack graph context: {unconnected_nodes[:5]}")

    scope_nodes = payload["domains"] + payload["subdomains"]
    scope_ids = {node["id"] for node in scope_nodes}
    guides = payload.get("topicGuides", [])
    guide_node_ids = [guide.get("node_id") for guide in guides]
    if len(set(guide_node_ids)) != len(guide_node_ids):
        errors.append("site topic guides contain duplicate node coverage")
    missing_guides = sorted(scope_ids - set(guide_node_ids))
    extra_guides = sorted(set(guide_node_ids) - scope_ids)
    if missing_guides or extra_guides:
        errors.append(
            f"site topic-guide coverage mismatch: missing={missing_guides[:5]} extra={extra_guides[:5]}"
        )
    core_ids = {node["id"] for node in payload["coreNodes"]}
    bridge_ids = {node["id"] for node in payload["bridges"]}
    problem_ids = {node["id"] for node in payload["problemTemplates"]}
    learning_ids = {node["id"] for node in payload["learningUnits"]}
    guide_by_node = {guide.get("node_id"): guide for guide in guides}
    supported_modes = {
        "empirical",
        "formal",
        "causal",
        "historical",
        "interpretive",
        "normative",
        "comparative",
        "synthetic",
        "design",
        "embodied",
    }
    relation_pairs = {
        (relation.get("source"), relation.get("target"))
        for relation in payload.get("relations", [])
    }
    required_scope_dimensions = {
        "objects",
        "actors",
        "timescales",
        "scales",
        "values_at_stake",
        "constraints",
    }
    knowledge_collections = {
        "domains": {node["id"] for node in payload["domains"]},
        "core_nodes": {node["id"] for node in payload["coreNodes"]},
        "thinking_models": {node["id"] for node in payload["thinkingModels"]},
        "universal_models": {node["id"] for node in payload["universalModels"]},
    }
    for problem in payload["problemTemplates"]:
        problem_id = problem["id"]
        if set(problem.get("scoping_dimensions", {})) != required_scope_dimensions:
            errors.append(f"problem workbench lacks six-dimensional scope: {problem_id}")
        if any(not values for values in problem.get("scoping_dimensions", {}).values()):
            errors.append(f"problem workbench contains an empty scope dimension: {problem_id}")
        if len(problem.get("success_criteria", [])) < 3:
            errors.append(f"problem workbench lacks success criteria: {problem_id}")
        if len(problem.get("evidence_requirements", [])) < 3:
            errors.append(f"problem workbench lacks evidence gates: {problem_id}")
        if len(problem.get("workflow", [])) < 5:
            errors.append(f"problem workbench lacks a five-stage action path: {problem_id}")
        for step in problem.get("workflow", []):
            if not all(step.get(field) for field in ("stage", "action", "output", "gate")):
                errors.append(f"problem workflow step lacks action, output or gate: {problem_id}")
        calls = problem.get("knowledge_calls", {})
        for field, allowed_ids in knowledge_collections.items():
            call_ids = calls.get(field, [])
            if not call_ids:
                errors.append(f"problem workbench has an empty knowledge layer {field}: {problem_id}")
            unknown_calls = sorted(set(call_ids) - allowed_ids)
            if unknown_calls:
                errors.append(f"problem workbench has unknown {field}: {problem_id} -> {unknown_calls[:3]}")
            missing_relations = [
                target for target in call_ids if (problem_id, target) not in relation_pairs
            ]
            if missing_relations:
                errors.append(
                    f"problem knowledge calls lack relation explanations: {problem_id} -> {missing_relations[:3]}"
                )
    for node in scope_nodes:
        guide = guide_by_node.get(node["id"])
        if not guide:
            continue
        expected_kind = "domain" if node in payload["domains"] else "subdomain"
        if guide.get("kind") != expected_kind or guide.get("parent_id") != node.get("parent"):
            errors.append(f"site topic guide has wrong hierarchy metadata: {node['id']}")
        if len(node.get("core_questions", [])) < (2 if expected_kind == "domain" else 1):
            errors.append(f"site topic guide lacks key questions: {node['id']}")
        if len(node.get("scope_includes", [])) < 4:
            errors.append(f"site topic guide lacks core concepts: {node['id']}")
        if not node.get("epistemic_modes") or not set(node["epistemic_modes"]).issubset(
            set(guide.get("inquiry_modes", []))
        ):
            errors.append(f"site topic guide lacks inquiry-method coverage: {node['id']}")
        unknown_modes = sorted(set(guide.get("inquiry_modes", [])) - supported_modes)
        if unknown_modes:
            errors.append(f"site topic guide has unsupported inquiry modes: {node['id']} -> {unknown_modes}")
        reference_sets = {
            "anchor_core_nodes": core_ids,
            "related_topics": scope_ids,
            "bridge_views": bridge_ids,
            "problem_templates": problem_ids,
            "learning_units": learning_ids,
        }
        for field, allowed_ids in reference_sets.items():
            values = guide.get(field, [])
            if field in {"anchor_core_nodes", "related_topics", "problem_templates", "learning_units"} and not values:
                errors.append(f"site topic guide has no {field}: {node['id']}")
            unknown = sorted(set(values) - allowed_ids)
            if unknown:
                errors.append(f"site topic guide has unknown {field}: {node['id']} -> {unknown[:3]}")
    for collection in node_collections:
        for node in collection:
            labels = node.get("labels", {})
            if set(labels) != {"zh", "en"} or not all(
                isinstance(value, str) and value.strip() for value in labels.values()
            ):
                errors.append(
                    f"site payload node lacks exact non-empty zh/en labels: {node.get('id')}"
                )
            if not isinstance(node.get("definition"), str) or not node["definition"].strip():
                errors.append(f"site detail node lacks a substantive definition: {node.get('id')}")

    if errors:
        print("SITE VALIDATION FAILED")
        for error in errors:
            print(f"- {error}")
        return 1
    print(
        "SITE VALIDATION OK: "
        f"{counts['domains']} domains, {counts['subdomains']} subdomains, "
        f"{counts['bridges']} bridge views, {counts['coreNodes']} core nodes, "
        f"{counts['thinkingModels']} thinking models, "
        f"{counts['universalModels']} universal models, "
        f"{counts['problemTemplates']} problem templates, "
        f"{counts['learningCandidates']} learning candidates, "
        f"{counts['learningUnits']} learning units, "
        f"{counts['frameworks']} operating frameworks, "
        f"{counts['topicGuides']} expanded H2/H3 topic guides, "
        "project-relative assets and required interaction surfaces present"
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
