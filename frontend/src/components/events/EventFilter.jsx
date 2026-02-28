import { useState } from 'react';
import { Filter, X } from 'lucide-react';
import { EVENT_TYPES } from '@utils/constants';

const EventFilter = ({ filters, onFilterChange, onClearFilters }) => {
  const [isExpanded, setIsExpanded] = useState(false);

  const handleFilterChange = (key, value) => {
    onFilterChange(key, value);
  };

  const handleClear = () => {
    onClearFilters();
  };

  const hasActiveFilters =
    filters.cameraId ||
    filters.eventType !== 'all' ||
    filters.viewed !== 'all' ||
    filters.startDate ||
    filters.endDate;

  return (
    <div className="bg-white dark:bg-gray-800 rounded-lg shadow p-4">
      <div className="flex items-center justify-between mb-4">
        <div className="flex items-center space-x-2">
          <Filter className="w-5 h-5 text-gray-600 dark:text-gray-400" />
          <h3 className="font-semibold text-gray-900 dark:text-white">Фильтры</h3>
          {hasActiveFilters && (
            <button
              onClick={handleClear}
              className="flex items-center space-x-1 text-sm text-primary-600 hover:text-primary-900 dark:text-primary-400 dark:hover:text-primary-300"
            >
              <X className="w-4 h-4" />
              <span>Очистить</span>
            </button>
          )}
        </div>
        <button
          onClick={() => setIsExpanded(!isExpanded)}
          className="text-gray-600 dark:text-gray-400 hover:text-gray-900 dark:hover:text-white transition-colors"
        >
          {isExpanded ? 'Свернуть' : 'Развернуть'}
        </button>
      </div>

      {isExpanded && (
        <div className="space-y-4">
          {/* Тип события */}
          <div>
            <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
              Тип события
            </label>
            <select
              value={filters.eventType || 'all'}
              onChange={(e) => handleFilterChange('eventType', e.target.value)}
              className="w-full px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent bg-white dark:bg-gray-700 text-gray-900 dark:text-white"
            >
              <option value="all">Все типы</option>
              <option value={EVENT_TYPES.MOTION}>Движение</option>
              <option value={EVENT_TYPES.INTRUSION}>Проникновение</option>
              <option value={EVENT_TYPES.LINE_CROSS}>Пересечение линии</option>
              <option value={EVENT_TYPES.OBJECT_LEFT}>Оставленный объект</option>
              <option value={EVENT_TYPES.OBJECT_REMOVED}>Удаленный объект</option>
              <option value={EVENT_TYPES.FACE_DETECTION}>Обнаружение лица</option>
              <option value={EVENT_TYPES.LICENSE_PLATE}>Распознавание номера</option>
              <option value={EVENT_TYPES.AUDIO_DETECTION}>Звуковое событие</option>
            </select>
          </div>

          {/* Камера */}
          <div>
            <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
              Камера
            </label>
            <select
              value={filters.cameraId || 'all'}
              onChange={(e) => handleFilterChange('cameraId', e.target.value === 'all' ? null : e.target.value)}
              className="w-full px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent bg-white dark:bg-gray-700 text-gray-900 dark:text-white"
            >
              <option value="all">Все камеры</option>
              {/* TODO: Добавить список камер */}
            </select>
          </div>

          {/* Просмотренные */}
          <div>
            <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
              Статус просмотра
            </label>
            <select
              value={filters.viewed || 'all'}
              onChange={(e) => handleFilterChange('viewed', e.target.value === 'all' ? null : e.target.value === 'viewed')}
              className="w-full px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent bg-white dark:bg-gray-700 text-gray-900 dark:text-white"
            >
              <option value="all">Все</option>
              <option value="false">Непросмотренные</option>
              <option value="true">Просмотренные</option>
            </select>
          </div>

          {/* Диапазон дат */}
          <div>
            <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
              Диапазон дат
            </label>
            <div className="flex space-x-2">
              <input
                type="date"
                value={filters.startDate || ''}
                onChange={(e) => handleFilterChange('startDate', e.target.value)}
                className="flex-1 px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent bg-white dark:bg-gray-700 text-gray-900 dark:text-white"
              />
              <input
                type="date"
                value={filters.endDate || ''}
                onChange={(e) => handleFilterChange('endDate', e.target.value)}
                className="flex-1 px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent bg-white dark:bg-gray-700 text-gray-900 dark:text-white"
              />
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default EventFilter;
