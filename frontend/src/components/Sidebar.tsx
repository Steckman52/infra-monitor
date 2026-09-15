import { Activity, Boxes, FileText, GitCompare, LayoutDashboard, Network, ScrollText } from 'lucide-react';
import { useLanguage } from '../i18n/LanguageContext';

export type NavKey = 'dashboard' | 'registry' | 'compatibility' | 'connections' | 'logs' | 'adrs';

interface SidebarProps {
  active: NavKey;
  onNavigate: (target: NavKey) => void;
}

function Sidebar({ active, onNavigate }: SidebarProps) {
  const { t } = useLanguage();

  const items: { key: NavKey; label: string; icon: React.ReactNode }[] = [
    { key: 'dashboard', label: t.nav.dashboard, icon: <LayoutDashboard /> },
    { key: 'registry', label: t.nav.services, icon: <Boxes /> },
    { key: 'compatibility', label: t.nav.compatibility, icon: <GitCompare /> },
    { key: 'connections', label: t.nav.connections, icon: <Network /> },
    { key: 'logs', label: t.nav.logs, icon: <ScrollText /> },
    { key: 'adrs', label: t.nav.adrs, icon: <FileText /> },
  ];

  return (
    <nav className="sidebar" aria-label="Sections">
      <div className="sidebar-brand">
        <div className="brand-mark">
          <Activity size={14} />
        </div>
        <span className="sidebar-brand-name">infra-monitor</span>
      </div>

      {items.map((item) => (
        <button
          key={item.key}
          type="button"
          className="nav-item"
          aria-current={active === item.key ? 'page' : undefined}
          onClick={() => onNavigate(item.key)}
        >
          {item.icon}
          <span>{item.label}</span>
        </button>
      ))}

      <div className="sidebar-footer">
        <span className="status-dot" aria-hidden="true"></span>
        <span>{t.nav.localInstance}</span>
      </div>
    </nav>
  );
}

export default Sidebar;
