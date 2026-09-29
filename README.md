# Infrastructure Monitoring Tool

A local-first tool for keeping track of what a team's infrastructure
actually consists of. Point it at the repositories and log directories you
already have on disk, and it builds a picture of them: which services
exist, which dependency versions disagree with each other, how services
connect, which errors keep recurring, and which architectural decisions
were recorded about them.

Everything runs on one machine against the local filesystem. There is no
network access, no telemetry, no external service, and no account — the
data never leaves the computer it was scanned on.

## What it does

Four features, each independently usable:

* **Service registry** — walks the repository roots you give it and
  registers every service it finds from its package manifest
  (`package.json`, `pom.xml`, `requirements.txt`, `go.mod`,
  `composer.json`). Manifests that are malformed or incomplete are
  reported as scan issues rather than silently skipped.
* **Dependency map** — flags dependencies shared by more than one service
  whose declared versions disagree, and derives a connection graph between
  services from `docker-compose.yml` networks and `depends_on` entries.
* **Log error analysis** — scans a local log directory, attributes files to
  registered services, and groups recurring errors by normalising the
  variable parts (timestamps, IDs, numbers) out of each message. Email
  addresses are redacted before anything is stored.
* **ADR module** — imports Markdown ADRs from `docs/adr/`, resolves their
  supersedes/amends relationships, links them to the services they concern,
  and flags any whose content resembles a leaked secret.

A dashboard ties the four together: what currently needs attention, and
when each scan last ran. The interface is available in English and Russian.

## Running it

One command. It creates the Python environment and builds the interface the
first time, then serves the interface and the API together from a single
process.

```bash
run.cmd
```

On macOS or Linux, use `./run.sh` instead. Then open
**http://localhost:8000**.

Requires Python 3.12+ and Node 20.19+ (or 22.12+, as Vite 8 needs) — Node
only for the one-off interface build. The database is a SQLite file created
on first run at `backend/data/registry.db`; deleting it resets everything.

<details>
<summary>Running the two processes separately, for frontend development</summary>

```bash
cd backend && uvicorn src.main:app --reload --port 8000
```

```bash
cd frontend && npm run dev
```

Vite then serves the interface on `http://localhost:5173` with hot reload,
proxying `/api/*` to the backend.
</details>

## Configuration

Nothing needs configuring to run it. For the cases that come up in practice,
these environment variables are read at startup:

| Variable | Default | Purpose |
|---|---|---|
| `INFRA_MONITOR_DB_PATH` | `backend/data/registry.db` | Where the database lives |
| `INFRA_MONITOR_MAX_DIRECTORIES` | `50000` | Directories visited per scan root; hitting it is reported, never silent |
| `INFRA_MONITOR_MAX_LOG_FILE_MB` | `200` | Larger log files are skipped and reported |
| `INFRA_MONITOR_EXCLUDED_DIRS` | — | Extra directory names to skip, comma-separated (e.g. `.gradle,Pods,build`) |
| `INFRA_MONITOR_ALLOWED_HOSTS` | — | Extra hostnames the API answers to, beyond `localhost` |
| `INFRA_MONITOR_PORT` | `8000` | Port used by `run.cmd` / `run.sh` |

The API has no authentication: it is meant for one person on their own
machine and only answers requests addressed to `localhost`. Don't expose it
on a network interface.

## Tests

```bash
cd backend && pytest
cd frontend && npm test
```

The backend suite covers the parsers against real-world formats, the scan
orchestration and its failure modes, the analysis functions, and every API
endpoint's contract. CI runs both suites and the production build on every
push.

## How it is built

* **Backend** — Python, FastAPI, SQLAlchemy, SQLite. See
  [backend/README.md](backend/README.md) for the module layout and the full
  endpoint list.
* **Frontend** — React, TypeScript, Vite. See
  [frontend/README.md](frontend/README.md).

The project was developed spec-first: every feature has a specification,
an implementation plan, and a task breakdown under [specs/](specs/), written
before the code. Design decisions that were not obvious in hindsight are
recorded as ADRs in [docs/adr/](docs/adr/) — the tool's own ADR module reads
them, so the project is its own test subject.

Development is governed by a
[constitution](.specify/memory/constitution.md) whose principles constrain
what the tool may do. Three of them shape it most visibly:

* **No AI/ML.** Every result is produced by explicit rules. Error grouping
  is regex normalisation, not clustering; version conflicts are version
  comparison, not prediction. Anything the tool reports can be traced to a
  specific line in a specific file.
* **Local-first.** No network access at any point, and a failure in one
  file never aborts a scan — it is reported and the scan continues.
* **No personal data.** Email addresses and credential values are redacted
  from anything the tool stores, log text and ADR content alike. IP
  addresses deliberately are not, since they are operationally necessary —
  the reasoning, and the limits of the redaction, are recorded in
  [ADR 0011](docs/adr/0011-redact-emails-not-ips-from-log-text.md).

## License

[MIT](LICENSE).
