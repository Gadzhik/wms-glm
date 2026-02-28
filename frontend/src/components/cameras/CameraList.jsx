import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { Plus, Search, Filter } from 'lucide-react';
import { useCameras } from '@hooks/useCameras';
import { CAMERA_STATUS } from '@utils/constants';
import { formatStatus, getStatusColor } from '@utils/format';
import CameraCard from './CameraCard';
import Loading from '@components/common/Loading';
import Error from '@components/common/Error';

const CameraList = () => {
  const navigate = useNavigate();
  const {
    cameras,
    isLoading,
    error,
    filters,
    setFilters,
    clearFilters,
    getOnlineCameras,
    getOfflineCameras,
    getErrorCameras,
  } = useCameras();

  const [searchTerm, setSearchTerm] = useState('');
  const [statusFilter, setStatusFilter] = useState('all');

  useEffect(() => {
    setFilters({ search: searchTerm, status: statusFilter });
  }, [searchTerm, statusFilter, setFilters]);

  const handleAddCamera = () => {
    navigate('/cameras/new');
  };

  const handleSearch = (e) => {
    setSearchTerm(e.target.value);
  };

  const handleStatusFilter = (status) => {
    setStatusFilter(status);
  };

  const handleRetry = () => {
    window.location.reload();
  };

  if (isLoading && cameras.length === 0) {
    return (
      <div className="flex items-center justify-center h-64">
        <Loading size="lg" text="Загрузка камер..." />
      </div>
    );
  }

  if (error) {
    return <Error message={error} onRetry={handleRetry} />;
  }

  const onlineCount = getOnlineCameras().length;
  const offlineCount = getOfflineCameras().length;
  const errorCount = getErrorCameras().length;

  return (
    <div className="space-y-6">
      {/* Заголовок и кнопки */}
      <div className="flex flex-col sm:flex-row justify-between items-start sm:items-center gap-4">
        <div>
          <h1 className="text-2xl font-bold text-gray-900 dark:text-white">
            Камеры
          </h1>
          <p className="text-gray-600 dark:text-gray-400 mt-1">
            Всего: {cameras.length} | Онлайн: {onlineCount} | Офлайн: {offlineCount} | Ошибки: {errorCount}
          </p>
        </div>
        <button
          onClick={handleAddCamera}
          className="flex items-center space-x-2 px-4 py-2 bg-primary-500 hover:bg-primary-600 text-white rounded-lg transition-colors"
        >
          <Plus className="w-5 h-5" />
          <span>Добавить камеру</span>
        </button>
      </div>

      {/* Фильтры и поиск */}
      <div className="bg-white dark:bg-gray-800 rounded-lg shadow p-4">
        <div className="flex flex-col sm:flex-row gap-4">
          {/* Поиск */}
          <div className="flex-1 relative">
            <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 w-5 h-5 text-gray-400" />
            <input
              type="text"
              placeholder="Поиск по названию или описанию..."
              value={searchTerm}
              onChange={handleSearch}
              className="w-full pl-10 pr-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent bg-white dark:bg-gray-700 text-gray-900 dark:text-white"
            />
          </div>

          {/* Фильтр по статусу */}
          <div className="flex items-center space-x-2">
            <Filter className="w-5 h-5 text-gray-400" />
            <div className="flex space-x-2">
              <button
                onClick={() => handleStatusFilter('all')}
                className={`px-3 py-2 rounded-lg transition-colors ${
                  statusFilter === 'all'
                    ? 'bg-primary-500 text-white'
                    : 'bg-gray-100 dark:bg-gray-700 text-gray-700 dark:text-gray-300 hover:bg-gray-200 dark:hover:bg-gray-600'
                }`}
              >
                Все
              </button>
              <button
                onClick={() => handleStatusFilter('online')}
                className={`px-3 py-2 rounded-lg transition-colors ${
                  statusFilter === 'online'
                    ? 'bg-success-500 text-white'
                    : 'bg-gray-100 dark:bg-gray-700 text-gray-700 dark:text-gray-300 hover:bg-gray-200 dark:hover:bg-gray-600'
                }`}
              >
                Онлайн
              </button>
              <button
                onClick={() => handleStatusFilter('offline')}
                className={`px-3 py-2 rounded-lg transition-colors ${
                  statusFilter === 'offline'
                    ? 'bg-danger-500 text-white'
                    : 'bg-gray-100 dark:bg-gray-700 text-gray-700 dark:text-gray-300 hover:bg-gray-200 dark:hover:bg-gray-600'
                }`}
              >
                Офлайн
              </button>
              <button
                onClick={() => handleStatusFilter('error')}
                className={`px-3 py-2 rounded-lg transition-colors ${
                  statusFilter === 'error'
                    ? 'bg-warning-500 text-white'
                    : 'bg-gray-100 dark:bg-gray-700 text-gray-700 dark:text-gray-300 hover:bg-gray-200 dark:hover:bg-gray-600'
                }`}
              >
                Ошибки
              </button>
            </div>
          </div>
        </div>
      </div>

      {/* Список камер */}
      {cameras.length === 0 ? (
        <div className="bg-white dark:bg-gray-800 rounded-lg shadow p-12 text-center">
          <div className="text-gray-400 dark:text-gray-500 mb-4">
            <svg
              className="w-16 h-16 mx-auto"
              fill="none"
              stroke="currentColor"
              viewBox="0 0 24 24"
            >
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                strokeWidth={2}
                d="M15 10l4.553-2.276A1 1 0 0121 8.618v6.764a1 1 0 01-1.447.894L15 14M5 18h8a2 2 0 002-2V8a2 2 0 00-2-2H5a2 2 0 00-2 2v8a2 2 0 002 2z"
              />
            </svg>
          </div>
          <h3 className="text-lg font-medium text-gray-900 dark:text-white mb-2">
            Нет камер
          </h3>
          <p className="text-gray-600 dark:text-gray-400 mb-6">
            Добавьте первую камеру для начала работы
          </p>
          <button
            onClick={handleAddCamera}
            className="inline-flex items-center space-x-2 px-6 py-3 bg-primary-500 hover:bg-primary-600 text-white rounded-lg transition-colors"
          >
            <Plus className="w-5 h-5" />
            <span>Добавить камеру</span>
          </button>
        </div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-6">
          {cameras.map((camera) => (
            <CameraCard key={camera.id} camera={camera} />
          ))}
        </div>
      )}
    </div>
  );
};

export default CameraList;
