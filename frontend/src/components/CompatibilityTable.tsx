import type { CompatibilityGroup } from '../services/api';

interface CompatibilityTableProps {
  groups: CompatibilityGroup[];
}

const STATUS_LABELS: Record<CompatibilityGroup['status'], string> = {
  compatible: 'Compatible',
  compatibility_risk: 'Compatibility risk',
};

function CompatibilityTable({ groups }: CompatibilityTableProps) {
  if (groups.length === 0) {
    return (
      <p>
        No dependencies are shared by more than one service, so there is nothing
        to compare yet.
      </p>
    );
  }

  return (
    <table className="compatibility-table">
      <thead>
        <tr>
          <th>Dependency</th>
          <th>Ecosystem</th>
          <th>Status</th>
          <th>Services &amp; Versions</th>
        </tr>
      </thead>
      <tbody>
        {groups.map((group) => (
          <tr key={`${group.ecosystem}:${group.name}`}>
            <td>{group.name}</td>
            <td>{group.ecosystem}</td>
            <td>
              {STATUS_LABELS[group.status]}
              {group.has_not_comparable && ' (some versions not comparable)'}
            </td>
            <td>
              <ul>
                {group.entries.map((entry) => (
                  <li key={entry.service_id}>
                    {entry.service_name}: {entry.declared_version ?? '—'}
                    {entry.major_version === null && ' (not comparable)'}
                  </li>
                ))}
              </ul>
            </td>
          </tr>
        ))}
      </tbody>
    </table>
  );
}

export default CompatibilityTable;
