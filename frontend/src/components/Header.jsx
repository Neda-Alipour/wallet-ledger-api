import React from 'react';
import { useLocation } from 'react-router-dom';
import { BellIcon } from './Icons';
import { useAuth } from '../context/AuthContext';

const PAGE_META = {
  '/dashboard':    { title: 'Dashboard',     subtitle: 'Overview of your wallets and recent activity.' },
  '/wallets':      { title: 'My Wallets',    subtitle: 'Manage your multi-currency accounts and balances.' },
  '/transactions': { title: 'Transactions',  subtitle: 'View and track your wallet transaction history.' },
  '/transfer':     { title: 'Send Money',    subtitle: 'Transfer funds securely to another user\'s wallet.' },
  '/profile':      { title: 'Settings',      subtitle: 'Manage your account credentials and profile.' },
};

export default function Header({ toggleMobileSidebar }) {
  const { user } = useAuth();
  const location = useLocation();

  const { title, subtitle } = PAGE_META[location.pathname] || PAGE_META['/dashboard'];
  const userInitial = (user?.name || user?.email || 'U').charAt(0).toUpperCase();
  const userLabel = user?.name || user?.email || '';

  return (
    <header className="app-header">
      {/* Left side: mobile hamburger + page title */}
      <div className="header-left">
        <button
          className="mobile-menu-toggle"
          onClick={toggleMobileSidebar}
          aria-label="Open navigation menu"
        >
          <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round">
            <line x1="3" y1="6" x2="21" y2="6" />
            <line x1="3" y1="12" x2="21" y2="12" />
            <line x1="3" y1="18" x2="21" y2="18" />
          </svg>
        </button>

        <div>
          <div className="header-page-title">{title}</div>
          <div className="header-page-subtitle">{subtitle}</div>
        </div>
      </div>

      {/* Right side: notification bell + user badge */}
      <div className="header-right">
        <button className="icon-btn-subtle" title="Notifications" aria-label="Notifications">
          <BellIcon className="nav-icon" />
        </button>

        {user && (
          <div className="user-profile-badge">
            <div className="user-avatar-small">{userInitial}</div>
            {userLabel && <span className="user-email-text">{userLabel}</span>}
          </div>
        )}
      </div>
    </header>
  );
}
