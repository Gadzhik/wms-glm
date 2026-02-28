import { useState, useEffect, useRef } from 'react';
import { Play, Pause, SkipBack, SkipForward, Volume2, VolumeX, Maximize2, Download } from 'lucide-react';
import { formatDuration } from '@utils/format';

const RecordingPlayer = ({ recordingUrl, startTime, endTime, onExport }) => {
  const videoRef = useRef(null);
  const [isPlaying, setIsPlaying] = useState(false);
  const [currentTime, setCurrentTime] = useState(0);
  const [duration, setDuration] = useState(0);
  const [isMuted, setIsMuted] = useState(false);
  const [volume, setVolume] = useState(1);
  const [playbackRate, setPlaybackRate] = useState(1);

  useEffect(() => {
    const video = videoRef.current;
    if (!video) return;

    const handleTimeUpdate = () => {
      setCurrentTime(video.currentTime);
    };

    const handleLoadedMetadata = () => {
      setDuration(video.duration);
    };

    const handlePlay = () => setIsPlaying(true);
    const handlePause = () => setIsPlaying(false);

    video.addEventListener('timeupdate', handleTimeUpdate);
    video.addEventListener('loadedmetadata', handleLoadedMetadata);
    video.addEventListener('play', handlePlay);
    video.addEventListener('pause', handlePause);

    return () => {
      video.removeEventListener('timeupdate', handleTimeUpdate);
      video.removeEventListener('loadedmetadata', handleLoadedMetadata);
      video.removeEventListener('play', handlePlay);
      video.removeEventListener('pause', handlePause);
    };
  }, [recordingUrl]);

  const togglePlay = () => {
    const video = videoRef.current;
    if (video) {
      if (isPlaying) {
        video.pause();
      } else {
        video.play();
      }
    }
  };

  const handleSeek = (e) => {
    const video = videoRef.current;
    if (video) {
      const seekTime = (e.target.value / 100) * duration;
      video.currentTime = seekTime;
    }
  };

  const skipBackward = () => {
    const video = videoRef.current;
    if (video) {
      video.currentTime = Math.max(0, video.currentTime - 5);
    }
  };

  const skipForward = () => {
    const video = videoRef.current;
    if (video) {
      video.currentTime = Math.min(duration, video.currentTime + 5);
    }
  };

  const toggleMute = () => {
    const video = videoRef.current;
    if (video) {
      video.muted = !isMuted;
      setIsMuted(!isMuted);
    }
  };

  const handleVolumeChange = (e) => {
    const video = videoRef.current;
    if (video) {
      video.volume = e.target.value;
      setVolume(e.target.value);
      setIsMuted(e.target.value === 0);
    }
  };

  const handlePlaybackRateChange = (rate) => {
    const video = videoRef.current;
    if (video) {
      video.playbackRate = rate;
      setPlaybackRate(rate);
    }
  };

  const handleFullscreen = () => {
    const video = videoRef.current;
    if (video) {
      if (document.fullscreenElement) {
        document.exitFullscreen();
      } else {
        video.requestFullscreen();
      }
    }
  };

  const progress = duration > 0 ? (currentTime / duration) * 100 : 0;

  return (
    <div className="bg-black rounded-lg overflow-hidden">
      {/* Видеоплеер */}
      <div className="relative aspect-video bg-black">
        <video
          ref={videoRef}
          src={recordingUrl}
          className="w-full h-full object-contain"
          onClick={togglePlay}
        />
      </div>

      {/* Панель управления */}
      <div className="bg-gray-900 p-4 space-y-3">
        {/* Прогресс бар */}
        <div className="flex items-center space-x-3">
          <span className="text-white text-sm font-mono w-12">
            {formatDuration(currentTime)}
          </span>
          <input
            type="range"
            min="0"
            max="100"
            value={progress}
            onChange={handleSeek}
            className="flex-1 h-2 bg-gray-700 rounded-lg appearance-none cursor-pointer"
            style={{
              background: `linear-gradient(to right, #0ea5e9 ${progress}%, #374151 ${progress}%)`,
            }}
          />
          <span className="text-white text-sm font-mono w-12">
            {formatDuration(duration)}
          </span>
        </div>

        {/* Кнопки управления */}
        <div className="flex items-center justify-between">
          <div className="flex items-center space-x-2">
            <button
              onClick={skipBackward}
              className="p-2 text-gray-400 hover:text-white transition-colors"
              title="Назад на 5 сек"
            >
              <SkipBack className="w-5 h-5" />
            </button>
            <button
              onClick={togglePlay}
              className="p-3 bg-primary-500 hover:bg-primary-600 text-white rounded-full transition-colors"
              title={isPlaying ? 'Пауза' : 'Воспроизвести'}
            >
              {isPlaying ? (
                <Pause className="w-5 h-5" />
              ) : (
                <Play className="w-5 h-5 ml-0.5" />
              )}
            </button>
            <button
              onClick={skipForward}
              className="p-2 text-gray-400 hover:text-white transition-colors"
              title="Вперед на 5 сек"
            >
              <SkipForward className="w-5 h-5" />
            </button>

            {/* Громкость */}
            <div className="flex items-center space-x-2 ml-4">
              <button
                onClick={toggleMute}
                className="p-2 text-gray-400 hover:text-white transition-colors"
              >
                {isMuted ? (
                  <VolumeX className="w-5 h-5" />
                ) : (
                  <Volume2 className="w-5 h-5" />
                )}
              </button>
              <input
                type="range"
                min="0"
                max="1"
                step="0.1"
                value={isMuted ? 0 : volume}
                onChange={handleVolumeChange}
                className="w-20 h-2 bg-gray-700 rounded-lg appearance-none cursor-pointer"
              />
            </div>

            {/* Скорость воспроизведения */}
            <div className="relative ml-4">
              <select
                value={playbackRate}
                onChange={(e) => handlePlaybackRateChange(parseFloat(e.target.value))}
                className="bg-gray-800 text-white text-sm rounded px-2 py-1 border border-gray-700 focus:outline-none focus:border-primary-500"
              >
                <option value={0.25}>0.25x</option>
                <option value={0.5}>0.5x</option>
                <option value={0.75}>0.75x</option>
                <option value={1}>1x</option>
                <option value={1.25}>1.25x</option>
                <option value={1.5}>1.5x</option>
                <option value={2}>2x</option>
              </select>
            </div>
          </div>

          <div className="flex items-center space-x-2">
            {onExport && (
              <button
                onClick={onExport}
                className="p-2 text-gray-400 hover:text-white transition-colors"
                title="Экспортировать"
              >
                <Download className="w-5 h-5" />
              </button>
            )}
            <button
              onClick={handleFullscreen}
              className="p-2 text-gray-400 hover:text-white transition-colors"
              title="Полный экран"
            >
              <Maximize2 className="w-5 h-5" />
            </button>
          </div>
        </div>
      </div>
    </div>
  );
};

export default RecordingPlayer;
