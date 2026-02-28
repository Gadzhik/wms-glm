import { NavLink } from 'react-router-dom';
import {
  LayoutDashboard,
  Video,
  Radio,
  Archive,
  AlertTriangle,
  Settings,
  ChevronLeft,
  ChevronRight,
} from 'lucide-react';

const Sidebar = ({ collapsed }) => {
  const menuItems = [
    { path: '/dashboard', icon: LayoutDashboard, label: 'Дашборд' },
    { path: '/cameras', icon: Video, label: 'Камеры' },
    { path: '/live', icon: Radio, label: 'Live' },
    { path: '/archive', icon: Archive, label: 'Архив' },
    { path: '/events', icon: AlertTriangle, label: 'События' },
    { path: '/settings', icon: Settings, label: 'Настройки' },
  ];

  return (
    <aside
      className={`fixed left-0 top-16 h-[calc(100vh-4rem)] bg-white dark:bg-gray-800 shadow-lg transition-all duration-300 z-40 ${
        collapsed ? 'w-16' : 'w-64'
      }`}
    >
      <nav className="p-4 space-y-2">
        {menuItems.map((item) => (
          <NavLink
            key={item.path}
            to={item.path}
            className={({ isActive }) =>
              `flex items-center space-x-3 px-4 py-3 rounded-lg transition-colors ${
                isActive
                  ? 'bg-primary-500 text-white'
                  : 'text-gray-700 dark:text-gray-300 hover:bg-gray-100 dark:hover:bg-gray-700'
              } ${collapsed ? 'justify-center' : ''}`
            }
          >
            <item.icon className="w-5 h-5 flex-shrink-0" />
            {!collapsed && <span className="font-medium">{item.label}</span>}
          </NavLink>
        ))}
      </nav>

      {/* Кнопка сворачивания */}
      <div className="absolute bottom-4 left-0 right-0 flex justify-center">
        <button
          className={`p-2 rounded-lg hover:bg-gray-100 dark:hover:bg-gray-700 transition-colors text-gray-600 dark:text-gray-300 ${
            collapsed ? 'justify-center' : ''
          }`}
        >
          {collapsed ? (
            <ChevronRight className="w-5 h-5" />
          ) : (
            <ChevronLeft className="w-5 h-5" />
          )}
        </button>
      </div>
    </aside>
  );
};

export default Sidebar;
