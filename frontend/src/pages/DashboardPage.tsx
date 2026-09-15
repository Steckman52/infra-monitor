import { Bug, CircleCheck, FileText, FileX, GitCompare, TriangleAlert } from 'lucide-react';
import { useEffect, useState } from 'react';
import { useLanguage } from '../i18n/LanguageContext';
import {
  getDashboard,
  listAdrIssues,
  listCompatibility,
  listErrorGroups,
  listScanIssues,
  type AdrIssue,
  type CompatibilityGroup,
  type DashboardSummary,
  type ErrorGroupSummary,
  type ScanIssue,
} from '../services/api';

interface DashboardPageProps {
  onViewRegistry: () => void;
  onViewScanIssues: () => void;
  onViewCompatibility: () => void;
  onViewLogs: () => void;
  onViewLogScanIssues: () => void;
  onViewAdrs: () => void;
  onViewAdrIssues: () => void;
  onSelectErrorGroup: (id: number) => void;
}

function formatTimestamp(value: string | null, never: string): string {
  if (!value) return never;
  // The backend always emits UTC timestamps, but SQLite/SQLAlchemy's plain
  // DateTime column strips the offset on round-trip, so the ISO string
  // arrives with no 'Z'/offset -- without this, JS parses a date-*time*
  // string (unlike a date-only one) as local time, not UTC.
  const hasOffset = /Z$|[+-]\d{2}:\d{2}$/.test(value);
  return new Date(hasOffset ? value : `${value}Z`).toLocaleString();
}

interface ActivityItem {
  key: string;
  icon: React.ReactNode;
  tone: 'warn' | 'crit';
  title: React.ReactNode;
  meta: string;
  onClick: () => void;
}

function DashboardPage({
  onViewRegistry,
  onViewScanIssues,
  onViewCompatibility,
  onViewLogs,
  onViewLogScanIssues,
  onViewAdrs,
  onViewAdrIssues,
  onSelectErrorGroup,
}: DashboardPageProps) {
  const { t } = useLanguage();
  const [summary, setSummary] = useState<DashboardSummary | null>(null);
  const [errorGroups, setErrorGroups] = useState<ErrorGroupSummary[]>([]);
  const [compatRisks, setCompatRisks] = useState<CompatibilityGroup[]>([]);
  const [scanIssues, setScanIssues] = useState<ScanIssue[]>([]);
  const [adrIssues, setAdrIssues] = useState<AdrIssue[]>([]);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    let cancelled = false;
    Promise.all([getDashboard(), listErrorGroups(), listCompatibility(), listScanIssues(), listAdrIssues()])
      .then(([dashboard, groups, compat, issues, adr]) => {
        if (cancelled) return;
        setSummary(dashboard);
        setErrorGroups(groups);
        setCompatRisks(compat.filter((g) => g.status === 'compatibility_risk'));
        setScanIssues(issues);
        setAdrIssues(adr);
      })
      .catch((err) => {
        if (!cancelled) setError(err instanceof Error ? err.message : 'Failed to load dashboard.');
      });
    return () => {
      cancelled = true;
    };
  }, []);

  if (error) {
    return (
      <p className="load-error" role="alert">
        <TriangleAlert /> {error}
      </p>
    );
  }

  if (!summary) {
    return <p className="loading-state">{t.common.loading}</p>;
  }

  const activity: ActivityItem[] = [];
  const topErrorGroup = errorGroups[0];
  if (topErrorGroup) {
    activity.push({
      key: 'error-group',
      icon: <Bug />,
      tone: 'crit',
      title: (
        <>
          {summary.error_groups_count} {t.dashboard.errorGroups.toLowerCase()}
        </>
      ),
      meta: `${t.errorGroupDetail.template}: ${topErrorGroup.normalized_template} (×${topErrorGroup.occurrence_count})`,
      onClick: () => onSelectErrorGroup(topErrorGroup.id),
    });
  }
  for (const risk of compatRisks.slice(0, 2)) {
    const [a, b] = risk.entries;
    activity.push({
      key: `compat-${risk.name}`,
      icon: <GitCompare />,
      tone: 'warn',
      title: <b>{risk.name}</b>,
      meta: a && b ? `${a.service_name} ${a.declared_version ?? '—'} ${t.serviceDetail.conflictsWith} ${b.service_name} ${b.declared_version ?? '—'}` : '',
      onClick: onViewCompatibility,
    });
  }
  const topScanIssue = scanIssues[0];
  if (topScanIssue) {
    activity.push({
      key: 'scan-issue',
      icon: <TriangleAlert />,
      tone: 'warn',
      title: <>{topScanIssue.repository_path}</>,
      meta: topScanIssue.reason,
      onClick: onViewScanIssues,
    });
  }
  const topAdrIssue = adrIssues[0];
  if (topAdrIssue) {
    activity.push({
      key: 'adr-issue',
      icon: <FileX />,
      tone: 'warn',
      title: <>{topAdrIssue.path.split(/[\\/]/).pop()}</>,
      meta: topAdrIssue.reason,
      onClick: onViewAdrIssues,
    });
  }

  const attentionCards = [
    {
      key: 'scanIssues',
      icon: <TriangleAlert />,
      label: t.dashboard.scanIssues,
      count: summary.scan_issues_count,
      onClick: onViewScanIssues,
    },
    {
      key: 'compat',
      icon: <GitCompare />,
      label: t.dashboard.compatibilityRisks,
      count: summary.compatibility_risks_count,
      onClick: onViewCompatibility,
    },
    {
      key: 'errorGroups',
      icon: <Bug />,
      label: t.dashboard.errorGroups,
      count: summary.error_groups_count,
      onClick: onViewLogs,
    },
    {
      key: 'logScanIssues',
      icon: <FileX />,
      label: t.dashboard.logScanIssues,
      count: summary.log_scan_issues_count,
      onClick: onViewLogScanIssues,
    },
    {
      key: 'adrIssues',
      icon: <FileX />,
      label: t.dashboard.adrIssues,
      count: summary.adr_issues_count,
      onClick: onViewAdrIssues,
    },
  ];

  return (
    <>
      <div className="scan-times">
        <span>
          {t.dashboard.scanRegistry}&nbsp;
          <b>{formatTimestamp(summary.last_registry_scan_at, t.dashboard.never)}</b>
        </span>
        <span>
          {t.dashboard.scanLogs}&nbsp;<b>{formatTimestamp(summary.last_log_scan_at, t.dashboard.never)}</b>
        </span>
      </div>

      <div className="section">
        <div className="section-head">
          <span className="section-title">{t.dashboard.attention}</span>
        </div>
        <div className="cards">
          {attentionCards.map((card) => (
            <button
              key={card.key}
              type="button"
              className={`card${card.count > 0 ? ' warn' : ''}`}
              onClick={card.onClick}
            >
              <div className="card-label">
                {card.icon}
                <span>{card.label}</span>
              </div>
              <div className="card-count">{card.count}</div>
              {card.count > 0 ? (
                <span className="badge warn">
                  <TriangleAlert />
                  <span>{t.dashboard.needsReview}</span>
                </span>
              ) : (
                <span className="badge good">
                  <CircleCheck />
                  <span>{t.dashboard.clear}</span>
                </span>
              )}
            </button>
          ))}
        </div>
      </div>

      <div className="section">
        <div className="overview-strip">
          <button type="button" className="overview-item" onClick={onViewRegistry}>
            <FileText />
            <div>
              <div className="overview-count">{summary.services_count}</div>
              <div className="overview-label">{t.dashboard.services}</div>
            </div>
          </button>
          <button type="button" className="overview-item" onClick={onViewAdrs}>
            <FileText />
            <div>
              <div className="overview-count">{summary.adrs_count}</div>
              <div className="overview-label">{t.dashboard.adrs}</div>
            </div>
          </button>
        </div>
      </div>

      <div className="section">
        <div className="panel">
          <div className="panel-head">
            <span className="panel-title">{t.dashboard.activity}</span>
          </div>
          {activity.length === 0 ? (
            <p className="empty-state">{t.dashboard.allClear}</p>
          ) : (
            activity.map((item) => (
              <button key={item.key} type="button" className="activity-row" onClick={item.onClick}>
                <div className={`activity-icon ${item.tone}`}>{item.icon}</div>
                <div>
                  <div className="activity-title">{item.title}</div>
                  {item.meta && <div className="activity-meta">{item.meta}</div>}
                </div>
              </button>
            ))
          )}
        </div>
      </div>
    </>
  );
}

export default DashboardPage;
