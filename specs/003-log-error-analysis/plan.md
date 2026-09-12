# Implementation Plan: Log Error Analysis & Grouping

**Branch**: `003-log-error-analysis` | **Date**: 2026-09-11 | **Spec**: [spec.md](./spec.md)

**Input**: Feature specification from `specs/003-log-error-analysis/spec.md`

## Summary

Add a second, independent scan (its own root, its own trigger — not the
repository scan from feature 001) that walks a local directory of exported
log files, attributes each file to a registered service by its immediate
parent directory name, detects error entries via a fixed severity-marker
set (capturing multi-line stack traces as one entry), normalizes each
entry's text into a template via regex substitution, and groups entries by
`(service or unattributed source, template)`. Results are persisted (not
computed on read, unlike feature 002's compatibility view) and surfaced as
a browsable per-service error report, a drill-down per group, and a
separate view of unattributed directories / unreadable files.

## Technical Context

**Language/Version**: Python 3.12 (backend), TypeScript + React 18
(frontend) — unchanged. No new third-party dependency: severity/continuation
matching, template normalization, and timestamp extraction all use
`re` and `datetime` from the standard library.

**Primary Dependencies**: None added beyond feature 001/002's stack.

**Storage**: Same SQLite database; adds three tables (`error_groups`,
`error_occurrences`, `log_scan_issues`) — a dedicated `log_scan_issues`
table rather than reusing the registry's `scan_issues` table, so the two
independently-triggered scans (repository scan vs. log scan) never clobber
each other's issue records (research.md §3).

**Testing**: pytest, same conventions — unit tests for severity/continuation
detection, normalization, and timestamp extraction; contract tests for the
new endpoints; an integration test scanning a fixture log tree covering a
matched service directory, an unattributed directory, a genuinely
unreadable file, and a rotated/compressed file that must be silently
excluded.

**Target Platform**: Same local FastAPI + React setup.

**Performance Goals**: Scanning and grouping 10,000 log lines across all
files completes in well under 10 seconds on a typical developer machine —
line-oriented regex matching, no per-line I/O beyond the initial read.

**Constraints**: The log scan is triggered independently of the repository
scan (FR-001) — it must not require re-running or being coupled to
`POST /api/scan`. A single malformed/unreadable file must not stop the
scan of the rest (FR-014). Multi-line capture is capped at a fixed maximum
line count per entry as a safety valve against pathological input.

**Scale/Scope**: Log volume is expected to be at the scale of a handful of
services' exported logs for review purposes, not a live aggregation
pipeline — consistent with the project's local-first, on-demand scanning
model established in features 001/002.

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

| Principle | Check | Status |
|---|---|---|
| I. No AI/ML in the Product | Error detection is a fixed marker list (FR-005); grouping is regex-based template substitution (FR-007), not statistical/ML clustering. Explicitly ruled out in spec Assumptions. | PASS |
| II. Local-First & Resilient | Reads only already-exported local log files; no live process tailing, no remote log service (spec Assumptions). | PASS |
| III. No Personal Data | The system does not extract, index, or specially treat personal data — raw log text is stored/shown verbatim as arbitrary text, exactly as ADR content is treated in feature 004's principle (spec Assumptions addresses this directly). | PASS |
| IV. Deterministic & Explainable | Every group traces to a specific marker match, continuation rule, and normalization substitution; unattributed logs are still analyzed and separately flagged, never silently dropped. | PASS |
| V. Test-First & Simplicity | Reuses the existing directory-exclusion list from feature 001's walker rather than inventing a parallel one; stores a bounded sample of occurrences per group (research.md §7) rather than every single one, avoiding unbounded storage growth for no analytical benefit. | PASS |
| VI. Documentation & Dogfooding | This plan's decisions (persist-at-scan-time vs. compute-on-read, dedicated issue table) get their own ADRs (see Complexity Tracking). | FOLLOW-UP tracked |
| VII. Permissive Licensing | No new dependency introduced. | PASS |
| VIII. ADR Integrity & Safety | Not exercised by this feature. | N/A |

No unresolved violations.

## Project Structure

### Documentation (this feature)

```text
specs/003-log-error-analysis/
├── plan.md              # This file (/speckit-plan command output)
├── research.md          # Phase 0 output (/speckit-plan command)
├── data-model.md        # Phase 1 output (/speckit-plan command)
├── quickstart.md        # Phase 1 output (/speckit-plan command)
├── contracts/           # Phase 1 output (/speckit-plan command)
└── tasks.md             # Phase 2 output (/speckit-tasks command - NOT created here)
```

### Source Code (repository root)

Extends the existing `backend/`/`frontend/` trees from features 001/002.

```text
backend/
├── src/
│   ├── models/
│   │   ├── error_group.py         # NEW
│   │   ├── error_occurrence.py    # NEW
│   │   └── log_scan_issue.py      # NEW
│   ├── scanning/
│   │   ├── error_detection.py     # NEW — severity markers + continuation capture
│   │   ├── normalization.py       # NEW — template substitution (research.md §5)
│   │   └── log_scan_service.py    # NEW — orchestrator, mirrors scan_service.py's
│   │                               #        transaction-per-scan pattern, independently
│   └── api/
│       ├── log_scan.py            # NEW — POST /api/log-scan
│       ├── error_groups.py        # NEW — GET /api/error-groups, /error-groups/{id}
│       └── log_scan_issues.py     # NEW — GET /api/log-scan-issues
└── tests/
    ├── unit/          # error_detection, normalization, timestamp extraction
    ├── contract/      # new endpoint contract tests
    └── integration/   # fixture log tree

frontend/
├── src/
│   ├── components/
│   │   ├── LogScanButton.tsx        # NEW
│   │   ├── ErrorGroupsTable.tsx     # NEW
│   │   ├── ErrorGroupDetail.tsx     # NEW
│   │   └── LogScanIssuesList.tsx    # NEW
│   ├── pages/
│   │   ├── LogsPage.tsx             # NEW
│   │   ├── ErrorGroupDetailPage.tsx # NEW
│   │   └── LogScanIssuesPage.tsx    # NEW
│   └── services/
│       └── api.ts                   # EXTENDED — new client functions
└── tests/
```

**Structure Decision**: Extend the existing two-tier layout in place. Log
scanning shares the walker's directory-exclusion list (research.md §6) but
gets its own file-discovery and orchestration modules, since attributing
files to services and capturing multi-line entries is a different shape of
work than manifest/compose parsing.

## Complexity Tracking

> Fill ONLY if Constitution Check has violations that must be justified

| Violation | Why Needed | Simpler Alternative Rejected Because |
|-----------|------------|---------------------------------------|
| None — the only open item is the same documentation follow-up pattern as features 001/002: author `docs/adr/0006-error-groups-persisted-at-scan-time.md` and `docs/adr/0007-dedicated-log-scan-issue-table.md` as plain MADR files. | n/a | n/a |
