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


def test_dashboard_runtime_image_excludes_package_managers() -> None:
    dockerfile = (ROOT / "apps" / "dashboard-web" / "Dockerfile").read_text(encoding="utf-8")
    runtime = dockerfile.split("FROM node:24-alpine AS runtime", maxsplit=1)[1]

    assert "rm -rf /usr/local/lib/node_modules/npm" in runtime
    assert 'CMD ["node", "apps/dashboard-web/server.js"]' in runtime
    assert '"dev"' not in runtime


def test_security_workflow_uses_osv_instead_of_registry_audit() -> None:
    workflow = (ROOT / ".github" / "workflows" / "security.yml").read_text(encoding="utf-8")

    assert "pnpm audit" not in workflow
    assert "google/osv-scanner-action/.github/workflows/osv-scanner-reusable.yml" in workflow


def test_ci_pnpm_version_matches_package_manager() -> None:
    package_json = (ROOT / "package.json").read_text(encoding="utf-8")
    workflow = (ROOT / ".github" / "workflows" / "ci.yml").read_text(encoding="utf-8")

    assert '"packageManager": "pnpm@11.15.0"' in package_json
    assert 'version: "11.15.0"' in workflow


def test_frontend_security_overrides_are_pinned() -> None:
    dashboard_package = (ROOT / "apps" / "dashboard-web" / "package.json").read_text(
        encoding="utf-8"
    )
    workspace = (ROOT / "pnpm-workspace.yaml").read_text(encoding="utf-8")

    assert '"next": "16.2.11"' in dashboard_package
    assert "brace-expansion: 5.0.8" in workspace
    assert "postcss: 8.5.18" in workspace
    assert "sharp: 0.35.0" in workspace
    assert "minimumReleaseAge: 10080" in workspace


def test_legacy_minimatch_patch_is_version_locked() -> None:
    workspace = (ROOT / "pnpm-workspace.yaml").read_text(encoding="utf-8")
    patch = (ROOT / "patches" / "minimatch@3.1.5.patch").read_text(encoding="utf-8")

    assert "minimatch@3.1.5: patches/minimatch@3.1.5.patch" in workspace
    assert "require('brace-expansion').expand" in patch
