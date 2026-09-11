# Frontend — Service Registry UI

React (Vite + TypeScript) single-page app for the infrastructure monitoring
system's service registry: trigger scans, browse discovered services, and
review scan issues. Talks to the [backend](../backend/README.md) over
`/api/*`.

## Structure

* `src/pages/` — `RegistryPage`, `ServiceDetailPage`, `ScanIssuesPage`, one
  per screen. `App.tsx` switches between them with simple local state (no
  router — three screens don't justify the dependency).
* `src/components/` — `ScanButton`, `ServiceTable`, `ServiceDetail`,
  `ScanIssuesList`.
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
