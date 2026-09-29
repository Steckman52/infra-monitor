# Feature Specification: Dependency Map & Version Compatibility

**Feature Branch**: `002-dependency-map`

**Created**: 2026-09-11

**Status**: Draft

**Input**: User description: "Карта зависимостей и проверка совместимости версий — на основе тех же манифестов плюс docker-compose.yml (связи между сервисами по общим сетям), плюс сравнение major-версий одноимённых зависимостей между сервисами реестра."

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Review version compatibility across the registry (Priority: P1)

An architect views a list of every dependency used by more than one service in
the registry, each showing an overall compatibility status and the exact
version declared by every contributing service.

**Why this priority**: This is the feature's core value and requires no new
scanning — it is computable entirely from data the service registry (feature
1) already collected, making it the cheapest and highest-value slice to
deliver first.

**Independent Test**: With a registry already populated (from feature 1)
containing at least two services that declare the same dependency with
different major versions, and one with an unclassifiable version string,
open the compatibility view and verify all three states (compatible, risk,
not comparable) are distinguishable.

**Acceptance Scenarios**:

1. **Given** two or more services declare the same dependency with the same
   major version, **When** the architect opens the compatibility view,
   **Then** that dependency is shown as "compatible" with every contributing
   service and its version listed.
2. **Given** two or more services declare the same dependency with different
   major versions, **When** the architect opens the compatibility view,
   **Then** that dependency is shown as a "compatibility risk", with every
   differing version and its service visible.
3. **Given** a service declares a dependency using a version string with no
   extractable leading number (e.g., a build-tool property placeholder),
   **When** the architect opens the compatibility view, **Then** that
   service's entry for the dependency is marked "not comparable", distinct
   from both "compatible" and "risk".
4. **Given** a dependency is declared by only one service in the registry,
   **When** the architect opens the compatibility view, **Then** that
   dependency does not appear, since compatibility is only meaningful across
   more than one service.

---

### User Story 2 - Review the service connection graph (Priority: P2)

An architect views a graph of connections between the company's services,
derived from `docker-compose.yml` files found while scanning, including
connections to infrastructure (databases, caches, etc.) that isn't itself a
registered service.

**Why this priority**: Builds on the registry with genuinely new scanned
data (network topology), independent of the compatibility view — valuable on
its own for understanding "what talks to what" before making an
infrastructure change.

**Independent Test**: Scan a set of repositories where at least one
`docker-compose.yml` declares two services sharing a network and a third
service via `image:` only (no local build), and verify the graph shows both
service-to-service and service-to-external-node connections.

**Acceptance Scenarios**:

1. **Given** two `docker-compose.yml` service blocks share a common network,
   **When** the architect opens the connection graph, **Then** a connection
   between the two corresponding nodes is shown.
2. **Given** a `docker-compose.yml` service block declares another under
   `depends_on`, **When** the architect opens the connection graph, **Then**
   a connection between them is shown, even without a shared network entry.
3. **Given** a `docker-compose.yml` service block uses `image:` with no
   `build:`, or its build path matches no registered service, **When** the
   architect opens the connection graph, **Then** that block appears as a
   distinct external node rather than being omitted.
4. **Given** a `docker-compose.yml` file is syntactically invalid, **When**
   a scan runs, **Then** the rest of the scan (registry and other compose
   files) completes normally and the invalid file is reported with a
   specific reason.

---

### User Story 3 - See a service's risks and connections in context (Priority: P3)

An architect opens a specific service's existing detail view (from feature
1) and sees, in that same place, which of its dependencies have a
compatibility risk and which other nodes it is connected to.

**Why this priority**: Ties User Story 1 and 2 together into the workflow an
architect actually uses — investigating one service before making a change
— but is additive polish once both underlying views exist.

**Independent Test**: With compatibility risks and connections already
computed (from User Stories 1 and 2), open one affected service's detail
view and confirm both are visible without navigating elsewhere.

**Acceptance Scenarios**:

1. **Given** a service has at least one dependency with a "compatibility
   risk" status, **When** the architect opens that service's detail view,
   **Then** the at-risk dependency and the reason are shown there.
2. **Given** a service is connected to other nodes per the connection graph,
   **When** the architect opens that service's detail view, **Then** those
   connections are listed there.

---

### Edge Cases

- What happens when a shared dependency has some services with matching
  major versions and other services with a "not comparable" version at the
  same time? The dependency's status reflects both facts: compatible among
  the comparable entries, but visibly flagged as containing at least one
  not-comparable entry — never silently treated as fully compatible.
- What happens when two nodes are connected by both a shared network and a
  `depends_on` declaration? The connection is represented once, not
  duplicated.
- What happens when two different `docker-compose.yml` files (in different
  repositories) each define a service using the same image (e.g.,
  `image: postgres`) with no local build context? They are treated as two
  distinct external nodes, scoped to their own repository, not merged into
  one.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: System MUST identify every dependency (name + ecosystem)
  declared by more than one service already present in the registry.
- **FR-002**: For each such shared dependency, System MUST determine a
  compatibility status by comparing the major version extracted from every
  contributing service's declared version string.
- **FR-003**: System MUST extract a major version from a declared version
  string deterministically: strip leading range-operator characters (`^`,
  `~`, `>=`, `<=`, `==`, `!=`, `>`, `<`) and any other leading non-digit
  characters, then take the leading run of digits up to the first `.` or the
  end of the string.
- **FR-004**: If a major version cannot be extracted from a declared version
  string, System MUST mark that service's entry for the dependency as "not
  comparable" rather than guessing or defaulting to compatible.
- **FR-005**: System MUST mark a shared dependency "compatible" when every
  comparable entry shares the same major version, "compatibility risk" when
  at least two comparable entries differ, and MUST separately flag the
  presence of any "not comparable" entries regardless of the compatible/risk
  determination among the rest. When *no* entry is comparable, System MUST
  mark the dependency "unknown" rather than "compatible": with nothing read,
  there is no agreement to report, and calling it compatible would be FR-004's
  prohibited "defaulting to compatible" applied to the whole dependency. This
  is the normal case for Maven modules, which inherit nearly every version
  from a parent POM or `dependencyManagement`.
- **FR-006**: System MUST present a browsable view of all shared
  dependencies, each with its status and the list of contributing services
  with their declared versions.
- **FR-007**: System MUST scan `docker-compose.yml` files found within the
  same repository paths already scanned for the registry.
- **FR-008**: For each service block in a `docker-compose.yml`, System MUST
  extract its build context path (if declared via `build`), its image (if
  declared via `image`), its declared networks, and its `depends_on`
  entries.
- **FR-009**: System MUST match a `docker-compose.yml` service block to a
  registered service by resolving the block's build context to an absolute
  path (relative to the `docker-compose.yml` file's location) and comparing
  it to registered services' repository paths.
- **FR-010**: When a service block has no build context, or its build
  context matches no registered service, System MUST represent it in the
  connection graph as a distinct external node, scoped to the
  `docker-compose.yml` file it came from.
- **FR-011**: System MUST record a connection between two nodes (registered
  services or external nodes) when they share at least one common network,
  or when one node's `depends_on` lists the other, without duplicating a
  connection established by both.
- **FR-012**: System MUST present a browsable view of the connection graph,
  showing each node and the other nodes it connects to.
- **FR-013**: System MUST isolate `docker-compose.yml` parsing failures the
  same way manifest parsing failures are isolated: an invalid file MUST NOT
  stop the rest of the scan, and MUST be recorded with a specific reason.
- **FR-014**: Users MUST be able to view, from an individual service's
  existing detail view, that service's compatibility risks and its
  connections to other nodes.
- **FR-015**: Re-running a scan MUST update both the compatibility statuses
  and the connection graph to reflect the current state of the scanned
  repositories.

### Key Entities

- **Dependency Compatibility**: A dependency (name + ecosystem) shared by
  more than one service. Attributes: overall status (compatible /
  compatibility risk), whether any entry is not-comparable, and the list of
  contributing services with their declared version and per-service
  comparability.
- **Service Connection**: A link between two nodes derived from
  `docker-compose.yml`. Attributes: the two nodes it connects (each either a
  registered service or an external node), the relationship basis (shared
  network and/or `depends_on`), and the source `docker-compose.yml` path.
- **External Node**: A `docker-compose.yml` service block with no matching
  registered service. Attributes: name as declared in the compose file,
  image (if any), source `docker-compose.yml` path/repository (for scoping
  distinct external nodes with the same name apart).

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: For every dependency shared by two or more services, a user
  can determine its compatibility status and every contributing service's
  version without inspecting the underlying manifests directly.
- **SC-002**: A version that cannot be classified is visibly distinguished
  from a compatible or at-risk one in 100% of cases — never silently
  absorbed into either category.
- **SC-003**: A user can identify every direct connection between the
  company's scanned services, including connections to infrastructure not
  present in the registry, without opening any `docker-compose.yml` file
  directly.
- **SC-004**: A single malformed `docker-compose.yml` never prevents any
  other valid one in the same scan from contributing to the connection
  graph.
- **SC-005**: Re-running a scan after a repository change (a dependency
  version bump, or a changed `docker-compose.yml` topology) reflects that
  change in both the compatibility view and the connection graph without
  manual intervention.
- **SC-006**: From a single service's detail view, a user can see all of
  that service's compatibility risks and network connections without
  navigating to a separate report.

## Assumptions

- Version compatibility checking compares major-version numbers only; it
  does not attempt to resolve or intersect full semantic version ranges
  (e.g., whether `^1.2.0` and `~1.5.0` truly overlap in every edge case) —
  that is a distinct, substantially larger undertaking.
- Version compatibility is computed entirely from data the service registry
  (feature 1) already collects; it requires no scanning step of its own.
- A `docker-compose.yml` service's build context is resolved relative to the
  location of that `docker-compose.yml` file, matching how Docker Compose
  itself resolves build paths.
- External nodes are scoped per `docker-compose.yml` file/repository: two
  external nodes with the same name in different repositories are distinct,
  since Docker Compose networks are isolated per project by default.
- Kubernetes manifests are out of scope for this version of the feature;
  deferred as a possible future extension, consistent with how other scope
  boundaries were deferred for the service registry.
