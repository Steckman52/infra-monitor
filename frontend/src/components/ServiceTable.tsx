import type { ServiceSummary } from '../services/api';

interface ServiceTableProps {
  services: ServiceSummary[];
}

function ServiceTable({ services }: ServiceTableProps) {
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
            <td>{service.name}</td>
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
