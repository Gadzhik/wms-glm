import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { Video, MapPin, Settings, Play } from 'lucide-react';
import { camerasAPI } from '@api/cameras';
import { formatStatus, getStatusColor, formatDateTime } from '@utils/format';
import CameraStatus from './CameraStatus';

const CameraCard = ({ camera }) => {
  const navigate = useNavigate();
  const [snapshot, setSnapshot] = useState(null);
  const [isLoadingSnapshot, setIsLoadingSnapshot] = useState(false);

  useEffect(() => {
    if (camera.status === 'online') {
      loadSnapshot();
    }
  }, [camera.id, camera.status]);

  const loadSnapshot = async () => {
    setIsLoadingSnapshot(true);
    try {
      const blob = await camerasAPI.getCameraSnapshot(camera.id);
      const url = URL.createObjectURL(blob);
      setSnapshot(url);
    } catch (error) {
      console.error('Ошибка загрузки превью:', error);
    } finally {
      setIsLoadingSnapshot(false);
    }
  };

  const handleViewLive = () => {
    navigate(`/live?camera=${camera.id}`);
  };

  const handleSettings = (e) => {
    e.stopPropagation();
    navigate(`/cameras/${camera.id}/edit`);
  };

  const statusColor = getStatusColor(camera.status);
  const statusColorClass = {
    success: 'bg-success-500',
    danger: 'bg-danger-500',
    warning: 'bg-warning-500',
    primary: 'bg-primary-500',
    default: 'bg-gray-500',
  }[statusColor];

  return (
    <div className="bg-white dark:bg-gray-800 rounded-lg shadow-md overflow-hidden hover:shadow-lg transition-shadow cursor-pointer group">
      {/* Превью камеры */}
      <div className="relative aspect-video bg-gray-900">
        {isLoadingSnapshot ? (
          <div className="absolute inset-0 flex items-center justify-center">
            <div className="w-8 h-8 border-3 border-primary-500 border-t-transparent rounded-full animate-spin"></div>
          </div>
        ) : snapshot ? (
          <img
            src={snapshot}
            alt={camera.name}
            className="w-full h-full object-cover"
          />
        ) : (
          <div className="absolute inset-0 flex items-center justify-center text-gray-600">
            <Video className="w-12 h-12" />
          </div>
        )}

        {/* Статус */}
        <div className="absolute top-2 left-2">
          <CameraStatus status={camera.status} />
        </div>

        {/* Кнопка Live */}
        <button
          onClick={handleViewLive}
          className="absolute inset-0 flex items-center justify-center bg-black bg-opacity-0 group-hover:bg-opacity-50 transition-all opacity-0 group-hover:opacity-100"
        >
          <div className="p-4 bg-white rounded-full shadow-lg transform scale-0 group-hover:scale-100 transition-transform">
            <Play className="w-8 h-8 text-primary-500 fill-current" />
          </div>
        </button>

        {/* Кнопка настроек */}
        <button
          onClick={handleSettings}
          className="absolute top-2 right-2 p-2 bg-white dark:bg-gray-800 rounded-lg shadow opacity-0 group-hover:opacity-100 transition-opacity hover:bg-gray-100 dark:hover:bg-gray-700"
        >
          <Settings className="w-4 h-4 text-gray-600 dark:text-gray-300" />
        </button>
      </div>

      {/* Информация о камере */}
      <div className="p-4">
        <h3 className="font-semibold text-gray-900 dark:text-white mb-1 truncate">
          {camera.name}
        </h3>
        {camera.description && (
          <p className="text-sm text-gray-600 dark:text-gray-400 mb-2 line-clamp-2">
            {camera.description}
          </p>
        )}

        <div className="flex items-center justify-between text-xs text-gray-500 dark:text-gray-400">
          <div className="flex items-center space-x-1">
            <MapPin className="w-3 h-3" />
            <span className="truncate">
              {camera.location || 'Не указано'}
            </span>
          </div>
          <span>{formatDateTime(camera.created_at, 'HH:mm')}</span>
        </div>

        {/* Дополнительная информация */}
        <div className="mt-3 pt-3 border-t border-gray-200 dark:border-gray-700">
          <div className="flex items-center justify-between text-xs">
            <span className="text-gray-500 dark:text-gray-400">
              {camera.recording_enabled ? 'Запись включена' : 'Запись выключена'}
            </span>
            <div className="flex items-center space-x-1">
              <div className={`w-2 h-2 rounded-full ${statusColorClass}`}></div>
              <span className="text-gray-600 dark:text-gray-300">
                {formatStatus(camera.status)}
              </span>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default CameraCard;
