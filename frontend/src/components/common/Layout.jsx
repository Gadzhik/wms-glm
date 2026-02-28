import { useState } from 'react';
import { Outlet } from 'react-router-dom';
import Header from './Header';
import Sidebar from './Sidebar';

const Layout = () => {
  const [sidebarCollapsed, setSidebarCollapsed] = useState(false);

  const toggleSidebar = () => {
    setSidebarCollapsed(!sidebarCollapsed);
  };

  return (
    <div className="min-h-screen bg-gray-100 dark:bg-gray-900">
      <Header onToggleSidebar={toggleSidebar} />
      <div className="flex">
        <Sidebar collapsed={sidebarCollapsed} />
        <main
          className={`flex-1 p-6 transition-all duration-300 ${
            sidebarCollapsed ? 'ml-16' : 'ml-64'
          }`}
        >
          <Outlet />
        </main>
      </div>
    </div>
  );
};

export default Layout;
