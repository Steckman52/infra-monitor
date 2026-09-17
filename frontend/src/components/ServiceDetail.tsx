import { Bug, FileText, GitCompare, Network } from 'lucide-react';
import { useLanguage } from '../i18n/LanguageContext';
import type { ServiceDetail as ServiceDetailData } from '../services/api';

interface ServiceDetailProps {
  service: ServiceDetailData;
  onSelectAdr: (id: number) => void;
  onSelectErrorGroup: (id: number) => void;
}

function ServiceDetail({ service, onSelectAdr, onSelectErrorGroup }: ServiceDetailProps) {
  const { t } = useLanguage();

  return (
    <>
      <div className="section">
        <div className="section-head">
          <span className="section-title">{service.name}</span>
        </div>
        <div className="panel panel-body">
          <dl className="detail-list">
            <dt>{t.serviceDetail.ecosystem}</dt>
            <dd>
              <span className="tag">{service.ecosystem}</span>
            </dd>
            <dt>{t.serviceDetail.repositoryPath}</dt>
            <dd className="cell-mono">{service.repository_path}</dd>
            <dt>{t.serviceDetail.manifestPath}</dt>
            <dd className="cell-mono">{service.manifest_path}</dd>
            <dt>{t.serviceDetail.status}</dt>
            <dd>
              <span className={`status-inline ${service.is_complete ? 'good' : 'warn'}`}>
                {service.is_complete ? t.registry.complete : t.registry.incomplete}
              </span>
            </dd>
          </dl>
        </div>
      </div>

      <div className="section">
        <div className="section-head">
          <span className="section-title">{t.serviceDetail.dependencies}</span>
        </div>
        <div className="panel">
          {service.dependencies.length === 0 ? (
            <p className="empty-state">{t.serviceDetail.noDependencies}</p>
          ) : (
            <table className="data-table">
              <thead>
                <tr>
                  <th>{t.common.name}</th>
                  <th>{t.serviceDetail.declaredVersion}</th>
                </tr>
              </thead>
              <tbody>
                {service.dependencies.map((dependency) => (
                  <tr key={dependency.name}>
                    <td className="cell-mono">{dependency.name}</td>
                    <td>{dependency.declared_version ?? '—'}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          )}
        </div>
      </div>

      <div className="section">
        <div className="section-head">
          <span className="section-title">{t.serviceDetail.compatibilityRisks}</span>
        </div>
        <div className="panel">
          {service.compatibility_risks.length === 0 ? (
            <p className="empty-state">{t.serviceDetail.noCompatibilityRisks}</p>
          ) : (
            service.compatibility_risks.map((risk) => (
              <div key={`${risk.ecosystem}:${risk.name}`} className="activity-row" style={{ cursor: 'default' }}>
                <div className="activity-icon warn">
                  <GitCompare />
                </div>
                <div>
                  <div className="activity-title">
                    <b>{risk.name}</b> ({risk.declared_version ?? '—'})
                  </div>
                  <div className="activity-meta">
                    {t.serviceDetail.conflictsWith}:{' '}
                    {risk.conflicting_with.map((c) => `${c.service_name} (${c.declared_version ?? '—'})`).join(', ')}
                  </div>
                </div>
              </div>
            ))
          )}
        </div>
      </div>

      <div className="section">
        <div className="section-head">
          <span className="section-title">{t.serviceDetail.connections}</span>
        </div>
        <div className="panel">
          {service.connections.length === 0 ? (
            <p className="empty-state">{t.serviceDetail.noConnections}</p>
          ) : (
            service.connections.map((edge, index) => (
              <div key={index} className="activity-row" style={{ cursor: 'default' }}>
                <div className="activity-icon">
                  <Network />
                </div>
                <div className="activity-title">
                  <b>{edge.node.name}</b>
                  {edge.node.type === 'external' &&
                    ` (${t.serviceDetail.external}${edge.node.repository_path ? ` — ${edge.node.repository_path}` : ''})`}{' '}
                  — {edge.relationship_basis.replace('_', ' ')}
                </div>
              </div>
            ))
          )}
        </div>
      </div>

      <div className="section">
        <div className="section-head">
          <span className="section-title">{t.serviceDetail.relatedAdrs}</span>
        </div>
        <div className="panel">
          {service.related_adrs.length === 0 ? (
            <p className="empty-state">{t.serviceDetail.noRelatedAdrs}</p>
          ) : (
            service.related_adrs.map((adr) => (
              <button
                key={adr.adr_id}
                type="button"
                className="activity-row"
                onClick={() => onSelectAdr(adr.adr_id)}
              >
                <div className="activity-icon">
                  <FileText />
                </div>
                <div className="activity-title">{adr.title}</div>
              </button>
            ))
          )}
        </div>
      </div>

      <div className="section">
        <div className="section-head">
          <span className="section-title">{t.serviceDetail.recentErrorGroups}</span>
        </div>
        <div className="panel">
          {service.recent_error_groups.length === 0 ? (
            <p className="empty-state">{t.serviceDetail.noErrorGroups}</p>
          ) : (
            service.recent_error_groups.map((group) => (
              <button
                key={group.id}
                type="button"
                className="activity-row"
                onClick={() => onSelectErrorGroup(group.id)}
              >
                <div className="activity-icon crit">
                  <Bug />
                </div>
                <div>
                  <div className="activity-title">
                    <b>{group.severity_marker}</b> {group.normalized_template}
                  </div>
                  <div className="activity-meta">{t.serviceDetail.occurrence(group.occurrence_count)}</div>
                </div>
              </button>
            ))
          )}
        </div>
      </div>
    </>
  );
}

export default ServiceDetail;
