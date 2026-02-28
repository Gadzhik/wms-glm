import { z } from 'zod';

// Схема валидации для формы входа
export const loginSchema = z.object({
  username: z
    .string()
    .min(1, 'Имя пользователя обязательно')
    .min(3, 'Минимум 3 символа'),
  password: z
    .string()
    .min(1, 'Пароль обязателен')
    .min(6, 'Минимум 6 символов'),
});

// Схема валидации для формы смены пароля
export const changePasswordSchema = z.object({
  oldPassword: z
    .string()
    .min(1, 'Текущий пароль обязателен'),
  newPassword: z
    .string()
    .min(1, 'Новый пароль обязателен')
    .min(6, 'Минимум 6 символов')
    .regex(/[A-Z]/, 'Пароль должен содержать хотя бы одну заглавную букву')
    .regex(/[a-z]/, 'Пароль должен содержать хотя бы одну строчную букву')
    .regex(/[0-9]/, 'Пароль должен содержать хотя бы одну цифру'),
  confirmPassword: z
    .string()
    .min(1, 'Подтверждение пароля обязательно'),
}).refine((data) => data.newPassword === data.confirmPassword, {
  message: 'Пароли не совпадают',
  path: ['confirmPassword'],
});

// Схема валидации для формы камеры
export const cameraSchema = z.object({
  name: z
    .string()
    .min(1, 'Название обязательно')
    .max(100, 'Максимум 100 символов'),
  description: z
    .string()
    .max(500, 'Максимум 500 символов')
    .optional(),
  rtsp_url: z
    .string()
    .min(1, 'RTSP URL обязателен')
    .url('Некорректный RTSP URL'),
  username: z
    .string()
    .optional(),
  password: z
    .string()
    .optional(),
  location: z
    .string()
    .max(100, 'Максимум 100 символов')
    .optional(),
  recording_enabled: z
    .boolean()
    .default(true),
  motion_detection: z
    .boolean()
    .default(false),
  ptz_enabled: z
    .boolean()
    .default(false),
  onvif_enabled: z
    .boolean()
    .default(false),
  onvif_port: z
    .number()
    .int()
    .min(1, 'Порт должен быть от 1 до 65535')
    .max(65535, 'Порт должен быть от 1 до 65535')
    .optional(),
  onvif_path: z
    .string()
    .optional(),
});

// Схема валидации для ONVIF discovery
export const onvifDiscoverySchema = z.object({
  ip_range: z
    .string()
    .min(1, 'IP диапазон обязателен')
    .regex(/^(\d{1,3}\.){3}\d{1,3}\/\d{1,2}$/, 'Некорректный IP диапазон'),
  port: z
    .number()
    .int()
    .min(1, 'Порт должен быть от 1 до 65535')
    .max(65535, 'Порт должен быть от 1 до 65535')
    .default(80),
  timeout: z
    .number()
    .int()
    .min(1, 'Таймаут должен быть от 1 до 60')
    .max(60, 'Таймаут должен быть от 1 до 60')
    .default(5),
});

// Схема валидации для экспорта записи
export const exportRecordingSchema = z.object({
  startTime: z
    .string()
    .min(1, 'Время начала обязательно'),
  endTime: z
    .string()
    .min(1, 'Время окончания обязательно'),
  format: z
    .enum(['mp4', 'avi', 'mkv'])
    .default('mp4'),
}).refine((data) => new Date(data.startTime) < new Date(data.endTime), {
  message: 'Время окончания должно быть позже времени начала',
  path: ['endTime'],
});

// Схема валидации для настроек хранения
export const storageSettingsSchema = z.object({
  maxStorageDays: z
    .number()
    .int()
    .min(1, 'Минимум 1 день')
    .max(3650, 'Максимум 3650 дней'),
  maxStorageSizeGB: z
    .number()
    .int()
    .min(1, 'Минимум 1 ГБ'),
  autoCleanup: z
    .boolean()
    .default(true),
  cleanupTime: z
    .string()
    .regex(/^([01]?[0-9]|2[0-3]):[0-5][0-9]$/, 'Некорректное время (HH:MM)'),
});

// Схема валидации для настроек записи
export const recordingSettingsSchema = z.object({
  defaultRecordingType: z
    .enum(['continuous', 'motion', 'event'])
    .default('continuous'),
  videoCodec: z
    .enum(['h264', 'h265', 'mjpeg'])
    .default('h264'),
  videoBitrate: z
    .number()
    .int()
    .min(100, 'Минимум 100 Кбит/с')
    .max(20000, 'Максимум 20000 Кбит/с'),
  videoResolution: z
    .enum(['720p', '1080p', '4K'])
    .default('1080p'),
  fps: z
    .number()
    .int()
    .min(1, 'Минимум 1 FPS')
    .max(60, 'Максимум 60 FPS')
    .default(25),
  audioEnabled: z
    .boolean()
    .default(false),
  audioCodec: z
    .enum(['aac', 'mp3', 'opus'])
    .default('aac'),
});

// Схема валидации для настроек уведомлений
export const notificationSettingsSchema = z.object({
  emailEnabled: z
    .boolean()
    .default(false),
  emailRecipients: z
    .array(z.string().email('Некорректный email'))
    .min(1, 'Минимум один получатель')
    .optional(),
  webhookEnabled: z
    .boolean()
    .default(false),
  webhookUrl: z
    .string()
    .url('Некорректный URL')
    .optional(),
  eventTypes: z
    .array(z.string())
    .min(1, 'Выберите хотя бы один тип события'),
});

// Схема валидации для расписания
export const scheduleSchema = z.object({
  name: z
    .string()
    .min(1, 'Название обязательно')
    .max(100, 'Максимум 100 символов'),
  cameraId: z
    .string()
    .min(1, 'Камера обязательна'),
  daysOfWeek: z
    .array(z.number().min(0).max(6))
    .min(1, 'Выберите хотя бы один день недели'),
  startTime: z
    .string()
    .regex(/^([01]?[0-9]|2[0-3]):[0-5][0-9]$/, 'Некорректное время (HH:MM)'),
  endTime: z
    .string()
    .regex(/^([01]?[0-9]|2[0-3]):[0-5][0-9]$/, 'Некорректное время (HH:MM)'),
  recordingType: z
    .enum(['continuous', 'motion', 'event'])
    .default('continuous'),
  enabled: z
    .boolean()
    .default(true),
}).refine((data) => data.startTime < data.endTime, {
  message: 'Время окончания должно быть позже времени начала',
  path: ['endTime'],
});

// Функция валидации формы
export const validateForm = (schema, data) => {
  try {
    schema.parse(data);
    return { success: true, errors: null };
  } catch (error) {
    if (error instanceof z.ZodError) {
      const errors = {};
      error.errors.forEach((err) => {
        const path = err.path.join('.');
        errors[path] = err.message;
      });
      return { success: false, errors };
    }
    return { success: false, errors: { general: 'Ошибка валидации' } };
  }
};

// Функция валидации поля
export const validateField = (schema, field, value) => {
  try {
    const fieldSchema = schema.shape[field];
    if (fieldSchema) {
      fieldSchema.parse(value);
    }
    return { success: true, error: null };
  } catch (error) {
    if (error instanceof z.ZodError) {
      return {
        success: false,
        error: error.errors[0]?.message || 'Ошибка валидации',
      };
    }
    return { success: false, error: 'Ошибка валидации' };
  }
};

// Валидация RTSP URL
export const isValidRTSPUrl = (url) => {
  try {
    const parsed = new URL(url);
    return parsed.protocol === 'rtsp:';
  } catch {
    return false;
  }
};

// Валидация IP адреса
export const isValidIP = (ip) => {
  const ipRegex = /^(\d{1,3}\.){3}\d{1,3}$/;
  if (!ipRegex.test(ip)) return false;
  return ip.split('.').every((octet) => {
    const num = parseInt(octet, 10);
    return num >= 0 && num <= 255;
  });
};

// Валидация порта
export const isValidPort = (port) => {
  const num = parseInt(port, 10);
  return !isNaN(num) && num >= 1 && num <= 65535;
};

// Валидация email
export const isValidEmail = (email) => {
  const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
  return emailRegex.test(email);
};

// Валидация времени (HH:MM)
export const isValidTime = (time) => {
  const timeRegex = /^([01]?[0-9]|2[0-3]):[0-5][0-9]$/;
  return timeRegex.test(time);
};
