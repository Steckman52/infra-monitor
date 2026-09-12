import { useEffect, useState } from 'react';
import LogScanIssuesList from '../components/LogScanIssuesList';
import { listLogScanIssues, type LogScanIssue } from '../services/api';

interface LogScanIssuesPageProps {
  onBack: () => void;
}

function LogScanIssuesPage({ onBack }: LogScanIssuesPageProps) {
  const [issues, setIssues] = useState<LogScanIssue[]>([]);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    let cancelled = false;
    listLogScanIssues()
      .then((data) => {
        if (!cancelled) setIssues(data);
      })
      .catch((err) => {
        if (!cancelled) {
          setError(err instanceof Error ? err.message : 'Failed to load log scan issues.');
        }
      });
    return () => {
      cancelled = true;
    };
  }, []);

  return (
    <div className="log-scan-issues-page">
      <button type="button" onClick={onBack}>
        ← Back to log errors
      </button>
      <h1>Log Scan Issues</h1>
      {error && (
        <p className="load-error" role="alert">
          {error}
        </p>
      )}
      <LogScanIssuesList issues={issues} />
    </div>
  );
}

export default LogScanIssuesPage;
