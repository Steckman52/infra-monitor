import { useEffect, useState } from 'react';
import AdrTable from '../components/AdrTable';
import { listAdrs, type AdrSummary } from '../services/api';

interface AdrsPageProps {
  onBack: () => void;
}

function AdrsPage({ onBack }: AdrsPageProps) {
  const [adrs, setAdrs] = useState<AdrSummary[]>([]);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    let cancelled = false;
    listAdrs()
      .then((data) => {
        if (!cancelled) setAdrs(data);
      })
      .catch((err) => {
        if (!cancelled) {
          setError(err instanceof Error ? err.message : 'Failed to load ADRs.');
        }
      });
    return () => {
      cancelled = true;
    };
  }, []);

  return (
    <div className="adrs-page">
      <button type="button" onClick={onBack}>
        ← Back to registry
      </button>
      <h1>Architectural Decision Records</h1>
      {error && (
        <p className="load-error" role="alert">
          {error}
        </p>
      )}
      <AdrTable adrs={adrs} />
    </div>
  );
}

export default AdrsPage;
