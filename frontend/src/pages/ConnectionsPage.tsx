import { TriangleAlert } from 'lucide-react';
import { useEffect, useState } from 'react';
import ConnectionGraphView from '../components/ConnectionGraphView';
import { listConnections, type NodeConnections } from '../services/api';

function ConnectionsPage() {
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
    <div className="section">
      {error && (
        <p className="load-error" role="alert">
          <TriangleAlert /> {error}
        </p>
      )}
      <div className="panel">
        <ConnectionGraphView nodes={nodes} />
      </div>
    </div>
  );
}

export default ConnectionsPage;
