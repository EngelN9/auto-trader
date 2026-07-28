"""CLI wrapper for the GitHub Actions pin validator."""

from __future__ import annotations

import sys
from pathlib import Path

from trading_system.observability.workflow_pins import find_unpinned_actions


def main() -> int:
    findings = find_unpinned_actions(Path(".github/workflows"))
    if findings:
        print("\n".join(findings))
        return 1
    print("All GitHub Actions are pinned to full commit SHAs.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
