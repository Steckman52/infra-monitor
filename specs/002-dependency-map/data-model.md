# Phase 1 Data Model: Dependency Map & Version Compatibility

## ExternalNode (new table)

A `docker-compose.yml` service block with no matching registered `Service`.

| Field | Type | Rules |
|---|---|---|
| `id` | integer, PK, autoincrement | |
| `name` | text, not null | Service block's key in the compose file (e.g. `postgres`) |
| `image` | text, nullable | The `image:` value, when present |
| `source_compose_path` | text, not null | Path to the `docker-compose.yml` this node came from |
| `repository_path` | text, not null | Repository root the compose file was found under — scopes this node so an identically-named node in another repository is a distinct row (per spec Assumptions) |

**Uniqueness**: `(name, source_compose_path)` is unique — the same compose
file is only ever scanned once per scan run, and a compose file cannot
declare the same service key twice.

## ServiceConnection (new table)

A connection between two nodes, where a node is either a registered
`Service` or an `ExternalNode`.

| Field | Type | Rules |
|---|---|---|
| `id` | integer, PK, autoincrement | |
| `from_service_id` | integer, FK → `Service.id`, nullable, `ON DELETE CASCADE` | Exactly one of `from_service_id` / `from_external_node_id` is set |
| `from_external_node_id` | integer, FK → `ExternalNode.id`, nullable, `ON DELETE CASCADE` | |
| `to_service_id` | integer, FK → `Service.id`, nullable, `ON DELETE CASCADE` | Exactly one of `to_service_id` / `to_external_node_id` is set |
| `to_external_node_id` | integer, FK → `ExternalNode.id`, nullable, `ON DELETE CASCADE` | |
| `relationship_basis` | text, not null | One of `shared_network`, `depends_on`, `both` (FR-011: a connection established by both is recorded once, with `both`, not as two rows) |
| `source_compose_path` | text, not null | Path to the `docker-compose.yml` this connection was derived from |

**Validation rule** (enforced at write time, not a DB constraint SQLite
can't easily express portably): exactly one of the two `from_*` columns is
non-null, and exactly one of the two `to_*` columns is non-null.

**Directionality note**: a connection is recorded once per unordered pair
per compose file; "from"/"to" reflects which side happened to be visited
first while building the graph, not a meaningful direction (a shared
network has no direction; `depends_on` does, but the graph treats both
uniformly as "these two nodes are connected").

## Dependency Compatibility (computed, not persisted)

Not a database table. Computed on each request from the existing `Service`
and `Dependency` tables (feature 1):

1. Group all `Dependency` rows by `(ecosystem, name)` joined through their
   owning `Service`.
2. Keep only groups spanning more than one distinct `Service` (FR-001).
3. For each row in a group, extract a major version per research.md §7.
4. A group's status is `compatible` if every row with an extractable major
   version shares the same value, `compatibility_risk` if at least two
   differ; the group also carries a separate `has_not_comparable` flag if
   any row's major version could not be extracted (FR-005) — the two facts
   are independent and both surfaced.

Conceptual shape returned by this computation:

- **name**, **ecosystem**
- **status**: `compatible` | `compatibility_risk`
- **has_not_comparable**: boolean
- **entries**: list of `{service_id, service_name, declared_version, major_version | null}`
