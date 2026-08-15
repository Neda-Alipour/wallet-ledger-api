import React, { useState } from 'react';
import { Outlet } from 'react-router-dom';
import Header from './Header';
import Sidebar from './Sidebar';

export default function Layout() {
  const [mobileSidebarOpen, setMobileSidebarOpen] = useState(false);

  const closeSidebar = () => setMobileSidebarOpen(false);
  const toggleSidebar = () => setMobileSidebarOpen((prev) => !prev);

  return (
    <div className="app-shell">
      {/* Mobile overlay backdrop */}
      {mobileSidebarOpen && (
        <div
          className="sidebar-backdrop"
          onClick={closeSidebar}
          aria-hidden="true"
        />
      )}

      {/* Left Sidebar */}
      <aside className={`app-sidebar ${mobileSidebarOpen ? 'mobile-open' : ''}`}>
        <Sidebar closeMobileSidebar={closeSidebar} />
      </aside>

      {/* Right: Main wrapper (header + content) */}
      <div className="main-wrapper">
        <Header toggleMobileSidebar={toggleSidebar} />
        <main className="content-area">
          <Outlet />
        </main>
      </div>
    </div>
  );
}
