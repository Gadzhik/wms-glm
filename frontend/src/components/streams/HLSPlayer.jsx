import { useEffect, useRef, forwardRef, useImperativeHandle } from 'react';
import Hls from 'hls.js';

const HLSPlayer = forwardRef(({ src, autoPlay = true, muted = true, onError }, ref) => {
  const videoRef = useRef(null);
  const hlsRef = useRef(null);

  useImperativeHandle(ref, () => ({
    setMuted: (muted) => {
      if (videoRef.current) {
        videoRef.current.muted = muted;
      }
    },
    play: () => {
      if (videoRef.current) {
        videoRef.current.play();
      }
    },
    pause: () => {
      if (videoRef.current) {
        videoRef.current.pause();
      }
    },
  }));

  useEffect(() => {
    const video = videoRef.current;
    if (!video) return;

    let hls = null;

    if (Hls.isSupported()) {
      hls = new Hls({
        enableWorker: true,
        lowLatencyMode: true,
        backBufferLength: 90,
      });

      hls.loadSource(src);
      hls.attachMedia(video);

      hls.on(Hls.Events.MANIFEST_PARSED, () => {
        if (autoPlay) {
          video.play().catch((err) => {
            console.error('Ошибка автозапуска:', err);
          });
        }
      });

      hls.on(Hls.Events.ERROR, (event, data) => {
        if (data.fatal) {
          switch (data.type) {
            case Hls.ErrorTypes.NETWORK_ERROR:
              console.error('Сетевая ошибка:', data);
              hls.startLoad();
              break;
            case Hls.ErrorTypes.MEDIA_ERROR:
              console.error('Ошибка медиа:', data);
              hls.recoverMediaError();
              break;
            default:
              console.error('Неустранимая ошибка:', data);
              hls.destroy();
              if (onError) onError();
              break;
          }
        }
      });

      hlsRef.current = hls;
    } else if (video.canPlayType('application/vnd.apple.mpegurl')) {
      // Safari native HLS
      video.src = src;
      video.addEventListener('loadedmetadata', () => {
        if (autoPlay) {
          video.play().catch((err) => {
            console.error('Ошибка автозапуска:', err);
          });
        }
      });

      video.addEventListener('error', () => {
        console.error('Ошибка воспроизведения');
        if (onError) onError();
      });
    }

    return () => {
      if (hls) {
        hls.destroy();
      }
    };
  }, [src, autoPlay, onError]);

  return (
    <video
      ref={videoRef}
      className="w-full h-full object-contain"
      autoPlay={autoPlay}
      muted={muted}
      playsInline
    />
  );
});

HLSPlayer.displayName = 'HLSPlayer';

export default HLSPlayer;
