import { create } from 'zustand';
import { recordingsAPI } from '@api/recordings';

export const recordingStore = create((set, get) => ({
  recordings: [],
  selectedRecording: null,
  timeline: [],
  isLoading: false,
  error: null,
  filters: {
    cameraId: null,
    startDate: null,
    endDate: null,
    type: 'all',
  },

  // Получить список записей
  fetchRecordings: async (params = {}) => {
    set({ isLoading: true, error: null });
    try {
      const data = await recordingsAPI.getRecordings(params);
      set({ recordings: data.items || data, isLoading: false });
      return data;
    } catch (error) {
      set({
        isLoading: false,
        error: error.userMessage || 'Ошибка загрузки записей',
      });
      throw error;
    }
  },

  // Получить запись по ID
  fetchRecording: async (recordingId) => {
    set({ isLoading: true, error: null });
    try {
      const recording = await recordingsAPI.getRecording(recordingId);
      set({ selectedRecording: recording, isLoading: false });
      return recording;
    } catch (error) {
      set({
        isLoading: false,
        error: error.userMessage || 'Ошибка загрузки записи',
      });
      throw error;
    }
  },

  // Получить записи камеры за период
  fetchCameraRecordings: async (cameraId, startDate, endDate) => {
    set({ isLoading: true, error: null });
    try {
      const data = await recordingsAPI.getCameraRecordings(
        cameraId,
        startDate,
        endDate
      );
      set({ recordings: data.items || data, isLoading: false });
      return data;
    } catch (error) {
      set({
        isLoading: false,
        error: error.userMessage || 'Ошибка загрузки записей камеры',
      });
      throw error;
    }
  },

  // Получить таймлайн записей
  fetchTimeline: async (cameraId, startDate, endDate) => {
    set({ isLoading: true, error: null });
    try {
      const data = await recordingsAPI.getTimeline(cameraId, startDate, endDate);
      set({ timeline: data, isLoading: false });
      return data;
    } catch (error) {
      set({
        isLoading: false,
        error: error.userMessage || 'Ошибка загрузки таймлайна',
      });
      throw error;
    }
  },

  // Получить URL для воспроизведения
  getPlaybackUrl: async (recordingId) => {
    try {
      const data = await recordingsAPI.getPlaybackUrl(recordingId);
      return data.url;
    } catch (error) {
      set({ error: error.userMessage || 'Ошибка получения URL воспроизведения' });
      throw error;
    }
  },

  // Экспорт записи
  exportRecording: async (recordingId, startTime, endTime, format = 'mp4') => {
    set({ isLoading: true, error: null });
    try {
      const data = await recordingsAPI.exportRecording(
        recordingId,
        startTime,
        endTime,
        format
      );
      set({ isLoading: false });
      return { success: true, exportId: data.export_id };
    } catch (error) {
      set({
        isLoading: false,
        error: error.userMessage || 'Ошибка экспорта записи',
      });
      return { success: false, error: error.userMessage || 'Ошибка экспорта записи' };
    }
  },

  // Получить статус экспорта
  fetchExportStatus: async (exportId) => {
    try {
      const data = await recordingsAPI.getExportStatus(exportId);
      return data;
    } catch (error) {
      set({ error: error.userMessage || 'Ошибка получения статуса экспорта' });
      throw error;
    }
  },

  // Скачать экспортированный файл
  downloadExport: async (exportId, filename = 'export.mp4') => {
    try {
      const blob = await recordingsAPI.downloadExport(exportId);
      const url = window.URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = filename;
      document.body.appendChild(a);
      a.click();
      window.URL.revokeObjectURL(url);
      document.body.removeChild(a);
      return { success: true };
    } catch (error) {
      set({ error: error.userMessage || 'Ошибка скачивания файла' });
      return { success: false, error: error.userMessage || 'Ошибка скачивания файла' };
    }
  },

  // Удалить запись
  deleteRecording: async (recordingId) => {
    set({ isLoading: true, error: null });
    try {
      await recordingsAPI.deleteRecording(recordingId);
      set((state) => ({
        recordings: state.recordings.filter((r) => r.id !== recordingId),
        selectedCamera:
          state.selectedRecording?.id === recordingId ? null : state.selectedRecording,
        isLoading: false,
      }));
      return { success: true };
    } catch (error) {
      set({
        isLoading: false,
        error: error.userMessage || 'Ошибка удаления записи',
      });
      return { success: false, error: error.userMessage || 'Ошибка удаления записи' };
    }
  },

  // Получить превью записи
  fetchRecordingThumbnail: async (recordingId, timestamp) => {
    try {
      const blob = await recordingsAPI.getRecordingThumbnail(recordingId, timestamp);
      return URL.createObjectURL(blob);
    } catch (error) {
      console.error('Ошибка получения превью:', error);
      return null;
    }
  },

  // Получить статистику записей
  fetchRecordingStats: async (params = {}) => {
    try {
      const data = await recordingsAPI.getRecordingStats(params);
      return data;
    } catch (error) {
      set({ error: error.userMessage || 'Ошибка получения статистики' });
      throw error;
    }
  },

  // Выбрать запись
  selectRecording: (recording) => set({ selectedRecording: recording }),

  // Очистить выбранную запись
  clearSelectedRecording: () => set({ selectedRecording: null }),

  // Обновить фильтры
  setFilters: (filters) => set({ filters: { ...get().filters, ...filters } }),

  // Очистить фильтры
  clearFilters: () =>
    set({
      filters: {
        cameraId: null,
        startDate: null,
        endDate: null,
        type: 'all',
      },
    }),

  // Очистить ошибку
  clearError: () => set({ error: null }),
}));
