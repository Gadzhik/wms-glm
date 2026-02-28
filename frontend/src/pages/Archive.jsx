import { useState } from 'react';
import { useSearchParams } from 'react-router-dom';
import { useCameras } from '@hooks/useCameras';
import RecordingList from '@components/recordings/RecordingList';
import Timeline from '@components/recordings/Timeline';
import RecordingPlayer from '@components/recordings/RecordingPlayer';
import { getStartOfDay, getEndOfDay } from '@utils/format';

const Archive = () => {
  const [searchParams] = useSearchParams();
  const view = searchParams.get('view') || 'list';
  const { cameras } = useCameras();
  const [selectedCamera, setSelectedCamera] = useState(null);
  const [selectedDate, setSelectedDate] = useState(new Date());
  const [selectedRecording, setSelectedRecording] = useState(null);

  const handleCameraChange = (cameraId) => {
    setSelectedCamera(cameraId);
  };

  const handleDateChange = (date) => {
    setSelectedDate(date);
  };

  const handleSegmentClick = (segment) => {
    setSelectedRecording(segment);
  };

  const handleExport = async (recordingId, startTime, endTime, format) => {
    // TODO: Реализовать экспорт
    console.log('Export:', recordingId, startTime, endTime, format);
  };

  if (view === 'play') {
    const recordingId = searchParams.get('recording');
    return (
      <div className="space-y-6">
        <h1 className="text-2xl font-bold text-gray-900 dark:text-white">
          Воспроизведение записи
        </h1>
        <RecordingPlayer
          recordingUrl={`/api/recordings/${recordingId}/play`}
          onExport={handleExport}
        />
      </div>
    );
  }

  if (view === 'timeline' && selectedCamera) {
    const startDate = getStartOfDay(selectedDate);
    const endDate = getEndOfDay(selectedDate);

    return (
      <div className="space-y-6">
        <div className="flex flex-col sm:flex-row justify-between items-start sm:items-center gap-4">
          <div>
            <h1 className="text-2xl font-bold text-gray-900 dark:text-white">
              Архив
            </h1>
            <p className="text-gray-600 dark:text-gray-400 mt-1">
              {selectedDate.toLocaleDateString('ru-RU')}
            </p>
          </div>

          <div className="flex items-center space-x-4">
            <select
              value={selectedCamera || ''}
              onChange={(e) => handleCameraChange(e.target.value || null)}
              className="px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent bg-white dark:bg-gray-700 text-gray-900 dark:text-white"
            >
              <option value="">Выберите камеру</option>
              {cameras.map((camera) => (
                <option key={camera.id} value={camera.id}>
                  {camera.name}
                </option>
              ))}
            </select>

            <input
              type="date"
              value={selectedDate.toISOString().split('T')[0]}
              onChange={(e) => handleDateChange(new Date(e.target.value))}
              className="px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent bg-white dark:bg-gray-700 text-gray-900 dark:text-white"
            />
          </div>
        </div>

        {selectedCamera && (
          <Timeline
            cameraId={selectedCamera}
            startDate={startDate}
            endDate={endDate}
            onSegmentClick={handleSegmentClick}
            selectedSegment={selectedRecording}
          />
        )}

        {selectedRecording && (
          <RecordingPlayer
            recordingUrl={`/api/recordings/${selectedRecording.id}/play`}
            startTime={selectedRecording.start_time}
            endTime={selectedRecording.end_time}
            onExport={handleExport}
          />
        )}
      </div>
    );
  }

  return <RecordingList />;
};

export default Archive;
