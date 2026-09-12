# Feature Specification: Log Error Analysis & Grouping

**Feature Branch**: `003-log-error-analysis`

**Created**: 2026-09-11

**Status**: Draft

**Input**: User description: "Анализ и группировка ошибок в логах, привязанных к конкретному сервису — без ИИ, по шаблонам/регуляркам."

## User Scenarios & Testing *(mandatory)*

Builds on the service registry (feature 001): a log file is attributed to a
service already present there, by directory/file naming convention — this
feature does not scan repositories itself, it scans a separate root
containing already-exported local log files.

### User Story 1 - Scan logs and browse grouped errors per service (Priority: P1)

An architect points the system at a local directory of exported log files
and sees, for each service already in the registry, a list of distinct
recurring errors with how many times each occurred — not a raw, repetitive
line-by-line dump.

**Why this priority**: This is the feature's core value: turning a pile of
repetitive raw log lines into a small number of distinct, actionable
problems per service. Everything else drills into or explains this view.

**Independent Test**: Point the system at a fixture log directory
containing a service-named subdirectory with 10+ near-duplicate error lines
(differing only in embedded numbers/identifiers) and verify they collapse
into a single group with the correct count.

**Acceptance Scenarios**:

1. **Given** log files under a subdirectory whose name matches a registered
   service, **When** the architect scans that log root, **Then** error
   entries found in those files are grouped per service, each group showing
   an occurrence count.
2. **Given** the same underlying error occurs multiple times with different
   embedded numbers, IDs, or other variable values, **When** the scan runs,
   **Then** those occurrences collapse into one group rather than appearing
   as separate entries.
3. **Given** a log file contains only informational/debug lines with no
   recognized error marker, **When** the scan runs, **Then** no error group
   is created from that file.
4. **Given** a log directory's name does not match any registered service,
   **When** the scan runs, **Then** its errors are not attributed to an
   arbitrary service (see User Story 3).

---

### User Story 2 - Drill into one error group (Priority: P2)

An architect opens a specific recurring error to see how often it happened,
over what time span, and a complete original example of the error text —
including a full multi-line stack trace when the log contained one.

**Why this priority**: Turns "this error happened 47 times" into something
actionable — what does it actually say, and is it still happening.

**Independent Test**: With groups already computed (User Story 1), open one
covering a multi-line stack trace and confirm the complete original text is
shown, not just its first line.

**Acceptance Scenarios**:

1. **Given** an error group with multiple occurrences, **When** the
   architect opens it, **Then** they see the normalized template, the
   total occurrence count, the earliest and latest occurrence timestamps
   (when extractable), and at least one complete original example
   (including any captured stack trace lines).
2. **Given** none of a group's occurrences have an extractable timestamp,
   **When** the architect opens it, **Then** the group is still shown with
   its example text, without a fabricated timestamp.

---

### User Story 3 - Log scan issues surfaced separately (Priority: P3)

An architect reviews which log directories could not be matched to any
registered service and which log files could not be read, kept visibly
separate from the grouped error report.

**Why this priority**: Prevents "missing" errors from being confused with
"nothing wrong" — mirrors the scan-issues pattern already established for
the registry (feature 001).

**Independent Test**: Scan a log root containing one directory whose name
matches no registered service and one genuinely unreadable file, and verify
both appear in a separate issues view rather than being silently dropped.

**Acceptance Scenarios**:

1. **Given** a log directory's name matches no registered service, **When**
   the scan runs, **Then** it appears in a separate unattributed list.
2. **Given** a log file cannot be read as text and isn't a recognized
   excluded format, **When** the scan runs, **Then** it is reported with a
   specific reason, without stopping the rest of the scan.
3. **Given** the underlying log files change and the architect re-scans,
   **When** the scan completes, **Then** groups and issues reflect the
   current state of the log files (previously-reported issues that are now
   resolved disappear).

---

### Edge Cases

- What happens when an error group would combine occurrences that share a
  normalized template but come from genuinely different services? They
  never do — grouping is always scoped per service first, then by
  template, so the same recurring bug in two services produces two
  separate groups.
- What happens when a multi-line error's continuation lines never end
  (e.g., corrupted or unusually formatted log content)? Capture is capped
  at a fixed maximum number of lines per entry, so one malformed entry
  cannot consume the rest of the file.
- What happens when a log root contains compressed/rotated files (e.g.,
  `.gz`)? They are excluded from scanning as a known, expected format —
  not reported as a scan issue, since this is normal, not a failure.
- What happens when two different error types occur back-to-back with no
  blank line between them? A new recognized error marker line always ends
  the previous entry's continuation capture, even without a blank line.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: System MUST allow the user to specify a root directory to
  scan for log files, independent of the repository roots used to build
  the service registry.
- **FR-002**: System MUST attempt to read, as UTF-8 text, every file under
  the log root with extension `.log`, `.txt`, or no extension; files with
  other extensions (e.g., compressed archives) MUST be excluded from the
  scan without being reported as an issue.
- **FR-003**: System MUST determine a log file's associated service by
  checking whether its immediate parent directory's name exactly matches a
  service name already present in the registry.
- **FR-004**: A log file whose parent directory name matches no registered
  service MUST be recorded as unattributed rather than silently dropped or
  attributed to an arbitrary service.
- **FR-005**: System MUST detect the start of an error entry at any
  physical line containing a recognized error/severity marker
  (case-insensitive), from a fixed, documented set (e.g. `ERROR`, `FATAL`,
  `SEVERE`, `CRITICAL`, `Exception`, `Traceback`, `panic:`, `Unhandled`).
- **FR-006**: System MUST include, as part of the same error entry, any
  immediately following lines recognized as stack-trace continuations
  (indented lines, or lines starting with `at `, `File `, or
  `Caused by:`), stopping at the first line matching none of these, a new
  error marker, or after a fixed maximum line count — whichever comes
  first.
- **FR-007**: System MUST normalize each error entry's first line into a
  template by replacing embedded digit sequences, UUID-shaped sequences,
  hexadecimal-looking sequences, and quoted substrings with fixed
  placeholders, before grouping.
- **FR-008**: System MUST group error entries sharing the same service and
  normalized template into one error group and record its occurrence
  count.
- **FR-009**: System MUST attempt to extract a timestamp from the start of
  each error entry's first line using a small set of common formats; an
  entry whose timestamp cannot be extracted MUST still be recorded, without
  a fabricated timestamp.
- **FR-010**: For each error group, System MUST track the earliest and
  latest occurrence timestamp among its entries that have one.
- **FR-011**: System MUST present a browsable view of error groups per
  service, each showing its normalized template, severity marker, and
  occurrence count.
- **FR-012**: Users MUST be able to open an error group and see its full
  list of occurrences (or a representative sample), including at least one
  complete original, unnormalized example.
- **FR-013**: System MUST present unattributed log directories and
  unreadable log files in a view separate from the grouped error report.
- **FR-014**: System MUST isolate a single unreadable or malformed log
  file's failure so it does not stop scanning of the remaining log files.
- **FR-015**: Re-running a log scan MUST replace previously computed error
  groups and log-scan issues to reflect the current state of the scanned
  log files.

### Key Entities

- **Error Group**: A distinct recurring error for one service (or
  unattributed). Attributes: service (or unattributed marker), normalized
  template, severity marker, occurrence count, earliest/latest occurrence
  timestamp, a complete original example text.
- **Error Occurrence**: One captured instance, possibly spanning multiple
  lines. Attributes: original raw text (including any captured
  continuation lines), extracted timestamp (nullable), source log file
  path, starting line number.
- **Log Scan Issue**: An unattributed log directory or an unreadable log
  file. Attributes: path, issue type (`unattributed` / `unreadable`),
  reason, detection timestamp.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: Ten or more near-duplicate error lines differing only in
  embedded identifiers collapse into a single group.
- **SC-002**: A user can determine which service every error group belongs
  to, or that it is unattributed, without opening any raw log file.
- **SC-003**: A user can view a complete original example of any error
  group, including a full multi-line stack trace when the source log
  contained one.
- **SC-004**: A single unreadable log file never prevents any other valid
  log file in the same scan from contributing to the report.
- **SC-005**: Re-running a log scan after the underlying log files change
  updates the report to reflect the current state, with no manual cleanup.

## Assumptions

- Log files already exist locally, already exported or copied ahead of
  time; the system does not tail live processes, connect to a remote log
  aggregation service, or require any running agent (Local-First).
- Error detection relies on the fixed severity-marker set in FR-005;
  supporting additional custom markers is a possible future extension.
- Multi-line capture uses simple, documented continuation rules and a
  fixed maximum line count per entry, bounding worst-case cost — it is not
  a full parser for every stack-trace format in existence.
- Normalization covers digits, UUIDs, hex sequences, and quoted
  substrings; it does not attempt full semantic comparison of arbitrary
  log messages, which would require statistical or ML-based techniques
  explicitly out of scope (Constitution Principle I).
- Timestamp extraction covers a small set of common formats (e.g.
  ISO-8601, `YYYY-MM-DD HH:MM:SS`); logs using other formats still group
  correctly but without first/last-seen timestamps.
- Raw log text — including any values it happens to already contain — is
  displayed exactly as captured from the source file. Constitution
  Principle III (No Personal Data) governs data this system deliberately
  collects about people; it does not require scanning arbitrary log
  content the user chooses to point the system at for incidental personal
  data, the same way ADR content is treated verbatim in the constitution's
  ADR Integrity principle.
