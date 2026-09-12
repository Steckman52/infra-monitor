# Implementation Plan: ADR Module

**Branch**: `004-adr-module` | **Date**: 2026-09-12 | **Spec**: [spec.md](./spec.md)

**Input**: Feature specification from `specs/004-adr-module/spec.md`

## Summary

Extend the existing registry scan (`POST /api/scan`, features 001/002) to
additionally walk each root for `docs/adr/*.md` files — unlike feature
003's logs, ADRs live inside the same source repositories already being
scanned, so this reuses the established "same roots, same transaction"
pattern from feature 002's compose scanning rather than introducing a
third independent scan trigger. Each Markdown file is parsed for title,
status, and date using this project's own MADR conventions; supersedes/
amends relationships are detected via keyword+link regex matching against
the whole file content; every ADR is associated with every registered
service inside its repository (many-to-many); a heuristic secret-pattern
check flags (not blocks) suspicious content; and a separate view surfaces
parse failures and secret warnings together.

## Technical Context

**Language/Version**: Python 3.12 (backend), TypeScript + React 18
(frontend) — unchanged. No new third-party dependency: Markdown is parsed
with `re` (stdlib) using the same fixed-heuristic approach as every prior
feature's text parsing — no Markdown AST library needed for this project's
own conventions.

**Primary Dependencies**: None added.

**Storage**: Same SQLite database; adds four tables (`adr_records`,
`adr_relationships`, `adr_service_associations`, `adr_import_issues`).
Persisted at scan time (like the registry, unlike feature 002's
on-read compatibility) — see research.md §1.

**Testing**: pytest, same conventions — unit tests for MADR field
extraction, status normalization, relationship-link detection, and the
secret-pattern heuristic; contract tests for the new endpoints and the
extended `POST /api/scan` response; an integration test scanning this
project's own real `docs/adr/` (dogfooding — see spec.md's Independent
Test for User Story 1) plus a fixture repo with a deliberately malformed
ADR and one containing a planted secret-like string.

**Target Platform**: Same local FastAPI + React setup.

**Performance Goals**: Parsing and relationship resolution for a few
hundred ADR files completes in well under 5 seconds — regex-based, line
and whole-file text operations only.

**Constraints**: ADR scanning MUST run inside the same `run_scan`
transaction as the registry and connection-graph scanning (research.md
§2), so relationships and service associations are always resolved
against one consistent snapshot, the same reasoning already applied to
compose-service matching in feature 002.

**Scale/Scope**: Same order of magnitude as the registry — this project's
own `docs/adr/` already has 7 real ADRs from features 001-003, which
doubles as genuine test material (Constitution Principle VI dogfooding).

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

| Principle | Check | Status |
|---|---|---|
| I. No AI/ML in the Product | Title/status/date extraction, relationship detection, and secret-pattern flagging are all fixed regex rules (FR-003/004/005/007). No ML/LLM anywhere. | PASS |
| II. Local-First & Resilient | Reads only local `docs/adr/*.md` files already inside the same scanned repository roots; no new network dependency. | PASS |
| III. No Personal Data | New tables store ADR text, status, dates, and file paths only — the same "arbitrary text, stored verbatim" treatment already applied to log content in feature 003. | PASS |
| IV. Deterministic & Explainable | Every relationship traces to a specific keyword+link match in a specific file; every secret warning traces to a specific matched pattern, never a black-box judgment. | PASS |
| V. Test-First & Simplicity | No Markdown AST library — this project's own fixed MADR conventions are simple enough for direct regex extraction (Principle VI dogfooding makes this concrete, not speculative). | PASS |
| VI. Documentation & Dogfooding | This feature is itself the mechanism that will one day browse this project's own ADRs (including the two new ones this plan adds) — the tightest dogfooding loop in the project so far. | PASS |
| VII. Permissive Licensing | No new dependency introduced. | PASS |
| VIII. ADR Integrity & Safety | Directly implements this principle's own requirements: immutable import (no create/edit/delete via the system, FR-013) and the heuristic secret-pattern check on import (FR-007), non-blocking. | PASS |

No unresolved violations.

## Project Structure

### Documentation (this feature)

```text
specs/004-adr-module/
├── plan.md              # This file (/speckit-plan command output)
├── research.md          # Phase 0 output (/speckit-plan command)
├── data-model.md        # Phase 1 output (/speckit-plan command)
├── quickstart.md        # Phase 1 output (/speckit-plan command)
├── contracts/           # Phase 1 output (/speckit-plan command)
└── tasks.md             # Phase 2 output (/speckit-tasks command - NOT created here)
```

### Source Code (repository root)

Extends the existing `backend/`/`frontend/` trees from features 001-003.

```text
backend/
├── src/
│   ├── models/
│   │   ├── adr_record.py             # NEW
│   │   ├── adr_relationship.py       # NEW
│   │   ├── adr_service_association.py # NEW
│   │   └── adr_import_issue.py       # NEW
│   ├── scanning/
│   │   ├── parsers/
│   │   │   └── adr_markdown.py       # NEW — title/status/date/links extraction
│   │   ├── adr_secrets.py            # NEW — heuristic pattern check
│   │   ├── adr_relationships.py      # NEW — link resolution across a scan's ADRs
│   │   └── scan_service.py           # EXTENDED — also walks docs/adr, builds
│   │                                  #             AdrRecord/relationships/associations
│   └── api/
│       ├── scan.py                   # EXTENDED — response gains adrs_found
│       ├── adrs.py                   # NEW — GET /api/adrs, /api/adrs/{id}
│       └── adr_issues.py             # NEW — GET /api/adr-issues
└── tests/
    ├── unit/          # adr_markdown, adr_secrets, adr_relationships
    ├── contract/      # new + extended endpoint contract tests
    └── integration/   # this project's own docs/adr/ + fixture repo

frontend/
├── src/
│   ├── components/
│   │   ├── AdrTable.tsx        # NEW
│   │   ├── AdrDetail.tsx       # NEW
│   │   └── AdrIssuesList.tsx   # NEW
│   ├── pages/
│   │   ├── AdrsPage.tsx        # NEW
│   │   ├── AdrDetailPage.tsx   # NEW
│   │   └── AdrIssuesPage.tsx   # NEW
│   └── services/
│       └── api.ts              # EXTENDED — new client functions
└── tests/
```

**Structure Decision**: Extend the existing two-tier layout in place, and
extend the existing registry scan rather than adding a fourth scan
trigger — ADRs are source-controlled content living in the same
repositories the registry already scans, unlike feature 003's runtime
logs.

## Complexity Tracking

> Fill ONLY if Constitution Check has violations that must be justified

| Violation | Why Needed | Simpler Alternative Rejected Because |
|-----------|------------|---------------------------------------|
| None — the only open item is the same documentation follow-up pattern as every prior feature: author `docs/adr/0008-adr-scan-extends-registry-scan.md` and `docs/adr/0009-adr-relationships-persisted-at-scan-time.md` as plain MADR files. | n/a | n/a |
