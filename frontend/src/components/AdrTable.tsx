import { TriangleAlert } from 'lucide-react';
import { useLanguage } from '../i18n/LanguageContext';
import type { AdrSummary } from '../services/api';

interface AdrTableProps {
  adrs: AdrSummary[];
  onSelectAdr: (id: number) => void;
}

function AdrTable({ adrs, onSelectAdr }: AdrTableProps) {
  const { t } = useLanguage();

  if (adrs.length === 0) {
    return <p className="empty-state">{t.adrs.empty}</p>;
  }

  return (
    <table className="data-table">
      <thead>
        <tr>
          <th>{t.common.name}</th>
          <th>{t.common.status}</th>
          <th>{t.adrs.date}</th>
          <th>{t.adrs.source}</th>
        </tr>
      </thead>
      <tbody>
        {adrs.map((adr) => (
          <tr key={adr.id} className="clickable" onClick={() => onSelectAdr(adr.id)}>
            <td className="cell-name">
              {adr.title}
              {adr.has_secret_warning && (
                <span title={t.adrs.secretWarning} style={{ marginLeft: 6, verticalAlign: 'middle', display: 'inline-flex' }}>
                  <TriangleAlert size={13} color="var(--warn)" />
                </span>
              )}
            </td>
            <td>{adr.normalized_status}</td>
            <td className="cell-mono">{adr.date ?? '—'}</td>
            <td className="cell-mono">{adr.source_path}</td>
          </tr>
        ))}
      </tbody>
    </table>
  );
}

export default AdrTable;
