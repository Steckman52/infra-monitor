# Phase 0 Research: Service Registry

## 1. `go.mod` parsing approach

**Decision**: Parse `go.mod` with a small hand-written line-oriented parser that
reads the `module` directive (for the service name/import path) and `require`
lines/blocks (for dependency name + version).

**Rationale**: The `go.mod` grammar actually used by this feature (module path,
require entries) is small and stable. A hand-written parser keeps the logic fully
deterministic and inspectable (Principle IV), with zero extra dependency to vet for
license/maintenance risk (Principle VII).

**Alternatives considered**: A third-party `go.mod` parser package — rejected for
this scope; the marginal robustness gain (handling `replace`/`exclude` directives we
don't need yet) doesn't justify an extra dependency for a diploma-scoped feature.

## 2. `pom.xml` parsing approach

**Decision**: Python's standard-library `xml.etree.ElementTree` to read
`groupId`, `artifactId`, and the `<dependencies>` block.

**Rationale**: Stdlib, zero extra dependency, sufficient for well-formed Maven POMs.
Matches Principle V (simplicity) — no need for XPath-heavy libraries at this scale.

**Alternatives considered**: `lxml` — rejected; adds a compiled dependency for
speed/XPath features not needed for manifest-sized XML files.

## 3. `requirements.txt` parsing approach

**Decision**: A small regex-based line parser that splits each non-comment,
non-flag line into a package name and an optional version specifier
(`==`, `>=`, `<=`, `~=`, etc.), consistent with Principle I (rule/regex-based
analysis only, no ML anywhere).

**Rationale**: Covers the common case directly from company codebases without an
extra dependency. Lines that don't match the expected shape (e.g., `-r other.txt`,
`-e .`, environment markers) are treated as non-dependency lines and skipped, not as
parse failures for the whole file.

**Alternatives considered**: A dedicated `requirements.txt` parser package —
rejected as unnecessary weight for a well-understood, simple line format.

## 4. `package.json` / `composer.json` parsing approach

**Decision**: Standard-library `json` module.

**Rationale**: Both are plain JSON; no reason to introduce anything beyond stdlib.

## 5. Directory traversal & exclusion strategy

**Decision**: `os.walk(..., topdown=True)`, pruning excluded directory names
(`node_modules`, `vendor`, `target`, `.venv`, `site-packages`, `__pycache__`, `.git`)
in-place from the `dirnames` list so the walk never descends into them.

**Rationale**: Pruning during the walk (rather than filtering discovered manifests
afterward) keeps scans fast on repositories with large vendored/installed
dependency trees, directly supporting the performance goal in Technical Context.

**Alternatives considered**: Filtering results after a full recursive walk —
rejected; wastes time descending into directories that can be enormous
(`node_modules` in particular) for no benefit.

## 6. Scan concurrency

**Decision**: Synchronous, sequential scan.

**Rationale**: At the target scale (low thousands of manifests), sequential I/O is
fast enough to meet the performance goal; concurrency would add complexity
(thread/async coordination, partial-failure aggregation) not justified at this
scope (Principle V).

**Alternatives considered**: `asyncio`-based concurrent file reads — rejected as
premature optimization.

## 7. Persistence layer

**Decision**: SQLAlchemy 2.0 declarative ORM models over a single SQLite file,
with the schema created via `Base.metadata.create_all()` on startup (no separate
migration tool).

**Rationale**: The ORM makes the `Service` → `Dependency` and `Service` →
`ScanIssue` relationships easy to query and will be reused by the Dependency Map
feature's queries. A migration framework (e.g., Alembic) is not justified yet: the
schema is expected to change infrequently, and `create_all()` is sufficient while
there is no production data to migrate (Principle V).

**Alternatives considered**: Raw `sqlite3` + hand-written SQL — rejected; harder to
extend cleanly across the three remaining features that will share this database.

## 8. Re-scan / idempotency strategy

**Decision**: Each scan runs inside a single database transaction that deletes all
previously scanned `Service`, `Dependency`, and `ScanIssue` rows and re-inserts the
current scan's results, committing only once the full scan completes successfully.

**Rationale**: Directly satisfies FR-014/SC-005 (registry reflects current
repository state after a re-scan, resolved issues disappear) without needing
per-manifest diff/upsert logic. Wrapping in one transaction also means a scan that
fails partway leaves the previous registry state intact rather than a half-updated
one.

**Alternatives considered**: Incremental upsert per manifest — rejected as
unnecessary complexity for this scale; full rebuild is fast enough.

## 9. API shape

**Decision**: `POST /api/scan` (trigger a scan, returns a summary count), 
`GET /api/services` (list), `GET /api/services/{id}` (detail with dependencies), 
`GET /api/scan-issues` (list).

**Rationale**: One resource per concept from data-model.md keeps each contract
small and independently testable, matching the three user stories' independent
acceptance tests.

**Alternatives considered**: A single combined "everything" endpoint — rejected;
would couple the three user stories' frontend views unnecessarily.

## Outcome

All Technical Context items are resolved; no `NEEDS CLARIFICATION` markers remain.
