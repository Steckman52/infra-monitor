import { FolderOpen, RefreshCw, TriangleAlert } from 'lucide-react';
import { useCallback, useEffect, useState } from 'react';
import ErrorGroupsTable from '../components/ErrorGroupsTable';
import { useLanguage } from '../i18n/LanguageContext';
import {
  getDashboard,
  listErrorGroups,
  pickDirectory,
  triggerLogScan,
  type ErrorGroupSummary,
  type LogScanResponse,
} from '../services/api';

interface LogsPageProps {
  onSelectGroup: (id: number) => void;
  onSelectService: (id: number) => void;
  onViewLogScanIssues: () => void;
}

function LogsPage({ onSelectGroup, onSelectService, onViewLogScanIssues }: LogsPageProps) {
  const { t } = useLanguage();
  const [groups, setGroups] = useState<ErrorGroupSummary[]>([]);
  const [root, setRoot] = useState('');
  const [isScanning, setIsScanning] = useState(false);
  const [isBrowsing, setIsBrowsing] = useState(false);
  // Prevents the table claiming there are no errors while the first
  // fetch is still in flight.
  const [isLoading, setIsLoading] = useState(true);
  const [lastScanSummary, setLastScanSummary] = useState<LogScanResponse | null>(null);
  const [error, setError] = useState<string | null>(null);

  const refreshGroups = useCallback(async () => {
    try {
      const data = await listErrorGroups();
      setGroups(data);
      setError(null);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to load error groups.');
    } finally {
      setIsLoading(false);
    }
  }, []);

  useEffect(() => {
    refreshGroups();
  }, [refreshGroups]);

  useEffect(() => {
    getDashboard()
      .then(({ last_log_roots }) => {
        if (last_log_roots.length > 0) setRoot((current) => current || last_log_roots[0]);
      })
      .catch(() => {
        // Prefilling is a convenience, never a reason to show an error.
      });
  }, []);

  const handleScan = async () => {
    const trimmedRoot = root.trim();
    if (!trimmedRoot) return;

    setIsScanning(true);
    setError(null);
    try {
      const result = await triggerLogScan(trimmedRoot);
      setLastScanSummary(result);
      await refreshGroups();
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Log scan failed.');
    } finally {
      setIsScanning(false);
    }
  };

  const handleBrowse = async () => {
    setIsBrowsing(true);
    try {
      const { path } = await pickDirectory();
      if (path) {
        setRoot(path);
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to open folder picker.');
    } finally {
      setIsBrowsing(false);
    }
  };

  return (
    <>
      {error && (
        <p className="load-error" role="alert">
          <TriangleAlert /> {error}
        </p>
      )}

      <div className="section">
        <div className="panel panel-body" style={{ display: 'flex', gap: 10, alignItems: 'center', flexWrap: 'wrap' }}>
          <input
            type="text"
            className="text-input"
            style={{ flex: 1, minWidth: 260 }}
            placeholder={t.logs.scanPlaceholder}
            value={root}
            onChange={(e) => setRoot(e.target.value)}
          />
          <button type="button" className="btn-secondary" onClick={handleBrowse} disabled={isBrowsing}>
            <FolderOpen />
            {t.common.browse}
          </button>
          <button type="button" className="btn-primary" onClick={handleScan} disabled={isScanning}>
            <RefreshCw className={isScanning ? 'spinning' : undefined} />
            {isScanning ? t.common.scanning : t.logs.scanBtn}
          </button>
        </div>
        {lastScanSummary && (
          <p className="card-detail" style={{ marginTop: 10 }}>
            {lastScanSummary.root_unreachable
              ? t.logs.unreachableRoot
              : t.logs.scanSummary(lastScanSummary.error_groups_found, lastScanSummary.issues_found)}
          </p>
        )}
      </div>

      <div className="section">
        <div className="section-head">
          <button type="button" className="link-button" onClick={onViewLogScanIssues}>
            {t.logs.viewLogScanIssues}
          </button>
        </div>
        <div className="panel">
          {isLoading ? (
            <p className="loading-state">{t.common.loading}</p>
          ) : (
            <ErrorGroupsTable groups={groups} onSelectGroup={onSelectGroup} onSelectService={onSelectService} />
          )}
        </div>
      </div>
    </>
  );
}

export default LogsPage;
