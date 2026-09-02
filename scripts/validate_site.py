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
        SITE / "og.png",
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
        "knowledge-network",
        "detail-dialog",
    ):
        if f'id="{required_id}"' not in html:
            errors.append(f"missing required site element: #{required_id}")
    if "<svg" in html.lower() or "<svg" in (SITE / "styles.css").read_text(
        encoding="utf-8"
    ).lower():
        errors.append("finished site must not contain model-authored SVG")
    if re.search(r'(?:src|href)="/(?!/)', html):
        errors.append("root-relative asset URL would break GitHub project Pages")

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
    }
    for key, expected in expected_counts.items():
        if counts.get(key) != expected:
            errors.append(f"payload count mismatch: {key} ({counts.get(key)} != {expected})")
    if counts["domains"] != 20 or counts["subdomains"] != 248:
        errors.append("site payload must expose the complete frozen H2/H3 map")
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
    ranks = [entry["rank"] for entry in payload["learningPriorities"]]
    if sorted(ranks) != list(range(1, 321)):
        errors.append("site payload learning ranks must be unique and contiguous from 1 to 320")

    node_collections = (
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
    for collection in node_collections:
        for node in collection:
            labels = node.get("labels", {})
            if set(labels) != {"zh", "en"} or not all(
                isinstance(value, str) and value.strip() for value in labels.values()
            ):
                errors.append(
                    f"site payload node lacks exact non-empty zh/en labels: {node.get('id')}"
                )

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
        "project-relative assets and required interaction surfaces present"
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
