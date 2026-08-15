import React from 'react';
import { NavLink, useNavigate } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import { LogoIcon, DashboardIcon, WalletsIcon, TransactionsIcon, SettingsIcon } from './Icons';

export default function Sidebar({ closeMobileSidebar }) {
  const { user, logout } = useAuth();
  const navigate = useNavigate();

  const handleLogout = async () => {
    closeMobileSidebar();
    await logout();
    navigate('/login');
  };

  const handleNavClick = () => {
    closeMobileSidebar();
  };

  const userInitial = (user?.name || user?.email || 'U').charAt(0).toUpperCase();
  const userLabel = user?.name || user?.email || 'User';

  return (
    <div className="sidebar-inner">
      {/* Brand */}
      <div className="sidebar-brand">
        <LogoIcon className="brand-svg" />
        <span className="brand-title">Wallet Ledger</span>
      </div>

      {/* Primary Navigation */}
      <nav className="sidebar-nav" aria-label="Main navigation">
        <NavLink
          to="/dashboard"
          className={({ isActive }) => `nav-link${isActive ? ' active' : ''}`}
          onClick={handleNavClick}
        >
          <DashboardIcon />
          <span>Dashboard</span>
        </NavLink>

        <NavLink
          to="/wallets"
          className={({ isActive }) => `nav-link${isActive ? ' active' : ''}`}
          onClick={handleNavClick}
        >
          <WalletsIcon />
          <span>My Wallets</span>
        </NavLink>

        <NavLink
          to="/transactions"
          className={({ isActive }) => `nav-link${isActive ? ' active' : ''}`}
          onClick={handleNavClick}
        >
          <TransactionsIcon />
          <span>Transactions</span>
        </NavLink>
      </nav>

      {/* Divider */}
      <div className="sidebar-divider" />

      {/* Secondary Navigation */}
      <nav className="sidebar-nav" aria-label="Secondary navigation">
        <NavLink
          to="/profile"
          className={({ isActive }) => `nav-link${isActive ? ' active' : ''}`}
          onClick={handleNavClick}
        >
          <SettingsIcon />
          <span>Settings</span>
        </NavLink>
      </nav>

      {/* Spacer */}
      <div style={{ flex: 1 }} />

      {/* User Profile Footer */}
      <div className="sidebar-user-footer">
        <div className="sidebar-user-info">
          <div className="user-avatar-circle">{userInitial}</div>
          <div className="user-text-details">
            <span className="user-display-name">{userLabel}</span>
            <span className="user-sub-label">Active Account</span>
          </div>
        </div>
        <button className="btn-logout-small" onClick={handleLogout} title="Logout">
          Logout
        </button>
      </div>
    </div>
  );
}
