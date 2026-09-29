# Backend — Service Registry, Dependency Map, Log Error Analysis & ADR Module

Python/FastAPI backend. Scans repository paths for package-manager
manifests (`package.json`, `pom.xml`, `requirements.txt`, `go.mod`,
`composer.json`), `docker-compose.yml` files, and `docs/adr/*.md` files,
resolving each manifest into a service entry, each compose file into a
connection graph, and each Markdown file into an imported ADR record with
its supersedes/amends relationships and related services. Independently,
scans a local log directory, attributing files to registered services and
grouping recurring errors. All of it stored in a local SQLite database. See
[specs/001-service-registry](../specs/001-service-registry/),
[specs/002-dependency-map](../specs/002-dependency-map/),
[specs/003-log-error-analysis](../specs/003-log-error-analysis/), and
[specs/004-adr-module](../specs/004-adr-module/) for the full
specifications, plans, and data models, and [docs/adr](../docs/adr/) for
the architectural decisions behind this backend.

## Structure

* `src/scanning/` — directory walker, one parser per manifest/compose/ADR
  format under `parsers/`, name resolution (FR-004), the `connection_graph`
  matcher, `adr_relationships.py` (supersedes/amends detection and
  dedup), `adr_secrets.py` (secret-pattern heuristic), the `scan_service`
  orchestrator (repository scan, one transaction, now covering the
  registry, connections, and ADRs together), `error_detection.py`/
  `normalization.py`, `pii_redaction.py` (strips email-shaped substrings
  from stored log text, per Principle III — see
  [ADR 0011](../docs/adr/0011-redact-emails-not-ips-from-log-text.md)),
  and the `log_scan_service` orchestrator (log scan, its own independent
  transaction).
* `src/analysis/` — `version_compatibility.py`: version extraction and
  compatibility grouping, computed on read (not persisted). Versions are
  compared on major alone, except while major is `0`, where SemVer makes
  the minor the breaking-change boundary and it is compared too.
* `src/models/` — SQLAlchemy models: `Service`, `Dependency`, `ScanIssue`,
  `ExternalNode`, `ServiceConnection`, `ErrorGroup`, `ErrorOccurrence`,
  `LogScanIssue`, `AdrRecord`, `AdrRelationship`, `AdrServiceAssociation`,
  `AdrImportIssue`.
* `src/api/` — FastAPI routers: `scan.py`, `services.py`, `scan_issues.py`,
  `compatibility.py`, `connections.py`, `log_scan.py`, `error_groups.py`,
  `log_scan_issues.py`, `adrs.py`, `adr_issues.py`, `dashboard.py`,
  `filesystem.py`.
* `src/db.py` — SQLite engine/session setup, and a startup check that refuses
  a database written by an older schema instead of failing later on every read.
* `src/config.py` — the `INFRA_MONITOR_*` environment variables (see the
  root README), each with a default that needs no configuration.

## Public interface

See the `contracts/api.md` file under each feature's spec directory for the
full request/response contract of every endpoint:

* `POST /api/scan` — scan the given repository root paths, replacing the
  registry, scan issues, external nodes, connections, and ADRs (records,
  relationships, service associations, import issues) together.
* `GET /api/services` — list registered services.
* `GET /api/services/{id}` — a service's full detail: dependencies, its own
  compatibility risks, and its own connections.
* `GET /api/scan-issues` — manifests/compose files that failed to parse or
  were incomplete.
* `GET /api/dependency-compatibility` — every dependency shared by more
  than one service, with a compatibility status.
* `GET /api/connections` — the full service/external-node connection graph
  derived from `docker-compose.yml`.
* `POST /api/log-scan` — scan a local log directory, independent of the
  repository scan.
* `GET /api/error-groups` / `GET /api/error-groups/{id}` — grouped,
  deduplicated errors per service, with drill-down detail.
* `GET /api/log-scan-issues` — unattributed log directories and unreadable
  log files.
* `GET /api/adrs` — list every imported ADR.
* `GET /api/adrs/{id}` — an ADR's full detail: content, its
  supersedes/superseded_by/amends/amended_by relationships, and related
  services.
* `GET /api/adr-issues` — ADR files that failed to parse, and imported ADRs
  flagged for resembling a secret.
* `GET /api/dashboard` — the cross-feature counts and last-scan timestamps
  the overview screen is built from.
* `GET /api/pick-directory` — opens a native folder-selection dialog on the
  machine running the backend and returns the chosen path, so scan roots
  can be picked instead of typed. Only meaningful because this tool's
  backend and browser always run on the same machine (Principle II).

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
