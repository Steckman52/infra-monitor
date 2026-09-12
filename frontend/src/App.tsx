import { useState } from 'react'
import CompatibilityPage from './pages/CompatibilityPage'
import ConnectionsPage from './pages/ConnectionsPage'
import RegistryPage from './pages/RegistryPage'
import ScanIssuesPage from './pages/ScanIssuesPage'
import ServiceDetailPage from './pages/ServiceDetailPage'

type View =
  | { name: 'registry' }
  | { name: 'service-detail'; serviceId: number }
  | { name: 'scan-issues' }
  | { name: 'compatibility' }
  | { name: 'connections' }

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

  return (
    <RegistryPage
      onSelectService={(serviceId) => setView({ name: 'service-detail', serviceId })}
      onViewScanIssues={() => setView({ name: 'scan-issues' })}
      onViewCompatibility={() => setView({ name: 'compatibility' })}
      onViewConnections={() => setView({ name: 'connections' })}
    />
  )
}

export default App
