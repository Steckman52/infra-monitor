import type { AdrIssue } from '../services/api';

interface AdrIssuesListProps {
  issues: AdrIssue[];
}

const ISSUE_TYPE_LABELS: Record<AdrIssue['type'], string> = {
  parse_failure: 'Parse failure',
  secret_warning: 'Possible secret',
};

function AdrIssuesList({ issues }: AdrIssuesListProps) {
  if (issues.length === 0) {
    return <p>No ADR issues. Every imported ADR parsed cleanly with no secret warnings.</p>;
  }

  return (
    <table className="adr-issues-table">
      <thead>
        <tr>
          <th>Type</th>
          <th>Path</th>
          <th>Reason</th>
        </tr>
      </thead>
      <tbody>
        {issues.map((issue, index) => (
          <tr key={index}>
            <td>{ISSUE_TYPE_LABELS[issue.type]}</td>
            <td>{issue.path}</td>
            <td>{issue.reason}</td>
          </tr>
        ))}
      </tbody>
    </table>
  );
}

export default AdrIssuesList;
