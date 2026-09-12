# Compute version compatibility on read instead of persisting it

* Status: accepted
* Date: 2026-09-11

## Context and Problem Statement

The dependency map feature needs to determine, for every dependency shared
by more than one registered service, whether their declared versions are
compatible (spec [002-dependency-map](../../specs/002-dependency-map/spec.md)).
Should this result be computed at scan time and stored, or computed on
demand when requested?

## Decision Drivers

* Constitution Principle V (Test-First & Simplicity): no additional
  synchronization burden if it isn't needed.
* The computation depends only on data the service registry (feature 001)
  already collects — no new scanning is required to produce it.
* Constitution Principle IV (Deterministic & Explainable): the result must
  always reflect the current registry, never a stale snapshot.

## Considered Options

* Compute fresh from `Service`/`Dependency` rows on every
  `GET /api/dependency-compatibility` request (and on-demand per service).
* Persist a `dependency_compatibility` table, recomputed and replaced
  during each scan alongside the registry.

## Decision Outcome

Chosen option: **compute on read**. The computation
(`compute_compatibility` in `backend/src/analysis/version_compatibility.py`)
groups already-loaded `Dependency` rows by `(ecosystem, name)` across
`Service` and classifies each group — a fast, purely in-memory operation at
the project's target scale (plan.md Performance Goals: well under 1 second
for a few hundred services). Persisting it would require a second write
path kept in sync with every scan and rescan, for no benefit at this scale.

### Positive Consequences

* Cannot go stale: there is no cached copy to invalidate. A `GET` right
  after any external change (e.g. a manually edited dependency, if that
  were ever exposed) already reflects it — no rescan needed even
  conceptually.
* No new database table, no delete-and-repopulate transaction to keep
  correct.

### Negative Consequences

* Recomputed on every request rather than served from a pre-aggregated
  table. Acceptable — this project's registry size makes the recomputation
  cost negligible, and it also has to run at scan time inside the service
  detail endpoint (002 US3), effectively already computed twice as
  frequently as a "once per scan" table would have been.

## Links

* [research.md §6](../../specs/002-dependency-map/research.md)
* [data-model.md](../../specs/002-dependency-map/data-model.md) — "Dependency Compatibility (computed, not persisted)"
