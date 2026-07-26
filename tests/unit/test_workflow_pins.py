from pathlib import Path

from trading_system.observability.workflow_pins import find_unpinned_actions


def test_repository_workflows_pin_actions_to_full_shas() -> None:
    root = Path(__file__).resolve().parents[2]

    assert find_unpinned_actions(root / ".github" / "workflows") == []


def test_unpinned_action_is_reported(tmp_path: Path) -> None:
    workflow = tmp_path / "unsafe.yml"
    workflow.write_text(
        "steps:\n  - uses: actions/checkout@v4\n",
        encoding="utf-8",
    )

    findings = find_unpinned_actions(tmp_path)

    assert len(findings) == 1
    assert "actions/checkout@v4" in findings[0]
