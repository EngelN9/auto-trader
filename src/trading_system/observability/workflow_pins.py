"""Reject GitHub Actions that are not pinned to a full commit SHA."""

from __future__ import annotations

import re
from pathlib import Path

USES_LINE = re.compile(r"^\s*(?:-\s*)?uses:\s*(?P<reference>\S+?)(?:\s+#.*)?$")
FULL_SHA = re.compile(r"^[0-9a-f]{40}$")


def find_unpinned_actions(workflow_directory: Path) -> list[str]:
    findings: list[str] = []
    for workflow in sorted(workflow_directory.glob("*.y*ml")):
        for line_number, line in enumerate(workflow.read_text(encoding="utf-8").splitlines(), 1):
            match = USES_LINE.match(line)
            if match is None:
                continue
            reference = match.group("reference")
            if reference.startswith("./"):
                continue
            separator = reference.rfind("@")
            revision = reference[separator + 1 :] if separator >= 0 else ""
            if separator <= 0 or FULL_SHA.fullmatch(revision) is None:
                findings.append(f"{workflow}:{line_number}: unpinned action {reference}")
    return findings
