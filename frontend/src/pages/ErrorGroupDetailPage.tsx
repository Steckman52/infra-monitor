import { TriangleAlert } from 'lucide-react';
import { useEffect, useState } from 'react';
import BackLink from '../components/BackLink';
import ErrorGroupDetail from '../components/ErrorGroupDetail';
import { useLanguage } from '../i18n/LanguageContext';
import { getErrorGroupDetail, type ErrorGroupDetail as ErrorGroupDetailData } from '../services/api';

interface ErrorGroupDetailPageProps {
  groupId: number;
  onBack: () => void;
}

function ErrorGroupDetailPage({ groupId, onBack }: ErrorGroupDetailPageProps) {
  const { t } = useLanguage();
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
    <>
      <BackLink onClick={onBack} label={t.nav.logs} />
      {error && (
        <p className="load-error" role="alert">
          <TriangleAlert /> {error}
        </p>
      )}
      {!error && !group && <p className="loading-state">{t.common.loading}</p>}
      {group && <ErrorGroupDetail group={group} />}
    </>
  );
}

export default ErrorGroupDetailPage;
