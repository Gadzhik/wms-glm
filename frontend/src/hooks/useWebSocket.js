import { useEffect, useRef, useCallback } from 'react';
import { authStore } from '@store/authStore';
import { cameraStore } from '@store/cameraStore';
import { eventStore } from '@store/eventStore';

export const useWebSocket = () => {
  const wsRef = useRef(null);
  const reconnectTimeoutRef = useRef(null);
  const messageHandlersRef = useRef(new Map());

  const connect = useCallback(() => {
    const token = authStore.getState().token;
    if (!token) return;

    const wsUrl = import.meta.env.VITE_WS_URL || 'ws://localhost:8000/ws';

    try {
      wsRef.current = new WebSocket(`${wsUrl}?token=${token}`);

      wsRef.current.onopen = () => {
        console.log('WebSocket подключен');
      };

      wsRef.current.onmessage = (event) => {
        try {
          const data = JSON.parse(event.data);
          console.log('WebSocket сообщение:', data);

          // Обработка разных типов сообщений
          switch (data.type) {
            case 'camera_status':
              cameraStore.getState().updateCameraStatus(
                data.camera_id,
                data.status
              );
              break;

            case 'event':
              eventStore.getState().addEvent(data.event);
              break;

            case 'event_update':
              eventStore.getState().updateEvent(data.event_id, data.updates);
              break;

            default:
              // Вызываем пользовательские обработчики
              const handlers = messageHandlersRef.current.get(data.type) || [];
              handlers.forEach((handler) => handler(data));
          }
        } catch (error) {
          console.error('Ошибка обработки WebSocket сообщения:', error);
        }
      };

      wsRef.current.onerror = (error) => {
        console.error('WebSocket ошибка:', error);
      };

      wsRef.current.onclose = () => {
        console.log('WebSocket отключен');
        // Пытаемся переподключиться через 5 секунд
        reconnectTimeoutRef.current = setTimeout(() => {
          connect();
        }, 5000);
      };
    } catch (error) {
      console.error('Ошибка подключения WebSocket:', error);
    }
  }, []);

  const disconnect = useCallback(() => {
    if (reconnectTimeoutRef.current) {
      clearTimeout(reconnectTimeoutRef.current);
    }
    if (wsRef.current) {
      wsRef.current.close();
      wsRef.current = null;
    }
  }, []);

  const sendMessage = useCallback((message) => {
    if (wsRef.current && wsRef.current.readyState === WebSocket.OPEN) {
      wsRef.current.send(JSON.stringify(message));
    } else {
      console.warn('WebSocket не подключен');
    }
  }, []);

  const onMessage = useCallback((type, handler) => {
    if (!messageHandlersRef.current.has(type)) {
      messageHandlersRef.current.set(type, []);
    }
    messageHandlersRef.current.get(type).push(handler);

    // Возвращаем функцию для отписки
    return () => {
      const handlers = messageHandlersRef.current.get(type) || [];
      const index = handlers.indexOf(handler);
      if (index > -1) {
        handlers.splice(index, 1);
      }
    };
  }, []);

  // Подключаемся при монтировании и наличии токена
  useEffect(() => {
    const token = authStore.getState().token;
    if (token) {
      connect();
    }

    return () => {
      disconnect();
    };
  }, [connect, disconnect]);

  // Отслеживаем изменения токена
  useEffect(() => {
    const unsubscribe = authStore.subscribe((state, prevState) => {
      if (state.token !== prevState.token) {
        if (state.token) {
          connect();
        } else {
          disconnect();
        }
      }
    });

    return unsubscribe;
  }, [connect, disconnect]);

  return {
    sendMessage,
    onMessage,
    isConnected: wsRef.current?.readyState === WebSocket.OPEN,
  };
};
