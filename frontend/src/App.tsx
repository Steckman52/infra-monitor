import { useState } from 'react'
import Layout from './components/Layout'
import type { NavKey } from './components/Sidebar'
import { useLanguage } from './i18n/LanguageContext'
import AdrDetailPage from './pages/AdrDetailPage'
import AdrIssuesPage from './pages/AdrIssuesPage'
import AdrsPage from './pages/AdrsPage'
import CompatibilityPage from './pages/CompatibilityPage'
import ConnectionsPage from './pages/ConnectionsPage'
import DashboardPage from './pages/DashboardPage'
import ErrorGroupDetailPage from './pages/ErrorGroupDetailPage'
import LogScanIssuesPage from './pages/LogScanIssuesPage'
import LogsPage from './pages/LogsPage'
import RegistryPage from './pages/RegistryPage'
import ScanIssuesPage from './pages/ScanIssuesPage'
import ServiceDetailPage from './pages/ServiceDetailPage'

type View =
  | { name: 'dashboard' }
  | { name: 'registry' }
  | { name: 'service-detail'; serviceId: number }
  | { name: 'scan-issues' }
  | { name: 'compatibility' }
  | { name: 'connections' }
  | { name: 'logs' }
  | { name: 'error-group-detail'; groupId: number }
  | { name: 'log-scan-issues' }
  | { name: 'adrs' }
  | { name: 'adr-detail'; adrId: number }
  | { name: 'adr-issues' }

const NAV_BY_VIEW: Record<View['name'], NavKey> = {
  dashboard: 'dashboard',
  registry: 'registry',
  'service-detail': 'registry',
  'scan-issues': 'registry',
  compatibility: 'compatibility',
  connections: 'connections',
  logs: 'logs',
  'error-group-detail': 'logs',
  'log-scan-issues': 'logs',
  adrs: 'adrs',
  'adr-detail': 'adrs',
  'adr-issues': 'adrs',
}

function App() {
  const [view, setView] = useState<View>({ name: 'dashboard' })
  const { t } = useLanguage()

  const goTo = (target: NavKey) => {
    setView({ name: target === 'registry' ? 'registry' : target } as View)
  }

  const layoutProps = { active: NAV_BY_VIEW[view.name], onNavigate: goTo }

  if (view.name === 'dashboard') {
    return (
      <Layout title={t.dashboard.title} {...layoutProps}>
        <DashboardPage
          onViewRegistry={() => setView({ name: 'registry' })}
          onViewScanIssues={() => setView({ name: 'scan-issues' })}
          onViewCompatibility={() => setView({ name: 'compatibility' })}
          onViewLogs={() => setView({ name: 'logs' })}
          onViewLogScanIssues={() => setView({ name: 'log-scan-issues' })}
          onViewAdrs={() => setView({ name: 'adrs' })}
          onViewAdrIssues={() => setView({ name: 'adr-issues' })}
          onSelectErrorGroup={(groupId) => setView({ name: 'error-group-detail', groupId })}
        />
      </Layout>
    )
  }

  if (view.name === 'service-detail') {
    return (
      <Layout title={t.nav.services} {...layoutProps}>
        <ServiceDetailPage
          serviceId={view.serviceId}
          onBack={() => setView({ name: 'registry' })}
          onSelectAdr={(adrId) => setView({ name: 'adr-detail', adrId })}
          onSelectErrorGroup={(groupId) => setView({ name: 'error-group-detail', groupId })}
        />
      </Layout>
    )
  }

  if (view.name === 'scan-issues') {
    return (
      <Layout title={t.scanIssues.title} {...layoutProps}>
        <ScanIssuesPage onBack={() => setView({ name: 'registry' })} />
      </Layout>
    )
  }

  if (view.name === 'compatibility') {
    return (
      <Layout title={t.compatibility.title} {...layoutProps}>
        <CompatibilityPage />
      </Layout>
    )
  }

  if (view.name === 'connections') {
    return (
      <Layout title={t.connections.title} {...layoutProps}>
        <ConnectionsPage />
      </Layout>
    )
  }

  if (view.name === 'error-group-detail') {
    return (
      <Layout title={t.nav.logs} {...layoutProps}>
        <ErrorGroupDetailPage groupId={view.groupId} onBack={() => setView({ name: 'logs' })} />
      </Layout>
    )
  }

  if (view.name === 'log-scan-issues') {
    return (
      <Layout title={t.logScanIssues.title} {...layoutProps}>
        <LogScanIssuesPage onBack={() => setView({ name: 'logs' })} />
      </Layout>
    )
  }

  if (view.name === 'adrs') {
    return (
      <Layout title={t.adrs.title} {...layoutProps}>
        <AdrsPage
          onSelectAdr={(adrId) => setView({ name: 'adr-detail', adrId })}
          onViewIssues={() => setView({ name: 'adr-issues' })}
        />
      </Layout>
    )
  }

  if (view.name === 'adr-detail') {
    return (
      <Layout title={t.nav.adrs} {...layoutProps}>
        <AdrDetailPage adrId={view.adrId} onBack={() => setView({ name: 'adrs' })} />
      </Layout>
    )
  }

  if (view.name === 'adr-issues') {
    return (
      <Layout title={t.adrIssues.title} {...layoutProps}>
        <AdrIssuesPage onBack={() => setView({ name: 'adrs' })} />
      </Layout>
    )
  }

  if (view.name === 'logs') {
    return (
      <Layout title={t.logs.title} {...layoutProps}>
        <LogsPage
          onSelectGroup={(groupId) => setView({ name: 'error-group-detail', groupId })}
          onSelectService={(serviceId) => setView({ name: 'service-detail', serviceId })}
          onViewLogScanIssues={() => setView({ name: 'log-scan-issues' })}
        />
      </Layout>
    )
  }

  return (
    <Layout title={t.registry.title} {...layoutProps}>
      <RegistryPage
        onSelectService={(serviceId) => setView({ name: 'service-detail', serviceId })}
        onViewScanIssues={() => setView({ name: 'scan-issues' })}
      />
    </Layout>
  )
}

export default App
