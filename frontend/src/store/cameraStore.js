import { create } from 'zustand';
import { camerasAPI } from '@api/cameras';

export const cameraStore = create((set, get) => ({
  cameras: [],
  selectedCamera: null,
  isLoading: false,
  error: null,
  filters: {
    status: 'all',
    search: '',
  },

  // Получить список камер
  fetchCameras: async (params = {}) => {
    set({ isLoading: true, error: null });
    try {
      const data = await camerasAPI.getCameras(params);
      set({ cameras: data.items || data, isLoading: false });
      return data;
    } catch (error) {
      set({
        isLoading: false,
        error: error.userMessage || 'Ошибка загрузки камер',
      });
      throw error;
    }
  },

  // Получить камеру по ID
  fetchCamera: async (cameraId) => {
    set({ isLoading: true, error: null });
    try {
      const camera = await camerasAPI.getCamera(cameraId);
      set({ isLoading: false });
      return camera;
    } catch (error) {
      set({
        isLoading: false,
        error: error.userMessage || 'Ошибка загрузки камеры',
      });
      throw error;
    }
  },

  // Создать камеру
  createCamera: async (cameraData) => {
    set({ isLoading: true, error: null });
    try {
      const camera = await camerasAPI.createCamera(cameraData);
      set((state) => ({
        cameras: [...state.cameras, camera],
        isLoading: false,
      }));
      return { success: true, camera };
    } catch (error) {
      set({
        isLoading: false,
        error: error.userMessage || 'Ошибка создания камеры',
      });
      return { success: false, error: error.userMessage || 'Ошибка создания камеры' };
    }
  },

  // Обновить камеру
  updateCamera: async (cameraId, cameraData) => {
    set({ isLoading: true, error: null });
    try {
      const camera = await camerasAPI.updateCamera(cameraId, cameraData);
      set((state) => ({
        cameras: state.cameras.map((c) =>
          c.id === cameraId ? camera : c
        ),
        selectedCamera:
          state.selectedCamera?.id === cameraId ? camera : state.selectedCamera,
        isLoading: false,
      }));
      return { success: true, camera };
    } catch (error) {
      set({
        isLoading: false,
        error: error.userMessage || 'Ошибка обновления камеры',
      });
      return { success: false, error: error.userMessage || 'Ошибка обновления камеры' };
    }
  },

  // Удалить камеру
  deleteCamera: async (cameraId) => {
    set({ isLoading: true, error: null });
    try {
      await camerasAPI.deleteCamera(cameraId);
      set((state) => ({
        cameras: state.cameras.filter((c) => c.id !== cameraId),
        selectedCamera:
          state.selectedCamera?.id === cameraId ? null : state.selectedCamera,
        isLoading: false,
      }));
      return { success: true };
    } catch (error) {
      set({
        isLoading: false,
        error: error.userMessage || 'Ошибка удаления камеры',
      });
      return { success: false, error: error.userMessage || 'Ошибка удаления камеры' };
    }
  },

  // Выбрать камеру
  selectCamera: (camera) => set({ selectedCamera: camera }),

  // Очистить выбранную камеру
  clearSelectedCamera: () => set({ selectedCamera: null }),

  // Обновить фильтры
  setFilters: (filters) => set({ filters: { ...get().filters, ...filters } }),

  // Очистить фильтры
  clearFilters: () =>
    set({
      filters: {
        status: 'all',
        search: '',
      },
    }),

  // Получить отфильтрованные камеры
  getFilteredCameras: () => {
    const { cameras, filters } = get();
    return cameras.filter((camera) => {
      const matchesStatus =
        filters.status === 'all' || camera.status === filters.status;
      const matchesSearch =
        !filters.search ||
        camera.name.toLowerCase().includes(filters.search.toLowerCase()) ||
        (camera.description &&
          camera.description.toLowerCase().includes(filters.search.toLowerCase()));
      return matchesStatus && matchesSearch;
    });
  },

  // Обновить статус камеры (для WebSocket обновлений)
  updateCameraStatus: (cameraId, status) => {
    set((state) => ({
      cameras: state.cameras.map((c) =>
        c.id === cameraId ? { ...c, status } : c
      ),
      selectedCamera:
        state.selectedCamera?.id === cameraId
          ? { ...state.selectedCamera, status }
          : state.selectedCamera,
    }));
  },

  // Очистить ошибку
  clearError: () => set({ error: null }),
}));
