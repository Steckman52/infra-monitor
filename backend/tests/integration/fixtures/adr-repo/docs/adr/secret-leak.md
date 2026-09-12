# Secret Leak Decision

* Status: accepted
* Date: 2026-01-05

## Context and Problem Statement

While documenting our AWS setup we accidentally pasted a real-looking key
into this record: AKIAABCDEFGHIJKLMNOP. It should have been redacted.

## Decision Outcome

Chosen option: use environment variables instead of hardcoded keys.
