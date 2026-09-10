# API Contract: Service Registry

Base path: `/api`. All responses are JSON. No authentication in this version — the
server is bound to `localhost` only (Principle II).

## `POST /api/scan`

Triggers a scan of the currently configured root paths, replacing the registry
contents (see research.md §8).

**Request body**:
```json
{ "roots": ["C:\\repos\\team-a", "C:\\repos\\team-b"] }
```

**Response** `200 OK`:
```json
{
  "services_found": 42,
  "issues_found": 3,
  "unreachable_roots": []
}
```

`unreachable_roots` lists any requested root path that could not be read (FR-010);
the scan still proceeds for the remaining roots.

## `GET /api/services`

Lists all registered services (complete and incomplete).

**Response** `200 OK`:
```json
[
  {
    "id": 1,
    "name": "payments-api",
    "ecosystem": "node",
    "repository_path": "C:\\repos\\team-a\\payments",
    "is_complete": true
  }
]
```

## `GET /api/services/{id}`

Returns full detail for one service, including its dependencies.

**Response** `200 OK`:
```json
{
  "id": 1,
  "name": "payments-api",
  "ecosystem": "node",
  "repository_path": "C:\\repos\\team-a\\payments",
  "manifest_path": "C:\\repos\\team-a\\payments\\package.json",
  "is_complete": true,
  "last_scanned_at": "2026-09-10T12:00:00Z",
  "dependencies": [
    { "name": "express", "declared_version": "^4.18.0" }
  ]
}
```

**Response** `404 Not Found` if `id` does not exist.

## `GET /api/scan-issues`

Lists all scan issues from the most recent scan.

**Response** `200 OK`:
```json
[
  {
    "id": 1,
    "manifest_path": "C:\\repos\\team-b\\broken\\package.json",
    "repository_path": "C:\\repos\\team-b\\broken",
    "issue_type": "unparsable",
    "reason": "Invalid JSON: Expecting ',' delimiter at line 12",
    "service_id": null,
    "detected_at": "2026-09-10T12:00:00Z"
  }
]
```
