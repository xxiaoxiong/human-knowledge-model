"""Quote inline bilingual YAML labels so commas remain part of scalar values."""

from __future__ import annotations

import json
from pathlib import Path
import re


ROOT = Path(__file__).resolve().parents[1]
TARGETS = [
    ROOT / "08-data/domains.yaml",
    ROOT / "08-data/subdomains.yaml",
    ROOT / "08-data/bridges.yaml",
]
LABEL_LINE = re.compile(
    r"^(?P<indent>\s*)labels:\s*\{zh:\s*(?P<zh>.*?),\s*en:\s*(?P<en>.*)\}\s*$"
)


def yaml_string(value: str) -> str:
    value = value.strip()
    if len(value) >= 2 and value[0] == value[-1] and value[0] in {'"', "'"}:
        return value
    return json.dumps(value, ensure_ascii=False)


def normalize_file(path: Path) -> int:
    lines = path.read_text(encoding="utf-8").splitlines()
    updated: list[str] = []
    changes = 0
    for line in lines:
        match = LABEL_LINE.match(line)
        if not match:
            updated.append(line)
            continue
        normalized = (
            f"{match.group('indent')}labels: "
            f"{{zh: {yaml_string(match.group('zh'))}, "
            f"en: {yaml_string(match.group('en'))}}}"
        )
        updated.append(normalized)
        changes += normalized != line
    if changes:
        path.write_text("\n".join(updated) + "\n", encoding="utf-8", newline="\n")
    return changes


def main() -> None:
    total = 0
    for path in TARGETS:
        changes = normalize_file(path)
        total += changes
        print(f"{path.relative_to(ROOT)}: normalized {changes} label lines")
    print(f"LABEL NORMALIZATION OK: {total} lines updated")


if __name__ == "__main__":
    main()
