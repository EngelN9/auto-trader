# Dependency review

Status: Milestone 0 review. Versions are locked in `uv.lock` and `pnpm-lock.yaml`.

| Dependency group | Purpose | License | Runtime path | Main risk / alternative |
|---|---|---|---|---|
| FastAPI, Uvicorn, HTTPX | Control and mock HTTP boundaries | MIT / BSD-3-Clause | Python services | Framework and parser vulnerabilities; alternatives include Starlette or stdlib boundaries |
| Pydantic | Frozen configuration and API schemas | MIT | Python services | Validation behavior changes; alternative is dataclasses plus explicit validation |
| PyYAML | Versioned YAML configuration | MIT | Startup only | Unsafe loaders are prohibited; alternative is JSON or TOML |
| Hatchling, uv | Build and reproducible environment | MIT / MIT or Apache-2.0 | Build tooling | Compromised packages or installer; verify locks and releases |
| Ruff, mypy, pytest, Hypothesis, pre-commit | Format, lint, typing, tests | MIT / MPL-2.0 | Development and CI | CI supply chain; alternatives are standard-library checks and other maintained tools |
| pip-audit | Python advisory scan | Apache-2.0 | CI only | Advisory coverage and false negatives; alternative is OSV Scanner |
| OSV Scanner | Lockfile advisory scan for the complete repository | Apache-2.0 | CI only | Database availability and ecosystem coverage; the reusable workflow is pinned to a reviewed commit |
| Next.js, React | Responsive dashboard skeleton | MIT | Dashboard | Large dependency surface and frequent updates; alternative is a smaller static TypeScript client |
| brace-expansion 5.0.8 override | Patched glob expansion used by frontend development tooling | MIT | Development and CI | Cross-major override for legacy minimatch consumers; lint and test verification is mandatory |
| minimatch 3.1.5 compatibility patch | Adapts legacy CommonJS import to brace-expansion 5.0.8 | ISC | Development and CI | One-line vendored patch must be removed once a compatible upstream release is available |
| PostCSS 8.5.18 override | Patched CSS processing used by Next.js and Vite | MIT | Build tooling | Transitive override may expose plugin compatibility changes; production build verification is mandatory |
| sharp 0.35.0 override | Next.js image runtime dependency with patched libvips | Apache-2.0 | Dashboard runtime | Overrides Next.js's vulnerable 0.34.x optional range; build and container smoke tests are required before promotion |
| TypeScript, ESLint, Vitest, type packages | Frontend typing, lint, tests | Apache-2.0 / MIT | Development and CI | Plugin supply chain; lockfile and review required |
| PostgreSQL image | Local topology placeholder | PostgreSQL License | Docker development | Mutable development tag; production must use an approved immutable digest |
| GitHub Actions listed in workflows | Checkout and tool setup | Mixed open-source | CI only | Actions must be pinned to full commit SHAs and granted minimal permissions |

Maintenance status is evaluated through lockfile review, advisory scanning, release activity, and
Dependabot or equivalent updates. None of these packages may be silently upgraded in a trading
release.

The dashboard container uses a multi-stage standalone build. Its runtime image contains only Node.js
and the traced Next.js server files; npm, pnpm, build caches, and development dependencies are
excluded from the final image.

The initial locks exclude packages published after 2026-07-19, providing a seven-day observation
window at bootstrap time. Future dependency pull requests must advance this cutoff deliberately
after advisory and release review.

Two narrowly scoped security exceptions bypass that observation window:

- `next@16.2.11`, `eslint-config-next@16.2.11`, their exact-version `@next/env` and
  `@next/eslint-plugin-next` companions, and the matching `@next/swc-*` platform binaries fix the
  advisories reported against 16.2.10 by OSV Scanner.
- `brace-expansion@5.0.8` is the first release containing the bounded-expansion fix. It is forced
  across legacy minimatch consumers and therefore requires the full frontend quality suite.

These exceptions do not disable `minimumReleaseAge`; they admit only the documented patched
versions. `postcss@8.5.18` and `sharp@0.35.0` already satisfy the seven-day window.

Legacy `minimatch@3.1.5` expects brace-expansion's old function-style CommonJS export. The
version-locked patch in `patches/minimatch@3.1.5.patch` changes only that import to the named
`expand` export provided by patched brace-expansion 5.0.8. pnpm records its patch hash in the
lockfile and fails installation if the patch no longer applies.
