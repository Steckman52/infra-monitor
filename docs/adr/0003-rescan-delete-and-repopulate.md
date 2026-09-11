# Re-scan replaces the registry by deleting and repopulating in one transaction

* Status: accepted
* Date: 2026-09-10

## Context and Problem Statement

FR-014 requires that re-running a scan makes the registry reflect the
current state of the scanned repositories: services that no longer exist
must disappear, new ones must appear, and resolved scan issues must be
cleared. How should a re-scan reconcile its results with what is already
stored?

## Decision Drivers

* Constitution Principle V (Test-First & Simplicity): prefer the simplest
  approach that satisfies the requirement over one that is only justified
  at a larger scale.
* Constitution Principle IV (Deterministic & Explainable): the registry's
  state after a scan must be fully explained by that scan's results, not by
  a mix of old and new data.
* Target scale (plan.md Performance Goals): roughly 500 manifests scanned
  in under 30 seconds.

## Considered Options

* Delete all `Service`/`Dependency`/`ScanIssue` rows and re-insert the
  current scan's results, in one transaction.
* Diff the new scan against existing rows and upsert/delete individual
  rows.

## Decision Outcome

Chosen option: **delete-and-repopulate in one transaction**. At the target
scale, a full rebuild is fast enough that there is no measurable benefit to
incremental diffing, and it trivially guarantees the registry always
matches exactly one scan's output — there is no possibility of stale rows
left over from a previous scan. Wrapping the delete and the inserts in one
transaction also means a scan that fails partway leaves the previous,
still-consistent registry state in place rather than a half-updated one.

### Positive Consequences

* FR-014/SC-005 (registry reflects current repository state after a
  re-scan) holds by construction, with no separate reconciliation logic to
  get wrong.
* Failure during a scan cannot leave the registry in a partially-updated
  state.

### Negative Consequences

* Every re-scan re-parses every manifest, even unchanged ones. Acceptable
  at the target scale; would need revisiting if the product later needed to
  scan a much larger number of repositories on every run.

## Links

* [research.md §8](../../specs/001-service-registry/research.md)
* [tasks.md T026](../../specs/001-service-registry/tasks.md)
