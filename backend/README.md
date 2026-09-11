# Backend — Service Registry

Python/FastAPI backend that scans repository paths for package-manager
manifests (`package.json`, `pom.xml`, `requirements.txt`, `go.mod`,
`composer.json`), resolves each into a service entry, and stores the
result in a local SQLite database. See
[specs/001-service-registry](../specs/001-service-registry/) for the full
specification, plan, and data model, and [docs/adr](../docs/adr/) for the
architectural decisions behind this module.

## Structure

* `src/scanning/` — directory walker, one parser per manifest format under
  `parsers/`, name resolution (FR-004), and the `scan_service` orchestrator
  that ties them together.
* `src/models/` — SQLAlchemy models: `Service`, `Dependency`, `ScanIssue`.
* `src/api/` — FastAPI routers: `scan.py`, `services.py`, `scan_issues.py`.
* `src/db.py` — SQLite engine/session setup.

## Public interface

See [specs/001-service-registry/contracts/api.md](../specs/001-service-registry/contracts/api.md)
for the full request/response contract of every endpoint:

* `POST /api/scan` — scan the given root paths, replacing the registry.
* `GET /api/services` — list registered services.
* `GET /api/services/{id}` — a service's full detail, including dependencies.
* `GET /api/scan-issues` — manifests that failed to parse or were incomplete.

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
