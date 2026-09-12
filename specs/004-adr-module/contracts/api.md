# API Contract: ADR Module

Base path: `/api`. No new scan trigger — `POST /api/scan` (features
001/002) now also populates the tables these endpoints read from.

## `POST /api/scan` (extended)

Adds one field to the existing feature-001/002 response:

```json
{
  "services_found": 12,
  "issues_found": 1,
  "unreachable_roots": [],
  "adrs_found": 7
}
```

## `GET /api/adrs`

Lists every imported ADR.

**Response** `200 OK`:
```json
[
  {
    "id": 1,
    "title": "Use SQLite instead of a client-server database",
    "normalized_status": "accepted",
    "raw_status": "accepted",
    "date": "2026-09-10",
    "source_path": "C:\\repos\\infra-tool\\docs\\adr\\0001-sqlite-over-server-db.md",
    "has_secret_warning": false
  }
]
```

## `GET /api/adrs/{id}`

Full detail for one ADR, including relationships and related services.

**Response** `200 OK`:
```json
{
  "id": 5,
  "title": "Persist error groups at scan time",
  "normalized_status": "accepted",
  "raw_status": "accepted",
  "date": "2026-09-12",
  "source_path": "C:\\repos\\infra-tool\\docs\\adr\\0006-error-groups-persisted-at-scan-time.md",
  "content": "# Persist error groups at scan time...\n...",
  "has_secret_warning": false,
  "supersedes": [],
  "superseded_by": [],
  "amends": [],
  "amended_by": [],
  "related_services": [
    { "service_id": 1, "service_name": "payments-api" }
  ]
}
```

**Response** `404 Not Found` if `id` does not exist.

## `GET /api/adr-issues`

Lists parse failures and secret warnings from the most recent scan.

**Response** `200 OK`:
```json
[
  { "type": "parse_failure", "path": "C:\\repos\\...\\docs\\adr\\broken.md", "reason": "No title heading found" },
  { "type": "secret_warning", "adr_id": 5, "path": "C:\\repos\\...\\docs\\adr\\0006-....md", "reason": "Text resembles an AWS access key" }
]
```
