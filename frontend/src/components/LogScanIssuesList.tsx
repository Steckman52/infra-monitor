import type { LogScanIssue } from '../services/api';

interface LogScanIssuesListProps {
  issues: LogScanIssue[];
}

const ISSUE_TYPE_LABELS: Record<LogScanIssue['issue_type'], string> = {
  unattributed: 'Unattributed directory',
  unreadable: 'Unreadable file',
};

function LogScanIssuesList({ issues }: LogScanIssuesListProps) {
  if (issues.length === 0) {
    return <p>No log scan issues. Every scanned log file was attributed and read successfully.</p>;
  }

  return (
    <table className="log-scan-issues-table">
      <thead>
        <tr>
          <th>Type</th>
          <th>Path</th>
          <th>Reason</th>
        </tr>
      </thead>
      <tbody>
        {issues.map((issue) => (
          <tr key={issue.id}>
            <td>{ISSUE_TYPE_LABELS[issue.issue_type]}</td>
            <td>{issue.path}</td>
            <td>{issue.reason}</td>
          </tr>
        ))}
      </tbody>
    </table>
  );
}

export default LogScanIssuesList;
