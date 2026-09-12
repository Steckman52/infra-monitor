import { useState } from 'react'
import CompatibilityPage from './pages/CompatibilityPage'
import ConnectionsPage from './pages/ConnectionsPage'
import ErrorGroupDetailPage from './pages/ErrorGroupDetailPage'
import LogScanIssuesPage from './pages/LogScanIssuesPage'
import LogsPage from './pages/LogsPage'
import RegistryPage from './pages/RegistryPage'
import ScanIssuesPage from './pages/ScanIssuesPage'
import ServiceDetailPage from './pages/ServiceDetailPage'

type View =
  | { name: 'registry' }
  | { name: 'service-detail'; serviceId: number }
  | { name: 'scan-issues' }
  | { name: 'compatibility' }
  | { name: 'connections' }
  | { name: 'logs' }
  | { name: 'error-group-detail'; groupId: number }
  | { name: 'log-scan-issues' }

function App() {
  const [view, setView] = useState<View>({ name: 'registry' })

  if (view.name === 'service-detail') {
    return (
      <ServiceDetailPage
        serviceId={view.serviceId}
        onBack={() => setView({ name: 'registry' })}
      />
    )
  }

  if (view.name === 'scan-issues') {
    return <ScanIssuesPage onBack={() => setView({ name: 'registry' })} />
  }

  if (view.name === 'compatibility') {
    return <CompatibilityPage onBack={() => setView({ name: 'registry' })} />
  }

  if (view.name === 'connections') {
    return <ConnectionsPage onBack={() => setView({ name: 'registry' })} />
  }

  if (view.name === 'error-group-detail') {
    return (
      <ErrorGroupDetailPage
        groupId={view.groupId}
        onBack={() => setView({ name: 'logs' })}
      />
    )
  }

  if (view.name === 'log-scan-issues') {
    return <LogScanIssuesPage onBack={() => setView({ name: 'logs' })} />
  }

  if (view.name === 'logs') {
    return (
      <LogsPage
        onBack={() => setView({ name: 'registry' })}
        onSelectGroup={(groupId) => setView({ name: 'error-group-detail', groupId })}
        onViewLogScanIssues={() => setView({ name: 'log-scan-issues' })}
      />
    )
  }

  return (
    <RegistryPage
      onSelectService={(serviceId) => setView({ name: 'service-detail', serviceId })}
      onViewScanIssues={() => setView({ name: 'scan-issues' })}
      onViewCompatibility={() => setView({ name: 'compatibility' })}
      onViewConnections={() => setView({ name: 'connections' })}
      onViewLogs={() => setView({ name: 'logs' })}
    />
  )
}

export default App
