import { useEffect, useState } from 'react';
import ServiceDetail from '../components/ServiceDetail';
import { getServiceDetail, type ServiceDetail as ServiceDetailData } from '../services/api';

interface ServiceDetailPageProps {
  serviceId: number;
  onBack: () => void;
  onSelectAdr: (id: number) => void;
  onSelectErrorGroup: (id: number) => void;
}

function ServiceDetailPage({ serviceId, onBack, onSelectAdr, onSelectErrorGroup }: ServiceDetailPageProps) {
  const [service, setService] = useState<ServiceDetailData | null>(null);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    let cancelled = false;
    getServiceDetail(serviceId)
      .then((data) => {
        if (!cancelled) setService(data);
      })
      .catch((err) => {
        if (!cancelled) {
          setError(err instanceof Error ? err.message : 'Failed to load service.');
        }
      });
    return () => {
      cancelled = true;
    };
  }, [serviceId]);

  return (
    <div className="service-detail-page">
      <button type="button" onClick={onBack}>
        ← Back to registry
      </button>
      {error && (
        <p className="load-error" role="alert">
          {error}
        </p>
      )}
      {!error && !service && <p>Loading…</p>}
      {service && (
        <ServiceDetail
          service={service}
          onSelectAdr={onSelectAdr}
          onSelectErrorGroup={onSelectErrorGroup}
        />
      )}
    </div>
  );
}

export default ServiceDetailPage;
