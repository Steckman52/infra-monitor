import type { ScanIssue } from '../services/api';

interface ScanIssuesListProps {
  issues: ScanIssue[];
}

const ISSUE_TYPE_LABELS: Record<ScanIssue['issue_type'], string> = {
  unparsable: 'Unparsable manifest',
  incomplete_data: 'Incomplete data',
  unreachable_path: 'Unreachable root path',
};

function ScanIssuesList({ issues }: ScanIssuesListProps) {
  if (issues.length === 0) {
    return <p>No scan issues. Every scanned manifest was parsed successfully.</p>;
  }

  return (
    <table className="scan-issues-table">
      <thead>
        <tr>
          <th>Type</th>
          <th>Manifest / Path</th>
          <th>Reason</th>
        </tr>
      </thead>
      <tbody>
        {issues.map((issue) => (
          <tr key={issue.id}>
            <td>{ISSUE_TYPE_LABELS[issue.issue_type]}</td>
            <td>{issue.manifest_path}</td>
            <td>{issue.reason}</td>
          </tr>
        ))}
      </tbody>
    </table>
  );
}

export default ScanIssuesList;
