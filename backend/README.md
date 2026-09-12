# Backend — Service Registry & Dependency Map

Python/FastAPI backend. Scans repository paths for package-manager
manifests (`package.json`, `pom.xml`, `requirements.txt`, `go.mod`,
`composer.json`) and `docker-compose.yml` files, resolving each manifest
into a service entry and each compose file into a connection graph, all
stored in a local SQLite database. See
[specs/001-service-registry](../specs/001-service-registry/) and
[specs/002-dependency-map](../specs/002-dependency-map/) for the full
specifications, plans, and data models, and [docs/adr](../docs/adr/) for
the architectural decisions behind this backend.

## Structure

* `src/scanning/` — directory walker, one parser per manifest/compose
  format under `parsers/`, name resolution (FR-004), the `connection_graph`
  matcher, and the `scan_service` orchestrator that ties all of it together
  in one transaction.
* `src/analysis/` — `version_compatibility.py`: major-version extraction
  and compatibility grouping, computed on read (not persisted).
* `src/models/` — SQLAlchemy models: `Service`, `Dependency`, `ScanIssue`,
  `ExternalNode`, `ServiceConnection`.
* `src/api/` — FastAPI routers: `scan.py`, `services.py`, `scan_issues.py`,
  `compatibility.py`, `connections.py`.
* `src/db.py` — SQLite engine/session setup.

## Public interface

See
[specs/001-service-registry/contracts/api.md](../specs/001-service-registry/contracts/api.md)
and
[specs/002-dependency-map/contracts/api.md](../specs/002-dependency-map/contracts/api.md)
for the full request/response contract of every endpoint:

* `POST /api/scan` — scan the given root paths, replacing the registry,
  scan issues, external nodes, and connections together.
* `GET /api/services` — list registered services.
* `GET /api/services/{id}` — a service's full detail: dependencies, its own
  compatibility risks, and its own connections.
* `GET /api/scan-issues` — manifests/compose files that failed to parse or
  were incomplete.
* `GET /api/dependency-compatibility` — every dependency shared by more
  than one service, with a compatibility status.
* `GET /api/connections` — the full service/external-node connection graph
  derived from `docker-compose.yml`.

## Running locally

```bash
python -m venv .venv
. .venv/Scripts/activate   # or: source .venv/bin/activate
pip install -r requirements.txt
uvicorn src.main:app --reload --port 8000
```

## Testing

```bash
pytest
```
