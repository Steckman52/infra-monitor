import { TriangleAlert } from 'lucide-react';
import { useLanguage } from '../i18n/LanguageContext';
import type { AdrDetail as AdrDetailData, RelatedAdr } from '../services/api';

interface AdrDetailProps {
  adr: AdrDetailData;
}

function RelatedAdrList({ label, items }: { label: string; items: RelatedAdr[] }) {
  if (items.length === 0) return null;
  return (
    <>
      <dt>{label}</dt>
      <dd>{items.map((item) => item.title).join(', ')}</dd>
    </>
  );
}

function AdrDetail({ adr }: AdrDetailProps) {
  const { t } = useLanguage();

  return (
    <>
      <div className="section">
        <div className="section-head">
          <span className="section-title">{adr.title}</span>
          {adr.has_secret_warning && (
            <span title={t.adrDetail.secretWarning} style={{ display: 'inline-flex' }}>
              <TriangleAlert size={14} color="var(--warn)" />
            </span>
          )}
        </div>
        <div className="panel panel-body">
          <dl className="detail-list">
            <dt>{t.adrDetail.status}</dt>
            <dd>{adr.normalized_status}</dd>
            <dt>{t.adrDetail.date}</dt>
            <dd className="cell-mono">{adr.date ?? '—'}</dd>
            <dt>{t.adrDetail.source}</dt>
            <dd className="cell-mono">{adr.source_path}</dd>
            <RelatedAdrList label={t.adrDetail.supersedes} items={adr.supersedes} />
            <RelatedAdrList label={t.adrDetail.supersededBy} items={adr.superseded_by} />
            <RelatedAdrList label={t.adrDetail.amends} items={adr.amends} />
            <RelatedAdrList label={t.adrDetail.amendedBy} items={adr.amended_by} />
            {adr.related_services.length > 0 && (
              <>
                <dt>{t.adrDetail.relatedServices}</dt>
                <dd>{adr.related_services.map((s) => s.service_name).join(', ')}</dd>
              </>
            )}
          </dl>
        </div>
      </div>

      <div className="section">
        <div className="section-head">
          <span className="section-title">{t.adrDetail.content}</span>
        </div>
        <div className="panel panel-body">
          <pre className="cell-mono" style={{ margin: 0, whiteSpace: 'pre-wrap', overflowX: 'auto' }}>
            {adr.content}
          </pre>
        </div>
      </div>
    </>
  );
}

export default AdrDetail;
