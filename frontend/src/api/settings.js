import apiClient from './client';

export const settingsAPI = {
  // Получить все настройки
  getSettings: async () => {
    const response = await apiClient.get('/settings');
    return response.data;
  },

  // Получить настройку по ключу
  getSetting: async (key) => {
    const response = await apiClient.get(`/settings/${key}`);
    return response.data;
  },

  // Обновить настройку
  updateSetting: async (key, value) => {
    const response = await apiClient.put(`/settings/${key}`, { value });
    return response.data;
  },

  // Обновить несколько настроек
  updateSettings: async (settings) => {
    const response = await apiClient.put('/settings', { settings });
    return response.data;
  },

  // Сбросить настройку до значения по умолчанию
  resetSetting: async (key) => {
    const response = await apiClient.post(`/settings/${key}/reset`);
    return response.data;
  },

  // Получить настройки хранения
  getStorageSettings: async () => {
    const response = await apiClient.get('/settings/storage');
    return response.data;
  },

  // Обновить настройки хранения
  updateStorageSettings: async (settings) => {
    const response = await apiClient.put('/settings/storage', settings);
    return response.data;
  },

  // Получить настройки записи
  getRecordingSettings: async () => {
    const response = await apiClient.get('/settings/recording');
    return response.data;
  },

  // Обновить настройки записи
  updateRecordingSettings: async (settings) => {
    const response = await apiClient.put('/settings/recording', settings);
    return response.data;
  },

  // Получить настройки уведомлений
  getNotificationSettings: async () => {
    const response = await apiClient.get('/settings/notifications');
    return response.data;
  },

  // Обновить настройки уведомлений
  updateNotificationSettings: async (settings) => {
    const response = await apiClient.put('/settings/notifications', settings);
    return response.data;
  },

  // Получить информацию о хранилище
  getStorageInfo: async () => {
    const response = await apiClient.get('/settings/storage/info');
    return response.data;
  },

  // Очистить старые записи
  cleanupOldRecordings: async (days) => {
    const response = await apiClient.post('/settings/storage/cleanup', { days });
    return response.data;
  },

  // Получить расписание записи
  getSchedules: async () => {
    const response = await apiClient.get('/settings/schedules');
    return response.data;
  },

  // Создать расписание
  createSchedule: async (schedule) => {
    const response = await apiClient.post('/settings/schedules', schedule);
    return response.data;
  },

  // Обновить расписание
  updateSchedule: async (scheduleId, schedule) => {
    const response = await apiClient.put(`/settings/schedules/${scheduleId}`, schedule);
    return response.data;
  },

  // Удалить расписание
  deleteSchedule: async (scheduleId) => {
    const response = await apiClient.delete(`/settings/schedules/${scheduleId}`);
    return response.data;
  },
};
