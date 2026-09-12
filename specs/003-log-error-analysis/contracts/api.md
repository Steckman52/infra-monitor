# API Contract: Log Error Analysis & Grouping

Base path: `/api`. Independent of feature 001's `POST /api/scan` — see
research.md §1.

## `POST /api/log-scan`

Scans the given root for log files, replacing all error groups,
occurrences, and log-scan issues.

**Request body**:
```json
{ "root": "C:\\logs" }
```

**Response** `200 OK`:
```json
{
  "error_groups_found": 12,
  "issues_found": 2
}
```

## `GET /api/error-groups`

Lists every error group, per service (or unattributed).

**Response** `200 OK`:
```json
[
  {
    "id": 1,
    "service_id": 1,
    "service_name": "payments-api",
    "unattributed_source_path": null,
    "normalized_template": "Connection refused: db:<NUM>",
    "severity_marker": "ERROR",
    "occurrence_count": 47,
    "first_seen": "2026-09-01T03:12:00",
    "last_seen": "2026-09-11T08:47:00"
  }
]
```

## `GET /api/error-groups/{id}`

Full detail for one group, including its sampled occurrences.

**Response** `200 OK`:
```json
{
  "id": 1,
  "service_id": 1,
  "service_name": "payments-api",
  "unattributed_source_path": null,
  "normalized_template": "Connection refused: db:<NUM>",
  "severity_marker": "ERROR",
  "occurrence_count": 47,
  "first_seen": "2026-09-01T03:12:00",
  "last_seen": "2026-09-11T08:47:00",
  "example_text": "2026-09-11 08:47:00 ERROR Connection refused: db:5432\n  at retry (db.js:42)",
  "occurrences": [
    {
      "raw_text": "2026-09-11 08:47:00 ERROR Connection refused: db:5432\n  at retry (db.js:42)",
      "occurred_at": "2026-09-11T08:47:00",
      "source_log_path": "C:\\logs\\payments-api\\app.log",
      "line_number": 1032
    }
  ]
}
```

**Response** `404 Not Found` if `id` does not exist.

## `GET /api/log-scan-issues`

Lists unattributed directories and unreadable files from the most recent
log scan.

**Response** `200 OK`:
```json
[
  {
    "id": 1,
    "path": "C:\\logs\\unknown-service",
    "issue_type": "unattributed",
    "reason": "No registered service named 'unknown-service'",
    "detected_at": "2026-09-11T12:00:00"
  }
]
```
