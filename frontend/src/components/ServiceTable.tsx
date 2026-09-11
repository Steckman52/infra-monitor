import type { ServiceSummary } from '../services/api';

interface ServiceTableProps {
  services: ServiceSummary[];
  onSelectService: (id: number) => void;
}

function ServiceTable({ services, onSelectService }: ServiceTableProps) {
  if (services.length === 0) {
    return <p>No services registered yet. Run a scan to populate the registry.</p>;
  }

  return (
    <table className="service-table">
      <thead>
        <tr>
          <th>Name</th>
          <th>Ecosystem</th>
          <th>Repository Path</th>
          <th>Status</th>
        </tr>
      </thead>
      <tbody>
        {services.map((service) => (
          <tr key={service.id}>
            <td>
              <button type="button" className="service-link" onClick={() => onSelectService(service.id)}>
                {service.name}
              </button>
            </td>
            <td>{service.ecosystem}</td>
            <td>{service.repository_path}</td>
            <td>{service.is_complete ? 'Complete' : 'Incomplete data'}</td>
          </tr>
        ))}
      </tbody>
    </table>
  );
}

export default ServiceTable;
