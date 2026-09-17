# Feature Specification: Service Registry

**Feature Branch**: `001-service-registry`

**Created**: 2026-09-10

**Status**: Draft

**Input**: User description: "Реестр сервисов автоматически строится путём сканирования файловой системы репозиториев компании на предмет манифестов пакетных менеджеров: package.json, pom.xml, requirements.txt, go.mod, composer.json. Для каждого найденного манифеста система извлекает: имя сервиса, язык/экосистему, путь к репозиторию, список прямых зависимостей с версиями. Реестр — только для чтения относительно исходных манифестов."

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Build and browse the service registry (Priority: P1)

An engineer or architect points the system at one or more repository locations, triggers a
scan, and sees a browsable registry of every service discovered from package-manager manifests
(`package.json`, `pom.xml`, `requirements.txt`, `go.mod`, `composer.json`).

**Why this priority**: This is the foundational capability the rest of the system (dependency
map, log analysis, ADR module) depends on. Without a populated registry, no other module has
data to work with. It is independently valuable on its own: even without drill-down detail, a
list of "what services exist and where" is useful to an architect who currently has no such
inventory.

**Independent Test**: Point the system at a set of test repositories containing a mix of the
five supported manifest types, run a scan, and verify the resulting list contains one entry per
manifest found, without needing any other feature to be built.

**Acceptance Scenarios**:

1. **Given** a root directory containing several repositories with supported manifests, **When**
   the user runs a scan, **Then** the registry shows one entry per manifest found, each with a
   derived name, ecosystem/language, and repository path.
2. **Given** a repository is a monorepo containing more than one manifest (e.g., a `package.json`
   for a frontend and a `pom.xml` for a backend service in different subfolders), **When** the
   scan runs, **Then** each manifest produces its own separate registry entry.
3. **Given** the registry was already built from a previous scan, **When** the user re-runs the
   scan after repositories changed (a service added, removed, or a manifest edited), **Then** the
   registry reflects the current state of the repositories without any manual edits.
4. **Given** a specified root directory or repository path does not exist or cannot be read,
   **When** the user runs a scan, **Then** the system reports that specific path as unreachable
   without aborting the scan of the other valid paths.

---

### User Story 2 - Inspect a service's details and dependencies (Priority: P2)

An engineer opens a single service's entry in the registry to see its full list of direct
dependencies with declared versions, its ecosystem/language, and the repository path it came
from.

**Why this priority**: Once the registry exists (P1), the next most valuable action is drilling
into a specific service — this is what turns a flat list into something actionable (e.g., before
proposing a version bump or investigating an incident).

**Independent Test**: With a registry already populated (from P1), open any service entry and
verify its dependency list, ecosystem, and repository path are all visible and match the source
manifest.

**Acceptance Scenarios**:

1. **Given** a service was registered from a manifest with declared dependencies, **When** the
   user opens that service's entry, **Then** every direct dependency and its declared version
   string is listed exactly as found in the source manifest.
2. **Given** a service's manifest declared zero dependencies, **When** the user opens that
   service's entry, **Then** the system shows an explicit empty dependency list rather than an
   error.

---

### User Story 3 - See what failed or is incomplete during a scan (Priority: P3)

An engineer reviews a separate list of scanning problems — manifests that could not be parsed at
all, and manifests that parsed but were missing data needed to fully populate a service entry —
so that registry gaps are visible and explainable rather than silently missing.

**Why this priority**: Builds trust in the registry's completeness. Lower priority than P1/P2
because the registry is still usable without this visibility, but without it, missing services
would be indistinguishable from services that were never scanned.

**Independent Test**: Run a scan against a set of repositories that intentionally includes one
syntactically invalid manifest and one manifest missing an expected field, then verify both
appear in the scan-issues view with an explanatory reason, separate from the normal service list.

**Acceptance Scenarios**:

1. **Given** a manifest file is syntactically invalid (e.g., malformed JSON, malformed XML, or an
   unparsable `go.mod`), **When** the scan runs, **Then** no service entry is created for that
   file, and it appears in a scan-issues list with the file path and a specific failure reason.
2. **Given** a manifest is syntactically valid but missing a field the system needs to fully
   describe the service (e.g., a `pom.xml` without `artifactId`, as is typical for a parent POM),
   **When** the scan runs, **Then** a service entry is still created, marked as having incomplete
   data, rather than being discarded.
3. **Given** a scan-issue was reported in a previous scan and the underlying manifest has since
   been fixed, **When** the user re-runs the scan, **Then** that issue no longer appears in the
   scan-issues list.

---

### Edge Cases

- What happens when two manifests in different repository paths resolve to the same derived
  service name? The system MUST disambiguate them (e.g., by appending a repository-path-derived
  suffix) rather than silently merging or overwriting one with the other.
- What happens when a manifest sits inside a well-known dependency-installation directory (e.g.,
  `node_modules`, `vendor`, `target`, `.venv`, `venv`, `env`, `site-packages`) nested within a scanned
  repository? These MUST be excluded from scanning — they belong to third-party dependencies,
  not to a company-owned service.
- What happens when the same directory contains two different manifest types (e.g., both
  `package.json` and `requirements.txt`, as in a mixed-stack project)? Each manifest MUST still
  produce its own separate service entry.
- What happens when a manifest file exists but is completely empty (zero bytes)? It MUST be
  treated as a parse failure and reported as a scan issue, not as a valid empty service.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: System MUST allow the user to specify one or more root directories or repository
  paths to scan.
- **FR-002**: System MUST scan the specified paths for manifest files of the following types:
  `package.json`, `pom.xml`, `requirements.txt`, `go.mod`, `composer.json`.
- **FR-003**: For each manifest successfully parsed, system MUST extract: service name,
  ecosystem/language, repository path, and the list of direct dependencies with their declared
  versions (where the manifest format provides version information).
- **FR-004**: System MUST derive each service's name using the following priority order: (1) an
  explicit name field in the manifest, when present (`name` in `package.json`/`composer.json`,
  `artifactId`/`groupId` in `pom.xml`, the last path segment of the `module` directive in
  `go.mod`); (2) the name of the manifest's parent directory, when no such field is present or
  applicable (this is always the case for `requirements.txt`); (3) a repository-path-derived
  suffix appended to the derived name, when two services would otherwise share the same name.
- **FR-005**: System MUST treat every discovered manifest as a distinct service, so that a
  repository containing multiple manifests (a monorepo) produces multiple registry entries.
- **FR-006**: System MUST exclude manifests located inside well-known dependency-installation
  directories (including but not limited to `node_modules`, `vendor`, `target`, `.venv`, `venv`, `env`,
  `site-packages`, `__pycache__`) from being registered as services.
- **FR-007**: System MUST parse each manifest independently, such that a parsing failure on one
  manifest file does not stop or affect the scanning of any other manifest file.
- **FR-008**: System MUST NOT create a service entry for a manifest that fails to parse (invalid
  syntax or empty file); instead it MUST record a scan issue containing the file path and the
  specific failure reason.
- **FR-009**: System MUST create a service entry, marked as having incomplete data, for a
  manifest that parses successfully but lacks a field required to fully describe the service,
  rather than discarding that manifest.
- **FR-010**: System MUST report a specified root directory or repository path that does not
  exist or is unreadable as a distinct, path-specific error, without aborting the scan of other
  valid paths.
- **FR-011**: System MUST present the registry as a browsable list of all successfully
  registered services (complete and incomplete).
- **FR-012**: Users MUST be able to open an individual service's entry and view its ecosystem/
  language, repository path, and full list of direct dependencies with declared versions.
- **FR-013**: Users MUST be able to view the list of scan issues (unparsable manifests) as a
  view separate from the list of registered services.
- **FR-014**: Users MUST be able to re-run a scan on demand; the registry and the scan-issues
  list MUST reflect the current state of the scanned repositories after the re-scan (resolved
  issues disappear, new services/issues appear, removed services/issues are removed).
- **FR-015**: The registry MUST be read-only with respect to its source manifests: the system
  MUST NOT provide a way to manually create or edit a service entry independently of what a scan
  produced.

### Key Entities

- **Service**: A single unit registered from one manifest file. Attributes: derived name,
  ecosystem/language (Node.js, Java, Python, Go, PHP), source repository path, source manifest
  file path, data-completeness status (complete / incomplete), list of dependencies.
- **Dependency**: A single direct dependency declared by a service's manifest. Attributes:
  dependency name, declared version string (as written in the manifest, unnormalized),
  the service it belongs to.
- **Scan Issue**: A record of a manifest that could not produce a service entry, or produced an
  incomplete one. Attributes: manifest file path, repository path, issue type (unparsable /
  incomplete data), specific reason/message, detection timestamp.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: After scanning a set of repositories, every syntactically valid manifest of the
  five supported types produces exactly one corresponding entry in the registry.
- **SC-002**: For any registered service, a user can determine its dependencies, ecosystem, and
  repository path entirely from the system, without opening the source repository directly.
- **SC-003**: A single unparsable manifest never prevents any other valid manifest present in the
  same scan from producing a registry entry.
- **SC-004**: A user can identify every manifest that failed to parse during a scan, along with a
  specific reason for each failure, entirely from the system's scan-issues view.
- **SC-005**: After a repository changes (service added, removed, or manifest edited) and the
  user re-runs a scan, the registry reflects the change with no manual editing required.
- **SC-006**: Two services whose names would otherwise collide are always distinguishable from
  one another in the registry.

## Assumptions

- The system has local filesystem access to already-checked-out repositories; cloning or
  fetching repositories from a remote VCS is out of scope for this feature (consistent with the
  project's local-first principle).
- Manifest files are UTF-8 encoded text.
- Dependency version strings are stored and displayed as written in the manifest, without
  semantic version normalization or resolution — that belongs to the Dependency Map feature.
- Scanning is triggered manually by the user on demand; there is no background file-system
  watcher or scheduled automatic re-scan in this version.
- Well-known dependency-installation directories (`node_modules`, `vendor`, `target`, `.venv`, `venv`, `env`,
  `site-packages`, `__pycache__`, and similar) are excluded from scanning by default.
- Manual override of an auto-derived service name is out of scope for this version (deferred as
  a future extension), so the name-derivation priority order in FR-004 is final for any given
  manifest state.
