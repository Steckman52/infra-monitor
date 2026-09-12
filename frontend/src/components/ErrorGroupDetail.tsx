import type { ErrorGroupDetail as ErrorGroupDetailData } from '../services/api';

interface ErrorGroupDetailProps {
  group: ErrorGroupDetailData;
}

function ErrorGroupDetail({ group }: ErrorGroupDetailProps) {
  return (
    <div className="error-group-detail">
      <h2>{group.severity_marker}</h2>
      <dl>
        <dt>Service</dt>
        <dd>{group.service_name ?? `Unattributed (${group.unattributed_source_path})`}</dd>
        <dt>Template</dt>
        <dd>{group.normalized_template}</dd>
        <dt>Occurrences</dt>
        <dd>{group.occurrence_count}</dd>
        <dt>First seen</dt>
        <dd>{group.first_seen ?? 'unknown'}</dd>
        <dt>Last seen</dt>
        <dd>{group.last_seen ?? 'unknown'}</dd>
      </dl>

      <h3>Example</h3>
      <pre className="error-example-text">{group.example_text}</pre>

      <h3>Occurrences (sample)</h3>
      <ul className="error-occurrences">
        {group.occurrences.map((occurrence, index) => (
          <li key={index}>
            <div>
              {occurrence.source_log_path}:{occurrence.line_number}
              {occurrence.occurred_at && ` — ${occurrence.occurred_at}`}
            </div>
            <pre>{occurrence.raw_text}</pre>
          </li>
        ))}
      </ul>
    </div>
  );
}

export default ErrorGroupDetail;
