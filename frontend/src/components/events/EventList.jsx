import { useState, useEffect } from 'react';
import { Search, Filter, Eye, EyeOff } from 'lucide-react';
import { useEvents } from '@hooks/useEvents';
import { useCameras } from '@hooks/useCameras';
import { formatDateTime, formatRelativeTime } from '@utils/format';
import { formatEventType, getEventTypeColor } from '@utils/format';
import { EVENT_TYPES } from '@utils/constants';
import Loading from '@components/common/Loading';
import Error from '@components/common/Error';
import EventCard from './EventCard';

const EventList = () => {
  const { events, isLoading, error, fetchEvents, markAsViewed, markManyAsViewed } = useEvents();
  const { cameras } = useCameras();
  const [searchTerm, setSearchTerm] = useState('');
  const [cameraFilter, setCameraFilter] = useState('all');
  const [typeFilter, setTypeFilter] = useState('all');
  const [viewedFilter, setViewedFilter] = useState('all');
  const [dateRange, setDateRange] = useState({ start: '', end: '' });
  const [selectedEvents, setSelectedEvents] = useState(new Set());

  useEffect(() => {
    loadEvents();
  }, [searchTerm, cameraFilter, typeFilter, viewedFilter, dateRange]);

  const loadEvents = async () => {
    const params = {};
    if (searchTerm) params.search = searchTerm;
    if (cameraFilter !== 'all') params.camera_id = cameraFilter;
    if (typeFilter !== 'all') params.event_type = typeFilter;
    if (viewedFilter !== 'all') params.viewed = viewedFilter === 'viewed';
    if (dateRange.start) params.start_date = dateRange.start;
    if (dateRange.end) params.end_date = dateRange.end;
    await fetchEvents(params);
  };

  const handleEventSelect = (eventId) => {
    const newSelected = new Set(selectedEvents);
    if (newSelected.has(eventId)) {
      newSelected.delete(eventId);
    } else {
      newSelected.add(eventId);
    }
    setSelectedEvents(newSelected);
  };

  const handleSelectAll = () => {
    if (selectedEvents.size === events.length) {
      setSelectedEvents(new Set());
    } else {
      setSelectedEvents(new Set(events.map((e) => e.id)));
    }
  };

  const handleMarkAsViewed = async (eventId) => {
    await markAsViewed(eventId);
  };

  const handleMarkSelectedAsViewed = async () => {
    if (selectedEvents.size > 0) {
      await markManyAsViewed(Array.from(selectedEvents));
      setSelectedEvents(new Set());
    }
  };

  const getCameraName = (cameraId) => {
    const camera = cameras.find((c) => c.id === cameraId);
    return camera?.name || 'Неизвестная камера';
  };

  const unviewedCount = events.filter((e) => !e.viewed).length;

  if (isLoading && events.length === 0) {
    return (
      <div className="flex items-center justify-center h-64">
        <Loading size="lg" text="Загрузка событий..." />
      </div>
    );
  }

  if (error) {
    return <Error message={error} onRetry={loadEvents} />;
  }

  return (
    <div className="space-y-6">
      {/* Заголовок */}
      <div className="flex flex-col sm:flex-row justify-between items-start sm:items-center gap-4">
        <div>
          <h1 className="text-2xl font-bold text-gray-900 dark:text-white">
            События
          </h1>
          <p className="text-gray-600 dark:text-gray-400 mt-1">
            Всего: {events.length} | Непросмотренных: {unviewedCount}
          </p>
        </div>
        {selectedEvents.size > 0 && (
          <button
            onClick={handleMarkSelectedAsViewed}
            className="flex items-center space-x-2 px-4 py-2 bg-primary-500 hover:bg-primary-600 text-white rounded-lg transition-colors"
          >
            <Eye className="w-4 h-4" />
            <span>Отметить как просмотренные ({selectedEvents.size})</span>
          </button>
        )}
      </div>

      {/* Фильтры */}
      <div className="bg-white dark:bg-gray-800 rounded-lg shadow p-4">
        <div className="flex flex-col lg:flex-row gap-4">
          {/* Поиск */}
          <div className="flex-1 relative">
            <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 w-5 h-5 text-gray-400" />
            <input
              type="text"
              placeholder="Поиск..."
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              className="w-full pl-10 pr-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent bg-white dark:bg-gray-700 text-gray-900 dark:text-white"
            />
          </div>

          {/* Фильтр по камере */}
          <select
            value={cameraFilter}
            onChange={(e) => setCameraFilter(e.target.value)}
            className="px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent bg-white dark:bg-gray-700 text-gray-900 dark:text-white"
          >
            <option value="all">Все камеры</option>
            {cameras.map((camera) => (
              <option key={camera.id} value={camera.id}>
                {camera.name}
              </option>
            ))}
          </select>

          {/* Фильтр по типу */}
          <select
            value={typeFilter}
            onChange={(e) => setTypeFilter(e.target.value)}
            className="px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent bg-white dark:bg-gray-700 text-gray-900 dark:text-white"
          >
            <option value="all">Все типы</option>
            <option value={EVENT_TYPES.MOTION}>Движение</option>
            <option value={EVENT_TYPES.INTRUSION}>Проникновение</option>
            <option value={EVENT_TYPES.LINE_CROSS}>Пересечение линии</option>
            <option value={EVENT_TYPES.FACE_DETECTION}>Обнаружение лица</option>
            <option value={EVENT_TYPES.LICENSE_PLATE}>Распознавание номера</option>
          </select>

          {/* Фильтр по просмотру */}
          <select
            value={viewedFilter}
            onChange={(e) => setViewedFilter(e.target.value)}
            className="px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent bg-white dark:bg-gray-700 text-gray-900 dark:text-white"
          >
            <option value="all">Все</option>
            <option value="unviewed">Непросмотренные</option>
            <option value="viewed">Просмотренные</option>
          </select>

          {/* Диапазон дат */}
          <div className="flex space-x-2">
            <input
              type="date"
              value={dateRange.start}
              onChange={(e) => setDateRange({ ...dateRange, start: e.target.value })}
              className="px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent bg-white dark:bg-gray-700 text-gray-900 dark:text-white"
            />
            <input
              type="date"
              value={dateRange.end}
              onChange={(e) => setDateRange({ ...dateRange, end: e.target.value })}
              className="px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent bg-white dark:bg-gray-700 text-gray-900 dark:text-white"
            />
          </div>
        </div>
      </div>

      {/* Список событий */}
      {events.length === 0 ? (
        <div className="bg-white dark:bg-gray-800 rounded-lg shadow p-12 text-center">
          <div className="text-gray-400 dark:text-gray-500 mb-4">
            <Filter className="w-16 h-16 mx-auto" />
          </div>
          <h3 className="text-lg font-medium text-gray-900 dark:text-white mb-2">
            Нет событий
          </h3>
          <p className="text-gray-600 dark:text-gray-400">
            События за выбранный период отсутствуют
          </p>
        </div>
      ) : (
        <div className="space-y-4">
          {/* Выбрать все */}
          <label className="flex items-center space-x-2 text-sm text-gray-600 dark:text-gray-400">
            <input
              type="checkbox"
              checked={selectedEvents.size === events.length && events.length > 0}
              onChange={handleSelectAll}
              className="w-4 h-4 text-primary-500 border-gray-300 rounded focus:ring-primary-500"
            />
            <span>Выбрать все</span>
          </label>

          {/* Список */}
          {events.map((event) => (
            <EventCard
              key={event.id}
              event={event}
              cameraName={getCameraName(event.camera_id)}
              selected={selectedEvents.has(event.id)}
              onSelect={() => handleEventSelect(event.id)}
              onMarkAsViewed={() => handleMarkAsViewed(event.id)}
            />
          ))}
        </div>
      )}
    </div>
  );
};

export default EventList;
