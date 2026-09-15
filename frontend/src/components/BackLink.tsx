import { ArrowLeft } from 'lucide-react';
import { useLanguage } from '../i18n/LanguageContext';

interface BackLinkProps {
  onClick: () => void;
  label?: string;
}

function BackLink({ onClick, label }: BackLinkProps) {
  const { t } = useLanguage();

  return (
    <button type="button" className="link-button" style={{ display: 'inline-flex', alignItems: 'center', gap: 6, marginBottom: 16 }} onClick={onClick}>
      <ArrowLeft size={14} />
      {label ?? t.common.back}
    </button>
  );
}

export default BackLink;
