# Quickstart: Service Registry

Validates the feature end-to-end against the acceptance scenarios in
[spec.md](./spec.md).

## Prerequisites

- Python 3.12+, Node.js (for the frontend build)
- A test fixture directory tree containing: one `package.json`, one `pom.xml`, one
  `requirements.txt`, one `go.mod`, one `composer.json` (each a valid, minimal
  manifest), plus one syntactically invalid `package.json` and one `pom.xml`
  missing `artifactId` (to exercise scan issues)

## Setup

```bash
cd backend
python -m venv .venv && . .venv/Scripts/activate  # or source .venv/bin/activate
pip install -r requirements.txt
uvicorn src.main:app --reload
```

```bash
cd frontend
npm install
npm run dev
```

## Validation steps

1. Open the frontend in a browser; the registry table is empty before any scan.
2. Trigger a scan against the fixture directory (via the UI's scan button, or
   directly: `curl -X POST http://localhost:8000/api/scan -d '{"roots":["<fixture path>"]}' -H "Content-Type: application/json"`).
3. **Expect** (User Story 1): the registry table shows exactly 5 services, one per
   valid manifest, each with a derived name, ecosystem, and repository path — see
   [contracts/api.md](./contracts/api.md).
4. Open the service derived from the manifest with declared dependencies.
   **Expect** (User Story 2): its dependency list matches the manifest exactly.
5. Open the Scan Issues view. **Expect** (User Story 3): the broken `package.json`
   appears with `issue_type: "unparsable"` and a specific reason; the `pom.xml`
   missing `artifactId` produced a service marked `is_complete: false` and also
   appears here with `issue_type: "incomplete_data"`.
6. Fix the broken `package.json` in the fixture tree and re-run the scan.
   **Expect** (SC-005): the corresponding scan issue disappears and a new service
   entry appears in its place.

## Out of scope for this quickstart

- Performance validation against the 500-manifest / 30-second target (covered by a
  dedicated integration test in `backend/tests/integration/`, not manual steps).
