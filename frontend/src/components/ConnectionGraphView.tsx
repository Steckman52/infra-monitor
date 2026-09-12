import type { NodeConnections } from '../services/api';

interface ConnectionGraphViewProps {
  nodes: NodeConnections[];
}

const BASIS_LABELS: Record<string, string> = {
  shared_network: 'shared network',
  depends_on: 'depends on',
  both: 'shared network + depends on',
};

function ConnectionGraphView({ nodes }: ConnectionGraphViewProps) {
  if (nodes.length === 0) {
    return (
      <p>
        No connections found yet. Scan repositories containing a
        docker-compose.yml to populate this view.
      </p>
    );
  }

  return (
    <ul className="connection-graph">
      {nodes.map((entry) => (
        <li key={`${entry.node.type}:${entry.node.id}`}>
          <strong>{entry.node.name}</strong>{' '}
          {entry.node.type === 'external' && '(external)'}
          <ul>
            {entry.connections.map((edge, index) => (
              <li key={index}>
                → {edge.node.name}
                {edge.node.type === 'external' && ' (external)'} —{' '}
                {BASIS_LABELS[edge.relationship_basis] ?? edge.relationship_basis}
              </li>
            ))}
          </ul>
        </li>
      ))}
    </ul>
  );
}

export default ConnectionGraphView;
