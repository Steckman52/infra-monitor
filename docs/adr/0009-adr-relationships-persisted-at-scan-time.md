# Persist ADR records, relationships, and service associations at scan time

* Status: accepted
* Date: 2026-09-13

## Context and Problem Statement

The ADR module (spec
[004-adr-module](../../specs/004-adr-module/spec.md)) needs to produce ADR
records, their supersedes/amends relationships, and their many-to-many
associations with registered services. Feature 002 established a precedent
of computing a similar cross-referencing view (dependency compatibility) on
every read rather than storing it (ADR 0004). Should ADR data follow that
pattern?

## Decision Drivers

* Constitution Principle V (Test-First & Simplicity): avoid repeated,
  unnecessary work, but also avoid repeated, unnecessary I/O and text
  processing.
* Unlike feature 002's compatibility view, producing an ADR record requires
  reading and regex-parsing arbitrary Markdown files from disk, then
  resolving cross-file link references against every other ADR in the
  scan — real I/O and text work, not a cheap re-aggregation of rows already
  in SQLite.

## Considered Options

* Persist `AdrRecord`/`AdrRelationship`/`AdrServiceAssociation` rows during
  `POST /api/scan`, the same way the registry (feature 001) and error
  groups (feature 003, ADR 0006) persist their results.
* Compute all three fresh on every `GET /api/adrs*` request, mirroring
  feature 002's `compute_compatibility`.

## Decision Outcome

Chosen option: **persist at scan time**. The same reasoning already applied
to feature 003's error groups applies here: feature 002's on-read
computation is cheap specifically because its inputs are already
structured `Service`/`Dependency` rows in SQLite. Here, the inputs are raw
Markdown files that must be read and regex-parsed, and relationship
resolution requires comparing every ADR's link targets against every other
ADR's path in the same scan — work that should happen once per scan, not
once per page view.

### Positive Consequences

* `GET /api/adrs`, `GET /api/adrs/{id}`, and `GET /api/adr-issues` are
  simple, fast reads of already-computed data.
* Relationship and association data is guaranteed consistent with the ADR
  records it references, since both are produced and replaced in the same
  transaction (data-model.md Notes).

### Negative Consequences

* Four tables are replaced in full on every scan rather than one on-read
  computation reusing already-persisted rows. Accepted — the same trade
  feature 003 already made, for the same reason: the cost profile of
  parsing raw files from disk is fundamentally different from aggregating
  rows already in the database.

## Links

* [research.md §2](../../specs/004-adr-module/research.md)
* [ADR 0004](0004-compatibility-computed-not-persisted.md) — the contrasting decision for feature 002
* [ADR 0006](0006-error-groups-persisted-at-scan-time.md) — the same decision made for feature 003
