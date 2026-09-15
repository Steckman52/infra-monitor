import { TriangleAlert } from 'lucide-react';
import { useEffect, useState } from 'react';
import BackLink from '../components/BackLink';
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
    <div className="section">
      <BackLink onClick={onBack} />
      {error && (
        <p className="load-error" role="alert">
          <TriangleAlert /> {error}
        </p>
      )}
      <div className="panel">
        <ScanIssuesList issues={issues} />
      </div>
    </div>
  );
}

export default ScanIssuesPage;
