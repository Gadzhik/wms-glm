import { useState, useEffect } from 'react';
import { Save, Trash2, RefreshCw, HardDrive } from 'lucide-react';
import { settingsAPI } from '@api/settings';
import Loading from '@components/common/Loading';
import { formatFileSize } from '@utils/format';

const StorageSettings = () => {
  const [settings, setSettings] = useState({
    maxStorageDays: 30,
    maxStorageSizeGB: 1000,
    autoCleanup: true,
    cleanupTime: '02:00',
  });
  const [storageInfo, setStorageInfo] = useState(null);
  const [isLoading, setIsLoading] = useState(true);
  const [isSaving, setIsSaving] = useState(false);
  const [isCleaning, setIsCleaning] = useState(false);

  useEffect(() => {
    loadSettings();
    loadStorageInfo();
  }, []);

  const loadSettings = async () => {
    try {
      const data = await settingsAPI.getStorageSettings();
      setSettings(data);
    } catch (error) {
      console.error('Ошибка загрузки настроек:', error);
    } finally {
      setIsLoading(false);
    }
  };

  const loadStorageInfo = async () => {
    try {
      const data = await settingsAPI.getStorageInfo();
      setStorageInfo(data);
    } catch (error) {
      console.error('Ошибка загрузки информации о хранилище:', error);
    }
  };

  const handleSave = async () => {
    setIsSaving(true);
    try {
      await settingsAPI.updateStorageSettings(settings);
    } catch (error) {
      console.error('Ошибка сохранения настроек:', error);
    } finally {
      setIsSaving(false);
    }
  };

  const handleCleanup = async () => {
    if (!confirm('Вы уверены, что хотите удалить старые записи?')) return;

    setIsCleaning(true);
    try {
      await settingsAPI.cleanupOldRecordings(settings.maxStorageDays);
      await loadStorageInfo();
    } catch (error) {
      console.error('Ошибка очистки:', error);
    } finally {
      setIsCleaning(false);
    }
  };

  if (isLoading) {
    return <Loading size="lg" text="Загрузка настроек..." />;
  }

  return (
    <div className="space-y-6">
      {/* Информация о хранилище */}
      {storageInfo && (
        <div className="bg-gray-50 dark:bg-gray-700 rounded-lg p-6">
          <div className="flex items-center space-x-3 mb-4">
            <HardDrive className="w-6 h-6 text-primary-500" />
            <h3 className="text-lg font-semibold text-gray-900 dark:text-white">
              Информация о хранилище
            </h3>
          </div>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <div className="bg-white dark:bg-gray-800 rounded-lg p-4">
              <p className="text-sm text-gray-600 dark:text-gray-400 mb-1">
                Использовано
              </p>
              <p className="text-2xl font-bold text-gray-900 dark:text-white">
                {formatFileSize(storageInfo.used)}
              </p>
            </div>
            <div className="bg-white dark:bg-gray-800 rounded-lg p-4">
              <p className="text-sm text-gray-600 dark:text-gray-400 mb-1">
                Свободно
              </p>
              <p className="text-2xl font-bold text-gray-900 dark:text-white">
                {formatFileSize(storageInfo.free)}
              </p>
            </div>
            <div className="bg-white dark:bg-gray-800 rounded-lg p-4">
              <p className="text-sm text-gray-600 dark:text-gray-400 mb-1">
                Всего
              </p>
              <p className="text-2xl font-bold text-gray-900 dark:text-white">
                {formatFileSize(storageInfo.total)}
              </p>
            </div>
          </div>
          {/* Прогресс бар */}
          <div className="mt-4">
            <div className="flex justify-between text-sm text-gray-600 dark:text-gray-400 mb-2">
              <span>Использовано</span>
              <span>{((storageInfo.used / storageInfo.total) * 100).toFixed(1)}%</span>
            </div>
            <div className="w-full bg-gray-200 dark:bg-gray-600 rounded-full h-2">
              <div
                className="bg-primary-500 h-2 rounded-full transition-all"
                style={{
                  width: `${(storageInfo.used / storageInfo.total) * 100}%`,
                }}
              ></div>
            </div>
          </div>
        </div>
      )}

      {/* Настройки */}
      <div className="bg-white dark:bg-gray-800 rounded-lg shadow p-6">
        <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-4">
          Настройки хранения
        </h3>

        <div className="space-y-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
              Максимальный срок хранения (дней)
            </label>
            <input
              type="number"
              value={settings.maxStorageDays}
              onChange={(e) =>
                setSettings({ ...settings, maxStorageDays: parseInt(e.target.value) })
              }
              min="1"
              max="3650"
              className="w-full px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent bg-white dark:bg-gray-700 text-gray-900 dark:text-white"
            />
            <p className="mt-1 text-xs text-gray-500 dark:text-gray-400">
              Записи старше указанного количества дней будут автоматически удалены
            </p>
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
              Максимальный размер хранилища (ГБ)
            </label>
            <input
              type="number"
              value={settings.maxStorageSizeGB}
              onChange={(e) =>
                setSettings({ ...settings, maxStorageSizeGB: parseInt(e.target.value) })
              }
              min="1"
              className="w-full px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent bg-white dark:bg-gray-700 text-gray-900 dark:text-white"
            />
            <p className="mt-1 text-xs text-gray-500 dark:text-gray-400">
              При достижении лимита старые записи будут удаляться автоматически
            </p>
          </div>

          <div className="flex items-center justify-between">
            <div>
              <label className="text-sm font-medium text-gray-700 dark:text-gray-300">
                Автоматическая очистка
              </label>
              <p className="text-xs text-gray-500 dark:text-gray-400">
                Удалять старые записи автоматически
              </p>
            </div>
            <input
              type="checkbox"
              checked={settings.autoCleanup}
              onChange={(e) =>
                setSettings({ ...settings, autoCleanup: e.target.checked })
              }
              className="w-5 h-5 text-primary-500 border-gray-300 rounded focus:ring-primary-500"
            />
          </div>

          {settings.autoCleanup && (
            <div>
              <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                Время очистки
              </label>
              <input
                type="time"
                value={settings.cleanupTime}
                onChange={(e) =>
                  setSettings({ ...settings, cleanupTime: e.target.value })
                }
                className="w-full px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent bg-white dark:bg-gray-700 text-gray-900 dark:text-white"
              />
            </div>
          )}
        </div>
      </div>

      {/* Кнопки */}
      <div className="flex justify-between">
        <button
          onClick={handleCleanup}
          disabled={isCleaning}
          className="flex items-center space-x-2 px-4 py-2 bg-danger-500 hover:bg-danger-600 text-white rounded-lg transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
        >
          {isCleaning ? (
            <Loading size="sm" />
          ) : (
            <Trash2 className="w-4 h-4" />
          )}
          <span>Удалить старые записи</span>
        </button>

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

export default StorageSettings;
