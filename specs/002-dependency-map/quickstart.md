# Quickstart: Dependency Map & Version Compatibility

Validates this feature end-to-end against the acceptance scenarios in
[spec.md](./spec.md). Assumes the feature 1 backend/frontend are already
runnable (see
[specs/001-service-registry/quickstart.md](../001-service-registry/quickstart.md)).

## Prerequisites

- The feature 1 fixture tree, extended with:
  - Two services that already share a dependency at different major
    versions (for the compatibility view)
  - A `docker-compose.yml` declaring: two services on a shared network,
    one `depends_on` relationship, and a service using `image:` only (no
    `build:`) to produce an external node
  - One syntactically invalid `docker-compose.yml`

## Setup

Same as feature 1 — `uvicorn src.main:app --reload` and `npm run dev`, no
new setup steps.

## Validation steps

1. Run a scan against the extended fixture tree (same `POST /api/scan` /
   scan button as feature 1 — no separate trigger for this feature).
2. Open the Dependency Compatibility view. **Expect** (User Story 1): the
   shared dependency with differing major versions shows as
   `compatibility_risk` with both services and their exact versions
   listed; a dependency with a not-comparable version is flagged
   separately, not silently marked compatible.
3. Open the Connections view. **Expect** (User Story 2): the two
   network-sharing services show a connection; the `depends_on`
   relationship shows a connection even without a shared network; the
   `image:`-only service appears as a distinct external node, not omitted.
4. Check that the invalid `docker-compose.yml` did not stop the rest of
   the scan, and that its failure is recorded with a specific reason
   (consistent with how feature 1 reports unparsable manifests).
5. Open one of the affected services' detail view (feature 1 screen).
   **Expect** (User Story 3): its compatibility risk and its connections
   are both visible there, without navigating to the separate views.
6. Change the `docker-compose.yml` topology (remove the shared network)
   and re-run the scan. **Expect** (SC-005): the connection graph reflects
   the change.

## Out of scope for this quickstart

- Kubernetes-derived connections (feature deferred per spec Assumptions).
- Full semantic version range intersection (feature deferred per spec
  Assumptions — only major-version comparison is validated here).

## Validation record

Last run 2026-09-11: steps 1-5 verified manually in-browser using
`backend/tests/integration/fixtures/compose/` and the
`repo-shared-dep-*`/`repo-enriched-*` fixtures (see feature commit history);
step 6 (re-scan reflects a removed connection) verified via the automated
`test_rescan_removes_connection_after_topology_change` integration test,
not manually re-run in-browser. All 61 backend tests pass, including the
`test_compatibility_computation_is_fast_at_scale` performance check (200
services, well under the 1-second target).
