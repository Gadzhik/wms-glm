// API URL
export const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000/api';
export const WS_URL = import.meta.env.VITE_WS_URL || 'ws://localhost:8000/ws';

// Приложение
export const APP_NAME = import.meta.env.VITE_APP_NAME || 'VMS';
export const APP_VERSION = import.meta.env.VITE_APP_VERSION || '1.0.0';

// Роли пользователей
export const USER_ROLES = {
  ADMIN: 'admin',
  OPERATOR: 'operator',
  VIEWER: 'viewer',
};

// Права доступа
export const PERMISSIONS = {
  // Камеры
  CAMERAS_VIEW: 'cameras:view',
  CAMERAS_CREATE: 'cameras:create',
  CAMERAS_UPDATE: 'cameras:update',
  CAMERAS_DELETE: 'cameras:delete',
  CAMERAS_CONTROL: 'cameras:control',

  // Записи
  RECORDINGS_VIEW: 'recordings:view',
  RECORDINGS_EXPORT: 'recordings:export',
  RECORDINGS_DELETE: 'recordings:delete',

  // События
  EVENTS_VIEW: 'events:view',
  EVENTS_MANAGE: 'events:manage',

  // Настройки
  SETTINGS_VIEW: 'settings:view',
  SETTINGS_UPDATE: 'settings:update',

  // Пользователи
  USERS_VIEW: 'users:view',
  USERS_CREATE: 'users:create',
  USERS_UPDATE: 'users:update',
  USERS_DELETE: 'users:delete',
};

// Статусы камеры
export const CAMERA_STATUS = {
  ONLINE: 'online',
  OFFLINE: 'offline',
  ERROR: 'error',
  RECORDING: 'recording',
  IDLE: 'idle',
};

// Типы записи
export const RECORDING_TYPES = {
  CONTINUOUS: 'continuous',
  MOTION: 'motion',
  EVENT: 'event',
  MANUAL: 'manual',
};

// Типы событий
export const EVENT_TYPES = {
  MOTION: 'motion',
  INTRUSION: 'intrusion',
  LINE_CROSS: 'line_cross',
  OBJECT_LEFT: 'object_left',
  OBJECT_REMOVED: 'object_removed',
  FACE_DETECTION: 'face_detection',
  LICENSE_PLATE: 'license_plate',
  AUDIO_DETECTION: 'audio_detection',
  SYSTEM: 'system',
  MANUAL: 'manual',
};

// Кодеки видео
export const VIDEO_CODECS = {
  H264: 'h264',
  H265: 'h265',
  MJPEG: 'mjpeg',
};

// Разрешения видео
export const VIDEO_RESOLUTIONS = {
  '720p': '1280x720',
  '1080p': '1920x1080',
  '4K': '3840x2160',
};

// Кодеки аудио
export const AUDIO_CODECS = {
  AAC: 'aac',
  MP3: 'mp3',
  OPUS: 'opus',
};

// Форматы экспорта
export const EXPORT_FORMATS = {
  MP4: 'mp4',
  AVI: 'avi',
  MKV: 'mkv',
};

// Дни недели
export const DAYS_OF_WEEK = {
  0: 'Воскресенье',
  1: 'Понедельник',
  2: 'Вторник',
  3: 'Среда',
  4: 'Четверг',
  5: 'Пятница',
  6: 'Суббота',
};

// Сокращенные дни недели
export const DAYS_OF_WEEK_SHORT = {
  0: 'Вс',
  1: 'Пн',
  2: 'Вт',
  3: 'Ср',
  4: 'Чт',
  5: 'Пт',
  6: 'Сб',
};

// Типы уведомлений
export const NOTIFICATION_TYPES = {
  EMAIL: 'email',
  WEBHOOK: 'webhook',
  SMS: 'sms',
};

// Приоритеты событий
export const EVENT_PRIORITIES = {
  LOW: 'low',
  MEDIUM: 'medium',
  HIGH: 'high',
  CRITICAL: 'critical',
};

// Направления PTZ
export const PTZ_DIRECTIONS = {
  UP: 'up',
  DOWN: 'down',
  LEFT: 'left',
  RIGHT: 'right',
  UP_LEFT: 'up_left',
  UP_RIGHT: 'up_right',
  DOWN_LEFT: 'down_left',
  DOWN_RIGHT: 'down_right',
  ZOOM_IN: 'zoom_in',
  ZOOM_OUT: 'zoom_out',
};

// Значения по умолчанию
export const DEFAULTS = {
  PAGE_SIZE: 20,
  MAX_PAGE_SIZE: 100,
  WS_RECONNECT_DELAY: 5000,
  WS_MAX_RECONNECT_ATTEMPTS: 10,
  SNAPSHOT_REFRESH_INTERVAL: 30000, // 30 секунд
  EVENT_POLL_INTERVAL: 10000, // 10 секунд
  RECORDING_PREVIEW_DURATION: 5, // 5 секунд
  EXPORT_TIMEOUT: 300000, // 5 минут
};

// Лимиты
export const LIMITS = {
  MAX_CAMERAS: 1000,
  MAX_RECORDINGS_PER_CAMERA: 10000,
  MAX_EVENTS_PER_CAMERA: 100000,
  MAX_CONCURRENT_STREAMS: 100,
  MAX_EXPORT_SIZE_GB: 10,
  MAX_SCHEDULES_PER_CAMERA: 10,
};

// Цвета для графиков
export const CHART_COLORS = [
  '#0ea5e9', // primary-500
  '#22c55e', // success-500
  '#f59e0b', // warning-500
  '#ef4444', // danger-500
  '#8b5cf6', // violet-500
  '#ec4899', // pink-500
  '#14b8a6', // teal-500
  '#f97316', // orange-500
];

// Локализация
export const LOCALE = 'ru-RU';
export const TIMEZONE = 'Europe/Moscow';

// Форматы даты и времени
export const DATE_FORMATS = {
  DATE: 'DD.MM.YYYY',
  TIME: 'HH:mm:ss',
  DATETIME: 'DD.MM.YYYY HH:mm:ss',
  DATETIME_SHORT: 'DD.MM.YYYY HH:mm',
  ISO: 'YYYY-MM-DDTHH:mm:ss',
};

// Параметры пагинации
export const PAGINATION_OPTIONS = [10, 20, 50, 100];

// Типы сортировки
export const SORT_ORDERS = {
  ASC: 'asc',
  DESC: 'desc',
};

// Поля сортировки для записей
export const RECORDING_SORT_FIELDS = [
  { value: 'start_time', label: 'Время начала' },
  { value: 'end_time', label: 'Время окончания' },
  { value: 'duration', label: 'Длительность' },
  { value: 'file_size', label: 'Размер файла' },
];

// Поля сортировки для событий
export const EVENT_SORT_FIELDS = [
  { value: 'timestamp', label: 'Время' },
  { value: 'type', label: 'Тип' },
  { value: 'priority', label: 'Приоритет' },
];

// Типы фильтров для событий
export const EVENT_FILTER_TYPES = [
  { value: 'all', label: 'Все' },
  { value: 'motion', label: 'Движение' },
  { value: 'intrusion', label: 'Проникновение' },
  { value: 'line_cross', label: 'Пересечение линии' },
  { value: 'face_detection', label: 'Обнаружение лица' },
  { value: 'license_plate', label: 'Распознавание номера' },
];

// Типы фильтров для записей
export const RECORDING_FILTER_TYPES = [
  { value: 'all', label: 'Все' },
  { value: 'continuous', label: 'Непрерывные' },
  { value: 'motion', label: 'По движению' },
  { value: 'event', label: 'По событию' },
  { value: 'manual', label: 'Ручные' },
];

// Статусы экспорта
export const EXPORT_STATUS = {
  PENDING: 'pending',
  PROCESSING: 'processing',
  COMPLETED: 'completed',
  FAILED: 'failed',
};

// Сообщения ошибок
export const ERROR_MESSAGES = {
  NETWORK_ERROR: 'Ошибка сети. Проверьте подключение к интернету.',
  SERVER_ERROR: 'Ошибка сервера. Попробуйте позже.',
  UNAUTHORIZED: 'Не авторизован. Войдите в систему.',
  FORBIDDEN: 'Нет доступа к этому ресурсу.',
  NOT_FOUND: 'Ресурс не найден.',
  VALIDATION_ERROR: 'Ошибка валидации данных.',
  UNKNOWN_ERROR: 'Произошла неизвестная ошибка.',
};

// Успешные сообщения
export const SUCCESS_MESSAGES = {
  CAMERA_CREATED: 'Камера успешно создана',
  CAMERA_UPDATED: 'Камера успешно обновлена',
  CAMERA_DELETED: 'Камера успешно удалена',
  RECORDING_EXPORTED: 'Запись успешно экспортирована',
  SETTINGS_SAVED: 'Настройки успешно сохранены',
  PASSWORD_CHANGED: 'Пароль успешно изменен',
  SCHEDULE_CREATED: 'Расписание успешно создано',
  SCHEDULE_UPDATED: 'Расписание успешно обновлено',
  SCHEDULE_DELETED: 'Расписание успешно удалено',
};

// Ключи localStorage
export const STORAGE_KEYS = {
  THEME: 'vms-theme',
  SIDEBAR_COLLAPSED: 'vms-sidebar-collapsed',
  GRID_VIEW_CAMERAS: 'vms-grid-view-cameras',
  GRID_VIEW_EVENTS: 'vms-grid-view-events',
  PAGE_SIZE: 'vms-page-size',
};
