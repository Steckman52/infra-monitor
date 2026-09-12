---
description: "Task list for Log Error Analysis & Grouping implementation"
---

# Tasks: Log Error Analysis & Grouping

**Input**: Design documents from `specs/003-log-error-analysis/`
**Prerequisites**: plan.md, spec.md, research.md, data-model.md, contracts/api.md, quickstart.md
**Builds on**: feature `001-service-registry` (for service names to match
against), already fully implemented. Independent of `002-dependency-map`.

**Tests**: Included and ordered before implementation — required by
Constitution Principle V, same as features 001/002.

**Organization**: Tasks are grouped by user story (from spec.md).

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies on incomplete tasks)
- **[Story]**: Maps the task to US1, US2, or US3 from spec.md
- File paths are relative to the repository root; `backend/`/`frontend/` already exist.

---

## Phase 1: Setup (Shared Infrastructure)

- [X] T001 [P] Create the log fixture scaffold at `backend/tests/integration/fixtures/logs/`: a `payments-api/` subdirectory (matching the existing registered service) with a log file containing 10+ near-duplicate `ERROR` lines differing only in embedded numbers, one multi-line stack-trace error, and some `INFO`-only lines; two unmatched subdirectories, `unknown-service/` and `another-unknown-service/`, each containing a log file with the *same* error text (to verify unattributed groups are scoped per source directory, not merged); one genuinely unreadable file (invalid encoding); one `.gz` file to confirm silent exclusion (FR-002)

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Shared schema and file discovery needed before any user story's scan logic can run

**⚠️ CRITICAL**: No user story work can begin until this phase is complete

- [X] T002 [P] Create the `ErrorGroup` model in `backend/src/models/error_group.py` per data-model.md: `id` PK; `service_id` FK → `Service.id` nullable `ON DELETE CASCADE`; `unattributed_source_path` text nullable; `normalized_template` text not null; `severity_marker` text not null; `occurrence_count` integer not null; `first_seen`/`last_seen` datetime nullable; `example_text` text not null
- [X] T003 [P] Create the `ErrorOccurrence` model in `backend/src/models/error_occurrence.py` per data-model.md: `id` PK; `error_group_id` FK → `ErrorGroup.id` not null `ON DELETE CASCADE`; `raw_text` text not null; `occurred_at` datetime nullable; `source_log_path` text not null; `line_number` integer not null
- [X] T004 [P] Create the `LogScanIssue` model in `backend/src/models/log_scan_issue.py` per data-model.md: `id` PK; `path` text not null; `issue_type` text not null, one of `unattributed`/`unreadable`; `reason` text not null; `detected_at` datetime not null
- [X] T005 Implement `find_log_files()` in `backend/src/scanning/walker.py`: walk a log root pruning the existing `EXCLUDED_DIR_NAMES` (research.md §6), yielding files with extension `.log`, `.txt`, or no extension (FR-002) — files with other extensions (e.g. `.gz`) are never yielded

**Checkpoint**: Foundation ready — user story implementation can now begin

---

## Phase 3: User Story 1 - Scan logs and browse grouped errors per service (Priority: P1) 🎯 MVP

**Goal**: Scan a log root, detect and group errors per matched service, and
present the resulting report.

**Independent Test**: Scan the T001 fixture tree and verify the 10+
near-duplicate lines collapse into one group with the correct count under
`payments-api`.

### Tests for User Story 1 ⚠️

- [X] T006 [P] [US1] Unit test for severity/continuation detection in `backend/tests/unit/test_error_detection.py` per research.md: each of the 8 markers matches case-insensitively; continuation lines (indented, `at `, `File `, `Caused by:`) are captured into the same entry; capture stops at a blank line, a new marker, or the fixed max-line cap
- [X] T007 [P] [US1] Unit test for template normalization in `backend/tests/unit/test_normalization.py` per research.md §5: UUID/hex/quoted-string substitution happens before bare-digit substitution, so a UUID is replaced as one token, not fragmented
- [X] T008 [P] [US1] Unit test for timestamp extraction per research.md §8: ISO-8601 and common-log-format prefixes are parsed; an unrecognized format returns `None` rather than raising
- [X] T009 [P] [US1] Contract test for `POST /api/log-scan` in `backend/tests/contract/test_log_scan_endpoint.py` per contracts/api.md
- [X] T010 [P] [US1] Contract test for `GET /api/error-groups` in `backend/tests/contract/test_error_groups_endpoint.py` per contracts/api.md
- [X] T011 [US1] Integration test in `backend/tests/integration/test_log_scan.py`: scan the T001 fixture tree, assert the near-duplicate lines collapse into one group with the correct `occurrence_count` (SC-001), the multi-line stack trace is captured as one entry, the `INFO`-only content produces no group, and the two unmatched directories with identical error text produce two distinct groups (keyed by `unattributed_source_path`, not merged — Edge Case, data-model.md grouping key); then, in a mutable copy of the fixture, add one new distinct error line and re-scan, asserting a new group appears without duplicating the existing ones (FR-015/SC-005)

### Implementation for User Story 1

- [X] T012 [US1] Implement `backend/src/scanning/error_detection.py`: the fixed severity-marker set (FR-005), a function that scans a file's lines and yields raw entries `(first_line, continuation_lines, start_line_number)` per the continuation/stop rules in research.md
- [X] T013 [P] [US1] Implement `backend/src/scanning/normalization.py`: `normalize_template(first_line)` applying UUID → hex → quoted-string → digit substitution in that order (research.md §5)
- [X] T014 [P] [US1] Implement timestamp extraction in `backend/src/scanning/error_detection.py` (or a small sibling module) per research.md §8
- [X] T015 [US1] Implement `backend/src/scanning/log_scan_service.py`: walk the log root via `find_log_files` (T005), attribute each file to a registered `Service` by parent-directory name or mark it unattributed, run detection (T012) + normalization (T013) + timestamp extraction (T014) per file, group entries by `(service_id or unattributed_source_path, normalized_template)`, cap stored `ErrorOccurrence` rows at 20 per group while keeping the true `occurrence_count` (research.md §7), record a `LogScanIssue` for each unattributed directory and unreadable file, and replace `error_groups`/`error_occurrences`/`log_scan_issues` in one transaction (depends on T002-T005, T012-T014)
- [X] T016 [US1] Implement `POST /api/log-scan` in `backend/src/api/log_scan.py` per contracts/api.md, register its router in `backend/src/main.py` (depends on T015)
- [X] T017 [US1] Implement `GET /api/error-groups` in `backend/src/api/error_groups.py` per contracts/api.md
- [X] T018 [P] [US1] Implement frontend API client functions `triggerLogScan()` and `listErrorGroups()` in `frontend/src/services/api.ts`
- [X] T019 [P] [US1] Implement `LogScanButton` component in `frontend/src/components/LogScanButton.tsx`
- [X] T020 [P] [US1] Implement `ErrorGroupsTable` component in `frontend/src/components/ErrorGroupsTable.tsx`
- [X] T021 [US1] Implement `LogsPage` in `frontend/src/pages/LogsPage.tsx` and add a navigation entry from `RegistryPage` (depends on T018-T020)

**Checkpoint**: User Story 1 is independently functional — this is the MVP for this feature.

---

## Phase 4: User Story 2 - Drill into one error group (Priority: P2)

**Goal**: Let a user open one error group and see its full context.

**Independent Test**: With groups already populated (US1), open the group
covering the multi-line stack trace and confirm the complete original text
is shown.

### Tests for User Story 2 ⚠️

- [X] T022 [P] [US2] Contract test for `GET /api/error-groups/{id}` in `backend/tests/contract/test_error_group_detail_endpoint.py` per contracts/api.md, including the `404` case
- [X] T023 [US2] Integration test in `backend/tests/integration/test_error_group_detail.py`: verify the multi-line-stack-trace group's `example_text` and sampled occurrences contain the complete original text, and that `first_seen`/`last_seen` reflect the extracted timestamps

### Implementation for User Story 2

- [X] T024 [US2] Implement `GET /api/error-groups/{id}` in `backend/src/api/error_groups.py` per contracts/api.md, `404` when not found (depends on T017)
- [X] T025 [P] [US2] Implement frontend API client function `getErrorGroupDetail(id)` in `frontend/src/services/api.ts`
- [X] T026 [P] [US2] Implement `ErrorGroupDetail` component in `frontend/src/components/ErrorGroupDetail.tsx`
- [X] T027 [US2] Implement `ErrorGroupDetailPage` in `frontend/src/pages/ErrorGroupDetailPage.tsx`, linked from `ErrorGroupsTable` rows (depends on T020, T025, T026)

**Checkpoint**: User Stories 1 AND 2 both work independently.

---

## Phase 5: User Story 3 - Log scan issues surfaced separately (Priority: P3)

**Goal**: Surface unattributed log directories and unreadable log files as
a separate, explainable view.

**Independent Test**: Scan the T001 fixture tree and verify the
`unknown-service/` directory and the unreadable file both appear in the
issues view, and the `.gz` file appears nowhere.

### Tests for User Story 3 ⚠️

- [X] T028 [P] [US3] Contract test for `GET /api/log-scan-issues` in `backend/tests/contract/test_log_scan_issues_endpoint.py` per contracts/api.md
- [X] T029 [US3] Integration test in `backend/tests/integration/test_log_scan_issues.py`: assert the unmatched directory produces an `unattributed` issue and the unreadable file produces an `unreadable` issue with a specific reason (Acceptance Scenarios 1-2), and that the `.gz` file produces no issue and no group anywhere (FR-002); and, separately, in a mutable copy of the fixture, rename the unattributed directory to match a registered service and re-scan, asserting the `unattributed` issue is gone and its errors now appear as a normal group (Acceptance Scenario 3, FR-015/SC-005)

### Implementation for User Story 3

- [X] T030 [US3] Implement `GET /api/log-scan-issues` in `backend/src/api/log_scan_issues.py` per contracts/api.md, register its router (depends on T015)
- [X] T031 [P] [US3] Implement frontend API client function `listLogScanIssues()` in `frontend/src/services/api.ts`
- [X] T032 [P] [US3] Implement `LogScanIssuesList` component in `frontend/src/components/LogScanIssuesList.tsx`
- [X] T033 [US3] Implement `LogScanIssuesPage` in `frontend/src/pages/LogScanIssuesPage.tsx` and add a navigation entry from `RegistryPage` (depends on T031, T032)

**Checkpoint**: All three user stories are independently functional.

---

## Phase 6: Polish & Cross-Cutting Concerns

- [X] T034 [P] Author `docs/adr/0006-error-groups-persisted-at-scan-time.md` and `docs/adr/0007-dedicated-log-scan-issue-table.md` as plain MADR files per plan.md's Complexity Tracking (Constitution Principle VI)
- [X] T035 [P] Update `backend/README.md` and `frontend/README.md` to document the three new endpoints and three new screens
- [X] T036 Add a performance sanity check in `backend/tests/integration/test_log_scan_performance.py` asserting 10,000 generated log lines are scanned and grouped in well under 10 seconds (plan.md Performance Goals)
- [X] T037 Run quickstart.md validation end-to-end and record the result

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies — start immediately
- **Foundational (Phase 2)**: Depends on Setup — BLOCKS all user stories
- **User Story 1 (Phase 3)**: Depends on Foundational only
- **User Story 2 (Phase 4)**: Depends on Foundational and US1's T017 (extends the same endpoint file); touches no other US1 files
- **User Story 3 (Phase 5)**: Depends on Foundational and US1's T015 (reads `LogScanIssue` rows US1's orchestrator already writes); touches no US1/US2 files otherwise
- **Polish (Phase 6)**: Depends on all three user stories being complete

### Parallel Opportunities

- T002, T003, T004 (Foundational models) can run in parallel with each other
- T006-T010 (US1 tests) can run in parallel with each other
- T013 and T014 (US1 normalization/timestamp) can run in parallel with each other
- T018-T020 (US1 frontend pieces) can run in parallel with each other
- Once Foundational and US1's T015/T017 exist, US2 and US3 can be implemented in parallel by different people

---

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Complete Phase 1: Setup
2. Complete Phase 2: Foundational
3. Complete Phase 3: User Story 1
4. **STOP and VALIDATE**: run T011 and the relevant quickstart.md steps

### Incremental Delivery

1. Setup + Foundational → foundation ready
2. User Story 1 → validate independently → MVP demo
3. User Story 2 → validate independently → demo
4. User Story 3 → validate independently → demo
5. Polish (ADRs, READMEs, performance check, quickstart run)

## Notes

- [P] tasks touch different files with no dependency on an incomplete task
- Tests are required by Constitution Principle V — write them first, confirm they fail, then implement
- No task in this list requires a network call or an AI/ML dependency, consistent with Constitution Principles I and II
- Raw log text is stored and displayed verbatim (spec Assumptions) — no redaction or personal-data handling is in scope
