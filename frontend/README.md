# Frontend — Service Registry, Dependency Map, Log Analysis & ADR UI

React (Vite + TypeScript) single-page app for the infrastructure monitoring
system: an overview dashboard, trigger scans, browse discovered services,
review scan issues, check dependency version compatibility, view the
docker-compose-derived connection graph, scan/browse grouped log errors per
service, and browse imported ADRs with their relationships, related
services, and import issues. Available in English and Russian. Talks to the
[backend](../backend/README.md) over `/api/*`.

## Structure

* `src/pages/` — `DashboardPage`, `RegistryPage`, `ServiceDetailPage`,
  `ScanIssuesPage`, `CompatibilityPage`, `ConnectionsPage`, `LogsPage`,
  `ErrorGroupDetailPage`, `LogScanIssuesPage`, `AdrsPage`,
  `AdrDetailPage`, `AdrIssuesPage`, one per screen. Each page renders only
  its own content; the surrounding shell comes from `Layout`. `App.tsx`
  switches between them with simple local state (no router — twelve screens
  still don't justify the dependency).
* `src/components/` — `Layout` (the persistent shell: `Sidebar` + topbar)
  and `Sidebar` wrap every screen; `LanguageToggle` and `BackLink` are
  shared controls. The rest render one screen's content each:
  `ServiceDetail`, `ScanIssuesList`, `CompatibilityTable`,
  `ConnectionGraphView`, `ErrorGroupsTable`, `ErrorGroupDetail`,
  `LogScanIssuesList`, `AdrTable`, `AdrDetail`, `AdrIssuesList`.
  `ServiceDetail` also renders that service's own compatibility risks,
  connections, related ADRs, and recent error groups.
* `src/i18n/` — `strings.ts` holds the EN/RU dictionaries (the Russian one
  is typed as `typeof en`, so a missing translation is a compile error);
  `LanguageContext.tsx` provides `useLanguage()` and persists the choice to
  `localStorage`.
* `src/index.css` — the design tokens (OKLCH colour ramps, type scale,
  radii, shadows) and the shared component classes every screen is built
  from.
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
