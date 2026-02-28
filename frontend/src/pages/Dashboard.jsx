import { useEffect, useState } from 'react';
import { Video, AlertTriangle, HardDrive, Clock, TrendingUp } from 'lucide-react';
import { useCameras } from '@hooks/useCameras';
import { useEvents } from '@hooks/useEvents';
import { useRecordings } from '@hooks/useRecordings';
import { formatDateTime, formatFileSize, formatDuration } from '@utils/format';
import Loading from '@components/common/Loading';

const Dashboard = () => {
  const { cameras, getOnlineCameras, getOfflineCameras } = useCameras();
  const { events, fetchEvents } = useEvents();
  const { recordings, fetchRecordingStats } = useRecordings();
  const [stats, setStats] = useState(null);
  const [recentEvents, setRecentEvents] = useState([]);

  useEffect(() => {
    loadDashboardData();
  }, []);

  const loadDashboardData = async () => {
    try {
      // Загрузка статистики
      const statsData = await fetchRecordingStats();
      setStats(statsData);

      // Загрузка последних событий
      const eventsData = await fetchEvents({ limit: 10, sort: '-timestamp' });
      setRecentEvents(eventsData.items || []);
    } catch (error) {
      console.error('Ошибка загрузки данных дашборда:', error);
    }
  };

  const onlineCameras = getOnlineCameras();
  const offlineCameras = getOfflineCameras();
  const unviewedEvents = events.filter((e) => !e.viewed).length;

  return (
    <div className="space-y-6">
      {/* Заголовок */}
      <div>
        <h1 className="text-2xl font-bold text-gray-900 dark:text-white">
          Дашборд
        </h1>
        <p className="text-gray-600 dark:text-gray-400 mt-1">
          Обзор системы видеонаблюдения
        </p>
      </div>

      {/* Статистика */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        {/* Камеры */}
        <div className="bg-white dark:bg-gray-800 rounded-lg shadow p-6">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-gray-600 dark:text-gray-400">Камеры</p>
              <p className="text-2xl font-bold text-gray-900 dark:text-white mt-1">
                {cameras.length}
              </p>
              <p className="text-xs text-gray-500 dark:text-gray-400 mt-1">
                {onlineCameras.length} онлайн • {offlineCameras.length} офлайн
              </p>
            </div>
            <div className="p-3 bg-primary-100 dark:bg-primary-900/30 rounded-lg">
              <Video className="w-6 h-6 text-primary-600 dark:text-primary-400" />
            </div>
          </div>
        </div>

        {/* События */}
        <div className="bg-white dark:bg-gray-800 rounded-lg shadow p-6">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-gray-600 dark:text-gray-400">События</p>
              <p className="text-2xl font-bold text-gray-900 dark:text-white mt-1">
                {events.length}
              </p>
              <p className="text-xs text-gray-500 dark:text-gray-400 mt-1">
                {unviewedEvents} непросмотренных
              </p>
            </div>
            <div className="p-3 bg-warning-100 dark:bg-warning-900/30 rounded-lg">
              <AlertTriangle className="w-6 h-6 text-warning-600 dark:text-warning-400" />
            </div>
          </div>
        </div>

        {/* Записи */}
        <div className="bg-white dark:bg-gray-800 rounded-lg shadow p-6">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-gray-600 dark:text-gray-400">Записи</p>
              <p className="text-2xl font-bold text-gray-900 dark:text-white mt-1">
                {recordings.length}
              </p>
              <p className="text-xs text-gray-500 dark:text-gray-400 mt-1">
                {stats ? formatFileSize(stats.totalSize) : '-'}
              </p>
            </div>
            <div className="p-3 bg-success-100 dark:bg-success-900/30 rounded-lg">
              <HardDrive className="w-6 h-6 text-success-600 dark:text-success-400" />
            </div>
          </div>
        </div>

        {/* Время работы */}
        <div className="bg-white dark:bg-gray-800 rounded-lg shadow p-6">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-gray-600 dark:text-gray-400">Время работы</p>
              <p className="text-2xl font-bold text-gray-900 dark:text-white mt-1">
                {stats ? formatDuration(stats.totalDuration) : '-'}
              </p>
              <p className="text-xs text-gray-500 dark:text-gray-400 mt-1">
                Общая длительность
              </p>
            </div>
            <div className="p-3 bg-info-100 dark:bg-info-900/30 rounded-lg">
              <Clock className="w-6 h-6 text-info-600 dark:text-info-400" />
            </div>
          </div>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Последние события */}
        <div className="bg-white dark:bg-gray-800 rounded-lg shadow p-6">
          <div className="flex items-center justify-between mb-4">
            <h2 className="text-lg font-semibold text-gray-900 dark:text-white">
              Последние события
            </h2>
            <TrendingUp className="w-5 h-5 text-gray-400" />
          </div>
          {recentEvents.length === 0 ? (
            <p className="text-center text-gray-500 dark:text-gray-400 py-8">
              Нет событий
            </p>
          ) : (
            <div className="space-y-3">
              {recentEvents.slice(0, 5).map((event) => (
                <div
                  key={event.id}
                  className="flex items-center justify-between p-3 bg-gray-50 dark:bg-gray-700 rounded-lg"
                >
                  <div className="flex-1">
                    <p className="font-medium text-gray-900 dark:text-white">
                      {event.title || event.type}
                    </p>
                    <p className="text-sm text-gray-600 dark:text-gray-400">
                      {formatDateTime(event.timestamp)}
                    </p>
                  </div>
                  {!event.viewed && (
                    <div className="w-2 h-2 bg-primary-500 rounded-full"></div>
                  )}
                </div>
              ))}
            </div>
          )}
        </div>

        {/* Статус камер */}
        <div className="bg-white dark:bg-gray-800 rounded-lg shadow p-6">
          <h2 className="text-lg font-semibold text-gray-900 dark:text-white mb-4">
            Статус камер
          </h2>
          {cameras.length === 0 ? (
            <p className="text-center text-gray-500 dark:text-gray-400 py-8">
              Нет камер
            </p>
          ) : (
            <div className="space-y-3">
              {cameras.slice(0, 5).map((camera) => (
                <div
                  key={camera.id}
                  className="flex items-center justify-between p-3 bg-gray-50 dark:bg-gray-700 rounded-lg"
                >
                  <div className="flex-1">
                    <p className="font-medium text-gray-900 dark:text-white">
                      {camera.name}
                    </p>
                    <p className="text-sm text-gray-600 dark:text-gray-400">
                      {camera.location || 'Не указано'}
                    </p>
                  </div>
                  <div
                    className={`w-3 h-3 rounded-full ${
                      camera.status === 'online'
                        ? 'bg-success-500'
                        : camera.status === 'offline'
                        ? 'bg-danger-500'
                        : 'bg-warning-500'
                    }`}
                  ></div>
                </div>
              ))}
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default Dashboard;
