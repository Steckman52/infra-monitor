import { useState } from 'react'
import RegistryPage from './pages/RegistryPage'
import ServiceDetailPage from './pages/ServiceDetailPage'

function App() {
  const [selectedServiceId, setSelectedServiceId] = useState<number | null>(null)

  if (selectedServiceId !== null) {
    return (
      <ServiceDetailPage
        serviceId={selectedServiceId}
        onBack={() => setSelectedServiceId(null)}
      />
    )
  }

  return <RegistryPage onSelectService={setSelectedServiceId} />
}

export default App
