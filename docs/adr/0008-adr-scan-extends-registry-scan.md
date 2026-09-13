# ADR import extends the registry scan, not a fourth independent trigger

* Status: accepted
* Date: 2026-09-13

## Context and Problem Statement

The ADR module (spec
[004-adr-module](../../specs/004-adr-module/spec.md)) needs to discover
`docs/adr/*.md` files inside the same repositories the registry already
scans. Feature 003 (log error analysis) introduced a second, independent
scan trigger (`POST /api/log-scan`) alongside the registry's
`POST /api/scan`. Should ADR import follow that precedent and get its own
`POST /api/adr-scan`, or extend an existing trigger?

## Decision Drivers

* Constitution Principle IV (Deterministic & Explainable): a scan's scope
  should match where its source data actually lives.
* `docs/adr/` is source-controlled content living inside the same
  repositories the registry scan (feature 001) and the docker-compose scan
  (feature 002) already walk — unlike feature 003's logs, which are runtime
  output living outside any source repository.

## Considered Options

* A dedicated `POST /api/adr-scan` mirroring feature 003's log scan.
* Extend the existing `run_scan` orchestrator (features 001/002) to also
  walk for `docs/adr/*.md`, reusing the same root paths already passed to
  `POST /api/scan`.

## Decision Outcome

Chosen option: **extend `run_scan`**. Feature 002 already resolved this
exact question for `docker-compose.yml` by extending `run_scan` rather than
adding a new endpoint, because compose files are source-controlled content
inside the scanned repositories. ADRs are in the same category. Feature
003's independent trigger was the right call specifically *because* logs
are a different kind of input (runtime output, external to the repository)
— not because every new scanned artifact automatically implies a new
endpoint. Extending `run_scan` also means one scan action always produces
one consistent snapshot across the registry, connections, and ADRs, rather
than requiring the user to remember and run a third, separate scan for
content that was already sitting in the repositories they just scanned.

### Positive Consequences

* No new scan trigger for the user to discover or remember.
* ADR data can never drift out of sync with the registry/connection data
  from a different point in time, since they're produced by the same call.

### Negative Consequences

* `run_scan` keeps growing with each feature that extends it. Accepted —
  the alternative (a new endpoint per scanned artifact type) would fragment
  a conceptually single "scan these repositories" action into several,
  which is a worse trade for a project this size.

## Links

* [research.md §1](../../specs/004-adr-module/research.md)
* [feature 002 ADR 0005](0005-compose-scan-in-same-transaction.md) — the precedent being followed
