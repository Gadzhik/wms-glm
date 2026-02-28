import { useState, useEffect, useRef } from 'react';
import { formatDateTime, formatTimelineTime } from '@utils/format';
import Loading from '@components/common/Loading';

const Timeline = ({ cameraId, startDate, endDate, onSegmentClick, selectedSegment }) => {
  const [timeline, setTimeline] = useState([]);
  const [isLoading, setIsLoading] = useState(true);
  const [hoveredSegment, setHoveredSegment] = useState(null);
  const containerRef = useRef(null);

  useEffect(() => {
    loadTimeline();
  }, [cameraId, startDate, endDate]);

  const loadTimeline = async () => {
    setIsLoading(true);
    try {
      // TODO: Загрузка таймлайна с API
      // const data = await recordingsAPI.getTimeline(cameraId, startDate, endDate);
      // setTimeline(data.segments || []);
      
      // Демо данные
      const segments = generateDemoSegments(startDate, endDate);
      setTimeline(segments);
    } catch (error) {
      console.error('Ошибка загрузки таймлайна:', error);
    } finally {
      setIsLoading(false);
    }
  };

  const generateDemoSegments = (start, end) => {
    const segments = [];
    const startTime = new Date(start).getTime();
    const endTime = new Date(end).getTime();
    const dayDuration = endTime - startTime;

    for (let i = 0; i < 24; i++) {
      const segmentStart = startTime + (dayDuration / 24) * i;
      const segmentEnd = segmentStart + (dayDuration / 24) * 0.8;
      
      if (Math.random() > 0.3) {
        segments.push({
          id: `segment-${i}`,
          start_time: new Date(segmentStart).toISOString(),
          end_time: new Date(segmentEnd).toISOString(),
          camera_id: cameraId,
          type: Math.random() > 0.5 ? 'continuous' : 'motion',
        });
      }
    }
    return segments;
  };

  const handleSegmentClick = (segment) => {
    if (onSegmentClick) {
      onSegmentClick(segment);
    }
  };

  const handleSegmentHover = (segment) => {
    setHoveredSegment(segment);
  };

  const getSegmentStyle = (segment) => {
    const totalDuration = new Date(endDate).getTime() - new Date(startDate).getTime();
    const segmentStart = new Date(segment.start_time).getTime();
    const segmentEnd = new Date(segment.end_time).getTime();
    const startOffset = ((segmentStart - new Date(startDate).getTime()) / totalDuration) * 100;
    const width = ((segmentEnd - segmentStart) / totalDuration) * 100;

    const isSelected = selectedSegment?.id === segment.id;
    const isHovered = hoveredSegment?.id === segment.id;

    const colorClass = segment.type === 'continuous' 
      ? 'bg-primary-500' 
      : 'bg-success-500';

    return {
      left: `${startOffset}%`,
      width: `${width}%`,
      opacity: isSelected ? 1 : isHovered ? 0.8 : 0.6,
    };
  };

  if (isLoading) {
    return (
      <div className="flex items-center justify-center h-32">
        <Loading size="md" text="Загрузка таймлайна..." />
      </div>
    );
  }

  return (
    <div className="space-y-4">
      {/* Заголовок */}
      <div className="flex items-center justify-between">
        <h3 className="text-lg font-semibold text-gray-900 dark:text-white">
          Таймлайн
        </h3>
        <div className="text-sm text-gray-600 dark:text-gray-400">
          {formatDateTime(startDate)} - {formatDateTime(endDate)}
        </div>
      </div>

      {/* Таймлайн */}
      <div
        ref={containerRef}
        className="relative h-16 bg-gray-200 dark:bg-gray-700 rounded-lg overflow-hidden cursor-pointer"
      >
        {/* Метки времени */}
        <div className="absolute top-0 left-0 right-0 flex justify-between px-2 text-xs text-gray-600 dark:text-gray-400">
          <span>00:00</span>
          <span>06:00</span>
          <span>12:00</span>
          <span>18:00</span>
          <span>24:00</span>
        </div>

        {/* Сегменты записей */}
        <div className="absolute top-4 bottom-0 left-0 right-0">
          {timeline.map((segment) => (
            <div
              key={segment.id}
              className={`absolute top-0 bottom-0 rounded-sm transition-all ${
                segment.type === 'continuous' ? 'bg-primary-500' : 'bg-success-500'
              } ${
                selectedSegment?.id === segment.id ? 'ring-2 ring-white' : ''
              } hover:opacity-100`}
              style={getSegmentStyle(segment)}
              onClick={() => handleSegmentClick(segment)}
              onMouseEnter={() => handleSegmentHover(segment)}
              onMouseLeave={() => handleSegmentHover(null)}
              title={`${formatDateTime(segment.start_time)} - ${formatDateTime(segment.end_time)}`}
            />
          ))}
        </div>

        {/* Индикатор текущего времени */}
        <div
          className="absolute top-0 bottom-0 w-0.5 bg-danger-500"
          style={{ left: '50%' }}
        >
          <div className="absolute -top-1 left-1/2 transform -translate-x-1/2 w-3 h-3 bg-danger-500 rounded-full"></div>
        </div>
      </div>

      {/* Информация о выбранном сегменте */}
      {hoveredSegment && (
        <div className="bg-white dark:bg-gray-800 rounded-lg shadow p-4">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-gray-600 dark:text-gray-400">
                Начало: {formatDateTime(hoveredSegment.start_time)}
              </p>
              <p className="text-sm text-gray-600 dark:text-gray-400">
                Окончание: {formatDateTime(hoveredSegment.end_time)}
              </p>
            </div>
            <span className={`px-2 py-1 text-xs rounded-full ${
              hoveredSegment.type === 'continuous'
                ? 'bg-primary-100 dark:bg-primary-900/30 text-primary-700 dark:text-primary-300'
                : 'bg-success-100 dark:bg-success-900/30 text-success-700 dark:text-success-300'
            }`}>
              {hoveredSegment.type === 'continuous' ? 'Непрерывная' : 'По движению'}
            </span>
          </div>
        </div>
      )}

      {/* Легенда */}
      <div className="flex items-center space-x-4 text-sm text-gray-600 dark:text-gray-400">
        <div className="flex items-center space-x-2">
          <div className="w-4 h-4 bg-primary-500 rounded"></div>
          <span>Непрерывная</span>
        </div>
        <div className="flex items-center space-x-2">
          <div className="w-4 h-4 bg-success-500 rounded"></div>
          <span>По движению</span>
        </div>
      </div>
    </div>
  );
};

export default Timeline;
