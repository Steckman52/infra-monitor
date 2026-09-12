import { useEffect, useState } from 'react';
import ErrorGroupDetail from '../components/ErrorGroupDetail';
import { getErrorGroupDetail, type ErrorGroupDetail as ErrorGroupDetailData } from '../services/api';

interface ErrorGroupDetailPageProps {
  groupId: number;
  onBack: () => void;
}

function ErrorGroupDetailPage({ groupId, onBack }: ErrorGroupDetailPageProps) {
  const [group, setGroup] = useState<ErrorGroupDetailData | null>(null);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    let cancelled = false;
    getErrorGroupDetail(groupId)
      .then((data) => {
        if (!cancelled) setGroup(data);
      })
      .catch((err) => {
        if (!cancelled) {
          setError(err instanceof Error ? err.message : 'Failed to load error group.');
        }
      });
    return () => {
      cancelled = true;
    };
  }, [groupId]);

  return (
    <div className="error-group-detail-page">
      <button type="button" onClick={onBack}>
        ← Back to log errors
      </button>
      {error && (
        <p className="load-error" role="alert">
          {error}
        </p>
      )}
      {!error && !group && <p>Loading…</p>}
      {group && <ErrorGroupDetail group={group} />}
    </div>
  );
}

export default ErrorGroupDetailPage;
