---
description: "Task list for ADR Module implementation"
---

# Tasks: ADR Module

**Input**: Design documents from `specs/004-adr-module/`
**Prerequisites**: plan.md, spec.md, research.md, data-model.md, contracts/api.md, quickstart.md
**Builds on**: feature `001-service-registry` (for service association),
already fully implemented. Extends the same scan orchestrator feature
`002-dependency-map` already extended for docker-compose.yml. Independent
of `003-log-error-analysis`.

**Tests**: Included and ordered before implementation — required by
Constitution Principle V, same as features 001-003.

**Organization**: Tasks are grouped by user story (from spec.md).

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies on incomplete tasks)
- **[Story]**: Maps the task to US1, US2, or US3 from spec.md
- File paths are relative to the repository root; `backend/`/`frontend/` already exist.

---

## Phase 1: Setup (Shared Infrastructure)

- [X] T001 [P] Create the ADR fixture repository at `backend/tests/integration/fixtures/adr-repo/`: `docs/adr/0001-first-decision.md` (plain, `Status: accepted`, no relationships); `docs/adr/0002-second-decision.md` (`Status: superseded by [0003-third-decision](0003-third-decision.md)`); `docs/adr/0003-third-decision.md` (`Status: accepted`, with a `## Links` section containing `Supersedes [0002-second-decision](0002-second-decision.md)` — the *same* logical relationship stated from both sides, to exercise dedup); `docs/adr/broken.md` (body text with no `#` title heading); `docs/adr/secret-leak.md` (a valid title/status, with an `AKIA`-shaped token planted in its body); `docs/adr/diagram.png` (a non-Markdown file, to exercise silent exclusion per FR-002); plus `service-a/package.json` and `service-b/package.json` (two real manifests in the same repository, to exercise the many-to-many service association). Also create a second, unrelated fixture repository at `backend/tests/integration/fixtures/adr-repo-2/docs/adr/0001-first-decision.md` — same filename as the main fixture's, to exercise cross-repository scoping (Edge Case)

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Shared schema needed before any user story's scan logic can run

**⚠️ CRITICAL**: No user story work can begin until this phase is complete

- [X] T002 [P] Create the `AdrRecord` model in `backend/src/models/adr_record.py` per data-model.md: `id` PK; `title` not null; `raw_status` nullable; `normalized_status` not null; `date` nullable; `source_path` not null unique; `repository_path` not null; `content` not null; `has_secret_warning` boolean not null default `false`
- [X] T003 [P] Create the `AdrRelationship` model in `backend/src/models/adr_relationship.py` per data-model.md: `id` PK; `from_adr_id`/`to_adr_id` FK → `AdrRecord.id` not null `ON DELETE CASCADE`; `relationship_type` one of `supersedes`/`amends`
- [X] T004 [P] Create the `AdrServiceAssociation` model in `backend/src/models/adr_service_association.py` per data-model.md: `id` PK; `adr_id` FK → `AdrRecord.id` not null `ON DELETE CASCADE`; `service_id` FK → `Service.id` not null `ON DELETE CASCADE`; unique on `(adr_id, service_id)`
- [X] T005 [P] Create the `AdrImportIssue` model in `backend/src/models/adr_import_issue.py` per data-model.md: `id` PK; `path` not null; `reason` not null; `detected_at` not null

**Checkpoint**: Foundation ready — user story implementation can now begin

---

## Phase 3: User Story 1 - Import and browse ADRs across repositories (Priority: P1) 🎯 MVP

**Goal**: Extend the registry scan to import ADRs (title, status, date,
secret-warning flag) and present a browsable list.

**Independent Test**: Scan the T001 fixture repository and verify the 4
valid ADRs (0001, 0002, 0003, secret-leak) appear with correct
title/status/date, `broken.md` does not appear as an ADR, and
`secret-leak.md` is flagged.

### Tests for User Story 1 ⚠️

- [X] T006 [P] [US1] Unit test for MADR field extraction and status normalization in `backend/tests/unit/test_adr_markdown.py` per research.md §3-4: title from the first `#` heading; `* Status:`/`* Date:` bullet extraction; `superseded` takes priority over other status keywords; a missing title raises the existing `ManifestParseError`; a missing/malformed date line leaves `date` as `None` rather than guessing
- [X] T007 [P] [US1] Unit test for the secret-pattern heuristic in `backend/tests/unit/test_adr_secrets.py` per research.md §8: each of the 3 fixed patterns (private-key header, AWS access key, generic credential assignment) is detected; ordinary prose is not flagged
- [X] T008 [P] [US1] Contract test asserting the extended `POST /api/scan` response includes `adrs_found` in `backend/tests/contract/test_scan_endpoint.py`
- [X] T009 [P] [US1] Contract test for `GET /api/adrs` in `backend/tests/contract/test_adrs_endpoint.py` per contracts/api.md
- [X] T010 [US1] Integration test in `backend/tests/integration/test_adr_scan.py`: scan the T001 fixture repository, assert exactly 4 `AdrRecord` rows with correct title/normalized_status/date, `broken.md` produces an `AdrImportIssue` instead of a record, `secret-leak.md`'s record has `has_secret_warning=True`, and `diagram.png` produces neither a record nor an issue (FR-002); then scan both `adr-repo` and `adr-repo-2` together and assert their same-named `0001-first-decision.md` files remain two distinct records, scoped by `source_path` (Edge Case); then, in a mutable copy, add a new ADR file and delete one of the existing ones, re-scan, and assert the new one appears while the deleted one's record is gone (FR-012/SC-006)

### Implementation for User Story 1

- [X] T011 [US1] Implement `backend/src/scanning/parsers/adr_markdown.py`: `parse(path) -> AdrFields` extracting title/raw_status/normalized_status/date/content per research.md §3-4, raising `ManifestParseError` when no title heading is found
- [X] T012 [P] [US1] Implement `backend/src/scanning/adr_secrets.py`: `check_for_secrets(content) -> bool` applying the three research.md §8 patterns
- [X] T013 [US1] Add `find_adr_files()` to `backend/src/scanning/walker.py`: walk a root yielding every `.md` file directly inside a `docs/adr` directory, same exclusion pruning as the other walkers
- [X] T014 [US1] Extend `run_scan` in `backend/src/scanning/scan_service.py` to also call `find_adr_files`, parse each via `adr_markdown` (T011), run the secrets check (T012), isolate parse failures as `AdrImportIssue` rows, and persist `AdrRecord` rows in the same transaction as the registry (depends on T002, T005, T011, T012, T013)
- [X] T015 [US1] Extend the `POST /api/scan` response model and handler in `backend/src/api/scan.py` to include `adrs_found` per contracts/api.md (depends on T014)
- [X] T016 [US1] Implement `GET /api/adrs` in `backend/src/api/adrs.py` per contracts/api.md
- [X] T017 [P] [US1] Extend the frontend `ScanResponse` type and `triggerScan()` handling for `adrs_found`, and add `listAdrs()` in `frontend/src/services/api.ts`
- [X] T018 [P] [US1] Implement `AdrTable` component in `frontend/src/components/AdrTable.tsx`
- [X] T019 [US1] Implement `AdrsPage` in `frontend/src/pages/AdrsPage.tsx` and add a navigation entry from `RegistryPage` (depends on T017, T018)

**Checkpoint**: User Story 1 is independently functional — this is the MVP for this feature.

---

## Phase 4: User Story 2 - View one ADR's relationships and related services (Priority: P2)

**Goal**: Detect supersedes/amends relationships and compute many-to-many
service associations, surfaced on a detail view.

**Independent Test**: With ADRs already imported (US1), open ADR 0003 and
confirm it shows exactly one `supersedes` relationship to 0002 (not two,
despite both files mentioning it) and both `service-a`/`service-b` as
related.

### Tests for User Story 2 ⚠️

- [X] T020 [P] [US2] Unit test for relationship detection in `backend/tests/unit/test_adr_relationships.py` per research.md §5-6: the whole-file regex matches all four keyword phrases with an accompanying link; "A superseded by B" and "B supersedes A" normalize to the same canonical `(from=B, to=A, type=supersedes)` tuple and deduplicate to one; a link to a file not present in the scan produces no relationship
- [X] T021 [P] [US2] Contract test for `GET /api/adrs/{id}` in `backend/tests/contract/test_adr_detail_endpoint.py` per contracts/api.md, including the `404` case
- [X] T022 [US2] Integration test in `backend/tests/integration/test_adr_relationships.py`: scan the T001 fixture repository, assert exactly one `AdrRelationship` row exists between 0002 and 0003 (Edge Case: dedup despite both-sided mention), and that both `service-a` and `service-b` are associated with all 4 imported ADRs (SC-005); then, in a mutable copy, delete `0003-third-decision.md` and re-scan, asserting 0002 no longer shows a relationship to it (Edge Case: dangling reference after re-scan)

### Implementation for User Story 2

- [X] T023 [US2] Implement `backend/src/scanning/adr_relationships.py`: `resolve_relationships(adr_records)` applying the research.md §5 regex across each record's content, resolving link targets by path (research.md §6) against the other records from the same scan, and deduplicating by canonical `(from_adr_id, to_adr_id, relationship_type)`
- [X] T024 [US2] Extend `run_scan` in `backend/src/scanning/scan_service.py` to call `resolve_relationships` (T023) after all `AdrRecord` rows exist, and to compute `AdrServiceAssociation` rows by matching each ADR's `repository_path` against registered services' `repository_path` (equal or nested, research.md §7) (depends on T003, T004, T023)
- [X] T025 [US2] Implement `GET /api/adrs/{id}` in `backend/src/api/adrs.py` per contracts/api.md: `content`, `supersedes`/`superseded_by`/`amends`/`amended_by` (queried from both sides of `AdrRelationship`), and `related_services`, `404` when not found (depends on T016, T024)
- [X] T026 [P] [US2] Implement frontend API client function `getAdrDetail(id)` in `frontend/src/services/api.ts`
- [X] T027 [P] [US2] Implement `AdrDetail` component in `frontend/src/components/AdrDetail.tsx`
- [X] T028 [US2] Implement `AdrDetailPage` in `frontend/src/pages/AdrDetailPage.tsx`, linked from `AdrTable` rows (depends on T018, T026, T027)

**Checkpoint**: User Stories 1 AND 2 both work independently.

---

## Phase 5: User Story 3 - Import issues surfaced separately (Priority: P3)

**Goal**: Combine parse failures and secret warnings into one dedicated
issues/warnings view.

**Independent Test**: Scan the T001 fixture repository and verify
`broken.md` and `secret-leak.md` both appear in the issues view with the
correct type and reason, while `secret-leak.md` still appears normally in
the ADR list too.

### Tests for User Story 3 ⚠️

- [X] T029 [P] [US3] Contract test for `GET /api/adr-issues` in `backend/tests/contract/test_adr_issues_endpoint.py` per contracts/api.md
- [X] T030 [US3] Integration test in `backend/tests/integration/test_adr_issues.py`: assert `broken.md` appears as `parse_failure` with a specific reason and `secret-leak.md` appears as `secret_warning` referencing its ADR id (Acceptance Scenarios 1-2); then, in a mutable copy, add a title heading to `broken.md` and re-scan, asserting its `parse_failure` is gone and it now appears as a normal ADR (Acceptance Scenario 3, FR-012/SC-006)

### Implementation for User Story 3

- [X] T031 [US3] Implement `GET /api/adr-issues` in `backend/src/api/adr_issues.py` per contracts/api.md, combining `AdrImportIssue` rows and `AdrRecord` rows where `has_secret_warning` is true, register its router (depends on T014)
- [X] T032 [P] [US3] Implement frontend API client function `listAdrIssues()` in `frontend/src/services/api.ts`
- [X] T033 [P] [US3] Implement `AdrIssuesList` component in `frontend/src/components/AdrIssuesList.tsx`
- [X] T034 [US3] Implement `AdrIssuesPage` in `frontend/src/pages/AdrIssuesPage.tsx` and add a navigation entry from `AdrsPage` (depends on T032, T033)

**Checkpoint**: All three user stories are independently functional.

---

## Phase 6: Polish & Cross-Cutting Concerns

- [ ] T035 [P] Author `docs/adr/0008-adr-scan-extends-registry-scan.md` and `docs/adr/0009-adr-relationships-persisted-at-scan-time.md` as plain MADR files per plan.md's Complexity Tracking (Constitution Principle VI) — these two ADRs will then be importable by this very feature once merged, on the next scan of this repository
- [ ] T036 [P] Update `backend/README.md` and `frontend/README.md` to document the extended scan response, the three new endpoints, and the three new screens
- [ ] T037 Add a performance sanity check in `backend/tests/integration/test_adr_scan_performance.py` asserting parsing and relationship resolution for a few hundred generated ADR files completes in well under 5 seconds (plan.md Performance Goals)
- [ ] T038 Run quickstart.md validation end-to-end against this project's own real `docs/adr/` (dogfooding), confirm no manual create/edit/delete affordance for an ADR exists anywhere in the API or UI (FR-013), and record the result

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies — start immediately
- **Foundational (Phase 2)**: Depends on Setup — BLOCKS all user stories
- **User Story 1 (Phase 3)**: Depends on Foundational only
- **User Story 2 (Phase 4)**: Depends on Foundational and US1's T014/T016 (extends the same scan orchestrator and `adrs.py` file)
- **User Story 3 (Phase 5)**: Depends on Foundational and US1's T014 (reads `AdrImportIssue`/`has_secret_warning` data US1's orchestrator already writes); touches no US1/US2 files otherwise
- **Polish (Phase 6)**: Depends on all three user stories being complete

### Parallel Opportunities

- T002-T005 (Foundational models) can all run in parallel with each other
- T006-T009 (US1 tests) can run in parallel with each other
- T017 and T018 (US1 frontend pieces) can run in parallel with each other
- T026 and T027 (US2 frontend pieces) can run in parallel with each other
- T032 and T033 (US3 frontend pieces) can run in parallel with each other
- US3 can be implemented in parallel with US2 by a different person once US1's T014 exists — both extend different, independent read endpoints

---

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Complete Phase 1: Setup
2. Complete Phase 2: Foundational
3. Complete Phase 3: User Story 1
4. **STOP and VALIDATE**: run T010 and the relevant quickstart.md steps —
   scanning this project's own real `docs/adr/` and seeing every existing
   ADR listed is already a demoable, dogfooded MVP

### Incremental Delivery

1. Setup + Foundational → foundation ready
2. User Story 1 → validate independently → MVP demo
3. User Story 2 → validate independently → demo
4. User Story 3 → validate independently → demo
5. Polish (two new ADRs, READMEs, performance check, quickstart run
   against this project's own repository)

## Notes

- [P] tasks touch different files with no dependency on an incomplete task
- Tests are required by Constitution Principle V — write them first, confirm they fail, then implement
- No task in this list requires a network call or an AI/ML dependency, consistent with Constitution Principles I and II
- FR-013 (no create/edit/delete via the system) has no implementing task by design — verified by its absence, the same treatment FR-015 got in feature 001 (T048)
