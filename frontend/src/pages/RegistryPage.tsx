import { useCallback, useEffect, useState } from 'react';
import ScanButton from '../components/ScanButton';
import ServiceTable from '../components/ServiceTable';
import { listServices, type ScanResponse, type ServiceSummary } from '../services/api';

interface RegistryPageProps {
  onSelectService: (id: number) => void;
  onViewScanIssues: () => void;
}

function RegistryPage({ onSelectService, onViewScanIssues }: RegistryPageProps) {
  const [services, setServices] = useState<ServiceSummary[]>([]);
  const [lastScanSummary, setLastScanSummary] = useState<ScanResponse | null>(null);
  const [loadError, setLoadError] = useState<string | null>(null);

  const refreshServices = useCallback(async () => {
    try {
      const data = await listServices();
      setServices(data);
      setLoadError(null);
    } catch (err) {
      setLoadError(err instanceof Error ? err.message : 'Failed to load services.');
    }
  }, []);

  useEffect(() => {
    refreshServices();
  }, [refreshServices]);

  const handleScanComplete = async (result: ScanResponse) => {
    setLastScanSummary(result);
    await refreshServices();
  };

  return (
    <div className="registry-page">
      <h1>Service Registry</h1>
      <button type="button" onClick={onViewScanIssues}>
        View scan issues
      </button>
      <ScanButton onScanComplete={handleScanComplete} />
      {lastScanSummary && (
        <p className="scan-summary">
          Found {lastScanSummary.services_found} service(s), {lastScanSummary.issues_found}{' '}
          issue(s).
          {lastScanSummary.unreachable_roots.length > 0 && (
            <> Unreachable roots: {lastScanSummary.unreachable_roots.join(', ')}</>
          )}
        </p>
      )}
      {loadError && (
        <p className="load-error" role="alert">
          {loadError}
        </p>
      )}
      <ServiceTable services={services} onSelectService={onSelectService} />
    </div>
  );
}

export default RegistryPage;
