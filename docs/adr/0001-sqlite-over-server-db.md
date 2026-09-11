# Use SQLite instead of a client-server database

* Status: accepted
* Date: 2026-09-10

## Context and Problem Statement

The service registry (and the dependency map, log analysis, and ADR modules
planned after it) need persistent, queryable storage with relational
integrity (services, dependencies, scan issues, and later cross-references
between them). What storage engine should the product use?

## Decision Drivers

* Constitution Principle II (Local-First & Resilient): the system must run
  entirely locally, without requiring a separately managed service.
* Constitution Principle V (Test-First & Simplicity): avoid infrastructure
  not justified by the project's actual scale.
* The tool is meant to be installed and run by a single engineer/architect
  on a workstation, not operated as a multi-tenant service.

## Considered Options

* SQLite (embedded, single file)
* PostgreSQL (client-server)
* MySQL/MariaDB (client-server)

## Decision Outcome

Chosen option: **SQLite**, because it requires no separate server process
to install, configure, or keep running, stores the entire registry as one
portable file, and is more than sufficient for the target scale (tens to a
few hundred repositories, low thousands of manifests — see plan.md's
Performance Goals).

### Positive Consequences

* Zero deployment/ops burden — satisfies Principle II directly.
* The whole registry can be copied, backed up, or reset by copying/deleting
  one file.

### Negative Consequences

* Write concurrency is limited compared to a client-server database. Not a
  concern here: scans are triggered by a single user, sequentially.

## Links

* See [research.md §7](../../specs/001-service-registry/research.md) for the
  related decision to access SQLite through SQLAlchemy's ORM.
