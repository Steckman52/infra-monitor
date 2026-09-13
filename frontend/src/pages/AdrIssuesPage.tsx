import { useEffect, useState } from 'react';
import AdrIssuesList from '../components/AdrIssuesList';
import { listAdrIssues, type AdrIssue } from '../services/api';

interface AdrIssuesPageProps {
  onBack: () => void;
}

function AdrIssuesPage({ onBack }: AdrIssuesPageProps) {
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
    <div className="adr-issues-page">
      <button type="button" onClick={onBack}>
        ← Back to ADRs
      </button>
      <h1>ADR Issues</h1>
      {error && (
        <p className="load-error" role="alert">
          {error}
        </p>
      )}
      <AdrIssuesList issues={issues} />
    </div>
  );
}

export default AdrIssuesPage;
