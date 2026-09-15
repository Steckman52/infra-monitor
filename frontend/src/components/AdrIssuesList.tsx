import { useLanguage } from '../i18n/LanguageContext';
import type { AdrIssue } from '../services/api';

interface AdrIssuesListProps {
  issues: AdrIssue[];
}

function AdrIssuesList({ issues }: AdrIssuesListProps) {
  const { t } = useLanguage();

  const typeLabels: Record<AdrIssue['type'], string> = {
    parse_failure: t.adrIssues.parseFailure,
    secret_warning: t.adrIssues.secretWarning,
  };

  if (issues.length === 0) {
    return <p className="empty-state">{t.adrIssues.empty}</p>;
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
        {issues.map((issue, index) => (
          <tr key={index}>
            <td>
              <span className="status-inline warn">{typeLabels[issue.type]}</span>
            </td>
            <td className="cell-mono">{issue.path}</td>
            <td>{issue.reason}</td>
          </tr>
        ))}
      </tbody>
    </table>
  );
}

export default AdrIssuesList;
