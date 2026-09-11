---
description: "Task list for Service Registry implementation"
---

# Tasks: Service Registry

**Input**: Design documents from `specs/001-service-registry/`
**Prerequisites**: plan.md, spec.md, research.md, data-model.md, contracts/api.md, quickstart.md

**Tests**: Included and ordered before implementation — required by Constitution
Principle V (Test-First & Simplicity), which mandates tests-before-implementation for
manifest parsing, name resolution, and scan-issue logic.

**Organization**: Tasks are grouped by user story (from spec.md) to enable
independent implementation and testing of each story.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies on incomplete tasks)
- **[Story]**: Maps the task to US1, US2, or US3 from spec.md
- File paths are relative to the repository root

## Path Conventions

Web application layout per plan.md: `backend/src/`, `backend/tests/`, `frontend/src/`, `frontend/tests/`.

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Project initialization and basic structure

- [ ] T001 Create the `backend/` and `frontend/` directory skeleton per plan.md Project Structure: `backend/src/{models,scanning,scanning/parsers,api}`, `backend/tests/{unit,contract,integration}`, `frontend/src/{components,pages,services}`, `frontend/tests`
- [ ] T002 Initialize the Python backend project in `backend/` (`pyproject.toml` or `requirements.txt`) with dependencies: `fastapi`, `pydantic`, `sqlalchemy`, `uvicorn`, `pytest`, `httpx` (for the FastAPI test client) — all MIT/BSD-licensed per constitution Principle VII
- [ ] T003 [P] Initialize the React frontend project in `frontend/` (`package.json`) with React 18 and a standard SPA build tool
- [ ] T004 [P] Create the fixture repository tree at `backend/tests/integration/fixtures/` containing: one valid manifest of each of the five supported types, one syntactically invalid `package.json`, one `pom.xml` missing `artifactId`, a `node_modules/` subfolder containing a decoy `package.json` (to verify exclusion per FR-006), and two `package.json` manifests in different subfolders that would derive the same name (no explicit `name` field, identical parent-directory name) to exercise the FR-004 rule-3 collision suffix end-to-end (SC-006)

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Core infrastructure that MUST be complete before ANY user story can be implemented

**⚠️ CRITICAL**: No user story work can begin until this phase is complete

- [ ] T005 Configure the SQLite engine/session in `backend/src/db.py`, pointing at a single local file (e.g. `data/registry.db`) per plan.md Storage — no external DB server
- [ ] T006 [P] Create the `Service` SQLAlchemy model in `backend/src/models/service.py` per data-model.md: `id` PK autoincrement; `name` text not null; `ecosystem` text not null, one of `node`/`java`/`python`/`go`/`php`; `repository_path` text not null; `manifest_path` text not null unique; `is_complete` boolean not null default `true`; `last_scanned_at` datetime not null
- [ ] T007 [P] Create the `Dependency` SQLAlchemy model in `backend/src/models/dependency.py` per data-model.md: `id` PK autoincrement; `service_id` FK → `Service.id` not null, `ON DELETE CASCADE`; `name` text not null; `declared_version` text nullable
- [ ] T008 [P] Create the `ScanIssue` SQLAlchemy model in `backend/src/models/scan_issue.py` per data-model.md: `id` PK autoincrement; `manifest_path` text not null; `repository_path` text not null; `issue_type` text not null, one of `unparsable`/`incomplete_data`/`unreachable_path`; `reason` text not null; `service_id` FK → `Service.id` nullable, `ON DELETE CASCADE`; `detected_at` datetime not null
- [ ] T009 Implement the directory-walk utility with exclusion pruning in `backend/src/scanning/walker.py`, using `os.walk(topdown=True)` and pruning `node_modules`, `vendor`, `target`, `.venv`, `site-packages`, `__pycache__`, `.git` from `dirnames` in place per research.md §5
- [ ] T010 Create the FastAPI app skeleton and router registration in `backend/src/main.py`

**Checkpoint**: Foundation ready — user story implementation can now begin

---

## Phase 3: User Story 1 - Build and browse the service registry (Priority: P1) 🎯 MVP

**Goal**: Scan configured repository paths and produce a browsable registry of
services derived from package-manager manifests.

**Independent Test**: Point the scanner at the fixture tree (T004), run a scan, and
verify the registry lists one entry per valid manifest, a monorepo yields multiple
entries, and an unreachable root is reported without aborting the rest.

### Tests for User Story 1 ⚠️

> Write these tests FIRST, ensure they FAIL before implementation

- [ ] T011 [P] [US1] Unit test for the `package.json` parser in `backend/tests/unit/test_parser_package_json.py`: name comes from the `name` field; dependencies and their declared versions are extracted verbatim
- [ ] T012 [P] [US1] Unit test for the `pom.xml` parser in `backend/tests/unit/test_parser_pom_xml.py`: name derived from `groupId`/`artifactId`; dependencies extracted from `<dependencies>`
- [ ] T013 [P] [US1] Unit test for the `requirements.txt` parser in `backend/tests/unit/test_parser_requirements_txt.py`: regex-based line parsing per research.md §3; `-r`/`-e`/environment-marker lines are skipped, not treated as parse failures
- [ ] T014 [P] [US1] Unit test for the `go.mod` parser in `backend/tests/unit/test_parser_go_mod.py`: name is the last path segment of the `module` directive; `require` entries extracted
- [ ] T015 [P] [US1] Unit test for the `composer.json` parser in `backend/tests/unit/test_parser_composer_json.py`
- [ ] T016 [P] [US1] Unit test for the name-resolution chain in `backend/tests/unit/test_name_resolution.py` per FR-004: explicit manifest field takes priority; parent-directory name is used when no field exists (e.g., `requirements.txt`); a repository-path-derived suffix is appended when two services would otherwise collide
- [ ] T017 [P] [US1] Contract test for `POST /api/scan` in `backend/tests/contract/test_scan_endpoint.py` against the request/response shape in contracts/api.md
- [ ] T018 [P] [US1] Contract test for `GET /api/services` in `backend/tests/contract/test_services_list_endpoint.py` against contracts/api.md
- [ ] T019 [US1] Integration test in `backend/tests/integration/test_scan_registry.py` running a full scan against the fixture tree (T004), asserting: one service per valid manifest (SC-001), a monorepo produces multiple entries (Acceptance Scenario 2), an unreachable root path is reported without aborting the scan of valid ones (Acceptance Scenario 4, FR-010), `node_modules` contents are excluded (FR-006), and the two same-named fixture manifests both appear in the registry as distinct entries disambiguated by a repository-path-derived suffix (FR-004 rule 3, SC-006)

### Implementation for User Story 1

- [ ] T020 [P] [US1] Implement the `package.json` parser in `backend/src/scanning/parsers/package_json.py`
- [ ] T021 [P] [US1] Implement the `pom.xml` parser in `backend/src/scanning/parsers/pom_xml.py`
- [ ] T022 [P] [US1] Implement the `requirements.txt` parser in `backend/src/scanning/parsers/requirements_txt.py`
- [ ] T023 [P] [US1] Implement the `go.mod` parser in `backend/src/scanning/parsers/go_mod.py`
- [ ] T024 [P] [US1] Implement the `composer.json` parser in `backend/src/scanning/parsers/composer_json.py`
- [ ] T025 [US1] Implement the name-resolution chain in `backend/src/scanning/name_resolution.py` per FR-004 (depends on T020-T024 parser output shape)
- [ ] T026 [US1] Implement the scan orchestrator in `backend/src/scanning/scan_service.py`: walks each requested root via the T009 walker, dispatches each manifest to its matching parser, isolates per-manifest parse failures so one bad file never stops the scan (FR-007), records a `ScanIssue` row for each unreachable root (`issue_type="unreachable_path"`, FR-010) and each unparsable manifest (`issue_type="unparsable"`, FR-008), marks a service `is_complete=false` and records a linked `ScanIssue` (`issue_type="incomplete_data"`) when a manifest parses but lacks a required field (FR-009), and persists all `Service`/`Dependency`/`ScanIssue` rows inside one transaction that replaces the prior scan's results (research.md §8) (depends on T025, T009, T006-T008)
- [ ] T027 [US1] Implement `POST /api/scan` in `backend/src/api/scan.py`, returning `{services_found, issues_found, unreachable_roots}` per contracts/api.md (depends on T026)
- [ ] T028 [US1] Implement `GET /api/services` in `backend/src/api/services.py`, returning the list shape per contracts/api.md
- [ ] T029 [P] [US1] Implement the frontend API client functions `triggerScan()` and `listServices()` in `frontend/src/services/api.ts` per contracts/api.md
- [ ] T030 [P] [US1] Implement the `ScanButton` component in `frontend/src/components/ScanButton.tsx`
- [ ] T031 [P] [US1] Implement the `ServiceTable` component in `frontend/src/components/ServiceTable.tsx`
- [ ] T032 [US1] Implement `RegistryPage` in `frontend/src/pages/RegistryPage.tsx`, composing `ScanButton` and `ServiceTable` (depends on T029-T031)

**Checkpoint**: User Story 1 is independently functional and testable — this is the MVP.

---

## Phase 4: User Story 2 - Inspect a service's details and dependencies (Priority: P2)

**Goal**: Let a user open a single service and see its full dependency list,
ecosystem, and repository path.

**Independent Test**: With the registry already populated (US1), open a service
entry and verify its dependency list matches the source manifest exactly.

### Tests for User Story 2 ⚠️

- [ ] T033 [P] [US2] Contract test for `GET /api/services/{id}` in `backend/tests/contract/test_service_detail_endpoint.py` per contracts/api.md, including the `404` case
- [ ] T034 [US2] Integration test in `backend/tests/integration/test_service_detail.py` asserting the dependency list matches the manifest exactly (Acceptance Scenario 1) and a manifest with zero dependencies yields an explicit empty list (Acceptance Scenario 2)

### Implementation for User Story 2

- [ ] T035 [US2] Implement `GET /api/services/{id}` in `backend/src/api/services.py`, returning full detail including dependencies per contracts/api.md, `404` when the id does not exist (depends on T028)
- [ ] T036 [P] [US2] Implement the frontend API client function `getServiceDetail(id)` in `frontend/src/services/api.ts`
- [ ] T037 [P] [US2] Implement the `ServiceDetail` component in `frontend/src/components/ServiceDetail.tsx`
- [ ] T038 [US2] Implement `ServiceDetailPage` in `frontend/src/pages/ServiceDetailPage.tsx`, linked from `ServiceTable` rows (depends on T031, T036, T037)

**Checkpoint**: User Stories 1 AND 2 both work independently.

---

## Phase 5: User Story 3 - See what failed or is incomplete during a scan (Priority: P3)

**Goal**: Surface unparsable and incomplete manifests as a separate, explainable
list of scan issues.

**Independent Test**: Scan the fixture tree's broken and incomplete manifests (T004)
and verify both appear in the scan-issues view with a specific reason, and that
fixing one and re-scanning removes it from the list.

### Tests for User Story 3 ⚠️

- [ ] T039 [P] [US3] Contract test for `GET /api/scan-issues` in `backend/tests/contract/test_scan_issues_endpoint.py` per contracts/api.md
- [ ] T040 [US3] Integration test in `backend/tests/integration/test_scan_issues.py` asserting: an invalid manifest produces an `issue_type="unparsable"` entry with a specific reason and no service (Acceptance Scenario 1); a `pom.xml` missing `artifactId` produces a service with `is_complete=false` plus a linked `issue_type="incomplete_data"` entry (Acceptance Scenario 2); fixing the manifest and re-scanning removes the resolved issue (Acceptance Scenario 3, SC-005); and, separately, adding a brand-new manifest to the fixture tree before a re-scan makes it appear as a new service while deleting a previously-scanned manifest before a re-scan makes its service and dependencies disappear (FR-014 add/remove sub-cases, SC-005)

### Implementation for User Story 3

- [ ] T041 [US3] Implement `GET /api/scan-issues` in `backend/src/api/scan_issues.py` per contracts/api.md (depends on T026 already persisting `ScanIssue` rows)
- [ ] T042 [P] [US3] Implement the frontend API client function `listScanIssues()` in `frontend/src/services/api.ts`
- [ ] T043 [P] [US3] Implement the `ScanIssuesList` component in `frontend/src/components/ScanIssuesList.tsx`
- [ ] T044 [US3] Implement `ScanIssuesPage` in `frontend/src/pages/ScanIssuesPage.tsx` (depends on T042, T043)

**Checkpoint**: All three user stories are independently functional.

---

## Phase 6: Polish & Cross-Cutting Concerns

- [ ] T045 [P] Author the dogfooding ADRs identified in plan.md's Complexity Tracking as plain MADR files: `docs/adr/0001-sqlite-over-server-db.md`, `docs/adr/0002-sqlalchemy-orm.md`, `docs/adr/0003-rescan-delete-and-repopulate.md` (Constitution Principle VI)
- [ ] T046 [P] Write `backend/README.md` and `frontend/README.md` covering each module's purpose, public interface, and run instructions (Constitution Principle VI)
- [ ] T047 Add a performance integration test in `backend/tests/integration/test_scan_performance.py` asserting a scan of ~500 generated manifests completes in under 30 seconds (plan.md Performance Goals)
- [ ] T048 Run the quickstart.md validation end-to-end, record the result, and confirm no manual create/edit affordance for a service entry exists anywhere in the API or frontend (FR-015)

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies — start immediately
- **Foundational (Phase 2)**: Depends on Setup — BLOCKS all user stories
- **User Story 1 (Phase 3)**: Depends on Foundational only
- **User Story 2 (Phase 4)**: Depends on Foundational; reads data US1's scan orchestrator produces, so is easiest to validate after US1 exists, but touches no US1 files
- **User Story 3 (Phase 5)**: Depends on Foundational and on `ScanIssue` rows already being written by US1's T026; touches no US1/US2 files otherwise
- **Polish (Phase 6)**: Depends on all three user stories being complete

### Parallel Opportunities

- T003 and T004 (Setup) can run in parallel with each other
- T006, T007, T008 (Foundational models) can run in parallel with each other
- T011-T018 (US1 tests) can all run in parallel with each other
- T020-T024 (US1 parsers) can all run in parallel with each other
- T029-T031 (US1 frontend pieces) can run in parallel with each other
- Once Foundational and US1's T026 are done, US2 and US3 can be implemented in parallel by different people (each touches disjoint files except the shared `frontend/src/services/api.ts`, where each adds a separate function)

---

## Parallel Example: User Story 1

```bash
# Tests together:
Task: "Unit test for package.json parser in backend/tests/unit/test_parser_package_json.py"
Task: "Unit test for pom.xml parser in backend/tests/unit/test_parser_pom_xml.py"
Task: "Unit test for requirements.txt parser in backend/tests/unit/test_parser_requirements_txt.py"
Task: "Unit test for go.mod parser in backend/tests/unit/test_parser_go_mod.py"
Task: "Unit test for composer.json parser in backend/tests/unit/test_parser_composer_json.py"

# Parsers together (after their tests fail red):
Task: "Implement package.json parser in backend/src/scanning/parsers/package_json.py"
Task: "Implement pom.xml parser in backend/src/scanning/parsers/pom_xml.py"
Task: "Implement requirements.txt parser in backend/src/scanning/parsers/requirements_txt.py"
Task: "Implement go.mod parser in backend/src/scanning/parsers/go_mod.py"
Task: "Implement composer.json parser in backend/src/scanning/parsers/composer_json.py"
```

---

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Complete Phase 1: Setup
2. Complete Phase 2: Foundational
3. Complete Phase 3: User Story 1
4. **STOP and VALIDATE**: run the T019 integration test and the relevant quickstart.md steps
5. This is a demoable MVP: point it at real repositories and see a populated registry

### Incremental Delivery

1. Setup + Foundational → foundation ready
2. User Story 1 → validate independently → MVP demo
3. User Story 2 → validate independently → demo
4. User Story 3 → validate independently → demo
5. Polish (ADRs, READMEs, performance test, quickstart run)

## Notes

- [P] tasks touch different files with no dependency on an incomplete task
- Tests are required by Constitution Principle V — write them first, confirm they fail, then implement
- Commit after each task or logical group
- No task in this list requires a network call or an AI/ML dependency, consistent with Constitution Principles I and II
