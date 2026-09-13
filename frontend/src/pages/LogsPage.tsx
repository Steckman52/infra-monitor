import { useCallback, useEffect, useState } from 'react';
import ErrorGroupsTable from '../components/ErrorGroupsTable';
import LogScanButton from '../components/LogScanButton';
import { listErrorGroups, type ErrorGroupSummary, type LogScanResponse } from '../services/api';

interface LogsPageProps {
  onBack: () => void;
  onSelectGroup: (id: number) => void;
  onSelectService: (id: number) => void;
  onViewLogScanIssues: () => void;
}

function LogsPage({ onBack, onSelectGroup, onSelectService, onViewLogScanIssues }: LogsPageProps) {
  const [groups, setGroups] = useState<ErrorGroupSummary[]>([]);
  const [lastScanSummary, setLastScanSummary] = useState<LogScanResponse | null>(null);
  const [loadError, setLoadError] = useState<string | null>(null);

  const refreshGroups = useCallback(async () => {
    try {
      const data = await listErrorGroups();
      setGroups(data);
      setLoadError(null);
    } catch (err) {
      setLoadError(err instanceof Error ? err.message : 'Failed to load error groups.');
    }
  }, []);

  useEffect(() => {
    refreshGroups();
  }, [refreshGroups]);

  const handleScanComplete = async (result: LogScanResponse) => {
    setLastScanSummary(result);
    await refreshGroups();
  };

  return (
    <div className="logs-page">
      <button type="button" onClick={onBack}>
        ← Back to registry
      </button>
      <h1>Log Errors</h1>
      <button type="button" onClick={onViewLogScanIssues}>
        View log scan issues
      </button>
      <LogScanButton onScanComplete={handleScanComplete} />
      {lastScanSummary && lastScanSummary.root_unreachable && (
        <p className="scan-error" role="alert">
          Log root path does not exist or is not a directory.
        </p>
      )}
      {lastScanSummary && !lastScanSummary.root_unreachable && (
        <p className="scan-summary">
          Found {lastScanSummary.error_groups_found} error group(s),{' '}
          {lastScanSummary.issues_found} issue(s).
        </p>
      )}
      {loadError && (
        <p className="load-error" role="alert">
          {loadError}
        </p>
      )}
      <ErrorGroupsTable groups={groups} onSelectGroup={onSelectGroup} onSelectService={onSelectService} />
    </div>
  );
}

export default LogsPage;
