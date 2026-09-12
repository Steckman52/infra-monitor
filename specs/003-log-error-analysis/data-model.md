# Phase 1 Data Model: Log Error Analysis & Grouping

## ErrorGroup (new table)

A distinct recurring error for one service, or for one unattributed source
directory.

| Field | Type | Rules |
|---|---|---|
| `id` | integer, PK, autoincrement | |
| `service_id` | integer, FK → `Service.id`, nullable, `ON DELETE CASCADE` | Null when unattributed |
| `unattributed_source_path` | text, nullable | Set only when `service_id` is null — the literal directory path, so two different unmatched directories never merge into one group (research.md §4) |
| `normalized_template` | text, not null | See Normalization below |
| `severity_marker` | text, not null | The specific marker that triggered detection (e.g. `ERROR`) |
| `occurrence_count` | integer, not null | True total, even beyond the stored sample cap |
| `first_seen` | datetime, nullable | Earliest occurrence with an extractable timestamp |
| `last_seen` | datetime, nullable | Latest occurrence with an extractable timestamp |
| `example_text` | text, not null | Verbatim text (including any captured continuation lines) of one representative occurrence |

**Grouping key**: `(service_id, unattributed_source_path, normalized_template)`
— unique per scan. One of `service_id` / `unattributed_source_path` is
always set, never both, never neither (enforced by construction in
`log_scan_service.py`, not a DB constraint — same approach as feature 002's
`ServiceConnection`).

## ErrorOccurrence (new table)

A bounded sample (up to 20 per group, research.md §7) of individual
captured instances.

| Field | Type | Rules |
|---|---|---|
| `id` | integer, PK, autoincrement | |
| `error_group_id` | integer, FK → `ErrorGroup.id`, not null, `ON DELETE CASCADE` | |
| `raw_text` | text, not null | Complete original text, including captured continuation lines |
| `occurred_at` | datetime, nullable | Null when no timestamp format matched (FR-009) |
| `source_log_path` | text, not null | |
| `line_number` | integer, not null | Starting line of this occurrence within its source file |

## LogScanIssue (new table)

An unattributed log directory or an unreadable log file.

| Field | Type | Rules |
|---|---|---|
| `id` | integer, PK, autoincrement | |
| `path` | text, not null | The directory (for `unattributed`) or file (for `unreadable`) |
| `issue_type` | text, not null | One of `unattributed`, `unreadable` |
| `reason` | text, not null | |
| `detected_at` | datetime, not null | |

## Notes

- All three tables are replaced in full within one transaction per log
  scan (research.md §1/§2), independent of the registry's own scan/replace
  transaction (feature 001).
- Compressed/rotated files (e.g. `.gz`) are never represented anywhere in
  this model — they are excluded from the walk entirely (FR-002), not
  recorded as an issue, since exclusion is expected, not a failure.
