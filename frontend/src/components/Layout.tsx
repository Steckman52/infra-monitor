import type { ReactNode } from 'react';
import LanguageToggle from './LanguageToggle';
import Sidebar, { type NavKey } from './Sidebar';

interface LayoutProps {
  title: string;
  active: NavKey;
  onNavigate: (target: NavKey) => void;
  actions?: ReactNode;
  children: ReactNode;
}

function Layout({ title, active, onNavigate, actions, children }: LayoutProps) {
  return (
    <div className="app-shell">
      <Sidebar active={active} onNavigate={onNavigate} />
      <div className="main">
        <div className="topbar">
          <span className="topbar-title">{title}</span>
          <div className="topbar-right">
            {actions}
            <LanguageToggle />
          </div>
        </div>
        <div className="content">{children}</div>
      </div>
    </div>
  );
}

export default Layout;
