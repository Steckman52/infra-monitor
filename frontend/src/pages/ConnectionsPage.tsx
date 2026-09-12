import { useEffect, useState } from 'react';
import ConnectionGraphView from '../components/ConnectionGraphView';
import { listConnections, type NodeConnections } from '../services/api';

interface ConnectionsPageProps {
  onBack: () => void;
}

function ConnectionsPage({ onBack }: ConnectionsPageProps) {
  const [nodes, setNodes] = useState<NodeConnections[]>([]);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    let cancelled = false;
    listConnections()
      .then((data) => {
        if (!cancelled) setNodes(data);
      })
      .catch((err) => {
        if (!cancelled) {
          setError(err instanceof Error ? err.message : 'Failed to load connections.');
        }
      });
    return () => {
      cancelled = true;
    };
  }, []);

  return (
    <div className="connections-page">
      <button type="button" onClick={onBack}>
        ← Back to registry
      </button>
      <h1>Service Connections</h1>
      {error && (
        <p className="load-error" role="alert">
          {error}
        </p>
      )}
      <ConnectionGraphView nodes={nodes} />
    </div>
  );
}

export default ConnectionsPage;
