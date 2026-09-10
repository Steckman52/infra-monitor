# Phase 1 Data Model: Service Registry

## Service

Represents one manifest discovered during a scan.

| Field | Type | Rules |
|---|---|---|
| `id` | integer, PK, autoincrement | |
| `name` | text, not null | Derived per FR-004 priority chain; never empty |
| `ecosystem` | text, not null | One of: `node`, `java`, `python`, `go`, `php` |
| `repository_path` | text, not null | Path to the repository root the manifest was found in |
| `manifest_path` | text, not null, unique | Full path to the source manifest file — one manifest = one service (FR-005); uniqueness also drives rescan replacement |
| `is_complete` | boolean, not null, default `true` | `false` marks a "data incomplete" entry per FR-009 |
| `last_scanned_at` | datetime, not null | Timestamp of the scan run that (re)produced this row |

**Relationships**: one `Service` has many `Dependency` rows (cascade delete) and may
be referenced by zero or more `ScanIssue` rows (for the `incomplete_data` case).

## Dependency

Represents one direct dependency declared by a service's manifest.

| Field | Type | Rules |
|---|---|---|
| `id` | integer, PK, autoincrement | |
| `service_id` | integer, FK → `Service.id`, not null, `ON DELETE CASCADE` | |
| `name` | text, not null | Dependency name as written in the manifest |
| `declared_version` | text, nullable | Verbatim version string from the manifest; `null` if the manifest declares a dependency with no version (edge case) |

## ScanIssue

Represents a manifest that failed to parse, or parsed with missing data.

| Field | Type | Rules |
|---|---|---|
| `id` | integer, PK, autoincrement | |
| `manifest_path` | text, not null | Path to the problematic manifest |
| `repository_path` | text, not null | Path to the repository root |
| `issue_type` | text, not null | One of: `unparsable`, `incomplete_data`, `unreachable_path` |
| `reason` | text, not null | Human-readable, specific failure reason (FR-008) |
| `service_id` | integer, FK → `Service.id`, nullable, `ON DELETE CASCADE` | Set only for `incomplete_data`, linking the issue to the degraded `Service` row it produced (User Story 3, Acceptance Scenario 2) |
| `detected_at` | datetime, not null | Timestamp of the scan run that detected this issue |

## Notes

- `unreachable_path` (FR-010, a root path that does not exist/is unreadable) is
  modeled as a `ScanIssue` with no `manifest_path` value (the specified root path is
  stored in `repository_path` instead) and no `service_id`, since no manifest was
  ever reached to produce a service.
- Name-collision disambiguation (FR-004 rule 3, Edge Cases) happens in the scanning
  logic before insertion — by the time a row is written, `name` is already
  collision-free; no separate table is needed to track this.
- Every rescan replaces the full contents of all three tables inside one
  transaction (see research.md §8) — there is no `updated_at`/versioning field
  because there is no partial-update path to distinguish.
