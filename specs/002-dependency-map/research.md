# Phase 0 Research: Dependency Map & Version Compatibility

## 1. When does docker-compose scanning run relative to the registry scan?

**Decision**: Extend the existing `run_scan` orchestrator (feature 1,
`backend/src/scanning/scan_service.py`) to also walk for `docker-compose.yml`
files during the same pass, and to replace the `external_nodes` /
`service_connections` tables in the **same transaction** as the registry
replace (feature 1's ADR 0003 pattern).

**Rationale**: A single transaction means the registry, the connection
graph, and (by extension) the compatibility view — computed from the
registry's own tables — always describe one consistent scan snapshot.
Running compose scanning as a separate, independently-triggered operation
would risk the connection graph referencing services from a stale or
different scan.

**Alternatives considered**: A second, independently-triggered scan
endpoint for compose files — rejected; adds a second scan trigger a user
would have to remember to run, and reopens the consistency problem this
feature's own FR-015 exists to avoid.

## 2. YAML parsing library

**Decision**: `PyYAML`, using `yaml.safe_load` exclusively.

**Rationale**: PyYAML is the de facto standard, MIT-licensed (Principle
VII), and `safe_load` avoids constructing arbitrary Python objects from
YAML tags — relevant here because `docker-compose.yml` files come from
arbitrary scanned repositories, not from a trusted source.

**Alternatives considered**: `ruamel.yaml` — rejected; its main advantage
(round-trip-preserving parsing, i.e. keeping comments/formatting on
rewrite) is irrelevant since this feature only ever reads compose files,
never writes them.

## 3. Handling docker-compose's flexible field shapes

**Decision**: The parser normalizes three fields that Compose allows in
more than one shape:
- `build`: either a bare string (the context path) or a mapping with a
  `context` key — both resolve to the same context path.
- `networks`: either a list of network names, or a mapping keyed by network
  name (with per-network config as values, which is ignored) — both
  resolve to a list of network names.
- `depends_on`: either a list of service names, or a mapping keyed by
  service name (the long syntax, with a `condition` per entry) — both
  resolve to a list of service names.

**Rationale**: All three shapes are valid, commonly-used Compose syntax;
handling only one would silently miss real files (violates Principle IV's
explainability — a connection that should exist would just be absent with
no indication why).

## 4. Matching a compose service block to a registered Service

**Decision**: Resolve the block's build context path relative to the
`docker-compose.yml` file's own directory into an absolute path, and match
it against registered services' `repository_path` (exact match). No match
(no `build:` key, or a resolved path matching no registered service)
produces an external node instead, scoped to the source repository (per
spec FR-009/FR-010, already settled during specification).

**Rationale**: Already established as the only sound, deterministic option
during specification — compose service *names* (`web`, `api`) are local
identifiers with no guaranteed relationship to a registry-derived service
name, so name-based matching would be unreliable.

## 5. Scope: exactly `docker-compose.yml`, not compose overrides

**Decision**: Scan files literally named `docker-compose.yml` (matching
FR-007's wording precisely). Multi-file Compose setups
(`docker-compose.override.yml`, `-f` file lists) are not merged in this
version.

**Rationale**: Keeps scope matched exactly to what was specified; merging
override files is a real Compose feature but adds meaningful parsing
complexity (layered merge semantics) not called for by the spec.

**Alternatives considered**: Also scanning `docker-compose.override.yml` —
deferred as a natural, low-risk future extension if needed, noted here so
it isn't forgotten rather than silently assumed out of scope forever.

## 6. Version compatibility: computed vs. persisted

**Decision**: Compute compatibility on every read from the `services` /
`dependencies` tables; do not persist a compatibility table.

**Rationale**: Per spec Assumptions, this requires no new scanning step —
it's a pure function of data the registry already has. Persisting it would
require a second write path to keep in sync with every scan and rescan,
for no benefit at this scale (Principle V).

**Alternatives considered**: Persisting computed compatibility rows,
refreshed each scan — rejected as an unnecessary synchronization burden;
computing on read is fast enough at the project's target scale (plan.md
Performance Goals).

## 7. Major-version extraction rule

**Decision**: A single regex applied to every declared version string
across all five ecosystems: strip a leading run of characters from the set
`^~>=<!` (covering `^`, `~`, `>=`, `<=`, `==`, `!=`, `>`, `<`), then strip
any further non-digit characters up to the first digit, then capture the
digit run up to the first `.` or end of string. No leading digit found ⇒
"not comparable" (FR-004).

**Rationale**: One rule for all ecosystems keeps the logic simple and
explainable, and was already validated conceptually during specification
against real examples collected in feature 1's manual testing (e.g. a
Maven property placeholder `${hamcrestVersion}` correctly yields "not
comparable" rather than a wrong guess).

**Alternatives considered**: A per-ecosystem semver/PEP-440/Maven-version
parser for each of the five formats — rejected; substantially more
implementation and test surface for a benefit (true range-intersection
checking) explicitly out of scope per spec Assumptions.

## Outcome

All Technical Context items are resolved; no `NEEDS CLARIFICATION` markers
remain.
