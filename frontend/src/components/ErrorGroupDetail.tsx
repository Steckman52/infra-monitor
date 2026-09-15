import { useLanguage } from '../i18n/LanguageContext';
import type { ErrorGroupDetail as ErrorGroupDetailData } from '../services/api';

interface ErrorGroupDetailProps {
  group: ErrorGroupDetailData;
}

function ErrorGroupDetail({ group }: ErrorGroupDetailProps) {
  const { t } = useLanguage();

  return (
    <>
      <div className="section">
        <div className="section-head">
          <span className="section-title">{group.severity_marker}</span>
        </div>
        <div className="panel panel-body">
          <dl className="detail-list">
            <dt>{t.errorGroupDetail.service}</dt>
            <dd>{group.service_name ?? t.errorGroupDetail.unattributed(group.unattributed_source_path ?? '')}</dd>
            <dt>{t.errorGroupDetail.template}</dt>
            <dd>{group.normalized_template}</dd>
            <dt>{t.errorGroupDetail.occurrences}</dt>
            <dd>{group.occurrence_count}</dd>
            <dt>{t.errorGroupDetail.firstSeen}</dt>
            <dd className="cell-mono">{group.first_seen ?? t.errorGroupDetail.unknown}</dd>
            <dt>{t.errorGroupDetail.lastSeen}</dt>
            <dd className="cell-mono">{group.last_seen ?? t.errorGroupDetail.unknown}</dd>
          </dl>
        </div>
      </div>

      <div className="section">
        <div className="section-head">
          <span className="section-title">{t.errorGroupDetail.example}</span>
        </div>
        <div className="panel panel-body">
          <pre className="cell-mono" style={{ margin: 0, whiteSpace: 'pre-wrap', overflowX: 'auto' }}>
            {group.example_text}
          </pre>
        </div>
      </div>

      <div className="section">
        <div className="section-head">
          <span className="section-title">{t.errorGroupDetail.occurrencesSample}</span>
        </div>
        <div className="panel">
          {group.occurrences.map((occurrence, index) => (
            <div key={index} className="activity-row" style={{ cursor: 'default' }}>
              <div style={{ width: '100%' }}>
                <div className="activity-meta">
                  {occurrence.source_log_path}:{occurrence.line_number}
                  {occurrence.occurred_at && ` — ${occurrence.occurred_at}`}
                </div>
                <pre className="cell-mono" style={{ margin: '4px 0 0', whiteSpace: 'pre-wrap', overflowX: 'auto' }}>
                  {occurrence.raw_text}
                </pre>
              </div>
            </div>
          ))}
        </div>
      </div>
    </>
  );
}

export default ErrorGroupDetail;
