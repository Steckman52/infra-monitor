# Scan docker-compose.yml inside the same transaction as the registry scan

* Status: accepted
* Date: 2026-09-11

## Context and Problem Statement

The dependency map feature's connection graph (spec
[002-dependency-map](../../specs/002-dependency-map/spec.md), User Story 2)
is built by additionally scanning `docker-compose.yml` files and matching
their service blocks to registered `Service` rows by build-context path.
Should this run as part of the existing `POST /api/scan` operation, or as
its own, separately-triggered scan?

## Decision Drivers

* FR-009 requires matching a compose service block to a registered
  `Service` by that service's `repository_path` — this only works
  correctly if both the registry and the connection graph describe the
  *same* scan snapshot.
* Constitution Principle IV (Deterministic & Explainable): the connection
  graph's correctness depends entirely on matching against a consistent
  registry state.
* Constitution Principle II (Local-First & Resilient) implicitly favors
  fewer moving parts a user has to operate correctly.

## Considered Options

* Extend `run_scan` (`backend/src/scanning/scan_service.py`) to also walk
  for `docker-compose.yml` and build the connection graph, all inside the
  one transaction that already replaces the registry.
* A second, independently-triggered endpoint/scan specifically for
  `docker-compose.yml` files.

## Decision Outcome

Chosen option: **one transaction, one scan**. `run_scan` now walks for
both manifests and `docker-compose.yml` files in the same pass, builds the
in-memory `Service` objects first, then matches compose blocks against
them by resolved build-context path before anything is committed. All of
`services`, `dependencies`, `scan_issues`, `external_nodes`, and
`service_connections` are replaced together in one commit.

A second, separate scan trigger would let a user run one without the
other, producing a connection graph that references services from a
different (older or newer) scan than the one currently displayed —
silently violating the exact invariant FR-009's matching logic depends on.

### Positive Consequences

* The connection graph can never reference a stale or mismatched registry
  snapshot — matching happens against services from the exact same scan.
* One user-facing action ("scan") instead of two to remember.

### Negative Consequences

* `run_scan` grew a second responsibility (compose scanning) alongside
  manifest scanning. Mitigated by keeping the compose-specific logic in
  its own modules (`scanning/parsers/docker_compose.py`,
  `scanning/connection_graph.py`) that `run_scan` merely orchestrates,
  rather than inlining it.

## Links

* [research.md §1](../../specs/002-dependency-map/research.md)
* [tasks.md T021](../../specs/002-dependency-map/tasks.md)
