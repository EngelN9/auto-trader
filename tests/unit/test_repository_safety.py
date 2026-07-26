import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]


def test_makefile_has_no_live_target() -> None:
    makefile = (ROOT / "Makefile").read_text(encoding="utf-8")

    assert re.search(r"^live\s*:", makefile, flags=re.MULTILINE) is None


def test_environment_example_contains_no_key_material() -> None:
    example = (ROOT / ".env.example").read_text(encoding="utf-8")

    assert "BEGIN PRIVATE KEY" not in example
    assert "API_KEY=" not in example
    assert "SECRET_KEY=" not in example
