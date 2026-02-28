import { useState, useEffect } from 'react';
import { Search, Filter, Download, Trash2, Play } from 'lucide-react';
import { useRecordings } from '@hooks/useRecordings';
import { useCameras } from '@hooks/useCameras';
import { formatDateTime, formatDuration, formatFileSize } from '@utils/format';
import Loading from '@components/common/Loading';
import Error from '@components/common/Error';
import ConfirmDialog from '@components/common/ConfirmDialog';

const RecordingList = () => {
  const { recordings, isLoading, error, filters, setFilters, fetchRecordings, deleteRecording } = useRecordings();
  const { cameras } = useCameras();
  const [searchTerm, setSearchTerm] = useState('');
  const [cameraFilter, setCameraFilter] = useState('all');
  const [typeFilter, setTypeFilter] = useState('all');
  const [dateRange, setDateRange] = useState({ start: '', end: '' });
  const [showDeleteDialog, setShowDeleteDialog] = useState(false);
  const [recordingToDelete, setRecordingToDelete] = useState(null);

  useEffect(() => {
    loadRecordings();
  }, [searchTerm, cameraFilter, typeFilter, dateRange]);

  const loadRecordings = async () => {
    const params = {};
    if (searchTerm) params.search = searchTerm;
    if (cameraFilter !== 'all') params.camera_id = cameraFilter;
    if (typeFilter !== 'all') params.type = typeFilter;
    if (dateRange.start) params.start_date = dateRange.start;
    if (dateRange.end) params.end_date = dateRange.end;
    await fetchRecordings(params);
  };

  const handleDelete = async () => {
    if (recordingToDelete) {
      const result = await deleteRecording(recordingToDelete.id);
      if (result.success) {
        setShowDeleteDialog(false);
        setRecordingToDelete(null);
      }
    }
  };

  const confirmDelete = (recording) => {
    setRecordingToDelete(recording);
    setShowDeleteDialog(true);
  };

  const handlePlay = (recording) => {
    // TODO: Открывать плеер для записи
    console.log('Play recording:', recording.id);
  };

  const handleDownload = async (recording) => {
    // TODO: Скачивание записи
    console.log('Download recording:', recording.id);
  };

  const getCameraName = (cameraId) => {
    const camera = cameras.find((c) => c.id === cameraId);
    return camera?.name || 'Неизвестная камера';
  };

  if (isLoading && recordings.length === 0) {
    return (
      <div className="flex items-center justify-center h-64">
        <Loading size="lg" text="Загрузка записей..." />
      </div>
    );
  }

  if (error) {
    return <Error message={error} onRetry={loadRecordings} />;
  }

  return (
    <div className="space-y-6">
      {/* Заголовок */}
      <div>
        <h1 className="text-2xl font-bold text-gray-900 dark:text-white">
          Архив записей
        </h1>
        <p className="text-gray-600 dark:text-gray-400 mt-1">
          Всего записей: {recordings.length}
        </p>
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
            <option value="continuous">Непрерывные</option>
            <option value="motion">По движению</option>
            <option value="event">По событию</option>
            <option value="manual">Ручные</option>
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

      {/* Список записей */}
      {recordings.length === 0 ? (
        <div className="bg-white dark:bg-gray-800 rounded-lg shadow p-12 text-center">
          <div className="text-gray-400 dark:text-gray-500 mb-4">
            <Play className="w-16 h-16 mx-auto" />
          </div>
          <h3 className="text-lg font-medium text-gray-900 dark:text-white mb-2">
            Нет записей
          </h3>
          <p className="text-gray-600 dark:text-gray-400">
            Записи за выбранный период отсутствуют
          </p>
        </div>
      ) : (
        <div className="bg-white dark:bg-gray-800 rounded-lg shadow overflow-hidden">
          <table className="min-w-full divide-y divide-gray-200 dark:divide-gray-700">
            <thead className="bg-gray-50 dark:bg-gray-700">
              <tr>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-300 uppercase tracking-wider">
                  Камера
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-300 uppercase tracking-wider">
                  Время начала
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-300 uppercase tracking-wider">
                  Длительность
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-300 uppercase tracking-wider">
                  Размер
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-300 uppercase tracking-wider">
                  Тип
                </th>
                <th className="px-6 py-3 text-right text-xs font-medium text-gray-500 dark:text-gray-300 uppercase tracking-wider">
                  Действия
                </th>
              </tr>
            </thead>
            <tbody className="bg-white dark:bg-gray-800 divide-y divide-gray-200 dark:divide-gray-700">
              {recordings.map((recording) => (
                <tr key={recording.id} className="hover:bg-gray-50 dark:hover:bg-gray-700">
                  <td className="px-6 py-4 whitespace-nowrap">
                    <div className="text-sm font-medium text-gray-900 dark:text-white">
                      {getCameraName(recording.camera_id)}
                    </div>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap">
                    <div className="text-sm text-gray-900 dark:text-white">
                      {formatDateTime(recording.start_time)}
                    </div>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap">
                    <div className="text-sm text-gray-900 dark:text-white">
                      {formatDuration(recording.duration)}
                    </div>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap">
                    <div className="text-sm text-gray-900 dark:text-white">
                      {formatFileSize(recording.file_size)}
                    </div>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap">
                    <span className="px-2 py-1 text-xs rounded-full bg-primary-100 dark:bg-primary-900/30 text-primary-700 dark:text-primary-300">
                      {recording.type}
                    </span>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-right text-sm font-medium">
                    <div className="flex items-center justify-end space-x-2">
                      <button
                        onClick={() => handlePlay(recording)}
                        className="p-2 text-primary-600 hover:text-primary-900 dark:text-primary-400 dark:hover:text-primary-300"
                        title="Воспроизвести"
                      >
                        <Play className="w-4 h-4" />
                      </button>
                      <button
                        onClick={() => handleDownload(recording)}
                        className="p-2 text-gray-600 hover:text-gray-900 dark:text-gray-400 dark:hover:text-gray-300"
                        title="Скачать"
                      >
                        <Download className="w-4 h-4" />
                      </button>
                      <button
                        onClick={() => confirmDelete(recording)}
                        className="p-2 text-danger-600 hover:text-danger-900 dark:text-danger-400 dark:hover:text-danger-300"
                        title="Удалить"
                      >
                        <Trash2 className="w-4 h-4" />
                      </button>
                    </div>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}

      {/* Диалог подтверждения удаления */}
      <ConfirmDialog
        isOpen={showDeleteDialog}
        title="Удалить запись"
        message={`Вы уверены, что хотите удалить запись от ${recordingToDelete ? formatDateTime(recordingToDelete.start_time) : ''}?`}
        confirmText="Удалить"
        cancelText="Отмена"
        onConfirm={handleDelete}
        onCancel={() => {
          setShowDeleteDialog(false);
          setRecordingToDelete(null);
        }}
        type="danger"
      />
    </div>
  );
};

export default RecordingList;
