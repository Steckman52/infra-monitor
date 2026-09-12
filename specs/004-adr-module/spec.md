# Feature Specification: ADR Module

**Feature Branch**: `004-adr-module`

**Created**: 2026-09-12

**Status**: Draft

**Input**: User description: "Модуль ADR (архитектурные решения) — структурированные записи, связанные с сервисами из реестра, со связями между самими решениями (одно отменяет/дополняет другое); автоматический импорт существующих ADR из папки docs/adr/ каждого репозитория (формат MADR)."

## User Scenarios & Testing *(mandatory)*

Builds on the service registry (feature 001): an ADR is associated with
every registered service inside the repository that contains it. This
module is import-only — it reads existing `docs/adr/*.md` files already
authored in Markdown; it does not provide a way to create or edit an ADR
through the system itself (Constitution Principle VI/VIII).

### User Story 1 - Import and browse ADRs across repositories (Priority: P1)

An architect points the system at repository roots and sees every
architectural decision record already documented under each repository's
`docs/adr/` folder, with its title, status, and date — without opening
each Markdown file individually.

**Why this priority**: This is the feature's core value: turning scattered
Markdown files across many repositories into one browsable inventory of
decisions. Everything else drills into or explains this view.

**Independent Test**: Point the system at this project's own repository
(which already documents its own architectural decisions as MADR files
under `docs/adr/`, per Constitution Principle VI) and verify every existing
ADR appears in the list with a title, status, and date.

**Acceptance Scenarios**:

1. **Given** a repository contains a `docs/adr/` folder with Markdown
   files following this project's MADR conventions, **When** the architect
   scans that repository, **Then** each file appears as one ADR with its
   title, status, and date.
2. **Given** an ADR's status text does not match any recognized keyword,
   **When** the scan runs, **Then** the ADR is still imported, with its
   status shown as unrecognized rather than guessed.
3. **Given** a `docs/adr/` folder contains a non-Markdown file, **When**
   the scan runs, **Then** that file is ignored, not reported as a problem.

---

### User Story 2 - View one ADR's relationships and related services (Priority: P2)

An architect opens a specific ADR and sees its full content, which other
ADRs it supersedes or is superseded by (or amends/is amended by), and
which registered services it relates to.

**Why this priority**: Turns a flat list into a decision history —
answering "is this still the current approach, and what replaced it" and
"which of my services does this affect."

**Independent Test**: With ADRs already imported (User Story 1), open an
ADR that documents a supersede relationship to another already-imported
ADR and confirm that relationship is shown without cross-referencing the
raw files.

**Acceptance Scenarios**:

1. **Given** an ADR's status or Links section documents that it supersedes
   or is superseded by another ADR already imported from the same
   repository, **When** the architect opens it, **Then** that relationship
   is shown, in both directions from either ADR's own detail view.
2. **Given** an ADR lives in a repository containing more than one
   registered service (a monorepo), **When** the architect opens it,
   **Then** every service registered within that repository is listed as
   related — not just one arbitrarily chosen service.
3. **Given** an ADR documents a relationship to a file that cannot be
   found in the current scan, **When** the architect opens it, **Then** no
   broken or dangling relationship is shown.

---

### User Story 3 - Import issues surfaced separately (Priority: P3)

An architect reviews which ADR files failed to parse and which imported
ADRs were flagged with a possible secret or credential in their text, kept
visibly separate from the normal browsable list.

**Why this priority**: Mirrors the issues pattern already established for
the registry (feature 001) and the log scan (feature 003) — nothing is
silently lost, and a heuristic safety check (Constitution Principle VIII)
needs visibility without blocking the import it's warning about.

**Independent Test**: Scan a repository containing one ADR file missing a
title and one ADR file containing an obvious token-shaped string, and
verify both are surfaced in a separate issues/warnings view.

**Acceptance Scenarios**:

1. **Given** an ADR file does not contain a recognizable title heading,
   **When** the scan runs, **Then** it is reported as a parsing issue with
   a specific reason, and the rest of the scan continues normally.
2. **Given** an ADR's text contains a pattern resembling a secret, token,
   or password, **When** the scan runs, **Then** the ADR is still imported
   in full, and a warning referencing it appears in the issues view.
3. **Given** the underlying ADR files change and the architect re-scans,
   **When** the scan completes, **Then** the imported ADRs, their
   relationships, and the issues/warnings all reflect the current state.

---

### Edge Cases

- What happens when two ADRs in different repositories share the same
  filename (e.g., both `0001-use-database.md`)? They remain two distinct
  ADR records, scoped by their own repository — never merged, the same
  scoping principle already used for external nodes (feature 002).
- What happens when an ADR has no discoverable relationship to any other
  ADR, and no related registered service? It is still imported normally,
  with empty relationship and related-service lists — not an error.
- What happens when a supersede/amend relationship is documented in only
  one direction (e.g., the newer ADR says "supersedes X" but X's own text
  says nothing about being superseded)? The relationship is still shown
  from both ADRs' detail views once detected from either side.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: System MUST allow the user to specify one or more root
  directories to scan for `docs/adr/*.md` files, consistent with how the
  registry scan specifies roots.
- **FR-002**: For each `docs/adr` directory found, System MUST treat every
  Markdown file directly inside it as one ADR record; non-Markdown files
  MUST be ignored, not reported.
- **FR-003**: System MUST extract each ADR's title (the first top-level
  heading), raw status text, and date, following this project's own MADR
  conventions (Constitution Principle VI).
- **FR-004**: System MUST derive a normalized status category — proposed,
  accepted, rejected, deprecated, superseded, or unrecognized — from the
  raw status text via fixed keyword matching, never a guess when no
  keyword matches.
- **FR-005**: System MUST detect a "supersedes"/"superseded by" or
  "amends"/"amended by" relationship between two ADRs by matching fixed
  keyword patterns against the status text and any Links-section entries,
  resolving the accompanying reference to another ADR already found in the
  same scan.
- **FR-006**: System MUST associate every ADR with every registered
  service whose repository path is the same as, or nested within, the
  repository directory containing that ADR's `docs/adr` folder — a
  many-to-many association, not a single owner (resolved in discussion:
  monorepos may have zero, one, or several related services).
- **FR-007**: System MUST run a heuristic, regex-based check for patterns
  resembling secrets, tokens, or passwords in each ADR's text at import
  time (Constitution Principle VIII) and record a non-blocking warning
  when found, without preventing the ADR from being imported.
- **FR-008**: System MUST isolate a single ADR file's parsing failure so
  it does not stop the rest of the scan, recording it as an issue instead.
- **FR-009**: System MUST present a browsable list of imported ADRs, each
  showing its title, normalized status, and date.
- **FR-010**: Users MUST be able to open an individual ADR and see its
  full content, normalized status, its supersede/amend relationships in
  both directions, and its related registered services.
- **FR-011**: System MUST present ADR files that failed to parse and ADRs
  flagged with a possible-secret warning in a view separate from the
  normal browsable list.
- **FR-012**: Re-running an ADR scan MUST replace previously imported
  ADRs, their relationships, and import issues to reflect the current
  state of the scanned `docs/adr` folders.
- **FR-013**: System MUST NOT provide any way to create, edit, or delete
  an ADR record through the system itself — content changes only happen
  by editing the source Markdown files and re-scanning.

### Key Entities

- **ADR Record**: title, raw status text, normalized status category,
  date (nullable), source file path, repository path (directory
  containing `docs/adr`), full content text, possible-secret warning flag.
- **ADR Relationship**: a link between two ADR records — relationship
  type (`supersedes` / `amends`) and direction.
- **ADR-Service Association**: a many-to-many link between an ADR record
  and a registered service.
- **ADR Import Issue**: a file that failed to parse, with a specific
  reason (distinct from the possible-secret warning, which applies to a
  successfully-imported ADR).

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: A user can browse every ADR found across scanned
  repositories with its status and date, without opening any raw file.
- **SC-002**: For any ADR documenting a supersede/amend relationship per
  this project's MADR conventions, a user can see that relationship
  without manually cross-referencing files.
- **SC-003**: An ADR containing an accidental secret-like pattern is
  flagged, and its content is imported in full regardless.
- **SC-004**: A single malformed ADR file never prevents any other valid
  ADR file in the same scan from being imported.
- **SC-005**: An ADR in a monorepo is associated with every service
  registered within that repository, not just one arbitrarily chosen
  service.
- **SC-006**: Re-running an ADR scan after the underlying files change
  updates the imported set to reflect the current state, with no manual
  cleanup.

## Assumptions

- ADR content is parsed using this project's own MADR conventions (a
  top-level title heading, `* Status:`/`* Date:` bullet lines, and an
  optional `## Links` section) — files that deviate significantly may
  still import with an unrecognized status rather than being rejected
  outright, per FR-004.
- The ADR module is import-only: content is authored and edited as plain
  Markdown files in the scanned repositories, never through this system's
  own UI (Constitution Principle VI/VIII) — mirrors the read-only design
  already established for the service registry (feature 001).
- Constitution Principle VIII's "immutability" governs how decisions are
  recorded in the source Markdown files themselves (never edited
  retroactively, only superseded by a new record); it does not prevent
  this system's own imported copy from being refreshed on re-scan to
  mirror the current state of those files, the same way the registry
  already works.
- Secret-pattern detection is a heuristic warning, not a guarantee — it
  does not redact, block, or otherwise alter the imported content itself.
- Kubernetes/CI pipeline references or other non-ADR documentation inside
  a `docs/` folder are out of scope; only files directly inside a
  `docs/adr/` subdirectory are treated as ADRs.
