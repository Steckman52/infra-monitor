import type { ServiceDetail as ServiceDetailData } from '../services/api';

interface ServiceDetailProps {
  service: ServiceDetailData;
}

function ServiceDetail({ service }: ServiceDetailProps) {
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
    </div>
  );
}

export default ServiceDetail;
