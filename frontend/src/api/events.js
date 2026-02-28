import apiClient from './client';

export const eventsAPI = {
  // Получить список событий
  getEvents: async (params = {}) => {
    const response = await apiClient.get('/events', { params });
    return response.data;
  },

  // Получить событие по ID
  getEvent: async (eventId) => {
    const response = await apiClient.get(`/events/${eventId}`);
    return response.data;
  },

  // Получить события камеры
  getCameraEvents: async (cameraId, params = {}) => {
    const response = await apiClient.get(`/cameras/${cameraId}/events`, { params });
    return response.data;
  },

  // Получить события по типу
  getEventsByType: async (eventType, params = {}) => {
    const response = await apiClient.get(`/events/type/${eventType}`, { params });
    return response.data;
  },

  // Получить превью события
  getEventThumbnail: async (eventId) => {
    const response = await apiClient.get(`/events/${eventId}/thumbnail`, {
      responseType: 'blob',
    });
    return response.data;
  },

  // Получить видео события
  getEventVideo: async (eventId) => {
    const response = await apiClient.get(`/events/${eventId}/video`);
    return response.data;
  },

  // Отметить событие как просмотренное
  markAsViewed: async (eventId) => {
    const response = await apiClient.post(`/events/${eventId}/view`);
    return response.data;
  },

  // Отметить события как просмотренные (множественные)
  markManyAsViewed: async (eventIds) => {
    const response = await apiClient.post('/events/view', {
      event_ids: eventIds,
    });
    return response.data;
  },

  // Получить статистику событий
  getEventStats: async (params = {}) => {
    const response = await apiClient.get('/events/stats', { params });
    return response.data;
  },

  // Получить события за период
  getEventsByPeriod: async (startDate, endDate, params = {}) => {
    const response = await apiClient.get('/events/period', {
      params: {
        start_date: startDate,
        end_date: endDate,
        ...params,
      },
    });
    return response.data;
  },

  // Удалить событие
  deleteEvent: async (eventId) => {
    const response = await apiClient.delete(`/events/${eventId}`);
    return response.data;
  },
};
