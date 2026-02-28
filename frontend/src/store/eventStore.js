import { create } from 'zustand';
import { eventsAPI } from '@api/events';

export const eventStore = create((set, get) => ({
  events: [],
  selectedEvent: null,
  isLoading: false,
  error: null,
  filters: {
    cameraId: null,
    eventType: 'all',
    startDate: null,
    endDate: null,
    viewed: 'all',
  },

  // Получить список событий
  fetchEvents: async (params = {}) => {
    set({ isLoading: true, error: null });
    try {
      const data = await eventsAPI.getEvents(params);
      set({ events: data.items || data, isLoading: false });
      return data;
    } catch (error) {
      set({
        isLoading: false,
        error: error.userMessage || 'Ошибка загрузки событий',
      });
      throw error;
    }
  },

  // Получить событие по ID
  fetchEvent: async (eventId) => {
    set({ isLoading: true, error: null });
    try {
      const event = await eventsAPI.getEvent(eventId);
      set({ selectedEvent: event, isLoading: false });
      return event;
    } catch (error) {
      set({
        isLoading: false,
        error: error.userMessage || 'Ошибка загрузки события',
      });
      throw error;
    }
  },

  // Получить события камеры
  fetchCameraEvents: async (cameraId, params = {}) => {
    set({ isLoading: true, error: null });
    try {
      const data = await eventsAPI.getCameraEvents(cameraId, params);
      set({ events: data.items || data, isLoading: false });
      return data;
    } catch (error) {
      set({
        isLoading: false,
        error: error.userMessage || 'Ошибка загрузки событий камеры',
      });
      throw error;
    }
  },

  // Получить события по типу
  fetchEventsByType: async (eventType, params = {}) => {
    set({ isLoading: true, error: null });
    try {
      const data = await eventsAPI.getEventsByType(eventType, params);
      set({ events: data.items || data, isLoading: false });
      return data;
    } catch (error) {
      set({
        isLoading: false,
        error: error.userMessage || 'Ошибка загрузки событий по типу',
      });
      throw error;
    }
  },

  // Получить события за период
  fetchEventsByPeriod: async (startDate, endDate, params = {}) => {
    set({ isLoading: true, error: null });
    try {
      const data = await eventsAPI.getEventsByPeriod(startDate, endDate, params);
      set({ events: data.items || data, isLoading: false });
      return data;
    } catch (error) {
      set({
        isLoading: false,
        error: error.userMessage || 'Ошибка загрузки событий за период',
      });
      throw error;
    }
  },

  // Получить превью события
  fetchEventThumbnail: async (eventId) => {
    try {
      const blob = await eventsAPI.getEventThumbnail(eventId);
      return URL.createObjectURL(blob);
    } catch (error) {
      console.error('Ошибка получения превью события:', error);
      return null;
    }
  },

  // Получить видео события
  fetchEventVideo: async (eventId) => {
    try {
      const data = await eventsAPI.getEventVideo(eventId);
      return data.url;
    } catch (error) {
      set({ error: error.userMessage || 'Ошибка получения видео события' });
      throw error;
    }
  },

  // Отметить событие как просмотренное
  markAsViewed: async (eventId) => {
    try {
      await eventsAPI.markAsViewed(eventId);
      set((state) => ({
        events: state.events.map((e) =>
          e.id === eventId ? { ...e, viewed: true } : e
        ),
        selectedEvent:
          state.selectedEvent?.id === eventId
            ? { ...state.selectedEvent, viewed: true }
            : state.selectedEvent,
      }));
      return { success: true };
    } catch (error) {
      set({ error: error.userMessage || 'Ошибка отметки события' });
      return { success: false, error: error.userMessage || 'Ошибка отметки события' };
    }
  },

  // Отметить несколько событий как просмотренные
  markManyAsViewed: async (eventIds) => {
    try {
      await eventsAPI.markManyAsViewed(eventIds);
      set((state) => ({
        events: state.events.map((e) =>
          eventIds.includes(e.id) ? { ...e, viewed: true } : e
        ),
        selectedEvent:
          state.selectedEvent && eventIds.includes(state.selectedEvent.id)
            ? { ...state.selectedEvent, viewed: true }
            : state.selectedEvent,
      }));
      return { success: true };
    } catch (error) {
      set({ error: error.userMessage || 'Ошибка отметки событий' });
      return { success: false, error: error.userMessage || 'Ошибка отметки событий' };
    }
  },

  // Получить статистику событий
  fetchEventStats: async (params = {}) => {
    try {
      const data = await eventsAPI.getEventStats(params);
      return data;
    } catch (error) {
      set({ error: error.userMessage || 'Ошибка получения статистики' });
      throw error;
    }
  },

  // Удалить событие
  deleteEvent: async (eventId) => {
    set({ isLoading: true, error: null });
    try {
      await eventsAPI.deleteEvent(eventId);
      set((state) => ({
        events: state.events.filter((e) => e.id !== eventId),
        selectedEvent:
          state.selectedEvent?.id === eventId ? null : state.selectedEvent,
        isLoading: false,
      }));
      return { success: true };
    } catch (error) {
      set({
        isLoading: false,
        error: error.userMessage || 'Ошибка удаления события',
      });
      return { success: false, error: error.userMessage || 'Ошибка удаления события' };
    }
  },

  // Выбрать событие
  selectEvent: (event) => set({ selectedEvent: event }),

  // Очистить выбранное событие
  clearSelectedEvent: () => set({ selectedEvent: null }),

  // Обновить фильтры
  setFilters: (filters) => set({ filters: { ...get().filters, ...filters } }),

  // Очистить фильтры
  clearFilters: () =>
    set({
      filters: {
        cameraId: null,
        eventType: 'all',
        startDate: null,
        endDate: null,
        viewed: 'all',
      },
    }),

  // Добавить новое событие (для WebSocket)
  addEvent: (event) => {
    set((state) => ({
      events: [event, ...state.events],
    }));
  },

  // Обновить событие (для WebSocket)
  updateEvent: (eventId, updates) => {
    set((state) => ({
      events: state.events.map((e) =>
        e.id === eventId ? { ...e, ...updates } : e
      ),
      selectedEvent:
        state.selectedEvent?.id === eventId
          ? { ...state.selectedEvent, ...updates }
          : state.selectedEvent,
    }));
  },

  // Очистить ошибку
  clearError: () => set({ error: null }),
}));
