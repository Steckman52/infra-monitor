import { useLanguage } from '../i18n/LanguageContext';
import type { ScanIssue } from '../services/api';

interface ScanIssuesListProps {
  issues: ScanIssue[];
}

function ScanIssuesList({ issues }: ScanIssuesListProps) {
  const { t } = useLanguage();

  const typeLabels: Record<ScanIssue['issue_type'], string> = {
    unparsable: t.scanIssues.unparsable,
    incomplete_data: t.scanIssues.incompleteData,
    unreachable_path: t.scanIssues.unreachablePath,
    scan_truncated: t.scanIssues.scanTruncated,
  };

  if (issues.length === 0) {
    return <p className="empty-state">{t.scanIssues.empty}</p>;
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
            <td className="cell-mono">{issue.manifest_path}</td>
            <td>{issue.reason}</td>
          </tr>
        ))}
      </tbody>
    </table>
  );
}

export default ScanIssuesList;
