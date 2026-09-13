import type { AdrDetail as AdrDetailData, RelatedAdr } from '../services/api';

interface AdrDetailProps {
  adr: AdrDetailData;
}

function RelatedAdrList({ label, items }: { label: string; items: RelatedAdr[] }) {
  if (items.length === 0) return null;
  return (
    <>
      <dt>{label}</dt>
      <dd>
        <ul>
          {items.map((item) => (
            <li key={item.adr_id}>{item.title}</li>
          ))}
        </ul>
      </dd>
    </>
  );
}

function AdrDetail({ adr }: AdrDetailProps) {
  return (
    <div className="adr-detail">
      <h2>
        {adr.title}
        {adr.has_secret_warning && <span title="Possible secret detected"> ⚠️</span>}
      </h2>
      <dl>
        <dt>Status</dt>
        <dd>{adr.normalized_status}</dd>
        <dt>Date</dt>
        <dd>{adr.date ?? '—'}</dd>
        <dt>Source</dt>
        <dd>{adr.source_path}</dd>
        <RelatedAdrList label="Supersedes" items={adr.supersedes} />
        <RelatedAdrList label="Superseded by" items={adr.superseded_by} />
        <RelatedAdrList label="Amends" items={adr.amends} />
        <RelatedAdrList label="Amended by" items={adr.amended_by} />
        {adr.related_services.length > 0 && (
          <>
            <dt>Related services</dt>
            <dd>
              <ul>
                {adr.related_services.map((service) => (
                  <li key={service.service_id}>{service.service_name}</li>
                ))}
              </ul>
            </dd>
          </>
        )}
      </dl>

      <h3>Content</h3>
      <pre className="adr-content">{adr.content}</pre>
    </div>
  );
}

export default AdrDetail;
