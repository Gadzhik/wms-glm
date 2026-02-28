import { useState, useEffect } from 'react';
import { Eye, Video, MapPin, AlertCircle } from 'lucide-react';
import { formatDateTime, formatRelativeTime } from '@utils/format';
import { formatEventType, getEventTypeColor } from '@utils/format';
import { eventsAPI } from '@api/events';

const EventCard = ({ event, cameraName, selected, onSelect, onMarkAsViewed }) => {
  const [thumbnail, setThumbnail] = useState(null);
  const [isLoadingThumbnail, setIsLoadingThumbnail] = useState(false);

  useEffect(() => {
    if (!event.viewed) {
      loadThumbnail();
    }
  }, [event.id]);

  const loadThumbnail = async () => {
    setIsLoadingThumbnail(true);
    try {
      const blob = await eventsAPI.getEventThumbnail(event.id);
      const url = URL.createObjectURL(blob);
      setThumbnail(url);
    } catch (error) {
      console.error('Ошибка загрузки превью:', error);
    } finally {
      setIsLoadingThumbnail(false);
    }
  };

  const eventTypeColor = getEventTypeColor(event.type);
  const eventTypeLabel = formatEventType(event.type);

  const colorClass = {
    warning: 'bg-warning-100 dark:bg-warning-900/30 text-warning-700 dark:text-warning-300',
    danger: 'bg-danger-100 dark:bg-danger-900/30 text-danger-700 dark:text-danger-300',
    primary: 'bg-primary-100 dark:bg-primary-900/30 text-primary-700 dark:text-primary-300',
    info: 'bg-info-100 dark:bg-info-900/30 text-info-700 dark:text-info-300',
    default: 'bg-gray-100 dark:bg-gray-700 text-gray-700 dark:text-gray-300',
  }[eventTypeColor];

  return (
    <div
      className={`bg-white dark:bg-gray-800 rounded-lg shadow-md overflow-hidden hover:shadow-lg transition-shadow ${
        !event.viewed ? 'border-l-4 border-l-primary-500' : ''
      }`}
    >
      <div className="flex">
        {/* Превью */}
        <div className="relative w-48 flex-shrink-0 bg-gray-900">
          {isLoadingThumbnail ? (
            <div className="absolute inset-0 flex items-center justify-center">
              <div className="w-6 h-6 border-2 border-primary-500 border-t-transparent rounded-full animate-spin"></div>
            </div>
          ) : thumbnail ? (
            <img
              src={thumbnail}
              alt={eventTypeLabel}
              className="w-full h-full object-cover"
            />
          ) : (
            <div className="absolute inset-0 flex items-center justify-center text-gray-600">
              <Video className="w-12 h-12" />
            </div>
          )}

          {/* Тип события */}
          <div className="absolute top-2 left-2">
            <span className={`px-2 py-1 text-xs rounded-full ${colorClass}`}>
              {eventTypeLabel}
            </span>
          </div>
        </div>

        {/* Информация */}
        <div className="flex-1 p-4">
          <div className="flex items-start justify-between">
            <div className="flex-1">
              {/* Заголовок */}
              <div className="flex items-center space-x-2 mb-2">
                {!event.viewed && (
                  <div className="w-2 h-2 bg-primary-500 rounded-full"></div>
                )}
                <h3 className="font-semibold text-gray-900 dark:text-white">
                  {event.title || eventTypeLabel}
                </h3>
              </div>

              {/* Описание */}
              {event.description && (
                <p className="text-sm text-gray-600 dark:text-gray-400 mb-2">
                  {event.description}
                </p>
              )}

              {/* Информация */}
              <div className="flex flex-wrap items-center gap-4 text-sm text-gray-500 dark:text-gray-400">
                <div className="flex items-center space-x-1">
                  <MapPin className="w-4 h-4" />
                  <span>{cameraName}</span>
                </div>
                <div>
                  <span>{formatDateTime(event.timestamp)}</span>
                  <span className="mx-2">•</span>
                  <span>{formatRelativeTime(event.timestamp)}</span>
                </div>
              </div>

              {/* Дополнительная информация */}
              {event.confidence !== undefined && (
                <div className="mt-2 text-sm text-gray-500 dark:text-gray-400">
                  Уверенность: {(event.confidence * 100).toFixed(1)}%
                </div>
              )}
            </div>

            {/* Чекбокс */}
            <div className="ml-4">
              <input
                type="checkbox"
                checked={selected}
                onChange={onSelect}
                className="w-5 h-5 text-primary-500 border-gray-300 rounded focus:ring-primary-500"
              />
            </div>
          </div>

          {/* Кнопки действий */}
          <div className="flex items-center justify-between mt-4 pt-4 border-t border-gray-200 dark:border-gray-700">
            <div className="text-xs text-gray-500 dark:text-gray-400">
              ID: {event.id}
            </div>
            {!event.viewed && (
              <button
                onClick={onMarkAsViewed}
                className="flex items-center space-x-1 px-3 py-1.5 text-sm text-primary-600 hover:text-primary-900 dark:text-primary-400 dark:hover:text-primary-300 transition-colors"
              >
                <Eye className="w-4 h-4" />
                <span>Просмотреть</span>
              </button>
            )}
          </div>
        </div>
      </div>
    </div>
  );
};

export default EventCard;
