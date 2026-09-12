# Phase 0 Research: Log Error Analysis & Grouping

## 1. A separate scan trigger, not an extension of `POST /api/scan`

**Decision**: A dedicated `POST /api/log-scan` endpoint with its own root
path input, independent of the repository-scanning `POST /api/scan`.

**Rationale**: FR-001 explicitly requires the log root to be independent of
repository roots. A log root is a fundamentally different kind of input (an
export of runtime output, not a source-code checkout) — folding it into the
existing `roots` parameter would conflate two unrelated concepts and force
every caller to know which kind of root they're passing.

**Alternatives considered**: Accepting an optional `log_roots` field on the
existing scan request — rejected; would make one endpoint responsible for
two independently-triggerable, independently-failing operations, and two
very different transactions.

## 2. Persist error groups at scan time, not compute-on-read

**Decision**: Unlike feature 002's dependency-compatibility view (computed
fresh on every request from already-structured rows), error groups are
computed once during the log scan and persisted.

**Rationale**: Producing a group requires re-reading and re-parsing
potentially large raw log files line by line — expensive I/O and regex
work that should not be repeated on every page view. Feature 002's
compatibility view was cheap to recompute because it only re-aggregated
data already sitting in structured `Service`/`Dependency` rows; there is no
equivalent shortcut here.

**Alternatives considered**: Re-scanning the log files on every
`GET /api/error-groups` request — rejected as unnecessary repeated I/O for
data that only changes when the user explicitly re-scans.

## 3. A dedicated `log_scan_issues` table, not reusing `scan_issues`

**Decision**: Log-scan issues (unattributed directories, unreadable files)
get their own table, separate from the registry's `scan_issues` table from
feature 001.

**Rationale**: `run_scan` (feature 001/002) replaces the entire
`scan_issues` table inside its own transaction every time it runs, and the
log scan needs to do the same for its own issues, independently. Sharing
one table would mean running either scan wipes out the other's
still-valid issue records — a subtle correctness bug, not just an
inconvenience.

**Alternatives considered**: Adding a `source` discriminator column to the
existing `scan_issues` table and filtering deletes by it — rejected;
adds conditional-delete logic to a table whose simple
"delete-all-then-repopulate" pattern (feature 001 ADR 0003) is exactly what
made it easy to reason about. Two independent tables keep both simple.

## 4. Unattributed logs are still analyzed, not skipped

**Decision**: A log file whose parent directory doesn't match a registered
service is still scanned for errors and grouped — grouped under a null
service, keyed additionally by the literal source directory path (so two
different unmatched directories never merge into one group) — *and* that
directory is separately recorded as a `log_scan_issue` (`unattributed`).

**Rationale**: Dropping the actual error content because attribution
failed would be a worse outcome than showing it under an "unattributed"
bucket — the whole point of Principle IV is that data is never silently
lost. The separate issue record still makes the attribution gap visible so
it can be fixed (e.g., by renaming the directory to match a registered
service).

**Alternatives considered**: Skip parsing entirely for unattributed
directories, only recording the issue — rejected; throws away real
analysis for a purely organizational problem (a wrong directory name) that
has nothing to do with whether the log content itself is useful.

## 5. Normalization substitution order

**Decision**: Apply substitutions most-specific-first: UUID-shaped
sequences, then hex-looking sequences (`0x...`), then quoted substrings,
then any remaining bare digit sequences last.

**Rationale**: A UUID or a hex address also contains digits; replacing bare
digits first would fragment those patterns into a mix of placeholders and
leftover characters instead of one clean substitution. Applying the most
specific pattern first and only then sweeping remaining digits avoids that.

## 6. Reuse the existing directory-exclusion list

**Decision**: The log-file walker prunes the same directory names already
excluded during manifest/compose scanning (`node_modules`, `vendor`,
`target`, `.venv`, `site-packages`, `__pycache__`, `.git`).

**Rationale**: Cheap, harmless defensive default if a user points the log
scan at a broader directory that happens to contain such folders; reuses
an already-tested rule rather than inventing a parallel one (Principle V).

## 7. Bounded occurrence storage per group

**Decision**: Store up to a fixed cap (20) example occurrences per error
group; the group's `occurrence_count` still reflects the true total even
once the cap is reached.

**Rationale**: FR-012 explicitly allows "a representative sample" rather
than requiring every occurrence to be stored. A frequently-recurring error
could otherwise generate unbounded rows for no additional analytical value
beyond the count and a representative example (Principle V).

**Alternatives considered**: Storing every occurrence — rejected;
unbounded growth with no corresponding user value once a handful of
examples have been seen.

## 8. Timestamp extraction formats

**Decision**: Try a small, fixed, ordered list of common prefixes against
the start of an entry's first line: ISO-8601 (`YYYY-MM-DDTHH:MM:SS`) and
the common log format (`YYYY-MM-DD HH:MM:SS`). First match wins; no match
leaves the occurrence's timestamp null (FR-009).

**Rationale**: Covers the overwhelming majority of real log timestamp
conventions without attempting a general-purpose date-format guesser,
consistent with Principle V.

## Outcome

All Technical Context items are resolved; no `NEEDS CLARIFICATION` markers
remain.
