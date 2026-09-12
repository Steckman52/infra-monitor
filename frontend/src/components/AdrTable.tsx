import type { AdrSummary } from '../services/api';

interface AdrTableProps {
  adrs: AdrSummary[];
}

function AdrTable({ adrs }: AdrTableProps) {
  if (adrs.length === 0) {
    return <p>No ADRs found. Scan a repository containing a docs/adr directory.</p>;
  }

  return (
    <table className="adr-table">
      <thead>
        <tr>
          <th>Title</th>
          <th>Status</th>
          <th>Date</th>
          <th>Source</th>
        </tr>
      </thead>
      <tbody>
        {adrs.map((adr) => (
          <tr key={adr.id}>
            <td>
              {adr.title}
              {adr.has_secret_warning && <span title="Possible secret detected"> ⚠️</span>}
            </td>
            <td>{adr.normalized_status}</td>
            <td>{adr.date ?? '—'}</td>
            <td>{adr.source_path}</td>
          </tr>
        ))}
      </tbody>
    </table>
  );
}

export default AdrTable;
