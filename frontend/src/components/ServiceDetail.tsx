import type { ServiceDetail as ServiceDetailData } from '../services/api';

interface ServiceDetailProps {
  service: ServiceDetailData;
  onSelectAdr: (id: number) => void;
  onSelectErrorGroup: (id: number) => void;
}

function ServiceDetail({ service, onSelectAdr, onSelectErrorGroup }: ServiceDetailProps) {
  return (
    <div className="service-detail">
      <h2>{service.name}</h2>
      <dl>
        <dt>Ecosystem</dt>
        <dd>{service.ecosystem}</dd>
        <dt>Repository path</dt>
        <dd>{service.repository_path}</dd>
        <dt>Manifest path</dt>
        <dd>{service.manifest_path}</dd>
        <dt>Status</dt>
        <dd>{service.is_complete ? 'Complete' : 'Incomplete data'}</dd>
      </dl>

      <h3>Dependencies</h3>
      {service.dependencies.length === 0 ? (
        <p>This service declares no dependencies.</p>
      ) : (
        <table className="dependency-table">
          <thead>
            <tr>
              <th>Name</th>
              <th>Declared Version</th>
            </tr>
          </thead>
          <tbody>
            {service.dependencies.map((dependency) => (
              <tr key={dependency.name}>
                <td>{dependency.name}</td>
                <td>{dependency.declared_version ?? '—'}</td>
              </tr>
            ))}
          </tbody>
        </table>
      )}

      <h3>Compatibility Risks</h3>
      {service.compatibility_risks.length === 0 ? (
        <p>No compatibility risks with other services.</p>
      ) : (
        <ul className="compatibility-risks">
          {service.compatibility_risks.map((risk) => (
            <li key={`${risk.ecosystem}:${risk.name}`}>
              <strong>{risk.name}</strong> ({risk.declared_version}) conflicts with:{' '}
              {risk.conflicting_with
                .map((c) => `${c.service_name} (${c.declared_version ?? '—'})`)
                .join(', ')}
            </li>
          ))}
        </ul>
      )}

      <h3>Connections</h3>
      {service.connections.length === 0 ? (
        <p>Not connected to any other service or external node.</p>
      ) : (
        <ul className="connections">
          {service.connections.map((edge, index) => (
            <li key={index}>
              {edge.node.name}
              {edge.node.type === 'external' && ' (external)'} —{' '}
              {edge.relationship_basis.replace('_', ' ')}
            </li>
          ))}
        </ul>
      )}

      <h3>Related ADRs</h3>
      {service.related_adrs.length === 0 ? (
        <p>No ADRs reference this service's repository.</p>
      ) : (
        <ul className="related-adrs">
          {service.related_adrs.map((adr) => (
            <li key={adr.adr_id}>
              <button type="button" className="adr-link" onClick={() => onSelectAdr(adr.adr_id)}>
                {adr.title}
              </button>
            </li>
          ))}
        </ul>
      )}

      <h3>Recent Error Groups</h3>
      {service.recent_error_groups.length === 0 ? (
        <p>No log errors attributed to this service.</p>
      ) : (
        <ul className="recent-error-groups">
          {service.recent_error_groups.map((group) => (
            <li key={group.id}>
              <button
                type="button"
                className="error-group-link"
                onClick={() => onSelectErrorGroup(group.id)}
              >
                {group.severity_marker}: {group.normalized_template}
              </button>{' '}
              ({group.occurrence_count} occurrence{group.occurrence_count === 1 ? '' : 's'})
            </li>
          ))}
        </ul>
      )}
    </div>
  );
}

export default ServiceDetail;
