import { useLanguage } from '../i18n/LanguageContext';
import type { ErrorGroupSummary } from '../services/api';
import { usePaged } from '../utils/paging';

interface ErrorGroupsTableProps {
  groups: ErrorGroupSummary[];
  onSelectGroup: (id: number) => void;
  onSelectService: (id: number) => void;
}

function ErrorGroupsTable({ groups, onSelectGroup, onSelectService }: ErrorGroupsTableProps) {
  const { t } = useLanguage();
  const page = usePaged(groups);

  if (groups.length === 0) {
    return <p className="empty-state">{t.logs.empty}</p>;
  }

  return (
    <>
    <table className="data-table">
      <thead>
        <tr>
          <th>{t.logs.service}</th>
          <th>{t.logs.severity}</th>
          <th>{t.logs.template}</th>
          <th>{t.logs.occurrences}</th>
          <th>{t.logs.lastSeen}</th>
        </tr>
      </thead>
      <tbody>
        {page.visible.map((group) => (
          <tr key={group.id}>
            <td>
              {group.service_id !== null ? (
                <button type="button" className="link-button" onClick={() => onSelectService(group.service_id as number)}>
                  {group.service_name}
                </button>
              ) : (
                <span className="cell-mono">{t.logs.unattributed(group.unattributed_source_path ?? '')}</span>
              )}
            </td>
            <td>
              <span className="status-inline crit">{group.severity_marker}</span>
            </td>
            <td>
              <button type="button" className="link-button" onClick={() => onSelectGroup(group.id)}>
                {group.normalized_template}
              </button>
            </td>
            <td>{group.occurrence_count}</td>
            <td className="cell-mono">{group.last_seen ?? '—'}</td>
          </tr>
        ))}
      </tbody>
    </table>
    {page.hasMore && (
      <div className="panel-body">
        <button type="button" className="btn-secondary" onClick={page.showMore}>
          {t.common.showMore(page.shown, page.total)}
        </button>
      </div>
    )}
    </>
  );
}

export default ErrorGroupsTable;
