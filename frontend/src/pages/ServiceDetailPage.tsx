import { TriangleAlert } from 'lucide-react';
import { useEffect, useState } from 'react';
import BackLink from '../components/BackLink';
import ServiceDetail from '../components/ServiceDetail';
import { useLanguage } from '../i18n/LanguageContext';
import { getServiceDetail, type ServiceDetail as ServiceDetailData } from '../services/api';

interface ServiceDetailPageProps {
  serviceId: number;
  onBack: () => void;
  onSelectAdr: (id: number) => void;
  onSelectErrorGroup: (id: number) => void;
}

function ServiceDetailPage({ serviceId, onBack, onSelectAdr, onSelectErrorGroup }: ServiceDetailPageProps) {
  const { t } = useLanguage();
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
    <>
      <BackLink onClick={onBack} label={t.nav.services} />
      {error && (
        <p className="load-error" role="alert">
          <TriangleAlert /> {error}
        </p>
      )}
      {!error && !service && <p className="loading-state">{t.common.loading}</p>}
      {service && <ServiceDetail service={service} onSelectAdr={onSelectAdr} onSelectErrorGroup={onSelectErrorGroup} />}
    </>
  );
}

export default ServiceDetailPage;
