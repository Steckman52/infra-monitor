# Quickstart: Log Error Analysis & Grouping

Validates this feature end-to-end against the acceptance scenarios in
[spec.md](./spec.md). Assumes the feature 001/002 backend/frontend are
already runnable and a registry scan has already been run at least once
(so registered service names exist to match against).

## Prerequisites

- A local log directory fixture containing:
  - A subdirectory named exactly after a registered service (e.g.
    `payments-api/`), with a log file containing 10+ near-duplicate error
    lines differing only in embedded numbers, plus one multi-line stack
    trace error
  - A subdirectory whose name matches no registered service
  - One genuinely unreadable file (e.g. invalid encoding)
  - One `.gz` file, to confirm it is silently excluded, not reported

## Setup

Same as features 001/002 — no new setup steps; `POST /api/log-scan` is
available on the same running backend.

## Validation steps

1. Trigger a log scan against the fixture directory (via the UI's log-scan
   button, or directly:
   `curl -X POST http://localhost:8000/api/log-scan -d '{"root":"<fixture path>"}' -H "Content-Type: application/json"`).
2. Open the Error Groups view. **Expect** (User Story 1): the 10+
   near-duplicate lines appear as a single group under the matched
   service, with the correct occurrence count; no group is created from
   any purely informational log content.
3. Open the group containing the multi-line stack trace. **Expect** (User
   Story 2): the complete original multi-line text is shown, along with
   occurrence count and first/last-seen timestamps.
4. Open the Log Scan Issues view. **Expect** (User Story 3): the
   non-matching subdirectory appears as `unattributed`, and the unreadable
   file appears as `unreadable` with a specific reason; the `.gz` file
   appears nowhere.
5. Add a new distinct error line to the fixture log and re-run the scan.
   **Expect** (SC-005): a new group appears reflecting the current state.

## Out of scope for this quickstart

- Full semantic/statistical log clustering (feature deferred per spec
  Assumptions — only regex-based template normalization is validated
  here).
- Live process log tailing (feature deferred per spec Assumptions — only
  scanning already-exported local files is validated here).

## Validation record

Last run 2026-09-12: steps 1-4 verified in-browser using
`backend/tests/integration/fixtures/logs/` (the Browser pane's frame
compositor was temporarily unavailable this session, so verification used
`get_page_text` plus JS-dispatched click/input events instead of
pixel-coordinate clicks — same React event handlers, same result); step 5
(re-scan reflects a new error line) verified via the automated
`test_rescan_adds_new_group_without_duplicating_existing` integration
test, not manually re-run in-browser. Along the way, a real bug was found
and fixed by the multi-line-stack-trace test: naive substring marker
matching treated `TypeError` as containing the `ERROR` marker, cutting off
`Caused by:` continuation lines — fixed with word-boundary matching. All
90 backend tests pass, including the `test_log_scan_of_10000_lines_completes_quickly`
performance check (well under the 10-second target).
