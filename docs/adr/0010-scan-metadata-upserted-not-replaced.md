# Track last-scan time in a dedicated upserted table, not replaced wholesale

* Status: accepted
* Date: 2026-09-13

## Context and Problem Statement

The cross-feature dashboard added after all four features were functionally
complete needs to show "when did the registry scan / log scan last run" so a
user can tell whether the data on screen might be stale. Every scan-produced
table so far follows the established delete-and-repopulate pattern (ADR
0003): `session.query(X).delete()` for every row that scan produces, then
re-insert the current scan's results, all in one transaction. Should "last
run time" be stored the same way?

## Decision Drivers

* Constitution Principle IV (Deterministic & Explainable): the dashboard's
  timestamps must reflect real scan history, not be silently lost or reset.
* The registry scan and the log scan are independently triggered (feature
  003's research.md §1, reaffirmed by ADR 0007) — one running must never
  reset or clobber the other's last-run time.

## Considered Options

* Follow the delete-and-repopulate pattern used by every other scan-produced
  table.
* A dedicated `ScanMetadata` table, one row per `scan_type`, updated in
  place (`record_scan()`: fetch the existing row for this scan_type and
  update its timestamp, or insert one if this is the first run).

## Decision Outcome

Chosen option: **a dedicated table, updated in place**. "When did scan type X
last run" is a fundamentally different kind of fact than the data a scan
produces: it isn't a snapshot derived from walking files this run, it's a
monotonically-advancing fact about the scan history itself. Modeling it as
delete-then-reinsert would work but misrepresents what's actually
happening — there is exactly one row per scan type, and a rescan doesn't
"delete history and produce new history," it advances the same fact forward.
A dedicated table (rather than reusing an existing one) also follows ADR
0007's precedent of keeping independently-triggered scans' own state in
their own rows, so a log scan can never overwrite the registry scan's
timestamp or vice versa.

### Positive Consequences

* `GET /api/dashboard` reads two simple `WHERE scan_type = ...` lookups.
* Adding a future third independently-triggered scan type only means one
  more `record_scan(session, "new_type", now)` call and one more row — no
  schema change.

### Negative Consequences

* This is the first table in the schema that deliberately does *not* follow
  the delete-and-repopulate convention every other table uses. Accepted —
  the convention exists to keep scan-produced *data* consistent with "what
  the filesystem currently looks like"; this table doesn't hold scan-produced
  data, it holds a fact about the scan process, so applying the same
  convention here would be following the letter of the pattern past the
  reason it exists.

## Links

* [ADR 0003](0003-rescan-delete-and-repopulate.md) — the pattern this table deliberately doesn't follow, and why
* [ADR 0007](0007-dedicated-log-scan-issue-table.md) — the precedent for keeping independently-triggered scans' state separate
