# Frontend — Service Registry & Dependency Map UI

React (Vite + TypeScript) single-page app for the infrastructure monitoring
system: trigger scans, browse discovered services, review scan issues,
check dependency version compatibility, and view the docker-compose-derived
connection graph. Talks to the [backend](../backend/README.md) over
`/api/*`.

## Structure

* `src/pages/` — `RegistryPage`, `ServiceDetailPage`, `ScanIssuesPage`,
  `CompatibilityPage`, `ConnectionsPage`, one per screen. `App.tsx` switches
  between them with simple local state (no router — five screens still
  don't justify the dependency).
* `src/components/` — `ScanButton`, `ServiceTable`, `ServiceDetail`,
  `ScanIssuesList`, `CompatibilityTable`, `ConnectionGraphView`.
  `ServiceDetail` also renders that service's own compatibility risks and
  connections.
* `src/services/api.ts` — typed `fetch` wrappers for every backend endpoint.

## Running locally

```bash
npm install
npm run dev
```

The dev server proxies `/api/*` to `http://localhost:8000` (see
`vite.config.ts`), so start the [backend](../backend/README.md) first.

## Building

```bash
npm run build
```
