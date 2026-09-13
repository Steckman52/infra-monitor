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

## Validation record

Last run 2026-09-13: step 1 verified in-browser by scanning this
project's own repository root — all 9 real ADRs (0001-0009, including
the two authored for this feature's own Polish phase) appeared with
correct title/status/date, alongside the fixture and test-fixture ADRs
picked up from the same root (14 total, no path collisions since every
fixture file's path is genuinely distinct). Step 2 verified against that
same live scan via `GET /api/adrs/{id}`: "Third Decision" shows
`supersedes: [Second Decision]` and both `adr-service-a`/`adr-service-b`
as related services. Step 3 verified in-browser: the ADR Issues view
showed `broken.md` as a parse failure and `secret-leak.md` as a secret
warning (AWS-key-specific reason), while `secret-leak.md` still appeared
normally in the plain ADR list. Step 4 (re-scan reflects an added/removed
ADR) was not manually re-run in-browser this session — it's covered by
the automated `test_rescan_reflects_added_and_removed_adr` and
`test_rescan_drops_relationship_after_target_deleted` integration tests.
FR-013 (no create/edit/delete affordance) confirmed by inspection: only
`GET` routes exist under `/api/adrs*`, and no frontend ADR component
renders a create/edit/delete control.

One real, pre-existing gap was found while validating step 1: passing
two **overlapping** scan roots (this project's own root, which already
contains the fixture repository nested inside it, plus that same fixture
path again explicitly) makes the same file get walked and parsed twice
in one scan, and `AdrRecord.source_path`'s unique constraint turns that
into an unhandled `IntegrityError` (500), correctly rolled back as one
transaction but not reported as a graceful `ScanIssue`/`AdrImportIssue`.
This is not specific to the ADR module — the same double-walk would
silently duplicate `Service` rows for manifests too, just without a
unique constraint to surface it. No spec (001-004) lists overlapping
root paths as a requirement or edge case, so this was left unfixed here
as out of scope for this feature's task list; flagged as a candidate
follow-up rather than patched silently. All 127 backend tests pass,
including the `test_scanning_a_few_hundred_adrs_completes_quickly`
performance check (300 generated ADRs with chained relationships, well
under the 5-second target).
