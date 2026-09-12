# Persist error groups at scan time instead of computing on read

* Status: accepted
* Date: 2026-09-12

## Context and Problem Statement

The log error analysis feature (spec
[003-log-error-analysis](../../specs/003-log-error-analysis/spec.md)) groups
detected errors by service and normalized template. Feature 002 established
a precedent of computing a similar aggregation (dependency compatibility) on
every read rather than storing it. Should error groups follow the same
pattern?

## Decision Drivers

* Constitution Principle V (Test-First & Simplicity): avoid repeated,
  unnecessary work, but also avoid repeated, unnecessary I/O.
* Unlike feature 002's compatibility view, producing an error group requires
  re-reading and re-parsing arbitrary-sized raw log files line by line.

## Considered Options

* Persist `ErrorGroup`/`ErrorOccurrence` rows during `POST /api/log-scan`,
  the same way the registry (feature 001) persists services.
* Compute groups fresh on every `GET /api/error-groups` request, mirroring
  feature 002's `compute_compatibility`.

## Decision Outcome

Chosen option: **persist at scan time**. Feature 002's on-read computation
was cheap because it only re-aggregated data already sitting in structured
`Service`/`Dependency` rows in SQLite — a fast, in-memory operation. Here,
the input is raw, potentially large text files on disk; re-reading and
re-parsing them on every page view would repeat expensive I/O and regex
work for data that only changes when the user explicitly re-scans.

### Positive Consequences

* `GET /api/error-groups` and `GET /api/error-groups/{id}` are simple,
  fast reads of already-computed data.

### Negative Consequences

* Requires its own replace-on-rescan transaction (`log_scan_service.py`),
  parallel to feature 001's registry pattern, rather than reusing feature
  002's on-read approach uniformly across the whole project. Accepted: the
  two aggregations have genuinely different cost profiles, so they
  reasonably use different strategies.

## Links

* [research.md §2](../../specs/003-log-error-analysis/research.md)
* [ADR 0004](0004-compatibility-computed-not-persisted.md) — the contrasting decision for feature 002
