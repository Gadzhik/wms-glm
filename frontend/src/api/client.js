import axios from 'axios';
import { authStore } from '@store/authStore';

const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000/api/v1';

const apiClient = axios.create({
  baseURL: API_URL,
  headers: {
    'Content-Type': 'application/json',
  },
  timeout: 30000,
});

// Request interceptor - добавить токен авторизации
apiClient.interceptors.request.use(
  (config) => {
    const token = authStore.getState().token;
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// Response interceptor - обработка ошибок и обновление токена
apiClient.interceptors.response.use(
  (response) => response,
  async (error) => {
    const originalRequest = error.config;

    // Если ошибка 401 и запрос еще не повторялся
    if (error.response?.status === 401 && !originalRequest._retry) {
      originalRequest._retry = true;

      try {
        // Пытаемся обновить токен
        const refreshToken = authStore.getState().refreshToken;
        if (refreshToken) {
          const response = await axios.post(`${API_URL}/auth/refresh`, {
            refresh_token: refreshToken,
          });

          const { access_token, refresh_token: newRefreshToken } = response.data;
          
          // Обновляем токены в store
          authStore.getState().setTokens(access_token, newRefreshToken);
          
          // Повторяем оригинальный запрос с новым токеном
          originalRequest.headers.Authorization = `Bearer ${access_token}`;
          return apiClient(originalRequest);
        }
      } catch (refreshError) {
        // Если не удалось обновить токен - выходим из системы
        authStore.getState().logout();
        window.location.href = '/login';
        return Promise.reject(refreshError);
      }
    }

    // Обработка других ошибок
    if (error.response) {
      // Ошибка от сервера
      const message = error.response.data?.detail || error.response.data?.message || 'Произошла ошибка';
      error.userMessage = message;
    } else if (error.request) {
      // Запрос отправлен, но ответ не получен
      error.userMessage = 'Нет ответа от сервера. Проверьте подключение к сети.';
    } else {
      // Ошибка при настройке запроса
      error.userMessage = error.message || 'Произошла ошибка при выполнении запроса';
    }

    return Promise.reject(error);
  }
);

export default apiClient;
