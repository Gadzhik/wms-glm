import { create } from 'zustand';
import { persist } from 'zustand/middleware';
import { authAPI } from '@api/auth';

export const authStore = create(
  persist(
    (set, get) => ({
      user: null,
      token: null,
      refreshToken: null,
      isAuthenticated: false,
      isLoading: false,
      error: null,

      // Вход в систему
      login: async (username, password) => {
        set({ isLoading: true, error: null });
        try {
          const data = await authAPI.login(username, password);
          set({
            user: data.user,
            token: data.access_token,
            refreshToken: data.refresh_token,
            isAuthenticated: true,
            isLoading: false,
            error: null,
          });
          return { success: true };
        } catch (error) {
          set({
            isLoading: false,
            error: error.userMessage || 'Ошибка входа',
            isAuthenticated: false,
          });
          return { success: false, error: error.userMessage || 'Ошибка входа' };
        }
      },

      // Выход из системы
      logout: async () => {
        try {
          await authAPI.logout();
        } catch (error) {
          console.error('Ошибка выхода:', error);
        } finally {
          set({
            user: null,
            token: null,
            refreshToken: null,
            isAuthenticated: false,
            error: null,
          });
        }
      },

      // Обновление токенов
      setTokens: (accessToken, newRefreshToken) => {
        set({
          token: accessToken,
          refreshToken: newRefreshToken || get().refreshToken,
        });
      },

      // Получение текущего пользователя
      getCurrentUser: async () => {
        set({ isLoading: true });
        try {
          const user = await authAPI.getCurrentUser();
          set({ user, isLoading: false });
          return user;
        } catch (error) {
          set({
            isLoading: false,
            error: error.userMessage || 'Ошибка получения данных пользователя',
          });
          throw error;
        }
      },

      // Смена пароля
      changePassword: async (oldPassword, newPassword) => {
        set({ isLoading: true, error: null });
        try {
          await authAPI.changePassword(oldPassword, newPassword);
          set({ isLoading: false, error: null });
          return { success: true };
        } catch (error) {
          set({
            isLoading: false,
            error: error.userMessage || 'Ошибка смены пароля',
          });
          return { success: false, error: error.userMessage || 'Ошибка смены пароля' };
        }
      },

      // Очистка ошибки
      clearError: () => set({ error: null }),

      // Обновление данных пользователя
      updateUser: (userData) => set({ user: { ...get().user, ...userData } }),
    }),
    {
      name: 'vms-auth-storage',
      partialize: (state) => ({
        user: state.user,
        token: state.token,
        refreshToken: state.refreshToken,
        isAuthenticated: state.isAuthenticated,
      }),
    }
  )
);
