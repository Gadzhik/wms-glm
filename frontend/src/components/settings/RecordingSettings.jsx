import { useState, useEffect } from 'react';
import { Save, Video, Volume2 } from 'lucide-react';
import { settingsAPI } from '@api/settings';
import Loading from '@components/common/Loading';

const RecordingSettings = () => {
  const [settings, setSettings] = useState({
    defaultRecordingType: 'continuous',
    videoCodec: 'h264',
    videoBitrate: 4000,
    videoResolution: '1080p',
    fps: 25,
    audioEnabled: false,
    audioCodec: 'aac',
  });
  const [isLoading, setIsLoading] = useState(true);
  const [isSaving, setIsSaving] = useState(false);

  useEffect(() => {
    loadSettings();
  }, []);

  const loadSettings = async () => {
    try {
      const data = await settingsAPI.getRecordingSettings();
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
      await settingsAPI.updateRecordingSettings(settings);
    } catch (error) {
      console.error('Ошибка сохранения настроек:', error);
    } finally {
      setIsSaving(false);
    }
  };

  if (isLoading) {
    return <Loading size="lg" text="Загрузка настроек..." />;
  }

  return (
    <div className="space-y-6">
      {/* Настройки видео */}
      <div className="bg-white dark:bg-gray-800 rounded-lg shadow p-6">
        <div className="flex items-center space-x-3 mb-4">
          <Video className="w-6 h-6 text-primary-500" />
          <h3 className="text-lg font-semibold text-gray-900 dark:text-white">
            Настройки видео
          </h3>
        </div>

        <div className="space-y-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
              Тип записи по умолчанию
            </label>
            <select
              value={settings.defaultRecordingType}
              onChange={(e) =>
                setSettings({ ...settings, defaultRecordingType: e.target.value })
              }
              className="w-full px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent bg-white dark:bg-gray-700 text-gray-900 dark:text-white"
            >
              <option value="continuous">Непрерывная</option>
              <option value="motion">По движению</option>
              <option value="event">По событию</option>
            </select>
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
              Кодек видео
            </label>
            <select
              value={settings.videoCodec}
              onChange={(e) =>
                setSettings({ ...settings, videoCodec: e.target.value })
              }
              className="w-full px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent bg-white dark:bg-gray-700 text-gray-900 dark:text-white"
            >
              <option value="h264">H.264</option>
              <option value="h265">H.265 (HEVC)</option>
              <option value="mjpeg">MJPEG</option>
            </select>
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
              Битрейт видео (Кбит/с)
            </label>
            <input
              type="number"
              value={settings.videoBitrate}
              onChange={(e) =>
                setSettings({ ...settings, videoBitrate: parseInt(e.target.value) })
              }
              min="100"
              max="20000"
              step="100"
              className="w-full px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent bg-white dark:bg-gray-700 text-gray-900 dark:text-white"
            />
            <p className="mt-1 text-xs text-gray-500 dark:text-gray-400">
              Рекомендуемые значения: 2000-8000 Кбит/с
            </p>
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
              Разрешение
            </label>
            <select
              value={settings.videoResolution}
              onChange={(e) =>
                setSettings({ ...settings, videoResolution: e.target.value })
              }
              className="w-full px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent bg-white dark:bg-gray-700 text-gray-900 dark:text-white"
            >
              <option value="720p">720p (1280x720)</option>
              <option value="1080p">1080p (1920x1080)</option>
              <option value="4K">4K (3840x2160)</option>
            </select>
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
              Частота кадров (FPS)
            </label>
            <input
              type="number"
              value={settings.fps}
              onChange={(e) =>
                setSettings({ ...settings, fps: parseInt(e.target.value) })
              }
              min="1"
              max="60"
              className="w-full px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent bg-white dark:bg-gray-700 text-gray-900 dark:text-white"
            />
            <p className="mt-1 text-xs text-gray-500 dark:text-gray-400">
              Рекомендуемые значения: 15-30 FPS
            </p>
          </div>
        </div>
      </div>

      {/* Настройки аудио */}
      <div className="bg-white dark:bg-gray-800 rounded-lg shadow p-6">
        <div className="flex items-center space-x-3 mb-4">
          <Volume2 className="w-6 h-6 text-primary-500" />
          <h3 className="text-lg font-semibold text-gray-900 dark:text-white">
            Настройки аудио
          </h3>
        </div>

        <div className="space-y-4">
          <div className="flex items-center justify-between">
            <div>
              <label className="text-sm font-medium text-gray-700 dark:text-gray-300">
                Запись аудио
              </label>
              <p className="text-xs text-gray-500 dark:text-gray-400">
                Записывать аудио вместе с видео
              </p>
            </div>
            <input
              type="checkbox"
              checked={settings.audioEnabled}
              onChange={(e) =>
                setSettings({ ...settings, audioEnabled: e.target.checked })
              }
              className="w-5 h-5 text-primary-500 border-gray-300 rounded focus:ring-primary-500"
            />
          </div>

          {settings.audioEnabled && (
            <div>
              <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                Кодек аудио
              </label>
              <select
                value={settings.audioCodec}
                onChange={(e) =>
                  setSettings({ ...settings, audioCodec: e.target.value })
                }
                className="w-full px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent bg-white dark:bg-gray-700 text-gray-900 dark:text-white"
              >
                <option value="aac">AAC</option>
                <option value="mp3">MP3</option>
                <option value="opus">Opus</option>
              </select>
            </div>
          )}
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

export default RecordingSettings;
