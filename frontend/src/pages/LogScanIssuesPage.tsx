import { TriangleAlert } from 'lucide-react';
import { useEffect, useState } from 'react';
import BackLink from '../components/BackLink';
import LogScanIssuesList from '../components/LogScanIssuesList';
import { useLanguage } from '../i18n/LanguageContext';
import { listLogScanIssues, type LogScanIssue } from '../services/api';

interface LogScanIssuesPageProps {
  onBack: () => void;
}

function LogScanIssuesPage({ onBack }: LogScanIssuesPageProps) {
  const { t } = useLanguage();
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
    <div className="section">
      <BackLink onClick={onBack} label={t.nav.logs} />
      {error && (
        <p className="load-error" role="alert">
          <TriangleAlert /> {error}
        </p>
      )}
      <div className="panel">
        <LogScanIssuesList issues={issues} />
      </div>
    </div>
  );
}

export default LogScanIssuesPage;
