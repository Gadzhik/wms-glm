import { useState, useEffect } from 'react';
import { useNavigate, useParams } from 'react-router-dom';
import { Save, X, TestTube, Search } from 'lucide-react';
import { useCameras } from '@hooks/useCameras';
import { camerasAPI } from '@api/cameras';
import { validateForm, cameraSchema } from '@utils/validation';
import Loading from '@components/common/Loading';
import { RECORDING_TYPES } from '@utils/constants';

const CameraForm = () => {
  const navigate = useNavigate();
  const { id } = useParams();
  const { createCamera, updateCamera, isLoading } = useCameras();
  const isEditing = !!id;

  const [formData, setFormData] = useState({
    name: '',
    description: '',
    rtsp_url: '',
    username: '',
    password: '',
    location: '',
    recording_enabled: true,
    motion_detection: false,
    ptz_enabled: false,
    onvif_enabled: false,
    onvif_port: 80,
    onvif_path: '/onvif/device_service',
  });

  const [errors, setErrors] = useState({});
  const [isTesting, setIsTesting] = useState(false);
  const [testResult, setTestResult] = useState(null);

  useEffect(() => {
    if (isEditing) {
      loadCamera();
    }
  }, [id]);

  const loadCamera = async () => {
    try {
      const camera = await camerasAPI.getCamera(id);
      setFormData({
        name: camera.name || '',
        description: camera.description || '',
        rtsp_url: camera.rtsp_url || '',
        username: camera.username || '',
        password: camera.password || '',
        location: camera.location || '',
        recording_enabled: camera.recording_enabled ?? true,
        motion_detection: camera.motion_detection ?? false,
        ptz_enabled: camera.ptz_enabled ?? false,
        onvif_enabled: camera.onvif_enabled ?? false,
        onvif_port: camera.onvif_port || 80,
        onvif_path: camera.onvif_path || '/onvif/device_service',
      });
    } catch (error) {
      console.error('Ошибка загрузки камеры:', error);
      navigate('/cameras');
    }
  };

  const handleChange = (e) => {
    const { name, value, type, checked } = e.target;
    setFormData((prev) => ({
      ...prev,
      [name]: type === 'checkbox' ? checked : value,
    }));
    // Очищаем ошибку при изменении поля
    if (errors[name]) {
      setErrors((prev) => {
        const newErrors = { ...prev };
        delete newErrors[name];
        return newErrors;
      });
    }
  };

  const handleTestConnection = async () => {
    setIsTesting(true);
    setTestResult(null);
    try {
      const result = await camerasAPI.testConnection(formData);
      setTestResult({
        success: true,
        message: 'Соединение установлено успешно',
      });
    } catch (error) {
      setTestResult({
        success: false,
        message: error.userMessage || 'Ошибка соединения',
      });
    } finally {
      setIsTesting(false);
    }
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    
    // Валидация
    const validation = validateForm(cameraSchema, formData);
    if (!validation.success) {
      setErrors(validation.errors);
      return;
    }

    const result = isEditing
      ? await updateCamera(id, formData)
      : await createCamera(formData);

    if (result.success) {
      navigate('/cameras');
    }
  };

  const handleCancel = () => {
    navigate('/cameras');
  };

  return (
    <div className="max-w-4xl mx-auto">
      <div className="mb-6">
        <h1 className="text-2xl font-bold text-gray-900 dark:text-white">
          {isEditing ? 'Редактировать камеру' : 'Добавить камеру'}
        </h1>
        <p className="text-gray-600 dark:text-gray-400 mt-1">
          {isEditing ? 'Измените параметры камеры' : 'Заполните данные для подключения камеры'}
        </p>
      </div>

      <form onSubmit={handleSubmit} className="space-y-6">
        {/* Основная информация */}
        <div className="bg-white dark:bg-gray-800 rounded-lg shadow p-6">
          <h2 className="text-lg font-semibold text-gray-900 dark:text-white mb-4">
            Основная информация
          </h2>
          
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div className="md:col-span-2">
              <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                Название *
              </label>
              <input
                type="text"
                name="name"
                value={formData.name}
                onChange={handleChange}
                className={`w-full px-4 py-2 border rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent bg-white dark:bg-gray-700 text-gray-900 dark:text-white ${
                  errors.name ? 'border-danger-500' : 'border-gray-300 dark:border-gray-600'
                }`}
                placeholder="Например: Камера входа"
              />
              {errors.name && (
                <p className="mt-1 text-sm text-danger-600 dark:text-danger-400">{errors.name}</p>
              )}
            </div>

            <div className="md:col-span-2">
              <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                Описание
              </label>
              <textarea
                name="description"
                value={formData.description}
                onChange={handleChange}
                rows={3}
                className="w-full px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent bg-white dark:bg-gray-700 text-gray-900 dark:text-white"
                placeholder="Описание камеры"
              />
            </div>

            <div className="md:col-span-2">
              <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                Расположение
              </label>
              <input
                type="text"
                name="location"
                value={formData.location}
                onChange={handleChange}
                className="w-full px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent bg-white dark:bg-gray-700 text-gray-900 dark:text-white"
                placeholder="Например: Главный вход"
              />
            </div>
          </div>
        </div>

        {/* Подключение */}
        <div className="bg-white dark:bg-gray-800 rounded-lg shadow p-6">
          <div className="flex items-center justify-between mb-4">
            <h2 className="text-lg font-semibold text-gray-900 dark:text-white">
              Подключение
            </h2>
            <button
              type="button"
              onClick={handleTestConnection}
              disabled={isTesting}
              className="flex items-center space-x-2 px-4 py-2 bg-gray-100 dark:bg-gray-700 hover:bg-gray-200 dark:hover:bg-gray-600 text-gray-700 dark:text-gray-300 rounded-lg transition-colors disabled:opacity-50"
            >
              {isTesting ? (
                <Loading size="sm" />
              ) : (
                <TestTube className="w-4 h-4" />
              )}
              <span>Тест соединения</span>
            </button>
          </div>

          {testResult && (
            <div
              className={`mb-4 p-4 rounded-lg ${
                testResult.success
                  ? 'bg-success-50 dark:bg-success-900/20 text-success-700 dark:text-success-300'
                  : 'bg-danger-50 dark:bg-danger-900/20 text-danger-700 dark:text-danger-300'
              }`}
            >
              {testResult.message}
            </div>
          )}

          <div className="space-y-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                RTSP URL *
              </label>
              <input
                type="text"
                name="rtsp_url"
                value={formData.rtsp_url}
                onChange={handleChange}
                className={`w-full px-4 py-2 border rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent bg-white dark:bg-gray-700 text-gray-900 dark:text-white ${
                  errors.rtsp_url ? 'border-danger-500' : 'border-gray-300 dark:border-gray-600'
                }`}
                placeholder="rtsp://username:password@192.168.1.100:554/stream"
              />
              {errors.rtsp_url && (
                <p className="mt-1 text-sm text-danger-600 dark:text-danger-400">{errors.rtsp_url}</p>
              )}
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                  Имя пользователя
                </label>
                <input
                  type="text"
                  name="username"
                  value={formData.username}
                  onChange={handleChange}
                  className="w-full px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent bg-white dark:bg-gray-700 text-gray-900 dark:text-white"
                  placeholder="admin"
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                  Пароль
                </label>
                <input
                  type="password"
                  name="password"
                  value={formData.password}
                  onChange={handleChange}
                  className="w-full px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent bg-white dark:bg-gray-700 text-gray-900 dark:text-white"
                  placeholder="••••••••"
                />
              </div>
            </div>
          </div>
        </div>

        {/* Настройки записи */}
        <div className="bg-white dark:bg-gray-800 rounded-lg shadow p-6">
          <h2 className="text-lg font-semibold text-gray-900 dark:text-white mb-4">
            Настройки записи
          </h2>

          <div className="space-y-4">
            <div className="flex items-center justify-between">
              <div>
                <label className="text-sm font-medium text-gray-700 dark:text-gray-300">
                  Включить запись
                </label>
                <p className="text-xs text-gray-500 dark:text-gray-400">
                  Автоматическая запись видео с камеры
                </p>
              </div>
              <input
                type="checkbox"
                name="recording_enabled"
                checked={formData.recording_enabled}
                onChange={handleChange}
                className="w-5 h-5 text-primary-500 border-gray-300 rounded focus:ring-primary-500"
              />
            </div>

            <div className="flex items-center justify-between">
              <div>
                <label className="text-sm font-medium text-gray-700 dark:text-gray-300">
                  Детекция движения
                </label>
                <p className="text-xs text-gray-500 dark:text-gray-400">
                  Запись по движению
                </p>
              </div>
              <input
                type="checkbox"
                name="motion_detection"
                checked={formData.motion_detection}
                onChange={handleChange}
                className="w-5 h-5 text-primary-500 border-gray-300 rounded focus:ring-primary-500"
              />
            </div>
          </div>
        </div>

        {/* ONVIF */}
        <div className="bg-white dark:bg-gray-800 rounded-lg shadow p-6">
          <div className="flex items-center justify-between mb-4">
            <h2 className="text-lg font-semibold text-gray-900 dark:text-white">
              ONVIF
            </h2>
            <input
              type="checkbox"
              name="onvif_enabled"
              checked={formData.onvif_enabled}
              onChange={handleChange}
              className="w-5 h-5 text-primary-500 border-gray-300 rounded focus:ring-primary-500"
            />
          </div>

          {formData.onvif_enabled && (
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                  Порт
                </label>
                <input
                  type="number"
                  name="onvif_port"
                  value={formData.onvif_port}
                  onChange={handleChange}
                  className="w-full px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent bg-white dark:bg-gray-700 text-gray-900 dark:text-white"
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                  Путь
                </label>
                <input
                  type="text"
                  name="onvif_path"
                  value={formData.onvif_path}
                  onChange={handleChange}
                  className="w-full px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent bg-white dark:bg-gray-700 text-gray-900 dark:text-white"
                />
              </div>
            </div>
          )}
        </div>

        {/* Кнопки */}
        <div className="flex justify-end space-x-4">
          <button
            type="button"
            onClick={handleCancel}
            className="flex items-center space-x-2 px-6 py-2 border border-gray-300 dark:border-gray-600 text-gray-700 dark:text-gray-300 rounded-lg hover:bg-gray-50 dark:hover:bg-gray-700 transition-colors"
          >
            <X className="w-5 h-5" />
            <span>Отмена</span>
          </button>
          <button
            type="submit"
            disabled={isLoading}
            className="flex items-center space-x-2 px-6 py-2 bg-primary-500 hover:bg-primary-600 text-white rounded-lg transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
          >
            {isLoading ? (
              <Loading size="sm" />
            ) : (
              <Save className="w-5 h-5" />
            )}
            <span>{isEditing ? 'Сохранить' : 'Создать'}</span>
          </button>
        </div>
      </form>
    </div>
  );
};

export default CameraForm;
