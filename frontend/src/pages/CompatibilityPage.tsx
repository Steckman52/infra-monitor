import { TriangleAlert } from 'lucide-react';
import { useEffect, useState } from 'react';
import CompatibilityTable from '../components/CompatibilityTable';
import { listCompatibility, type CompatibilityGroup } from '../services/api';

function CompatibilityPage() {
  const [groups, setGroups] = useState<CompatibilityGroup[]>([]);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    let cancelled = false;
    listCompatibility()
      .then((data) => {
        if (!cancelled) setGroups(data);
      })
      .catch((err) => {
        if (!cancelled) {
          setError(err instanceof Error ? err.message : 'Failed to load compatibility data.');
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
        <CompatibilityTable groups={groups} />
      </div>
    </div>
  );
}

export default CompatibilityPage;
