import { TriangleAlert } from 'lucide-react';
import { useEffect, useState } from 'react';
import AdrIssuesList from '../components/AdrIssuesList';
import BackLink from '../components/BackLink';
import { useLanguage } from '../i18n/LanguageContext';
import { listAdrIssues, type AdrIssue } from '../services/api';

interface AdrIssuesPageProps {
  onBack: () => void;
}

function AdrIssuesPage({ onBack }: AdrIssuesPageProps) {
  const { t } = useLanguage();
  const [issues, setIssues] = useState<AdrIssue[]>([]);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    let cancelled = false;
    listAdrIssues()
      .then((data) => {
        if (!cancelled) setIssues(data);
      })
      .catch((err) => {
        if (!cancelled) {
          setError(err instanceof Error ? err.message : 'Failed to load ADR issues.');
        }
      });
    return () => {
      cancelled = true;
    };
  }, []);

  return (
    <div className="section">
      <BackLink onClick={onBack} label={t.nav.adrs} />
      {error && (
        <p className="load-error" role="alert">
          <TriangleAlert /> {error}
        </p>
      )}
      <div className="panel">
        <AdrIssuesList issues={issues} />
      </div>
    </div>
  );
}

export default AdrIssuesPage;
