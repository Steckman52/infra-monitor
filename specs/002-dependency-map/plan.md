# Implementation Plan: Dependency Map & Version Compatibility

**Branch**: `002-dependency-map` | **Date**: 2026-09-11 | **Spec**: [spec.md](./spec.md)

**Input**: Feature specification from `specs/002-dependency-map/spec.md`

## Summary

Add two capabilities on top of the existing service registry (feature 1):
(1) a version-compatibility view computed entirely from already-scanned
`Service`/`Dependency` rows — comparing major-version numbers across
services that share a dependency — and (2) a service connection graph built
by additionally scanning `docker-compose.yml` files during the same scan
pass, matching each compose service block to a registered `Service` by its
resolved `build:` context path, and representing unmatched blocks as
external nodes. Both are surfaced on their own browsable views and folded
into the existing per-service detail view from feature 1.

## Technical Context

**Language/Version**: Python 3.12 (backend), TypeScript + React 18
(frontend) — unchanged from feature 1.

**Primary Dependencies**: Adds `PyYAML` (MIT) to the existing FastAPI /
Pydantic / SQLAlchemy / Uvicorn stack, needed to parse `docker-compose.yml`.
Uses `yaml.safe_load` specifically — never `yaml.load` with the default
loader — since these files come from arbitrary scanned repositories and
must not be able to construct arbitrary Python objects.

**Storage**: Same SQLite database as feature 1; adds two tables
(`external_nodes`, `service_connections`). Version compatibility is **not**
persisted — it is computed on read from existing `services`/`dependencies`
rows (per spec Assumptions), so no new table is needed for it.

**Testing**: pytest, same conventions as feature 1 — unit tests for the
`docker-compose.yml` parser and the major-version-extraction/comparison
logic, contract tests for the two new endpoints and the extended service
detail endpoint, an integration test scanning a fixture tree with a
multi-service compose file (shared network + `depends_on` + an
`image:`-only external node) plus a broken compose file.

**Target Platform**: Same local FastAPI + React setup as feature 1.

**Performance Goals**: Compatibility computation and connection-graph
retrieval each complete in well under 1 second at the project's target
scale (a few hundred services, low thousands of dependency rows) — pure
in-memory grouping over data already in SQLite, no new I/O per request.

**Constraints**: `docker-compose.yml` scanning MUST happen within the same
scan pass and the same replace-on-rescan transaction as the existing
registry scan (research.md §1), so the registry, the connection graph, and
(implicitly) the compatibility view always describe one consistent scan
snapshot.

**Scale/Scope**: Same as feature 1 — this feature adds no new scale
dimension of its own; it operates over the same registry.

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

| Principle | Check | Status |
|---|---|---|
| I. No AI/ML in the Product | Major-version extraction is a regex-based rule (FR-003); compose parsing and node/edge matching are rule-based path comparisons. No ML/LLM anywhere. | PASS |
| II. Local-First & Resilient | No new external calls; `docker-compose.yml` files are read from the same local repository paths already scanned. | PASS |
| III. No Personal Data | New tables (`external_nodes`, `service_connections`) store only compose service names, images, network/dependency relationships, and file paths — no personal data. | PASS |
| IV. Deterministic & Explainable | Every connection traces to a specific shared network name or `depends_on` entry in a specific `docker-compose.yml`; every compatibility status traces to the specific declared version strings it was computed from. | PASS |
| V. Test-First & Simplicity | Compatibility is computed, not persisted, avoiding a redundant table and a second write path to keep in sync. Compose parsing reuses the existing scan pass rather than introducing a second scan trigger. | PASS |
| VI. Documentation & Dogfooding | This plan's own decisions (compatibility computed vs. persisted; PyYAML + `safe_load`; single unified scan transaction) get their own ADRs alongside feature 1's (see Complexity Tracking). | FOLLOW-UP tracked |
| VII. Permissive Licensing | `PyYAML` is MIT-licensed. No new frontend dependency needed. | PASS |
| VIII. ADR Integrity & Safety | Not directly exercised by this feature. | N/A |

No unresolved violations.

## Project Structure

### Documentation (this feature)

```text
specs/002-dependency-map/
├── plan.md              # This file (/speckit-plan command output)
├── research.md          # Phase 0 output (/speckit-plan command)
├── data-model.md        # Phase 1 output (/speckit-plan command)
├── quickstart.md        # Phase 1 output (/speckit-plan command)
├── contracts/           # Phase 1 output (/speckit-plan command)
└── tasks.md             # Phase 2 output (/speckit-tasks command - NOT created here)
```

### Source Code (repository root)

This feature extends the existing `backend/` and `frontend/` trees from
feature 1 rather than introducing new top-level directories.

```text
backend/
├── src/
│   ├── models/
│   │   ├── external_node.py       # NEW
│   │   └── service_connection.py  # NEW
│   ├── scanning/
│   │   ├── parsers/
│   │   │   └── docker_compose.py  # NEW — build/image/networks/depends_on
│   │   ├── connection_graph.py    # NEW — matches compose blocks to Services,
│   │   │                          #        builds ExternalNode/ServiceConnection rows
│   │   └── scan_service.py        # EXTENDED — also invokes compose scanning
│   │                               #             inside the same transaction
│   ├── analysis/
│   │   └── version_compatibility.py  # NEW — pure computation, no persistence
│   └── api/
│       ├── compatibility.py       # NEW — GET /api/dependency-compatibility
│       ├── connections.py         # NEW — GET /api/connections
│       └── services.py            # EXTENDED — detail response gains
│                                   #            compatibility_risks + connections
└── tests/
    ├── unit/          # docker_compose parser, version_compatibility tests
    ├── contract/      # new + extended endpoint contract tests
    └── integration/   # fixture tree with compose files

frontend/
├── src/
│   ├── components/
│   │   ├── CompatibilityTable.tsx   # NEW
│   │   └── ConnectionGraphView.tsx  # NEW
│   ├── pages/
│   │   ├── CompatibilityPage.tsx    # NEW
│   │   └── ConnectionsPage.tsx      # NEW
│   └── services/
│       └── api.ts                   # EXTENDED — new client functions
└── tests/
```

**Structure Decision**: Extend the existing two-tier `backend/`/`frontend/`
layout from feature 1 in place — this feature has no independent runtime
identity; it reads and enriches the same registry.

## Complexity Tracking

> Fill ONLY if Constitution Check has violations that must be justified

| Violation | Why Needed | Simpler Alternative Rejected Because |
|-----------|------------|---------------------------------------|
| None — the only open item is the same documentation follow-up pattern as feature 1: author `docs/adr/0004-compatibility-computed-not-persisted.md` and `docs/adr/0005-compose-scan-in-same-transaction.md` as plain MADR files, since the ADR *module* feature still doesn't exist yet. | n/a | n/a |
