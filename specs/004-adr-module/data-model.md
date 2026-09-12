# Phase 1 Data Model: ADR Module

## AdrRecord (new table)

One imported ADR file.

| Field | Type | Rules |
|---|---|---|
| `id` | integer, PK, autoincrement | |
| `title` | text, not null | First `# ` heading (research.md §3); a file with none is a parse failure (`AdrImportIssue`), not a record |
| `raw_status` | text, nullable | Verbatim value of the `* Status:` line, if present |
| `normalized_status` | text, not null | One of `proposed`/`accepted`/`rejected`/`deprecated`/`superseded`/`unrecognized` (research.md §4) |
| `date` | date, nullable | Parsed only if the `* Date:` line matches `YYYY-MM-DD` exactly |
| `source_path` | text, not null, unique | The ADR's own Markdown file path |
| `repository_path` | text, not null | Grandparent of the `docs/adr` directory (research.md §7) |
| `content` | text, not null | Full raw file content, verbatim |
| `has_secret_warning` | boolean, not null, default `false` | Set when any research.md §8 pattern matches |

## AdrRelationship (new table)

A directed supersedes/amends link between two ADRs.

| Field | Type | Rules |
|---|---|---|
| `id` | integer, PK, autoincrement | |
| `from_adr_id` | integer, FK → `AdrRecord.id`, not null, `ON DELETE CASCADE` | |
| `to_adr_id` | integer, FK → `AdrRecord.id`, not null, `ON DELETE CASCADE` | |
| `relationship_type` | text, not null | One of `supersedes`, `amends` |

**Direction convention**: `from_adr_id` is the ADR whose text contained the
match; e.g. a `superseded by` match on ADR A pointing to ADR B produces a
row with `from_adr_id=B`, `to_adr_id=A`, `relationship_type=supersedes`
(B supersedes A) — normalizing both "supersedes" and "superseded by"
phrasing into the same canonical direction so a detail view only has to
query `from_adr_id` / `to_adr_id` symmetrically, the same way feature
002's `ServiceConnection` is queried from both sides.

## AdrServiceAssociation (new table)

Many-to-many link between an ADR and a registered service.

| Field | Type | Rules |
|---|---|---|
| `id` | integer, PK, autoincrement | |
| `adr_id` | integer, FK → `AdrRecord.id`, not null, `ON DELETE CASCADE` | |
| `service_id` | integer, FK → `Service.id`, not null, `ON DELETE CASCADE` | |

**Uniqueness**: `(adr_id, service_id)` is unique.

## AdrImportIssue (new table)

A file that failed to parse (distinct from `has_secret_warning`, which
applies to a successfully-imported `AdrRecord`).

| Field | Type | Rules |
|---|---|---|
| `id` | integer, PK, autoincrement | |
| `path` | text, not null | |
| `reason` | text, not null | |
| `detected_at` | datetime, not null | |

## Notes

- All four tables are replaced in full within the same transaction as the
  registry/connection-graph replace (research.md §1/§2) — one `run_scan`
  call produces one consistent snapshot across all of it.
- The combined "issues and warnings" view (FR-011, User Story 3) is built
  by the API layer from two sources: `AdrImportIssue` rows (parse
  failures) and `AdrRecord` rows where `has_secret_warning` is true — not
  a single merged table, since they represent genuinely different things
  (a file that isn't an ADR at all, vs. an ADR that is one but needs a
  second look).
