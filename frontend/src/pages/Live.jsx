import { useState } from 'react';
import { useSearchParams } from 'react-router-dom';
import { useCameras } from '@hooks/useCameras';
import { Grid, List } from 'lucide-react';
import LiveStream from '@components/streams/LiveStream';
import Loading from '@components/common/Loading';

const Live = () => {
  const [searchParams] = useSearchParams();
  const cameraId = searchParams.get('camera');
  const { cameras, isLoading } = useCameras();
  const [viewMode, setViewMode] = useState('grid');

  if (isLoading) {
    return (
      <div className="flex items-center justify-center h-64">
        <Loading size="lg" text="Загрузка камер..." />
      </div>
    );
  }

  const displayCameras = cameraId
    ? cameras.filter((c) => c.id === cameraId)
    : cameras.filter((c) => c.status === 'online');

  return (
    <div className="space-y-6">
      {/* Заголовок */}
      <div className="flex flex-col sm:flex-row justify-between items-start sm:items-center gap-4">
        <div>
          <h1 className="text-2xl font-bold text-gray-900 dark:text-white">
            Live просмотр
          </h1>
          <p className="text-gray-600 dark:text-gray-400 mt-1">
            {displayCameras.length} камер онлайн
          </p>
        </div>

        <div className="flex items-center space-x-2">
          <button
            onClick={() => setViewMode('grid')}
            className={`p-2 rounded-lg transition-colors ${
              viewMode === 'grid'
                ? 'bg-primary-500 text-white'
                : 'bg-gray-100 dark:bg-gray-700 text-gray-700 dark:text-gray-300'
            }`}
            title="Сетка"
          >
            <Grid className="w-5 h-5" />
          </button>
          <button
            onClick={() => setViewMode('list')}
            className={`p-2 rounded-lg transition-colors ${
              viewMode === 'list'
                ? 'bg-primary-500 text-white'
                : 'bg-gray-100 dark:bg-gray-700 text-gray-700 dark:text-gray-300'
            }`}
            title="Список"
          >
            <List className="w-5 h-5" />
          </button>
        </div>
      </div>

      {/* Список камер */}
      {displayCameras.length === 0 ? (
        <div className="bg-white dark:bg-gray-800 rounded-lg shadow p-12 text-center">
          <p className="text-gray-600 dark:text-gray-400">
            {cameraId ? 'Камера не найдена или офлайн' : 'Нет онлайн камер'}
          </p>
        </div>
      ) : (
        <div
          className={
            viewMode === 'grid'
              ? 'grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-4'
              : 'space-y-4'
          }
        >
          {displayCameras.map((camera) => (
            <div key={camera.id} className="bg-white dark:bg-gray-800 rounded-lg shadow overflow-hidden">
              <LiveStream cameraId={camera.id} />
              <div className="p-3">
                <h3 className="font-medium text-gray-900 dark:text-white">
                  {camera.name}
                </h3>
                <p className="text-sm text-gray-600 dark:text-gray-400">
                  {camera.location || 'Не указано'}
                </p>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
};

export default Live;
