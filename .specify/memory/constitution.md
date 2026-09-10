<!--
Sync Impact Report
- Version change: [TEMPLATE] → 1.0.0 (initial ratification)
- Modified principles: n/a (first concrete adoption; template placeholders replaced)
- Added principles:
  - I. No AI/ML in the Product
  - II. Local-First & Resilient
  - III. No Personal Data
  - IV. Deterministic & Explainable
  - V. Test-First & Simplicity
  - VI. Documentation & Dogfooding
  - VII. Permissive Licensing
  - VIII. ADR Integrity & Safety
- Added sections: Scope Boundaries, Development Workflow
- Removed sections: none (template's generic Section 2/3 slots renamed and filled)
- Deferred items:
  - Dependency license scanning for *scanned* company repositories (as opposed to the
    product's own dependencies) is explicitly out of scope for v1.0.0 — recorded under
    Scope Boundaries as a candidate future extension, not a TODO.
- Templates requiring follow-up: none checked automatically by this command; verify
  .specify/templates/plan-template.md, spec-template.md, tasks-template.md, and
  .claude/skills/*/SKILL.md stay consistent with these principles during /speckit-plan.
-->

# Information System for Corporate Software Infrastructure Monitoring & ADR Management Constitution

## Core Principles

### I. No AI/ML in the Product
All analysis performed by the system — log error grouping, version compatibility checks,
dependency relationship mapping — MUST be implemented exclusively through deterministic
rules, templates, and regular expressions. The product MUST NOT embed or call machine
learning models, embeddings, LLMs, or any statistical/AI-based inference at runtime.
Rationale: this is a hard, non-negotiable requirement of the diploma project; every
analytical feature must remain fully rule-based and auditable.

### II. Local-First & Resilient
The system MUST run entirely on local infrastructure and MUST NOT require cloud services
or external APIs for its core functionality (service registry, dependency map, log
analysis, ADR module). Unavailability of any external service (e.g., package registries,
VCS hosting APIs) MUST NOT cause core functionality to fail; the system degrades
gracefully (e.g., using cached or already-scanned data) rather than blocking.
Rationale: corporate infrastructure tools must remain usable in air-gapped or
network-restricted environments and must not create a dependency on third-party uptime.

### III. No Personal Data
The system MUST NOT collect, store, or process personal data about individuals (names,
emails, usernames, IP addresses tied to a person, etc.). Only technical infrastructure
data is in scope: repositories, services, dependency versions, network/port relationships,
log error signatures, and architectural decisions.
Rationale: keeps the system's data model unambiguous and avoids any privacy/compliance
obligations that would be disproportionate to a technical infrastructure tool.

### IV. Deterministic & Explainable
Every analytical result (a version incompatibility, a log error group, a dependency
relationship between services) MUST be traceable to the specific rule, pattern, or
source manifest/file that produced it. The system MUST NOT expose a result without
being able to show its derivation. No black-box behavior is permitted anywhere.
Rationale: directly enforces Principle I and makes the system's output verifiable and
defensible in an academic/diploma review context.

### V. Test-First & Simplicity
Critical logic — package manifest parsing, version comparison, log pattern matching,
ADR/MADR import — MUST have tests written before implementation. The overall
architecture MUST stay simple and proportionate to the scope of a diploma project:
avoid speculative abstractions, unnecessary layers, or infrastructure not justified by
a current requirement.
Rationale: keeps the project deliverable within diploma timelines while still
demonstrating sound engineering practice on the parts most likely to break silently.

### VI. Documentation & Dogfooding
Every module MUST have minimal documentation covering its purpose, public interface,
and how to run it. The project's own architectural decisions MUST be recorded as ADRs
in this repository's `docs/adr/`, using the same ADR module and MADR format that the
system itself implements for its users.
Rationale: demonstrates the system's own methodology is practical by applying it to
itself, and keeps design rationale discoverable for the diploma defense.

### VII. Permissive Licensing
All dependencies and libraries used by the product itself MUST carry permissive
licenses (MIT, Apache-2.0, BSD, or equivalent). Copyleft licenses (GPL, AGPL, and
similar) MUST NOT be introduced into the product's own stack.
Rationale: avoids licensing obligations inappropriate for an academic deliverable.
Scanning the *licenses of dependencies inside company repositories being monitored* is
a distinct, larger feature and is explicitly out of scope for v1.0.0 (see Scope
Boundaries).

### VIII. ADR Integrity & Safety
The history of architectural decisions MUST be immutable: records are never deleted or
rewritten after the fact. A decision that changes is recorded as a new ADR marked
`superseded`/`deprecated` with an explicit reference to the record it replaces,
consistent with the MADR format. When importing ADRs from a repository's `docs/adr/`,
the system MUST run a heuristic, regex-based check for patterns resembling secrets,
tokens, or passwords in the imported text and MUST surface a warning — it MUST NOT
silently block or discard the import on this basis.
Rationale: keeps decision history trustworthy while acknowledging ADRs may reference
sensitive architecture details even though Principle III excludes personal data.

## Scope Boundaries

The product's functional scope for this diploma project is limited to four modules:
(1) service registry built by scanning package-manager manifests (`package.json`,
`pom.xml`, `requirements.txt`, `go.mod`, `composer.json`); (2) a dependency map and
version-compatibility check derived from those manifests plus `docker-compose.yml` /
Kubernetes manifests; (3) rule/regex-based log error analysis and grouping per service;
(4) an ADR module with cross-references between decisions and automatic import of
existing MADR-format ADRs from each repository's `docs/adr/`.

Features that resemble but exceed this scope MUST be treated as future extensions, not
silently absorbed into the current version. Known deferred extension: scanning and
flagging the *licenses of dependencies inside scanned company repositories* (distinct
from Principle VII, which governs only the product's own dependencies).

## Development Workflow

This project follows Spec-Driven Development via GitHub Spec Kit. Every feature MUST
pass through `/speckit-specify` → (optional `/speckit-clarify`) → `/speckit-plan` →
`/speckit-tasks` → (optional `/speckit-analyze`) → `/speckit-implement` before being
considered done. A plan that violates a Core Principle MUST document the violation and
justification in its Complexity Tracking section rather than silently deviating.
Test gates from Principle V apply before a task implementing critical logic is marked
complete.

## Governance

This constitution supersedes all other project practices and templates. Amendments
require: (1) a documented rationale for the change, (2) a version bump following the
policy below, (3) review of `.specify/templates/*` and `.claude/skills/*` for
consistency with the amended text. All `/speckit-plan` and `/speckit-tasks` runs MUST
verify alignment with this constitution; unjustified complexity or deviation MUST be
rejected or explicitly justified in the plan's Complexity Tracking section.

Versioning policy (semantic versioning applied to governance text):
- MAJOR: backward-incompatible principle removals or redefinitions.
- MINOR: a new principle or section added, or existing guidance materially expanded.
- PATCH: wording clarifications, typo fixes, non-semantic refinements.

**Version**: 1.0.0 | **Ratified**: 2026-09-10 | **Last Amended**: 2026-09-10
