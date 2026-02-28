import { useState, useEffect, useRef } from 'react';
import { Maximize2, Volume2, VolumeX, Settings } from 'lucide-react';
import HLSPlayer from './HLSPlayer';
import StreamControls from './StreamControls';
import { camerasAPI } from '@api/cameras';
import Loading from '@components/common/Loading';

const LiveStream = ({ cameraId, autoPlay = true, muted = true, showControls = true }) => {
  const [streamUrl, setStreamUrl] = useState(null);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState(null);
  const [isMuted, setIsMuted] = useState(muted);
  const [isFullscreen, setIsFullscreen] = useState(false);
  const [showSettings, setShowSettings] = useState(false);
  const playerRef = useRef(null);
  const containerRef = useRef(null);

  useEffect(() => {
    loadStream();
    return () => {
      // Cleanup
    };
  }, [cameraId]);

  const loadStream = async () => {
    setIsLoading(true);
    setError(null);
    try {
      const data = await camerasAPI.getCameraStream(cameraId, 'hls');
      setStreamUrl(data.url);
    } catch (err) {
      setError(err.userMessage || 'Ошибка загрузки потока');
    } finally {
      setIsLoading(false);
    }
  };

  const handleMuteToggle = () => {
    setIsMuted(!isMuted);
    if (playerRef.current) {
      playerRef.current.setMuted(!isMuted);
    }
  };

  const handleFullscreen = () => {
    if (!isFullscreen) {
      if (containerRef.current.requestFullscreen) {
        containerRef.current.requestFullscreen();
      } else if (containerRef.current.webkitRequestFullscreen) {
        containerRef.current.webkitRequestFullscreen();
      } else if (containerRef.current.msRequestFullscreen) {
        containerRef.current.msRequestFullscreen();
      }
    } else {
      if (document.exitFullscreen) {
        document.exitFullscreen();
      } else if (document.webkitExitFullscreen) {
        document.webkitExitFullscreen();
      } else if (document.msExitFullscreen) {
        document.msExitFullscreen();
      }
    }
    setIsFullscreen(!isFullscreen);
  };

  const handleRetry = () => {
    loadStream();
  };

  return (
    <div
      ref={containerRef}
      className="relative bg-black rounded-lg overflow-hidden group"
      style={{ aspectRatio: '16/9' }}
    >
      {isLoading && (
        <div className="absolute inset-0 flex items-center justify-center bg-gray-900">
          <Loading size="lg" text="Загрузка потока..." />
        </div>
      )}

      {error && (
        <div className="absolute inset-0 flex items-center justify-center bg-gray-900 p-4">
          <div className="text-center">
            <p className="text-danger-400 mb-4">{error}</p>
            <button
              onClick={handleRetry}
              className="px-4 py-2 bg-primary-500 hover:bg-primary-600 text-white rounded-lg transition-colors"
            >
              Повторить
            </button>
          </div>
        </div>
      )}

      {streamUrl && !isLoading && !error && (
        <HLSPlayer
          ref={playerRef}
          src={streamUrl}
          autoPlay={autoPlay}
          muted={isMuted}
          onError={handleRetry}
        />
      )}

      {/* Оверлей при наведении */}
      {showControls && streamUrl && !isLoading && !error && (
        <div className="absolute inset-0 bg-gradient-to-t from-black/60 via-transparent to-transparent opacity-0 group-hover:opacity-100 transition-opacity">
          {/* Верхняя панель */}
          <div className="absolute top-0 left-0 right-0 p-4 flex items-center justify-between">
            <div className="flex items-center space-x-2">
              <div className="w-2 h-2 bg-red-500 rounded-full animate-pulse"></div>
              <span className="text-white text-sm font-medium">LIVE</span>
            </div>
            <button
              onClick={() => setShowSettings(!showSettings)}
              className="p-2 text-white hover:bg-white/20 rounded-lg transition-colors"
            >
              <Settings className="w-5 h-5" />
            </button>
          </div>

          {/* Нижняя панель */}
          <div className="absolute bottom-0 left-0 right-0 p-4">
            <div className="flex items-center justify-between">
              <div className="flex items-center space-x-2">
                <button
                  onClick={handleMuteToggle}
                  className="p-2 text-white hover:bg-white/20 rounded-lg transition-colors"
                >
                  {isMuted ? (
                    <VolumeX className="w-5 h-5" />
                  ) : (
                    <Volume2 className="w-5 h-5" />
                  )}
                </button>
              </div>

              <button
                onClick={handleFullscreen}
                className="p-2 text-white hover:bg-white/20 rounded-lg transition-colors"
              >
                <Maximize2 className="w-5 h-5" />
              </button>
            </div>
          </div>
        </div>
      )}

      {/* Панель настроек */}
      {showSettings && (
        <div className="absolute top-12 right-4 bg-gray-900/95 rounded-lg shadow-xl p-4 w-64">
          <h3 className="text-white font-medium mb-3">Настройки</h3>
          <div className="space-y-3">
            <div>
              <label className="text-gray-400 text-sm block mb-1">Качество</label>
              <select className="w-full bg-gray-800 text-white rounded px-3 py-2 text-sm">
                <option>Авто</option>
                <option>Высокое</option>
                <option>Среднее</option>
                <option>Низкое</option>
              </select>
            </div>
            <div>
              <label className="text-gray-400 text-sm block mb-1">Задержка</label>
              <select className="w-full bg-gray-800 text-white rounded px-3 py-2 text-sm">
                <option>Низкая</option>
                <option>Средняя</option>
                <option>Высокая</option>
              </select>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default LiveStream;
