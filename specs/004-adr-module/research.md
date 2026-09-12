# Phase 0 Research: ADR Module

## 1. Extend the registry scan, not a fourth independent trigger

**Decision**: ADR scanning runs inside the existing `run_scan`
orchestrator (features 001/002), reusing the same root paths already
passed to `POST /api/scan`, rather than a new `POST /api/adr-scan`
endpoint.

**Rationale**: `docs/adr/` is source-controlled content living inside the
same repositories the registry already scans — this is exactly the
situation feature 002 already resolved by extending `run_scan` for
`docker-compose.yml`, rather than introducing a separate trigger. Feature
003's logs got their own independent trigger specifically *because* logs
are runtime output living outside the source repository, not because
"new scanned artifact" always implies a new endpoint. ADRs clearly belong
to the first category.

**Alternatives considered**: A dedicated `POST /api/adr-scan` mirroring
feature 003 — rejected; would force the user to remember and run a third
scan action for content that's already inside the repositories they just
scanned, and would reopen the cross-scan-consistency problem feature
002's ADR 0005 already solved for compose data.

## 2. Persist ADR records and relationships at scan time

**Decision**: Like the registry and unlike feature 002's on-read
compatibility view, ADR records, relationships, and service associations
are computed once during the scan and persisted.

**Rationale**: Producing them requires reading and regex-parsing
Markdown files and resolving cross-file link references — real I/O and
text work that shouldn't repeat on every page view, the same reasoning
already applied to feature 003's error groups (ADR 0006).

## 3. MADR parsing: fixed regex over this project's own conventions

**Decision**: No Markdown AST/parser library. Extract via regex, matched
against this project's own established MADR shape (Constitution
Principle VI, and literally demonstrated by this project's own 7 existing
ADRs):
- **Title**: the first line matching `^#\s+(.+)$`.
- **Status**: a line matching `^\*\s*Status:\s*(.+)$` (case-insensitive on
  the label).
- **Date**: a line matching `^\*\s*Date:\s*(\d{4}-\d{2}-\d{2})`.

**Rationale**: A full CommonMark parser is unjustified weight for
extracting three fixed, line-anchored fields from a project's own
self-authored convention (Principle V). If a file's status/date lines
don't match, FR-004 already specifies "unrecognized" rather than a parser
crash — the feature degrades gracefully by design, not by exception
handling.

**Alternatives considered**: A Markdown library (e.g. `markdown-it-py`) to
walk a real AST — rejected as unneeded weight; would also require mapping
MADR's various real-world dialects, when this project only needs to
recognize its own.

## 4. Status normalization keyword order

**Decision**: Check keywords in this fixed priority order against the raw
status text (case-insensitive substring match): `superseded` → `deprecated`
→ `rejected` → `accepted` → `proposed` → else `unrecognized`.

**Rationale**: `superseded` is checked first because a real status value
often reads like "superseded by [ADR-0005](...)", which doesn't contain
any of the other keywords — but ordering it first is a defensive,
explainable rule rather than an accident of which substring happens to
appear.

## 5. Relationship detection: one regex over the whole file

**Decision**: Search the entire raw file content (not just the Status
line or just a Links section) for the pattern:
`(?i)\b(supersedes|superseded by|amends|amended by)\b[^\n]*?\[[^\]]*\]\(([^)]+)\)`
— i.e., one of the four keyword phrases followed, on the same line, by a
Markdown link. The keyword determines both the relationship type
(`supersedes` or `amends`) and its direction; the link's target is
resolved relative to the current ADR file's directory.

**Rationale**: This project's own ADRs put such references either in the
Status line or in a `## Links` section (both already appear in this
project's real ADR 0004 body, structurally). Searching the whole file
with one regex covers both without needing to separately locate a
"Links" section header first — simpler, and just as explainable, since
the match itself is the explanation shown to the user.

**Alternatives considered**: Requiring the link to appear only under a
`## Links` heading — rejected; the Status field is an equally common,
equally intentional place for this in real MADR usage, and restricting
detection to one location would silently miss the other.

## 6. Resolving a relationship's target ADR

**Decision**: Resolve the matched link path relative to the current ADR
file's own directory into an absolute path, then look it up against the
set of ADR file paths found in this same scan (built in an initial pass
before relationships are resolved in a second pass). No match ⇒ no
relationship row (Edge Case, spec.md) — never a dangling reference.

**Rationale**: Consistent with feature 002's build-context resolution
(ADR 0002-in-spirit): match by resolved path, not by name, and treat "no
match" as a legitimate, explainable absence rather than an error.

## 7. Many-to-many ADR-to-service association

**Decision**: For each ADR, compute its repository root as the
grandparent of its `docs/adr` directory (i.e., `.../REPO/docs/adr/x.md` →
repository root `.../REPO`). Associate the ADR with every registered
`Service` whose `repository_path`, once resolved, equals or is nested
under that repository root.

**Rationale**: Already resolved in discussion (spec.md, FR-006) — a
monorepo's single `docs/adr/` folder legitimately relates to every
service inside it, not one arbitrarily chosen owner.

## 8. Secret-pattern heuristic (Constitution Principle VIII)

**Decision**: Three fixed, documented regex patterns, checked against an
ADR's full content:
- A private-key header: `-----BEGIN (RSA |EC |)PRIVATE KEY-----`
- An AWS-style access key ID: `AKIA[0-9A-Z]{16}`
- A generic credential-looking assignment:
  `(?i)\b(password|passwd|secret|token|api[_-]?key)\b\s*[:=]\s*['"]?[A-Za-z0-9\-_/+=]{8,}`

A match sets `has_secret_warning=True` on the `AdrRecord` and adds an
entry to the combined issues/warnings view (FR-011) — it never blocks or
redacts the import (FR-007/SC-003).

**Rationale**: A small, fixed pattern set is exactly what Principle
VIII asks for ("эвристическая проверка... по регулярным выражениям") and
what Principle I permits (rule-based, not statistical). These three
patterns cover the most common accidental-secret shapes without
attempting an exhaustive, false-positive-prone secret scanner — that
would be a distinct, much larger tool.

## Outcome

All Technical Context items are resolved; no `NEEDS CLARIFICATION` markers
remain.
