import { useEffect, useState } from 'react';
import ScanIssuesList from '../components/ScanIssuesList';
import { listScanIssues, type ScanIssue } from '../services/api';

interface ScanIssuesPageProps {
  onBack: () => void;
}

function ScanIssuesPage({ onBack }: ScanIssuesPageProps) {
  const [issues, setIssues] = useState<ScanIssue[]>([]);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    let cancelled = false;
    listScanIssues()
      .then((data) => {
        if (!cancelled) setIssues(data);
      })
      .catch((err) => {
        if (!cancelled) {
          setError(err instanceof Error ? err.message : 'Failed to load scan issues.');
        }
      });
    return () => {
      cancelled = true;
    };
  }, []);

  return (
    <div className="scan-issues-page">
      <button type="button" onClick={onBack}>
        ← Back to registry
      </button>
      <h1>Scan Issues</h1>
      {error && (
        <p className="load-error" role="alert">
          {error}
        </p>
      )}
      <ScanIssuesList issues={issues} />
    </div>
  );
}

export default ScanIssuesPage;
