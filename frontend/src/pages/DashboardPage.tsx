import { useEffect, useState } from 'react';
import { getDashboard, type DashboardSummary } from '../services/api';

interface DashboardPageProps {
  onViewRegistry: () => void;
  onViewScanIssues: () => void;
  onViewCompatibility: () => void;
  onViewLogs: () => void;
  onViewLogScanIssues: () => void;
  onViewAdrs: () => void;
  onViewAdrIssues: () => void;
}

function formatTimestamp(value: string | null): string {
  return value ? new Date(value).toLocaleString() : 'never';
}

function DashboardPage({
  onViewRegistry,
  onViewScanIssues,
  onViewCompatibility,
  onViewLogs,
  onViewLogScanIssues,
  onViewAdrs,
  onViewAdrIssues,
}: DashboardPageProps) {
  const [summary, setSummary] = useState<DashboardSummary | null>(null);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    let cancelled = false;
    getDashboard()
      .then((data) => {
        if (!cancelled) setSummary(data);
      })
      .catch((err) => {
        if (!cancelled) {
          setError(err instanceof Error ? err.message : 'Failed to load dashboard.');
        }
      });
    return () => {
      cancelled = true;
    };
  }, []);

  return (
    <div className="dashboard-page">
      <h1>Infrastructure Dashboard</h1>
      {error && (
        <p className="load-error" role="alert">
          {error}
        </p>
      )}
      {!error && !summary && <p>Loading…</p>}
      {summary && (
        <>
          <p className="scan-timestamps">
            Last registry scan: {formatTimestamp(summary.last_registry_scan_at)}
            {' · '}
            Last log scan: {formatTimestamp(summary.last_log_scan_at)}
          </p>
          <div className="dashboard-cards">
            <button type="button" className="dashboard-card" onClick={onViewRegistry}>
              <span className="dashboard-card-count">{summary.services_count}</span>
              <span className="dashboard-card-label">Services</span>
            </button>
            <button type="button" className="dashboard-card" onClick={onViewScanIssues}>
              <span className="dashboard-card-count">{summary.scan_issues_count}</span>
              <span className="dashboard-card-label">Scan Issues</span>
            </button>
            <button type="button" className="dashboard-card" onClick={onViewCompatibility}>
              <span className="dashboard-card-count">{summary.compatibility_risks_count}</span>
              <span className="dashboard-card-label">Compatibility Risks</span>
            </button>
            <button type="button" className="dashboard-card" onClick={onViewLogs}>
              <span className="dashboard-card-count">{summary.error_groups_count}</span>
              <span className="dashboard-card-label">Log Error Groups</span>
            </button>
            <button type="button" className="dashboard-card" onClick={onViewLogScanIssues}>
              <span className="dashboard-card-count">{summary.log_scan_issues_count}</span>
              <span className="dashboard-card-label">Log Scan Issues</span>
            </button>
            <button type="button" className="dashboard-card" onClick={onViewAdrs}>
              <span className="dashboard-card-count">{summary.adrs_count}</span>
              <span className="dashboard-card-label">ADRs</span>
            </button>
            <button type="button" className="dashboard-card" onClick={onViewAdrIssues}>
              <span className="dashboard-card-count">{summary.adr_issues_count}</span>
              <span className="dashboard-card-label">ADR Issues</span>
            </button>
          </div>
        </>
      )}
    </div>
  );
}

export default DashboardPage;
