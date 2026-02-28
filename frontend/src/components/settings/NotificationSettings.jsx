import { useState, useEffect } from 'react';
import { Save, Mail, Globe, Plus, X } from 'lucide-react';
import { settingsAPI } from '@api/settings';
import Loading from '@components/common/Loading';

const NotificationSettings = () => {
  const [settings, setSettings] = useState({
    emailEnabled: false,
    emailRecipients: [],
    webhookEnabled: false,
    webhookUrl: '',
    eventTypes: [],
  });
  const [isLoading, setIsLoading] = useState(true);
  const [isSaving, setIsSaving] = useState(false);
  const [newEmail, setNewEmail] = useState('');

  useEffect(() => {
    loadSettings();
  }, []);

  const loadSettings = async () => {
    try {
      const data = await settingsAPI.getNotificationSettings();
      setSettings(data);
    } catch (error) {
      console.error('Ошибка загрузки настроек:', error);
    } finally {
      setIsLoading(false);
    }
  };

  const handleSave = async () => {
    setIsSaving(true);
    try {
      await settingsAPI.updateNotificationSettings(settings);
    } catch (error) {
      console.error('Ошибка сохранения настроек:', error);
    } finally {
      setIsSaving(false);
    }
  };

  const handleAddEmail = () => {
    if (newEmail && !settings.emailRecipients.includes(newEmail)) {
      setSettings({
        ...settings,
        emailRecipients: [...settings.emailRecipients, newEmail],
      });
      setNewEmail('');
    }
  };

  const handleRemoveEmail = (email) => {
    setSettings({
      ...settings,
      emailRecipients: settings.emailRecipients.filter((e) => e !== email),
    });
  };

  const handleEventTypeToggle = (eventType) => {
    setSettings({
      ...settings,
      eventTypes: settings.eventTypes.includes(eventType)
        ? settings.eventTypes.filter((t) => t !== eventType)
        : [...settings.eventTypes, eventType],
    });
  };

  const eventTypes = [
    { value: 'motion', label: 'Движение' },
    { value: 'intrusion', label: 'Проникновение' },
    { value: 'line_cross', label: 'Пересечение линии' },
    { value: 'object_left', label: 'Оставленный объект' },
    { value: 'object_removed', label: 'Удаленный объект' },
    { value: 'face_detection', label: 'Обнаружение лица' },
    { value: 'license_plate', label: 'Распознавание номера' },
    { value: 'audio_detection', label: 'Звуковое событие' },
    { value: 'system', label: 'Системные события' },
  ];

  if (isLoading) {
    return <Loading size="lg" text="Загрузка настроек..." />;
  }

  return (
    <div className="space-y-6">
      {/* Email уведомления */}
      <div className="bg-white dark:bg-gray-800 rounded-lg shadow p-6">
        <div className="flex items-center space-x-3 mb-4">
          <Mail className="w-6 h-6 text-primary-500" />
          <h3 className="text-lg font-semibold text-gray-900 dark:text-white">
            Email уведомления
          </h3>
        </div>

        <div className="space-y-4">
          <div className="flex items-center justify-between">
            <div>
              <label className="text-sm font-medium text-gray-700 dark:text-gray-300">
                Включить email уведомления
              </label>
              <p className="text-xs text-gray-500 dark:text-gray-400">
                Отправлять уведомления на email
              </p>
            </div>
            <input
              type="checkbox"
              checked={settings.emailEnabled}
              onChange={(e) =>
                setSettings({ ...settings, emailEnabled: e.target.checked })
              }
              className="w-5 h-5 text-primary-500 border-gray-300 rounded focus:ring-primary-500"
            />
          </div>

          {settings.emailEnabled && (
            <div>
              <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                Получатели
              </label>
              <div className="space-y-2">
                {settings.emailRecipients.map((email) => (
                  <div
                    key={email}
                    className="flex items-center justify-between bg-gray-50 dark:bg-gray-700 rounded-lg px-4 py-2"
                  >
                    <span className="text-gray-900 dark:text-white">{email}</span>
                    <button
                      onClick={() => handleRemoveEmail(email)}
                      className="text-gray-400 hover:text-danger-500 transition-colors"
                    >
                      <X className="w-4 h-4" />
                    </button>
                  </div>
                ))}
                <div className="flex space-x-2">
                  <input
                    type="email"
                    value={newEmail}
                    onChange={(e) => setNewEmail(e.target.value)}
                    onKeyPress={(e) => e.key === 'Enter' && handleAddEmail()}
                    placeholder="email@example.com"
                    className="flex-1 px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent bg-white dark:bg-gray-700 text-gray-900 dark:text-white"
                  />
                  <button
                    onClick={handleAddEmail}
                    className="px-4 py-2 bg-primary-500 hover:bg-primary-600 text-white rounded-lg transition-colors"
                  >
                    <Plus className="w-4 h-4" />
                  </button>
                </div>
              </div>
            </div>
          )}
        </div>
      </div>

      {/* Webhook уведомления */}
      <div className="bg-white dark:bg-gray-800 rounded-lg shadow p-6">
        <div className="flex items-center space-x-3 mb-4">
          <Globe className="w-6 h-6 text-primary-500" />
          <h3 className="text-lg font-semibold text-gray-900 dark:text-white">
            Webhook уведомления
          </h3>
        </div>

        <div className="space-y-4">
          <div className="flex items-center justify-between">
            <div>
              <label className="text-sm font-medium text-gray-700 dark:text-gray-300">
                Включить webhook уведомления
              </label>
              <p className="text-xs text-gray-500 dark:text-gray-400">
                Отправлять уведомления на webhook URL
              </p>
            </div>
            <input
              type="checkbox"
              checked={settings.webhookEnabled}
              onChange={(e) =>
                setSettings({ ...settings, webhookEnabled: e.target.checked })
              }
              className="w-5 h-5 text-primary-500 border-gray-300 rounded focus:ring-primary-500"
            />
          </div>

          {settings.webhookEnabled && (
            <div>
              <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                Webhook URL
              </label>
              <input
                type="url"
                value={settings.webhookUrl}
                onChange={(e) =>
                  setSettings({ ...settings, webhookUrl: e.target.value })
                }
                placeholder="https://example.com/webhook"
                className="w-full px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent bg-white dark:bg-gray-700 text-gray-900 dark:text-white"
              />
            </div>
          )}
        </div>
      </div>

      {/* Типы событий */}
      <div className="bg-white dark:bg-gray-800 rounded-lg shadow p-6">
        <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-4">
          Типы событий для уведомлений
        </h3>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
          {eventTypes.map((eventType) => (
            <label
              key={eventType.value}
              className="flex items-center space-x-3 p-3 border border-gray-200 dark:border-gray-700 rounded-lg cursor-pointer hover:bg-gray-50 dark:hover:bg-gray-700 transition-colors"
            >
              <input
                type="checkbox"
                checked={settings.eventTypes.includes(eventType.value)}
                onChange={() => handleEventTypeToggle(eventType.value)}
                className="w-4 h-4 text-primary-500 border-gray-300 rounded focus:ring-primary-500"
              />
              <span className="text-gray-900 dark:text-white">{eventType.label}</span>
            </label>
          ))}
        </div>
      </div>

      {/* Кнопка сохранения */}
      <div className="flex justify-end">
        <button
          onClick={handleSave}
          disabled={isSaving}
          className="flex items-center space-x-2 px-6 py-2 bg-primary-500 hover:bg-primary-600 text-white rounded-lg transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
        >
          {isSaving ? (
            <Loading size="sm" />
          ) : (
            <Save className="w-4 h-4" />
          )}
          <span>Сохранить</span>
        </button>
      </div>
    </div>
  );
};

export default NotificationSettings;
