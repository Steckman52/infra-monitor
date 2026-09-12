# A dedicated log_scan_issues table, not a shared one

* Status: accepted
* Date: 2026-09-12

## Context and Problem Statement

The log error analysis feature (spec
[003-log-error-analysis](../../specs/003-log-error-analysis/spec.md)) needs
to record unattributed log directories and unreadable log files. Feature
001 already has a `scan_issues` table serving an analogous purpose for the
registry scan. Should log-scan issues reuse that table, or get their own?

## Decision Drivers

* Constitution Principle IV (Deterministic & Explainable): each scan's
  results, including its issues, must be fully explained by that scan —
  never mixed with another, unrelated scan's leftovers.
* The registry scan (`POST /api/scan`) and the log scan
  (`POST /api/log-scan`) are independently triggered (research.md §1) —
  a user can run either one without the other.

## Considered Options

* A dedicated `log_scan_issues` table, replaced in its own transaction by
  `run_log_scan`.
* Reuse the existing `scan_issues` table, adding a `source` discriminator
  column to distinguish registry-scan issues from log-scan issues.

## Decision Outcome

Chosen option: **a dedicated table**. `run_scan` (feature 001) replaces the
entire `scan_issues` table every time it runs — `session.query(ScanIssue).delete()`
followed by re-inserting the current scan's issues, all in one transaction
(feature 001 ADR 0003). If log-scan issues shared that table, running
`POST /api/scan` would wipe out still-valid log-scan issues, and vice
versa — a correctness bug, not just an inconvenience, given the two scans
are meant to be fully independent (FR-001).

### Positive Consequences

* Both scans keep the simple "delete-all-then-repopulate" pattern that
  made `scan_issues` easy to reason about, without adding conditional
  delete logic keyed on a discriminator column.
* Running one scan can never silently erase the other's issue history.

### Negative Consequences

* One more table in the schema. Accepted — the alternative (a shared table
  with delete-by-discriminator logic) trades a small schema increase for a
  correctness risk that isn't worth it at this scale.

## Links

* [research.md §3](../../specs/003-log-error-analysis/research.md)
* [feature 001 ADR 0003](0003-rescan-delete-and-repopulate.md) — the pattern being kept simple
