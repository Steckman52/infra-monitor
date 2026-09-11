---
description: "Task list for Dependency Map & Version Compatibility implementation"
---

# Tasks: Dependency Map & Version Compatibility

**Input**: Design documents from `specs/002-dependency-map/`
**Prerequisites**: plan.md, spec.md, research.md, data-model.md, contracts/api.md, quickstart.md
**Builds on**: feature `001-service-registry`, already fully implemented.

**Tests**: Included and ordered before implementation — required by Constitution
Principle V, same as feature 001.

**Organization**: Tasks are grouped by user story (from spec.md).

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies on incomplete tasks)
- **[Story]**: Maps the task to US1, US2, or US3 from spec.md
- File paths are relative to the repository root; `backend/`/`frontend/` already
  exist from feature 001.

---

## Phase 1: Setup (Shared Infrastructure)

- [ ] T001 [P] Add `PyYAML` to `backend/requirements.txt` (MIT-licensed, per constitution Principle VII; used via `yaml.safe_load` only, per research.md §2)
- [ ] T002 [P] Create a `docker-compose.yml` fixture scaffold at `backend/tests/integration/fixtures/compose/`: a valid file declaring two services on a shared network, one `depends_on` relationship, and one service using `image:` only (no `build:`); plus one syntactically invalid `docker-compose.yml`

---

## Phase 2: Foundational (Blocking Prerequisites)

No additional foundational work is needed: this feature builds entirely on
feature 001's existing database engine, FastAPI app, and scan orchestrator.
Proceed directly to the user stories below.

---

## Phase 3: User Story 1 - Review version compatibility across the registry (Priority: P1) 🎯 MVP

**Goal**: Compute and present compatibility status for every dependency
shared by more than one registered service — no new scanning required.

**Independent Test**: With the feature-001 registry already populated,
extend it with two services declaring the same dependency at different
major versions and one with an unparseable version, then verify the
compatibility view distinguishes all three states.

### Tests for User Story 1 ⚠️

- [ ] T003 [P] [US1] Unit test for major-version extraction in `backend/tests/unit/test_version_extraction.py` per research.md §7: `^4.18.0`→4, `~1.5.0`→1, `>=2.31.0`→2, `v1.9.1`→1, `5.3.20`→5, `${hamcrestVersion}`→not comparable
- [ ] T004 [P] [US1] Unit test for compatibility grouping/status logic in `backend/tests/unit/test_compatibility_grouping.py` per data-model.md: same-major → `compatible`; differing major → `compatibility_risk`; a not-comparable entry sets `has_not_comparable` independently of the status among the rest (Edge Case); a dependency used by only one service is excluded (FR-001)
- [ ] T005 [P] [US1] Contract test for `GET /api/dependency-compatibility` in `backend/tests/contract/test_compatibility_endpoint.py` per contracts/api.md
- [ ] T006 [US1] Integration test in `backend/tests/integration/test_compatibility.py`: scan a fixture tree containing two services sharing a dependency at different major versions and one service with a not-comparable version, then verify the computed compatibility list matches Acceptance Scenarios 1-4

### Implementation for User Story 1

- [ ] T007 [US1] Implement `extract_major_version()` in `backend/src/analysis/version_compatibility.py` per research.md §7
- [ ] T008 [US1] Implement `compute_compatibility(session)` in the same file, grouping `Dependency` rows by `(ecosystem, name)` across `Service`, per data-model.md's computed shape (depends on T007)
- [ ] T009 [US1] Implement `GET /api/dependency-compatibility` in `backend/src/api/compatibility.py` per contracts/api.md, register its router in `backend/src/main.py` (depends on T008)
- [ ] T010 [P] [US1] Implement frontend API client function `listCompatibility()` in `frontend/src/services/api.ts` per contracts/api.md
- [ ] T011 [P] [US1] Implement `CompatibilityTable` component in `frontend/src/components/CompatibilityTable.tsx`
- [ ] T012 [US1] Implement `CompatibilityPage` in `frontend/src/pages/CompatibilityPage.tsx` and add a navigation entry from `RegistryPage` (depends on T010, T011)

**Checkpoint**: User Story 1 is independently functional — this is the MVP for this feature.

---

## Phase 4: User Story 2 - Review the service connection graph (Priority: P2)

**Goal**: Scan `docker-compose.yml` files alongside the registry scan and
present the resulting connection graph, including external nodes.

**Independent Test**: Scan the fixture tree from T002 and verify the graph
shows the shared-network connection, the `depends_on` connection, and the
`image:`-only service as a distinct external node.

### Tests for User Story 2 ⚠️

- [ ] T013 [P] [US2] Unit test for the `docker-compose.yml` parser in `backend/tests/unit/test_parser_docker_compose.py` per research.md §3: `build` as a bare string and as `{context: ...}`; `networks` as a list and as a mapping; `depends_on` as a list and as a mapping — all four shape pairs must normalize to the same result
- [ ] T014 [P] [US2] Unit test for build-context-to-service matching and external-node creation in `backend/tests/unit/test_connection_graph.py` per research.md §4: a matching build path resolves to the registered service; a missing/non-matching build path produces an external node scoped to its repository (Edge Case: two same-named external nodes in different repos stay distinct)
- [ ] T015 [P] [US2] Contract test for `GET /api/connections` in `backend/tests/contract/test_connections_endpoint.py` per contracts/api.md
- [ ] T016 [US2] Integration test in `backend/tests/integration/test_connections.py`: scan the T002 fixture tree, verify the shared-network connection (Acceptance Scenario 1), the `depends_on` connection (Acceptance Scenario 2), the `image:`-only external node (Acceptance Scenario 3), and that the broken `docker-compose.yml` is isolated and reported without stopping the rest of the scan (Acceptance Scenario 4, FR-013)

### Implementation for User Story 2

- [ ] T017 [P] [US2] Create the `ExternalNode` model in `backend/src/models/external_node.py` per data-model.md: `id` PK; `name` not null; `image` nullable; `source_compose_path` not null; `repository_path` not null; unique on `(name, source_compose_path)`
- [ ] T018 [P] [US2] Create the `ServiceConnection` model in `backend/src/models/service_connection.py` per data-model.md: `id` PK; `from_service_id`/`from_external_node_id` (nullable FKs, exactly one set); `to_service_id`/`to_external_node_id` (nullable FKs, exactly one set); `relationship_basis` one of `shared_network`/`depends_on`/`both`; `source_compose_path` not null
- [ ] T019 [US2] Implement the `docker-compose.yml` parser in `backend/src/scanning/parsers/docker_compose.py`, normalizing `build`/`networks`/`depends_on` per research.md §3, raising the existing `ManifestParseError` on invalid YAML (parsed via `yaml.safe_load`)
- [ ] T020 [US2] Implement `backend/src/scanning/connection_graph.py`: resolve each compose service's build context to an absolute path, match against registered services' `repository_path` (FR-009), create `ExternalNode` rows for unmatched blocks (FR-010), and build `ServiceConnection` rows from shared networks and `depends_on`, collapsing a pair connected both ways into one `both` row (FR-011) (depends on T017, T018, T019)
- [ ] T021 [US2] Extend `run_scan` in `backend/src/scanning/scan_service.py` to also walk for `docker-compose.yml` files in the same roots, invoke `connection_graph`, and replace the `external_nodes`/`service_connections` tables in the same transaction as the registry replace (research.md §1) (depends on T020)
- [ ] T022 [US2] Implement `GET /api/connections` in `backend/src/api/connections.py` per contracts/api.md, register its router (depends on T021)
- [ ] T023 [P] [US2] Implement frontend API client function `listConnections()` in `frontend/src/services/api.ts`
- [ ] T024 [P] [US2] Implement `ConnectionGraphView` component in `frontend/src/components/ConnectionGraphView.tsx`
- [ ] T025 [US2] Implement `ConnectionsPage` in `frontend/src/pages/ConnectionsPage.tsx` and add a navigation entry from `RegistryPage` (depends on T023, T024)

**Checkpoint**: User Stories 1 AND 2 both work independently.

---

## Phase 5: User Story 3 - See a service's risks and connections in context (Priority: P3)

**Goal**: Surface a service's own compatibility risks and connections on
its existing feature-001 detail view.

**Independent Test**: With US1 and US2 already producing risks/connections,
open a service detail view for an affected service and confirm both are
visible without navigating elsewhere.

### Tests for User Story 3 ⚠️

- [ ] T026 [US3] Extend the contract test in `backend/tests/contract/test_service_detail_endpoint.py` to assert the `GET /api/services/{id}` response includes `compatibility_risks` and `connections` fields (empty arrays when none apply)
- [ ] T027 [US3] Integration test in `backend/tests/integration/test_service_detail_enrichment.py`: scan a fixture combining a compatibility risk and a compose connection for the same service, then verify both appear correctly in that service's detail data (Acceptance Scenarios 1-2)

### Implementation for User Story 3

- [ ] T028 [US3] Extend `ServiceDetail` and `get_service_detail` in `backend/src/api/services.py` to include `compatibility_risks` (via `compute_compatibility`, filtered to this service, from T008) and `connections` (via the connection graph, filtered to this service's node, from T020/T022) per contracts/api.md (depends on T008, T020)
- [ ] T029 [P] [US3] Extend the `ServiceDetail` TypeScript type in `frontend/src/services/api.ts` with `compatibility_risks` and `connections` fields
- [ ] T030 [US3] Render a "Compatibility Risks" and a "Connections" section in `frontend/src/components/ServiceDetail.tsx` (depends on T029)

**Checkpoint**: All three user stories are independently functional.

---

## Phase 6: Polish & Cross-Cutting Concerns

- [ ] T031 [P] Author `docs/adr/0004-compatibility-computed-not-persisted.md` and `docs/adr/0005-compose-scan-in-same-transaction.md` as plain MADR files per plan.md's Complexity Tracking (Constitution Principle VI)
- [ ] T032 [P] Update `backend/README.md` and `frontend/README.md` to document the two new endpoints/screens and the extended service detail response
- [ ] T033 Add a performance sanity check in `backend/tests/integration/test_compatibility_performance.py` asserting `compute_compatibility` over ~200 services with shared dependencies completes in well under 1 second (plan.md Performance Goals)
- [ ] T034 Run quickstart.md validation end-to-end and record the result

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies — start immediately
- **Foundational (Phase 2)**: Empty — nothing blocks the user stories beyond feature 001's existing foundation
- **User Story 1 (Phase 3)**: Depends on Setup only; needs no new persisted models
- **User Story 2 (Phase 4)**: Depends on Setup (needs the T002 fixtures and T001 dependency); independent of US1's files
- **User Story 3 (Phase 5)**: Depends on US1 (T008) and US2 (T020/T022) being complete — it aggregates their outputs onto the existing detail endpoint rather than duplicating logic
- **Polish (Phase 6)**: Depends on all three user stories being complete

### Parallel Opportunities

- T001 and T002 (Setup) can run in parallel
- T003-T005 (US1 tests) can run in parallel with each other
- T013-T015 (US2 tests) can run in parallel with each other
- T017 and T018 (US2 models) can run in parallel with each other
- T010/T011 (US1 frontend) and T023/T024 (US2 frontend) can run in parallel across stories once their respective backend endpoints exist
- US1 (Phase 3) and US2 (Phase 4) can be implemented in parallel by different people once Setup is done — US3 must wait for both

---

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Complete Phase 1: Setup
2. Complete Phase 3: User Story 1
3. **STOP and VALIDATE**: run T006 and the relevant quickstart.md steps — the compatibility view alone is already useful without the connection graph

### Incremental Delivery

1. Setup → foundation ready (nothing new to build)
2. User Story 1 → validate independently → demo
3. User Story 2 → validate independently → demo
4. User Story 3 → validate independently (requires 1 and 2) → demo
5. Polish (ADRs, READMEs, performance check, quickstart run)

## Notes

- [P] tasks touch different files with no dependency on an incomplete task
- Tests are required by Constitution Principle V — write them first, confirm they fail, then implement
- No task in this list requires a network call or an AI/ML dependency, consistent with Constitution Principles I and II
- `docker-compose.yml` content is parsed with `yaml.safe_load` only (research.md §2) — never the default unsafe loader
