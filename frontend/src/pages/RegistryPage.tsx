import { FolderOpen, RefreshCw, TriangleAlert } from 'lucide-react';
import { useCallback, useEffect, useMemo, useState } from 'react';
import { useLanguage } from '../i18n/LanguageContext';
import {
  getDashboard,
  listServices,
  pickDirectory,
  triggerScan,
  type ScanResponse,
  type ServiceSummary,
} from '../services/api';
import { usePaged } from '../utils/paging';

interface RegistryPageProps {
  onSelectService: (id: number) => void;
  onViewScanIssues: () => void;
}

function RegistryPage({ onSelectService, onViewScanIssues }: RegistryPageProps) {
  const { t } = useLanguage();
  const [services, setServices] = useState<ServiceSummary[]>([]);
  const [rootsInput, setRootsInput] = useState('');
  const [filterQuery, setFilterQuery] = useState('');
  const [isScanning, setIsScanning] = useState(false);
  const [isBrowsing, setIsBrowsing] = useState(false);
  // Without this the table renders "no services registered yet" during the
  // very first fetch, actively telling the user their registry is empty
  // while it is still being read.
  const [isLoading, setIsLoading] = useState(true);
  const [lastScanSummary, setLastScanSummary] = useState<ScanResponse | null>(null);
  const [error, setError] = useState<string | null>(null);

  const refreshServices = useCallback(async () => {
    try {
      const data = await listServices();
      setServices(data);
      setError(null);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to load services.');
    } finally {
      setIsLoading(false);
    }
  }, []);

  useEffect(() => {
    refreshServices();
  }, [refreshServices]);

  // The roots used to live only in this component's state, so a refresh
  // lost them and the user had to retype every path from memory.
  useEffect(() => {
    getDashboard()
      .then(({ last_registry_roots }) => {
        if (last_registry_roots.length > 0) {
          setRootsInput((current) => current || last_registry_roots.join('\n'));
        }
      })
      .catch(() => {
        // Prefilling is a convenience; failing to do it must not surface
        // an error over a page that otherwise loaded fine.
      });
  }, []);

  const handleScan = async () => {
    const roots = rootsInput
      .split('\n')
      .map((line) => line.trim())
      .filter(Boolean);
    if (roots.length === 0) return;

    setIsScanning(true);
    setError(null);
    try {
      const result = await triggerScan(roots);
      setLastScanSummary(result);
      await refreshServices();
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Scan failed.');
    } finally {
      setIsScanning(false);
    }
  };

  const handleBrowse = async () => {
    setIsBrowsing(true);
    try {
      const { path } = await pickDirectory();
      if (path) {
        setRootsInput((current) => (current.trim() ? `${current.replace(/\n+$/, '')}\n${path}` : path));
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to open folder picker.');
    } finally {
      setIsBrowsing(false);
    }
  };

  const normalizedQuery = filterQuery.trim().toLowerCase();
  // Memoized, not recomputed per render: usePaged resets to the first page
  // whenever its list changes identity, so a fresh array on every render
  // would reset it on every click of "show more" while a filter is active.
  const filteredServices = useMemo(
    () =>
      normalizedQuery
        ? services.filter(
            (s) =>
              s.name.toLowerCase().includes(normalizedQuery) || s.ecosystem.toLowerCase().includes(normalizedQuery),
          )
        : services,
    [services, normalizedQuery],
  );
  const page = usePaged(filteredServices);

  return (
    <>
      {error && (
        <p className="load-error" role="alert">
          <TriangleAlert /> {error}
        </p>
      )}

      <div className="section">
        <div className="panel">
          <div className="panel-body" style={{ display: 'flex', gap: 10, alignItems: 'flex-start', flexWrap: 'wrap' }}>
            <textarea
              className="text-input"
              style={{ flex: 1, minWidth: 260 }}
              rows={2}
              placeholder={t.registry.scanPlaceholder}
              value={rootsInput}
              onChange={(e) => setRootsInput(e.target.value)}
            />
            <button type="button" className="btn-secondary" onClick={handleBrowse} disabled={isBrowsing}>
              <FolderOpen />
              {t.common.browse}
            </button>
            <button type="button" className="btn-primary" onClick={handleScan} disabled={isScanning}>
              <RefreshCw className={isScanning ? 'spinning' : undefined} />
              {isScanning ? t.common.scanning : t.common.scan}
            </button>
          </div>
          {lastScanSummary && (
            <div className="panel-body" style={{ paddingTop: 0 }}>
              <p className="card-detail" style={{ margin: 0 }}>
                {t.registry.scanSummary(lastScanSummary.services_found, lastScanSummary.issues_found, lastScanSummary.adrs_found)}
                {lastScanSummary.unreachable_roots.length > 0 && (
                  <>
                    {' '}
                    {t.registry.unreachableRoots} {lastScanSummary.unreachable_roots.join(', ')}
                  </>
                )}
              </p>
            </div>
          )}
        </div>
      </div>

      <div className="section">
        <div className="section-head">
          <button type="button" className="link-button" onClick={onViewScanIssues}>
            {t.registry.viewScanIssues}
          </button>
        </div>

        <input
          type="text"
          className="text-input"
          style={{ marginBottom: 12, width: '100%', maxWidth: 320 }}
          placeholder={t.registry.filterPlaceholder}
          value={filterQuery}
          onChange={(e) => setFilterQuery(e.target.value)}
        />

        <div className="panel">
          {isLoading ? (
            <p className="loading-state">{t.common.loading}</p>
          ) : filteredServices.length === 0 ? (
            <p className="empty-state">{t.registry.empty}</p>
          ) : (
            <table className="data-table">
              <thead>
                <tr>
                  <th>{t.common.name}</th>
                  <th>{t.registry.ecosystem}</th>
                  <th>{t.common.status}</th>
                </tr>
              </thead>
              <tbody>
                {page.visible.map((service) => (
                  <tr key={service.id} className="clickable" onClick={() => onSelectService(service.id)}>
                    <td className="cell-name">{service.name}</td>
                    <td>
                      <span className="tag">{service.ecosystem}</span>
                    </td>
                    <td>
                      <span className={`status-inline ${service.is_complete ? 'good' : 'warn'}`}>
                        {service.is_complete ? t.registry.complete : t.registry.incomplete}
                      </span>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          )}
          {!isLoading && page.hasMore && (
            <div className="panel-body">
              <button type="button" className="btn-secondary" onClick={page.showMore}>
                {t.common.showMore(page.shown, page.total)}
              </button>
            </div>
          )}
        </div>
      </div>
    </>
  );
}

export default RegistryPage;
