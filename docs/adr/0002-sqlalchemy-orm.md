# Access SQLite through SQLAlchemy's ORM instead of raw `sqlite3`

* Status: accepted
* Date: 2026-09-10

## Context and Problem Statement

Given the decision to use SQLite ([ADR 0001](0001-sqlite-over-server-db.md)),
the backend needs a way to define and query the `Service`, `Dependency`, and
`ScanIssue` tables and their relationships (see
[data-model.md](../../specs/001-service-registry/data-model.md)). Should
this go through Python's standard-library `sqlite3` module directly, or
through an ORM?

## Decision Drivers

* Constitution Principle V (Test-First & Simplicity): pick the option that
  keeps the codebase easy to extend, not the one with the fewest
  dependencies at any cost.
* The dependency map, log analysis, and ADR modules planned for this same
  project will need to query and cross-reference this same schema.
* Constitution Principle VII (Permissive Licensing): any library used must
  carry a permissive license.

## Considered Options

* Raw `sqlite3` (standard library) with hand-written SQL
* SQLAlchemy 2.0 declarative ORM

## Decision Outcome

Chosen option: **SQLAlchemy 2.0 ORM**, because the registry's relationships
(`Service` 1—N `Dependency`, `Service` 1—N `ScanIssue`) are exactly the kind
of structure an ORM expresses more clearly than hand-written SQL, and this
schema is expected to grow as later features (dependency map, ADR
cross-references) are added. SQLAlchemy is MIT-licensed, satisfying
Principle VII.

Schema creation uses `Base.metadata.create_all()` at startup rather than a
migration framework (e.g. Alembic) — not justified yet, since there is no
production data to migrate through schema changes at this stage
(Principle V).

### Positive Consequences

* Relationships and cascading deletes are declared once on the model and
  reused by every query site.
* Easier to extend when later features need to join across these tables.

### Negative Consequences

* One additional dependency compared to the standard-library-only option.
  Accepted as a reasonable, permissively-licensed trade-off.

## Links

* [research.md §7](../../specs/001-service-registry/research.md)
