import { useState } from 'react';
import { HardDrive, Video, Bell, User, Shield, Database } from 'lucide-react';
import StorageSettings from './StorageSettings';
import RecordingSettings from './RecordingSettings';
import NotificationSettings from './NotificationSettings';

const SettingsPanel = () => {
  const [activeTab, setActiveTab] = useState('storage');

  const tabs = [
    { id: 'storage', label: 'Хранилище', icon: HardDrive },
    { id: 'recording', label: 'Запись', icon: Video },
    { id: 'notifications', label: 'Уведомления', icon: Bell },
    { id: 'profile', label: 'Профиль', icon: User },
    { id: 'security', label: 'Безопасность', icon: Shield },
  ];

  return (
    <div className="space-y-6">
      {/* Заголовок */}
      <div>
        <h1 className="text-2xl font-bold text-gray-900 dark:text-white">
          Настройки
        </h1>
        <p className="text-gray-600 dark:text-gray-400 mt-1">
          Управление настройками системы
        </p>
      </div>

      {/* Табы */}
      <div className="bg-white dark:bg-gray-800 rounded-lg shadow">
        <div className="border-b border-gray-200 dark:border-gray-700">
          <nav className="flex space-x-8 px-6" aria-label="Tabs">
            {tabs.map((tab) => (
              <button
                key={tab.id}
                onClick={() => setActiveTab(tab.id)}
                className={`flex items-center space-x-2 py-4 px-1 border-b-2 font-medium text-sm transition-colors ${
                  activeTab === tab.id
                    ? 'border-primary-500 text-primary-600 dark:text-primary-400'
                    : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300 dark:text-gray-400 dark:hover:text-gray-300'
                }`}
              >
                <tab.icon className="w-4 h-4" />
                <span>{tab.label}</span>
              </button>
            ))}
          </nav>
        </div>

        {/* Контент табов */}
        <div className="p-6">
          {activeTab === 'storage' && <StorageSettings />}
          {activeTab === 'recording' && <RecordingSettings />}
          {activeTab === 'notifications' && <NotificationSettings />}
          {activeTab === 'profile' && (
            <div className="text-center py-12 text-gray-500 dark:text-gray-400">
              <User className="w-16 h-16 mx-auto mb-4" />
              <p>Настройки профиля в разработке</p>
            </div>
          )}
          {activeTab === 'security' && (
            <div className="text-center py-12 text-gray-500 dark:text-gray-400">
              <Shield className="w-16 h-16 mx-auto mb-4" />
              <p>Настройки безопасности в разработке</p>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default SettingsPanel;
