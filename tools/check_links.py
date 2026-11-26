#!/usr/bin/env python3
"""Check the Markdown files in this repository.

Docs here refer to other files as backticked paths instead of hyperlinks, so a
renamed file leaves a dead reference that nothing else catches. This script
checks, for every tracked-looking Markdown file:

  1. every backticked path that looks like a repository file exists;
  2. the file starts with one H1 and has at least one `##` section
     (the MCP server splits documents at `##` headings).

Standard library only. Exit code 1 if anything is wrong.
"""
from __future__ import annotations

import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SKIP_DIRS = {".git", ".venv", "node_modules", "__pycache__"}
EXTENSIONS = (".md", ".py", ".yaml", ".yml", ".json", ".csv", ".toml")
TOP_LEVEL = ("docs/", "services/", "reports/", "data/", "tools/", ".github/")
CODE_SPAN = re.compile(r"`([^`\n]+)`")


def markdown_files() -> list[Path]:
    return sorted(p for p in ROOT.rglob("*.md") if not SKIP_DIRS & set(p.relative_to(ROOT).parts))


def candidates(path: Path, text: str) -> list[tuple[str, Path]]:
    """Backticked spans that claim to be a file in this repository."""
    found = []
    in_fence = False
    for line in text.splitlines():
        if line.lstrip().startswith("```"):
            in_fence = not in_fence
            continue
        if in_fence:
            continue
        for span in CODE_SPAN.findall(line):
            if any(ch in span for ch in " *<>{}$") or "://" in span or not span.endswith(EXTENSIONS):
                continue
            in_service = path.name == "README.md" and path.parent.parent.name == "services"
            if in_service and "/" in span and (path.parent / span).exists():
                # Service READMEs use paths relative to the service folder.
                found.append((span, path.parent / span))
            elif span.startswith(TOP_LEVEL) or span in ("README.md", "CONTRIBUTING.md", "pyproject.toml"):
                found.append((span, ROOT / span))
            elif in_service and "/" in span and not span.startswith("/"):
                found.append((span, path.parent / span))
    return found


def main() -> int:
    problems: list[str] = []
    files = markdown_files()
    refs = 0
    for path in files:
        rel = path.relative_to(ROOT).as_posix()
        text = path.read_text(encoding="utf-8")
        lines = [ln for ln in text.splitlines() if ln.strip()]
        if not lines or not lines[0].startswith("# "):
            problems.append(f"{rel}: first line is not an H1 heading")
        if not any(ln.startswith("## ") for ln in lines):
            problems.append(f"{rel}: no '##' section")
        for span, target in candidates(path, text):
            refs += 1
            if not target.exists():
                problems.append(f"{rel}: referenced file does not exist: {span}")
    for problem in problems:
        print(problem)
    print(f"{len(files)} Markdown files, {refs} file references checked, {len(problems)} problem(s)")
    return 1 if problems else 0


if __name__ == "__main__":
    sys.exit(main())
