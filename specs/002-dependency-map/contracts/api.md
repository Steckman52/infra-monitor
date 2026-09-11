# API Contract: Dependency Map & Version Compatibility

Base path: `/api`. Extends the contract from
[specs/001-service-registry/contracts/api.md](../../001-service-registry/contracts/api.md).
No new scan trigger — `POST /api/scan` (feature 1) now also populates the
tables these endpoints read from.

## `GET /api/dependency-compatibility`

Lists every dependency shared by more than one service, with its
compatibility status.

**Response** `200 OK`:
```json
[
  {
    "name": "lodash",
    "ecosystem": "node",
    "status": "compatibility_risk",
    "has_not_comparable": false,
    "entries": [
      { "service_id": 1, "service_name": "payments-api", "declared_version": "^4.17.21", "major_version": 4 },
      { "service_id": 7, "service_name": "legacy-worker", "declared_version": "^3.10.0", "major_version": 3 }
    ]
  }
]
```

## `GET /api/connections`

Lists every node (registered service or external node) and the nodes it
connects to.

**Response** `200 OK`:
```json
[
  {
    "node": { "type": "service", "id": 1, "name": "payments-api" },
    "connections": [
      { "node": { "type": "external", "id": 3, "name": "postgres" }, "relationship_basis": "depends_on" },
      { "node": { "type": "service", "id": 2, "name": "orders-api" }, "relationship_basis": "shared_network" }
    ]
  },
  {
    "node": { "type": "external", "id": 3, "name": "postgres" },
    "connections": [
      { "node": { "type": "service", "id": 1, "name": "payments-api" }, "relationship_basis": "depends_on" }
    ]
  }
]
```

## `GET /api/services/{id}` (extended)

Adds two fields to the existing feature-1 response, both empty arrays when
the service has no risks/connections:

```json
{
  "id": 1,
  "name": "payments-api",
  "...": "...(unchanged fields from feature 1)...",
  "compatibility_risks": [
    { "name": "lodash", "ecosystem": "node", "declared_version": "^4.17.21", "conflicting_with": [{ "service_id": 7, "service_name": "legacy-worker", "declared_version": "^3.10.0" }] }
  ],
  "connections": [
    { "node": { "type": "external", "id": 3, "name": "postgres" }, "relationship_basis": "depends_on" }
  ]
}
```
