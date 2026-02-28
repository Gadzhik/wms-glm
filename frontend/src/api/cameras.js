import apiClient from './client';

export const camerasAPI = {
  // Получить список всех камер
  getCameras: async (params = {}) => {
    const response = await apiClient.get('/cameras', { params });
    return response.data;
  },

  // Получить камеру по ID
  getCamera: async (cameraId) => {
    const response = await apiClient.get(`/cameras/${cameraId}`);
    return response.data;
  },

  // Создать новую камеру
  createCamera: async (cameraData) => {
    const response = await apiClient.post('/cameras', cameraData);
    return response.data;
  },

  // Обновить камеру
  updateCamera: async (cameraId, cameraData) => {
    const response = await apiClient.put(`/cameras/${cameraId}`, cameraData);
    return response.data;
  },

  // Удалить камеру
  deleteCamera: async (cameraId) => {
    const response = await apiClient.delete(`/cameras/${cameraId}`);
    return response.data;
  },

  // Получить превью камеры
  getCameraSnapshot: async (cameraId) => {
    const response = await apiClient.get(`/cameras/${cameraId}/snapshot`, {
      responseType: 'blob',
    });
    return response.data;
  },

  // Получить поток камеры
  getCameraStream: async (cameraId, format = 'hls') => {
    const response = await apiClient.get(`/cameras/${cameraId}/stream`, {
      params: { format },
    });
    return response.data;
  },

  // ONVIF discovery
  discoverONVIF: async (params) => {
    const response = await apiClient.post('/cameras/discover', params);
    return response.data;
  },

  // Получить PTZ пресеты камеры
  getPTZPresets: async (cameraId) => {
    const response = await apiClient.get(`/cameras/${cameraId}/ptz/presets`);
    return response.data;
  },

  // Управление PTZ
  ptzMove: async (cameraId, direction, speed = 1) => {
    const response = await apiClient.post(`/cameras/${cameraId}/ptz/move`, {
      direction,
      speed,
    });
    return response.data;
  },

  ptzStop: async (cameraId) => {
    const response = await apiClient.post(`/cameras/${cameraId}/ptz/stop`);
    return response.data;
  },

  ptzGotoPreset: async (cameraId, presetId) => {
    const response = await apiClient.post(`/cameras/${cameraId}/ptz/goto`, {
      preset_id: presetId,
    });
    return response.data;
  },

  // Тест соединения с камерой
  testConnection: async (cameraData) => {
    const response = await apiClient.post('/cameras/test', cameraData);
    return response.data;
  },

  // Получить статус камеры
  getCameraStatus: async (cameraId) => {
    const response = await apiClient.get(`/cameras/${cameraId}/status`);
    return response.data;
  },
};
