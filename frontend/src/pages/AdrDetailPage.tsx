import { TriangleAlert } from 'lucide-react';
import { useEffect, useState } from 'react';
import AdrDetail from '../components/AdrDetail';
import BackLink from '../components/BackLink';
import { useLanguage } from '../i18n/LanguageContext';
import { getAdrDetail, type AdrDetail as AdrDetailData } from '../services/api';

interface AdrDetailPageProps {
  adrId: number;
  onBack: () => void;
}

function AdrDetailPage({ adrId, onBack }: AdrDetailPageProps) {
  const { t } = useLanguage();
  const [adr, setAdr] = useState<AdrDetailData | null>(null);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    let cancelled = false;
    getAdrDetail(adrId)
      .then((data) => {
        if (!cancelled) setAdr(data);
      })
      .catch((err) => {
        if (!cancelled) {
          setError(err instanceof Error ? err.message : 'Failed to load ADR.');
        }
      });
    return () => {
      cancelled = true;
    };
  }, [adrId]);

  return (
    <>
      <BackLink onClick={onBack} label={t.nav.adrs} />
      {error && (
        <p className="load-error" role="alert">
          <TriangleAlert /> {error}
        </p>
      )}
      {!error && !adr && <p className="loading-state">{t.common.loading}</p>}
      {adr && <AdrDetail adr={adr} />}
    </>
  );
}

export default AdrDetailPage;
