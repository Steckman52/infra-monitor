import { useEffect, useState } from 'react';
import CompatibilityTable from '../components/CompatibilityTable';
import { listCompatibility, type CompatibilityGroup } from '../services/api';

interface CompatibilityPageProps {
  onBack: () => void;
}

function CompatibilityPage({ onBack }: CompatibilityPageProps) {
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
    <div className="compatibility-page">
      <button type="button" onClick={onBack}>
        ← Back to registry
      </button>
      <h1>Dependency Compatibility</h1>
      {error && (
        <p className="load-error" role="alert">
          {error}
        </p>
      )}
      <CompatibilityTable groups={groups} />
    </div>
  );
}

export default CompatibilityPage;
