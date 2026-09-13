import { useEffect, useState } from 'react';
import AdrDetail from '../components/AdrDetail';
import { getAdrDetail, type AdrDetail as AdrDetailData } from '../services/api';

interface AdrDetailPageProps {
  adrId: number;
  onBack: () => void;
}

function AdrDetailPage({ adrId, onBack }: AdrDetailPageProps) {
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
    <div className="adr-detail-page">
      <button type="button" onClick={onBack}>
        ← Back to ADRs
      </button>
      {error && (
        <p className="load-error" role="alert">
          {error}
        </p>
      )}
      {!error && !adr && <p>Loading…</p>}
      {adr && <AdrDetail adr={adr} />}
    </div>
  );
}

export default AdrDetailPage;
