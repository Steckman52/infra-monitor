# Quickstart: ADR Module

Validates this feature end-to-end against the acceptance scenarios in
[spec.md](./spec.md). Uses this project's own `docs/adr/` as real
dogfooded test material (spec.md's Independent Test for User Story 1),
plus a small fixture repo for the error/warning paths.

## Prerequisites

- This project's own repository root (already contains 7 real MADR files
  under `docs/adr/`, written across features 001-003).
- A fixture repository containing:
  - A `docs/adr/` folder with one well-formed ADR that documents a
    `Superseded by [...]` reference to a second ADR in the same folder
  - One ADR file with no title heading (a parse failure)
  - One ADR file whose content contains a planted secret-like string
    (e.g. an `AKIA...`-shaped token)
  - One or more registered services inside the same fixture repository
    (to validate the many-to-many association)

## Setup

Same as features 001-003 — no new setup steps; ADR data is populated by
the same `POST /api/scan` / scan button already used for the registry.

## Validation steps

1. Run a scan against this project's own repository root. **Expect**
   (User Story 1): all 7+ existing ADRs appear in the ADR list with their
   title, status, and date.
2. Run a scan against the fixture repository (alongside its manifests, so
   its services are registered too). Open the ADR that documents the
   supersede relationship. **Expect** (User Story 2): the relationship is
   shown from both ADRs' detail views, and every service registered in
   that fixture repository appears as related.
3. Open the ADR Issues view. **Expect** (User Story 3): the title-less
   file appears as a parse failure with a specific reason, and the
   planted-secret ADR appears as a warning — while still being fully
   readable in the normal ADR list, not blocked.
4. Add a new ADR file to the fixture repository and re-run the scan.
   **Expect** (SC-006): the new ADR appears, and previously-resolved
   issues that no longer apply are gone.

## Out of scope for this quickstart

- Creating or editing an ADR through the system itself (feature is
  import-only per FR-013).
- Non-MADR-shaped ADR templates from third-party conventions (feature
  recognizes this project's own MADR shape, per spec Assumptions).
