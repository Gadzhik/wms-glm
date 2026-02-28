import apiClient from './client';

export const recordingsAPI = {
  // Получить список записей
  getRecordings: async (params = {}) => {
    const response = await apiClient.get('/recordings', { params });
    return response.data;
  },

  // Получить запись по ID
  getRecording: async (recordingId) => {
    const response = await apiClient.get(`/recordings/${recordingId}`);
    return response.data;
  },

  // Получить записи камеры за период
  getCameraRecordings: async (cameraId, startDate, endDate, params = {}) => {
    const response = await apiClient.get(`/cameras/${cameraId}/recordings`, {
      params: {
        start_date: startDate,
        end_date: endDate,
        ...params,
      },
    });
    return response.data;
  },

  // Получить таймлайн записей
  getTimeline: async (cameraId, startDate, endDate) => {
    const response = await apiClient.get(`/recordings/timeline`, {
      params: {
        camera_id: cameraId,
        start_date: startDate,
        end_date: endDate,
      },
    });
    return response.data;
  },

  // Получить URL для воспроизведения записи
  getPlaybackUrl: async (recordingId) => {
    const response = await apiClient.get(`/recordings/${recordingId}/play`);
    return response.data;
  },

  // Экспорт фрагмента записи
  exportRecording: async (recordingId, startTime, endTime, format = 'mp4') => {
    const response = await apiClient.post(`/recordings/${recordingId}/export`, {
      start_time: startTime,
      end_time: endTime,
      format,
    });
    return response.data;
  },

  // Получить статус экспорта
  getExportStatus: async (exportId) => {
    const response = await apiClient.get(`/recordings/exports/${exportId}`);
    return response.data;
  },

  // Скачать экспортированный файл
  downloadExport: async (exportId) => {
    const response = await apiClient.get(`/recordings/exports/${exportId}/download`, {
      responseType: 'blob',
    });
    return response.data;
  },

  // Удалить запись
  deleteRecording: async (recordingId) => {
    const response = await apiClient.delete(`/recordings/${recordingId}`);
    return response.data;
  },

  // Получить превью записи
  getRecordingThumbnail: async (recordingId, timestamp) => {
    const response = await apiClient.get(`/recordings/${recordingId}/thumbnail`, {
      params: { timestamp },
      responseType: 'blob',
    });
    return response.data;
  },

  // Получить статистику записей
  getRecordingStats: async (params = {}) => {
    const response = await apiClient.get('/recordings/stats', { params });
    return response.data;
  },
};
