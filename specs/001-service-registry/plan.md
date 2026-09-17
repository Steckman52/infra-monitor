# Implementation Plan: Service Registry

**Branch**: `001-service-registry` | **Date**: 2026-09-10 | **Spec**: [spec.md](./spec.md)

**Input**: Feature specification from `specs/001-service-registry/spec.md`

## Summary

Build a locally-run service registry that scans a set of repository paths for
package-manager manifests (`package.json`, `pom.xml`, `requirements.txt`, `go.mod`,
`composer.json`), extracts one service entry per manifest via deterministic,
rule-based parsing and name resolution, and stores the result in a local SQLite
database. A FastAPI backend exposes the scan trigger and read endpoints; a React
frontend lets an engineer browse the registry, inspect a service's dependencies, and
review scan issues (unparsable or incomplete manifests) separately from valid entries.

## Technical Context

**Language/Version**: Python 3.12 (backend), TypeScript + React 18 (frontend)

**Primary Dependencies**: FastAPI, Pydantic, SQLAlchemy 2.0 (ORM over SQLite),
Uvicorn (ASGI server) on the backend; React 18 + a standard SPA build tool on the
frontend. No dependency has any AI/ML capability (Principle I).

**Storage**: SQLite, a single local file (e.g., `data/registry.db`); no external
database server (Principle II).

**Testing**: pytest for backend logic — unit tests per manifest parser, per
name-resolution rule, and per scan-issue case (Principle V); contract tests for the
FastAPI endpoints; an integration test that scans a fixture directory tree covering
all five manifest types plus one broken and one incomplete manifest. No dedicated
frontend test suite is required for this feature — the frontend only renders data
the backend already validated; manual verification via `quickstart.md` is sufficient
at this scope.

**Target Platform**: Runs locally on a developer/engineer workstation (Linux,
Windows, or macOS) as a local HTTP server bound to `localhost`, opened in a browser.
No cloud hosting.

**Project Type**: Web application (separate `backend/` + `frontend/`).

**Performance Goals**: A scan of roughly 500 manifests across the five supported
types completes in under 30 seconds on a typical developer machine.

**Constraints**: Fully offline-capable — scanning, parsing, and storage require no
network access; directory traversal MUST prune excluded directories (`node_modules`,
`vendor`, `target`, `.venv`, `venv`, `env`, `site-packages`, `__pycache__`, `.git`) rather than
walking into them, to keep scan time bounded on large repositories.

**Scale/Scope**: Single-user local install per engineer/architect; on the order of
tens to a few hundred repositories and low thousands of manifests total — not a
multi-tenant SaaS scale.

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

| Principle | Check | Status |
|---|---|---|
| I. No AI/ML in the Product | Scanning/parsing/name-resolution use only stdlib parsing + explicit rule chains from spec FR-004/007/008/009. No ML/LLM dependency anywhere in the stack. | PASS |
| II. Local-First & Resilient | SQLite local file; FastAPI + React served locally; no external API calls are part of the scan path. Unreachable root paths are reported per-path (FR-010) without aborting the rest. | PASS |
| III. No Personal Data | Schema (see data-model.md) stores only service/dependency/scan-issue technical fields — no user identity fields exist anywhere in the model. | PASS |
| IV. Deterministic & Explainable | Every derived field (name, ecosystem, completeness, issue reason) traces to a specific parser rule or manifest field, per FR-004/007/008/009 and data-model.md. | PASS |
| V. Test-First & Simplicity | pytest tests for parsers/name-resolution/scan-issues precede implementation (enforced at task ordering in `/speckit-tasks`); architecture kept to two components (backend, frontend) with no extra layers. | PASS (enforce ordering in tasks.md) |
| VI. Documentation & Dogfooding | This plan's own architectural decisions (SQLite over a server DB, SQLAlchemy over raw `sqlite3`, delete-and-repopulate rescan strategy, custom manifest parsers over third-party parser libraries) MUST be recorded as this project's own ADRs in `docs/adr/` once the ADR module exists or as plain MADR files up front. | FOLLOW-UP: author ADRs (see Complexity Tracking note below) |
| VII. Permissive Licensing | FastAPI (MIT), Pydantic (MIT), SQLAlchemy (MIT), Uvicorn (BSD-3), pytest (MIT), React (MIT) — all permissive, no GPL/AGPL. | PASS |
| VIII. ADR Integrity & Safety | Not directly exercised by this feature (applies to the ADR module feature); no ADR-deletion capability exists anywhere in this plan. | N/A for this feature |

No unresolved violations. See **Complexity Tracking** for the one follow-up item
(dogfooding ADRs), which is a documentation obligation, not a design violation.

## Project Structure

### Documentation (this feature)

```text
specs/001-service-registry/
├── plan.md              # This file (/speckit-plan command output)
├── research.md          # Phase 0 output (/speckit-plan command)
├── data-model.md        # Phase 1 output (/speckit-plan command)
├── quickstart.md        # Phase 1 output (/speckit-plan command)
├── contracts/           # Phase 1 output (/speckit-plan command)
└── tasks.md             # Phase 2 output (/speckit-tasks command - NOT created here)
```

### Source Code (repository root)

```text
backend/
├── src/
│   ├── models/          # SQLAlchemy models: Service, Dependency, ScanIssue
│   ├── scanning/         # directory walk, per-format manifest parsers, name resolution
│   ├── api/              # FastAPI routers: scan, services, scan-issues
│   └── db.py             # SQLite engine/session setup
└── tests/
    ├── unit/             # parser + name-resolution + scan-issue unit tests
    ├── contract/         # FastAPI endpoint contract tests
    └── integration/      # full scan against a fixture repository tree

frontend/
├── src/
│   ├── components/       # ServiceTable, ServiceDetail, ScanIssuesList, ScanButton
│   ├── pages/            # RegistryPage, ServiceDetailPage, ScanIssuesPage
│   └── services/         # API client for the backend
└── tests/
```

**Structure Decision**: Web application layout (Option 2) — a Python/FastAPI
`backend/` and a React `frontend/`, matching the two-tier stack confirmed for the
whole project. This same `backend/` and `frontend/` tree will be extended, not
duplicated, by the remaining three features (dependency map, log analysis, ADR
module).

## Complexity Tracking

> Fill ONLY if Constitution Check has violations that must be justified

| Violation | Why Needed | Simpler Alternative Rejected Because |
|-----------|------------|---------------------------------------|
| None — the only open item is a documentation follow-up (dogfooding ADRs for this plan's own architectural decisions), not a principle violation. It is tracked here so it is not lost: author `docs/adr/0001-sqlite-over-server-db.md`, `docs/adr/0002-sqlalchemy-orm.md`, and `docs/adr/0003-rescan-delete-and-repopulate.md` (plain MADR files) either now or as an early task in `/speckit-tasks`, since the ADR *module* feature (which would otherwise host them) has not been built yet. | n/a | n/a |
