import { useLanguage } from '../i18n/LanguageContext';
import type { LogScanIssue } from '../services/api';

interface LogScanIssuesListProps {
  issues: LogScanIssue[];
}

function LogScanIssuesList({ issues }: LogScanIssuesListProps) {
  const { t } = useLanguage();

  const typeLabels: Record<LogScanIssue['issue_type'], string> = {
    unattributed: t.logScanIssues.unattributed,
    unreadable: t.logScanIssues.unreadable,
  };

  if (issues.length === 0) {
    return <p className="empty-state">{t.logScanIssues.empty}</p>;
  }

  return (
    <table className="data-table">
      <thead>
        <tr>
          <th>{t.common.type}</th>
          <th>{t.common.path}</th>
          <th>{t.common.reason}</th>
        </tr>
      </thead>
      <tbody>
        {issues.map((issue) => (
          <tr key={issue.id}>
            <td>
              <span className="status-inline warn">{typeLabels[issue.issue_type]}</span>
            </td>
            <td className="cell-mono">{issue.path}</td>
            <td>{issue.reason}</td>
          </tr>
        ))}
      </tbody>
    </table>
  );
}

export default LogScanIssuesList;
