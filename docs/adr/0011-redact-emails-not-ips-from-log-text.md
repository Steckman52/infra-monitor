# Redact email addresses from stored log text; leave IP addresses alone

* Status: accepted
* Date: 2026-09-13

## Context and Problem Statement

Constitution Principle III prohibits the system from collecting, storing, or
processing personal data, explicitly naming "names, emails, usernames, IP
addresses tied to a person" as examples, while explicitly scoping log data
to "log error signatures." Feature 003 stores raw, unredacted log text
verbatim in `ErrorGroup.example_text` and `ErrorOccurrence.raw_text` so a
user can see the actual failing line, not just its normalized template — a
multi-perspective code review flagged this as a real gap: an application log
line can legitimately contain an email, username, or IP address, and none of
it was ever redacted before storage or display.

## Decision Drivers

* Constitution Principle III, applied literally: emails are named as a
  prohibited example.
* Constitution Principle I (No AI/ML): any redaction must be a small, fixed,
  rule-based heuristic — the same philosophy already applied to the ADR
  module's secret-pattern detection (research.md §8 in
  004-adr-module), not a statistical PII scanner.
* The log analysis feature's entire diagnostic value depends on showing
  *which* infrastructure endpoint failed and *why* — over-redacting would
  make the feature useless for its stated purpose.

## Considered Options

* Redact nothing (status quo) — rejected, the finding is real.
* Stop storing raw text entirely, keep only the normalized template —
  rejected: removes the "Example"/occurrence drill-down capability the
  feature was built to provide, a much larger regression than the actual
  gap warrants.
* Redact a fixed set of PII-shaped patterns (email addresses) before
  persisting, leave IP addresses alone.
* Redact both email addresses and IP addresses before persisting.

## Decision Outcome

Chosen option: **redact email addresses only**, via one fixed regex
(`[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}`) applied to a log entry's
first line and full raw text before either is used to build the normalized
template or stored as `example_text`/`raw_text` (`pii_redaction.py`,
applied in `log_scan_service.py`). An email address in a log line is
essentially always a personal identifier — there is no infrastructure
reason for one to appear in error output, so redacting it costs nothing
diagnostically.

IP addresses are deliberately **not** redacted. In the infrastructure logs
this tool is built to analyze, an IP address is overwhelmingly a
service/network identifier (which pod, which upstream, which database host
failed to respond) rather than data "tied to a person" — the qualifier
Principle III itself uses. Redacting every IP-shaped string would remove
information that is frequently the entire point of the log entry ("Connection
refused: 10.0.0.5:5432") while providing little real privacy benefit for
machine-to-machine traffic. Usernames are also not redacted: unlike emails
and IPs, there is no fixed pattern that reliably identifies a username
without an unacceptable false-positive rate against ordinary log vocabulary.

### Positive Consequences

* Closes the concrete gap the review found, with a one-file, easily-audited
  change.
* Consistent with the ADR module's own established pattern: a small, fixed,
  documented pattern set, never a blocker to the scan itself.

### Negative Consequences

* Not exhaustive — a username or a person's real name embedded in free-text
  log output would still pass through unredacted. Accepted: this project's
  own constitution asks for the same class of heuristic already used for
  ADR secret detection, not a general-purpose PII scrubber, which would be
  a substantially larger and statistically-driven tool in its own right.

## Amendment (2026-09-25): credentials, and the ADR path

A security audit demonstrated two gaps in the decision as originally
implemented, both now closed in `pii_redaction.py`.

**Credentials were not covered.** The audit captured a root password and an
SSH passphrase out of a log line, stored verbatim and served back through
the API — including into `normalized_template`, which the *list* endpoint
returns, so it was on screen without opening a detail view. Credentials are
not personal data, so Principle III does not strictly reach them; but this
tool stores what it reads from files the user did not write, into a database
that gets backed up and copied to colleagues. The same fixed-pattern
heuristic now also replaces credential *values* (`password=`, `token=`,
`api_key=`, provider-shaped keys such as `AKIA…`/`ghp_…`, credentials inside
a URL, and the body of a PEM private-key block).

Two deliberate limits: the key **name** is kept and only its value replaced,
so the redacted line still tells an operator *what* to go and rotate; and
patterns match an assignment rather than guessing at bare high-entropy
strings, because a redactor that fires on ordinary log traffic destroys the
feature it is protecting. Free-prose secrets ("the root pw is hunter2")
still pass through — the same accepted limit as usernames above.

**Redaction was applied on the log path only.** `AdrRecord.content` stored
and served the entire raw Markdown of every imported ADR, so an ADR
recording an incident carried its participants' emails, and a pasted private
key was returned verbatim by `GET /api/adrs/{id}` — by the same endpoint
that had already flagged it with `has_secret_warning`. ADR content now goes
through the same redaction. The secret **check** deliberately still runs on
the original text, so redaction cannot hide a leak from the warning that
exists to report it, and the record itself is never withheld: per the ADR
module's own principle, a secret warning is a flag, never a blocker.

## Links

* [Constitution Principle III](../../.specify/memory/constitution.md)
* [004-adr-module research.md §8](../../specs/004-adr-module/research.md) — the secret-pattern heuristic this decision's philosophy mirrors
