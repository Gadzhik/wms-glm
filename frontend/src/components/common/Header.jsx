import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { Menu, X, User, LogOut, Bell } from 'lucide-react';
import { useAuth } from '@hooks/useAuth';
import { APP_NAME } from '@utils/constants';

const Header = ({ onToggleSidebar }) => {
  const navigate = useNavigate();
  const { user, logout, isAdmin } = useAuth();
  const [showUserMenu, setShowUserMenu] = useState(false);
  const [showNotifications, setShowNotifications] = useState(false);

  const handleLogout = async () => {
    await logout();
    navigate('/login');
  };

  const handleProfile = () => {
    navigate('/settings');
    setShowUserMenu(false);
  };

  return (
    <header className="bg-white dark:bg-gray-800 shadow-md h-16 fixed top-0 left-0 right-0 z-50">
      <div className="flex items-center justify-between h-full px-4">
        <div className="flex items-center space-x-4">
          <button
            onClick={onToggleSidebar}
            className="p-2 rounded-lg hover:bg-gray-100 dark:hover:bg-gray-700 transition-colors"
          >
            <Menu className="w-6 h-6 text-gray-600 dark:text-gray-300" />
          </button>
          <h1 className="text-xl font-bold text-gray-800 dark:text-white">
            {APP_NAME}
          </h1>
        </div>

        <div className="flex items-center space-x-4">
          {/* Уведомления */}
          <div className="relative">
            <button
              onClick={() => setShowNotifications(!showNotifications)}
              className="p-2 rounded-lg hover:bg-gray-100 dark:hover:bg-gray-700 transition-colors relative"
            >
              <Bell className="w-6 h-6 text-gray-600 dark:text-gray-300" />
              <span className="absolute top-1 right-1 w-2 h-2 bg-red-500 rounded-full"></span>
            </button>
            
            {showNotifications && (
              <div className="absolute right-0 mt-2 w-80 bg-white dark:bg-gray-800 rounded-lg shadow-lg border border-gray-200 dark:border-gray-700">
                <div className="p-4 border-b border-gray-200 dark:border-gray-700">
                  <h3 className="font-semibold text-gray-800 dark:text-white">
                    Уведомления
                  </h3>
                </div>
                <div className="max-h-64 overflow-y-auto">
                  <div className="p-4 text-center text-gray-500 dark:text-gray-400">
                    Нет новых уведомлений
                  </div>
                </div>
              </div>
            )}
          </div>

          {/* Меню пользователя */}
          <div className="relative">
            <button
              onClick={() => setShowUserMenu(!showUserMenu)}
              className="flex items-center space-x-2 p-2 rounded-lg hover:bg-gray-100 dark:hover:bg-gray-700 transition-colors"
            >
              <User className="w-6 h-6 text-gray-600 dark:text-gray-300" />
              <span className="hidden md:block text-gray-800 dark:text-white font-medium">
                {user?.username || 'Пользователь'}
              </span>
            </button>

            {showUserMenu && (
              <div className="absolute right-0 mt-2 w-48 bg-white dark:bg-gray-800 rounded-lg shadow-lg border border-gray-200 dark:border-gray-700">
                <div className="p-4 border-b border-gray-200 dark:border-gray-700">
                  <p className="font-semibold text-gray-800 dark:text-white">
                    {user?.username}
                  </p>
                  <p className="text-sm text-gray-500 dark:text-gray-400">
                    {user?.email}
                  </p>
                  <span className="inline-block mt-1 px-2 py-1 text-xs rounded-full bg-primary-100 dark:bg-primary-900 text-primary-600 dark:text-primary-300">
                    {user?.role === 'admin' ? 'Администратор' : 'Оператор'}
                  </span>
                </div>
                <div className="py-1">
                  <button
                    onClick={handleProfile}
                    className="w-full px-4 py-2 text-left text-gray-700 dark:text-gray-300 hover:bg-gray-100 dark:hover:bg-gray-700 transition-colors"
                  >
                    Настройки
                  </button>
                  <button
                    onClick={handleLogout}
                    className="w-full px-4 py-2 text-left text-red-600 dark:text-red-400 hover:bg-gray-100 dark:hover:bg-gray-700 transition-colors flex items-center space-x-2"
                  >
                    <LogOut className="w-4 h-4" />
                    <span>Выйти</span>
                  </button>
                </div>
              </div>
            )}
          </div>
        </div>
      </div>
    </header>
  );
};

export default Header;
