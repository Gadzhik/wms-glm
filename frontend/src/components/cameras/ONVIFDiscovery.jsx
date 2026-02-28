import { useState } from 'react';
import { Search, RefreshCw, Plus } from 'lucide-react';
import { camerasAPI } from '@api/cameras';
import Loading from '@components/common/Loading';

const ONVIFDiscovery = ({ onCameraSelect }) => {
  const [isScanning, setIsScanning] = useState(false);
  const [discoveredCameras, setDiscoveredCameras] = useState([]);
  const [scanParams, setScanParams] = useState({
    ip_range: '192.168.1.0/24',
    port: 80,
    timeout: 5,
  });

  const handleScan = async () => {
    setIsScanning(true);
    setDiscoveredCameras([]);
    try {
      const result = await camerasAPI.discoverONVIF(scanParams);
      setDiscoveredCameras(result.cameras || []);
    } catch (error) {
      console.error('Ошибка сканирования:', error);
    } finally {
      setIsScanning(false);
    }
  };

  const handleAddCamera = (camera) => {
    if (onCameraSelect) {
      onCameraSelect(camera);
    }
  };

  return (
    <div className="space-y-6">
      {/* Параметры сканирования */}
      <div className="bg-white dark:bg-gray-800 rounded-lg shadow p-6">
        <h2 className="text-lg font-semibold text-gray-900 dark:text-white mb-4">
          Параметры сканирования
        </h2>

        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
              IP диапазон
            </label>
            <input
              type="text"
              value={scanParams.ip_range}
              onChange={(e) =>
                setScanParams({ ...scanParams, ip_range: e.target.value })
              }
              className="w-full px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent bg-white dark:bg-gray-700 text-gray-900 dark:text-white"
              placeholder="192.168.1.0/24"
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
              Порт
            </label>
            <input
              type="number"
              value={scanParams.port}
              onChange={(e) =>
                setScanParams({ ...scanParams, port: parseInt(e.target.value) })
              }
              className="w-full px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent bg-white dark:bg-gray-700 text-gray-900 dark:text-white"
              min="1"
              max="65535"
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
              Таймаут (сек)
            </label>
            <input
              type="number"
              value={scanParams.timeout}
              onChange={(e) =>
                setScanParams({ ...scanParams, timeout: parseInt(e.target.value) })
              }
              className="w-full px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent bg-white dark:bg-gray-700 text-gray-900 dark:text-white"
              min="1"
              max="60"
            />
          </div>
        </div>

        <div className="mt-4 flex justify-end">
          <button
            onClick={handleScan}
            disabled={isScanning}
            className="flex items-center space-x-2 px-6 py-2 bg-primary-500 hover:bg-primary-600 text-white rounded-lg transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
          >
            {isScanning ? (
              <Loading size="sm" />
            ) : (
              <Search className="w-5 h-5" />
            )}
            <span>{isScanning ? 'Сканирование...' : 'Сканировать'}</span>
          </button>
        </div>
      </div>

      {/* Результаты сканирования */}
      {discoveredCameras.length > 0 && (
        <div className="bg-white dark:bg-gray-800 rounded-lg shadow p-6">
          <div className="flex items-center justify-between mb-4">
            <h2 className="text-lg font-semibold text-gray-900 dark:text-white">
              Найденные камеры ({discoveredCameras.length})
            </h2>
            <button
              onClick={handleScan}
              disabled={isScanning}
              className="flex items-center space-x-2 px-4 py-2 bg-gray-100 dark:bg-gray-700 hover:bg-gray-200 dark:hover:bg-gray-600 text-gray-700 dark:text-gray-300 rounded-lg transition-colors"
            >
              <RefreshCw className="w-4 h-4" />
              <span>Обновить</span>
            </button>
          </div>

          <div className="space-y-4">
            {discoveredCameras.map((camera, index) => (
              <div
                key={index}
                className="border border-gray-200 dark:border-gray-700 rounded-lg p-4 hover:bg-gray-50 dark:hover:bg-gray-700 transition-colors"
              >
                <div className="flex items-start justify-between">
                  <div className="flex-1">
                    <h3 className="font-medium text-gray-900 dark:text-white">
                      {camera.name || `Камера ${index + 1}`}
                    </h3>
                    <p className="text-sm text-gray-600 dark:text-gray-400 mt-1">
                      {camera.ip}:{camera.port}
                    </p>
                    {camera.manufacturer && (
                      <p className="text-xs text-gray-500 dark:text-gray-400 mt-1">
                        {camera.manufacturer} {camera.model}
                      </p>
                    )}
                    {camera.location && (
                      <p className="text-xs text-gray-500 dark:text-gray-400 mt-1">
                        {camera.location}
                      </p>
                    )}
                  </div>
                  <button
                    onClick={() => handleAddCamera(camera)}
                    className="flex items-center space-x-2 px-4 py-2 bg-primary-500 hover:bg-primary-600 text-white rounded-lg transition-colors"
                  >
                    <Plus className="w-4 h-4" />
                    <span>Добавить</span>
                  </button>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {discoveredCameras.length === 0 && !isScanning && (
        <div className="bg-white dark:bg-gray-800 rounded-lg shadow p-12 text-center">
          <div className="text-gray-400 dark:text-gray-500 mb-4">
            <Search className="w-16 h-16 mx-auto" />
          </div>
          <h3 className="text-lg font-medium text-gray-900 dark:text-white mb-2">
            Камеры не найдены
          </h3>
          <p className="text-gray-600 dark:text-gray-400">
            Запустите сканирование для поиска ONVIF камер в сети
          </p>
        </div>
      )}
    </div>
  );
};

export default ONVIFDiscovery;
