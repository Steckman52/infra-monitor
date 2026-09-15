import { useLanguage } from '../i18n/LanguageContext';

function LanguageToggle() {
  const { lang, setLang } = useLanguage();

  return (
    <div className="lang-toggle" role="tablist" aria-label="Language">
      <button type="button" aria-pressed={lang === 'en'} onClick={() => setLang('en')}>
        EN
      </button>
      <button type="button" aria-pressed={lang === 'ru'} onClick={() => setLang('ru')}>
        RU
      </button>
    </div>
  );
}

export default LanguageToggle;
