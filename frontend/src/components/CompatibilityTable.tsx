import { useLanguage } from '../i18n/LanguageContext';
import type { CompatibilityGroup } from '../services/api';

interface CompatibilityTableProps {
  groups: CompatibilityGroup[];
}

function CompatibilityTable({ groups }: CompatibilityTableProps) {
  const { t } = useLanguage();

  if (groups.length === 0) {
    return <p className="empty-state">{t.compatibility.empty}</p>;
  }

  return (
    <table className="data-table">
      <thead>
        <tr>
          <th>{t.compatibility.dependency}</th>
          <th>{t.compatibility.ecosystem}</th>
          <th>{t.common.status}</th>
          <th>{t.compatibility.services}</th>
        </tr>
      </thead>
      <tbody>
        {groups.map((group) => (
          <tr key={`${group.ecosystem}:${group.name}`}>
            <td className="cell-name">{group.name}</td>
            <td>
              <span className="tag">{group.ecosystem}</span>
            </td>
            <td>
              <span className={`status-inline ${group.status === 'compatible' ? 'good' : 'warn'}`}>
                {group.status === 'compatible' ? t.compatibility.compatible : t.compatibility.compatibilityRisk}
              </span>
              {group.has_not_comparable && (
                <span className="activity-meta"> ({t.compatibility.someNotComparable})</span>
              )}
            </td>
            <td>
              {group.entries.map((entry, index) => (
                <div key={entry.service_id} className="activity-meta" style={{ marginTop: index === 0 ? 0 : 4 }}>
                  <b>{entry.service_name}</b>: {entry.declared_version ?? '—'}
                  {entry.major_version === null && ` (${t.compatibility.notComparable})`}
                </div>
              ))}
            </td>
          </tr>
        ))}
      </tbody>
    </table>
  );
}

export default CompatibilityTable;
