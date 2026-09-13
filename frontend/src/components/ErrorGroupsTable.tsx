import type { ErrorGroupSummary } from '../services/api';

interface ErrorGroupsTableProps {
  groups: ErrorGroupSummary[];
  onSelectGroup: (id: number) => void;
  onSelectService: (id: number) => void;
}

function ErrorGroupsTable({ groups, onSelectGroup, onSelectService }: ErrorGroupsTableProps) {
  if (groups.length === 0) {
    return <p>No error groups yet. Scan a log directory to populate this view.</p>;
  }

  return (
    <table className="error-groups-table">
      <thead>
        <tr>
          <th>Service</th>
          <th>Severity</th>
          <th>Template</th>
          <th>Occurrences</th>
          <th>Last Seen</th>
        </tr>
      </thead>
      <tbody>
        {groups.map((group) => (
          <tr key={group.id}>
            <td>
              {group.service_id !== null ? (
                <button
                  type="button"
                  className="service-link"
                  onClick={() => onSelectService(group.service_id as number)}
                >
                  {group.service_name}
                </button>
              ) : (
                `Unattributed (${group.unattributed_source_path})`
              )}
            </td>
            <td>{group.severity_marker}</td>
            <td>
              <button type="button" className="error-group-link" onClick={() => onSelectGroup(group.id)}>
                {group.normalized_template}
              </button>
            </td>
            <td>{group.occurrence_count}</td>
            <td>{group.last_seen ?? '—'}</td>
          </tr>
        ))}
      </tbody>
    </table>
  );
}

export default ErrorGroupsTable;
