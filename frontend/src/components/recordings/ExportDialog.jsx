import { useState } from 'react';
import { Download, X } from 'lucide-react';
import { formatDateTime } from '@utils/format';

const ExportDialog = ({ isOpen, recording, onClose, onExport }) => {
  const [startTime, setStartTime] = useState('');
  const [endTime, setEndTime] = useState('');
  const [format, setFormat] = useState('mp4');
  const [isExporting, setIsExporting] = useState(false);

  useEffect(() => {
    if (recording && isOpen) {
      setStartTime(formatDateTime(recording.start_time, 'YYYY-MM-DDTHH:mm'));
      setEndTime(formatDateTime(recording.end_time, 'YYYY-MM-DDTHH:mm'));
    }
  }, [recording, isOpen]);

  const handleExport = async () => {
    if (!recording) return;

    setIsExporting(true);
    try {
      const result = await onExport(recording.id, startTime, endTime, format);
      if (result.success) {
        onClose();
      }
    } finally {
      setIsExporting(false);
    }
  };

  if (!isOpen || !recording) return null;

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center">
      {/* Overlay */}
      <div
        className="absolute inset-0 bg-black bg-opacity-50"
        onClick={onClose}
      ></div>

      {/* Dialog */}
      <div className="relative bg-white dark:bg-gray-800 rounded-lg shadow-xl max-w-md w-full mx-4 p-6">
        <div className="flex items-center justify-between mb-6">
          <h2 className="text-xl font-semibold text-gray-900 dark:text-white">
            Экспорт записи
          </h2>
          <button
            onClick={onClose}
            className="p-2 text-gray-400 hover:text-gray-600 dark:hover:text-gray-300 transition-colors"
          >
            <X className="w-5 h-5" />
          </button>
        </div>

        <div className="space-y-4">
          {/* Информация о записи */}
          <div className="bg-gray-50 dark:bg-gray-700 rounded-lg p-4">
            <p className="text-sm text-gray-600 dark:text-gray-400">
              <span className="font-medium">Камера:</span> {recording.camera_name || 'Неизвестно'}
            </p>
            <p className="text-sm text-gray-600 dark:text-gray-400">
              <span className="font-medium">Начало:</span> {formatDateTime(recording.start_time)}
            </p>
            <p className="text-sm text-gray-600 dark:text-gray-400">
              <span className="font-medium">Окончание:</span> {formatDateTime(recording.end_time)}
            </p>
          </div>

          {/* Время начала */}
          <div>
            <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
              Время начала
            </label>
            <input
              type="datetime-local"
              value={startTime}
              onChange={(e) => setStartTime(e.target.value)}
              className="w-full px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent bg-white dark:bg-gray-700 text-gray-900 dark:text-white"
            />
          </div>

          {/* Время окончания */}
          <div>
            <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
              Время окончания
            </label>
            <input
              type="datetime-local"
              value={endTime}
              onChange={(e) => setEndTime(e.target.value)}
              className="w-full px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent bg-white dark:bg-gray-700 text-gray-900 dark:text-white"
            />
          </div>

          {/* Формат */}
          <div>
            <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
              Формат
            </label>
            <select
              value={format}
              onChange={(e) => setFormat(e.target.value)}
              className="w-full px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent bg-white dark:bg-gray-700 text-gray-900 dark:text-white"
            >
              <option value="mp4">MP4</option>
              <option value="avi">AVI</option>
              <option value="mkv">MKV</option>
            </select>
          </div>
        </div>

        {/* Кнопки */}
        <div className="flex justify-end space-x-3 mt-6">
          <button
            onClick={onClose}
            disabled={isExporting}
            className="px-4 py-2 border border-gray-300 dark:border-gray-600 text-gray-700 dark:text-gray-300 rounded-lg hover:bg-gray-50 dark:hover:bg-gray-700 transition-colors disabled:opacity-50"
          >
            Отмена
          </button>
          <button
            onClick={handleExport}
            disabled={isExporting || !startTime || !endTime}
            className="flex items-center space-x-2 px-4 py-2 bg-primary-500 hover:bg-primary-600 text-white rounded-lg transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
          >
            {isExporting ? (
              <>
                <div className="w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin"></div>
                <span>Экспорт...</span>
              </>
            ) : (
              <>
                <Download className="w-4 h-4" />
                <span>Экспортировать</span>
              </>
            )}
          </button>
        </div>
      </div>
    </div>
  );
};

export default ExportDialog;
