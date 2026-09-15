import { TriangleAlert } from 'lucide-react';
import { useEffect, useState } from 'react';
import AdrTable from '../components/AdrTable';
import { useLanguage } from '../i18n/LanguageContext';
import { listAdrs, type AdrSummary } from '../services/api';

interface AdrsPageProps {
  onSelectAdr: (id: number) => void;
  onViewIssues: () => void;
}

function AdrsPage({ onSelectAdr, onViewIssues }: AdrsPageProps) {
  const { t } = useLanguage();
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
    <>
      {error && (
        <p className="load-error" role="alert">
          <TriangleAlert /> {error}
        </p>
      )}
      <div className="section">
        <div className="section-head">
          <button type="button" className="link-button" onClick={onViewIssues}>
            {t.adrs.viewIssues}
          </button>
        </div>
        <div className="panel">
          <AdrTable adrs={adrs} onSelectAdr={onSelectAdr} />
        </div>
      </div>
    </>
  );
}

export default AdrsPage;
