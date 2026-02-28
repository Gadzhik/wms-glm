import dayjs from 'dayjs';
import relativeTime from 'dayjs/plugin/relativeTime';
import duration from 'dayjs/plugin/duration';
import 'dayjs/locale/ru';

dayjs.extend(relativeTime);
dayjs.extend(duration);
dayjs.locale('ru');

// Форматирование даты и времени
export const formatDateTime = (date, format = 'DD.MM.YYYY HH:mm:ss') => {
  if (!date) return '-';
  return dayjs(date).format(format);
};

// Форматирование только даты
export const formatDate = (date, format = 'DD.MM.YYYY') => {
  if (!date) return '-';
  return dayjs(date).format(format);
};

// Форматирование только времени
export const formatTime = (date, format = 'HH:mm:ss') => {
  if (!date) return '-';
  return dayjs(date).format(format);
};

// Относительное время (например, "5 минут назад")
export const formatRelativeTime = (date) => {
  if (!date) return '-';
  return dayjs(date).fromNow();
};

// Форматирование длительности
export const formatDuration = (seconds) => {
  if (!seconds && seconds !== 0) return '-';
  const dur = dayjs.duration(seconds, 'seconds');
  const hours = Math.floor(dur.asHours());
  const minutes = dur.minutes();
  const secs = dur.seconds();

  if (hours > 0) {
    return `${hours}:${String(minutes).padStart(2, '0')}:${String(secs).padStart(2, '0')}`;
  }
  return `${minutes}:${String(secs).padStart(2, '0')}`;
};

// Форматирование размера файла
export const formatFileSize = (bytes) => {
  if (!bytes && bytes !== 0) return '-';
  const units = ['B', 'KB', 'MB', 'GB', 'TB'];
  let size = bytes;
  let unitIndex = 0;

  while (size >= 1024 && unitIndex < units.length - 1) {
    size /= 1024;
    unitIndex++;
  }

  return `${size.toFixed(2)} ${units[unitIndex]}`;
};

// Форматирование числа с разделителями
export const formatNumber = (number, locale = 'ru-RU') => {
  if (number === null || number === undefined) return '-';
  return new Intl.NumberFormat(locale).format(number);
};

// Форматирование процента
export const formatPercent = (value, decimals = 1) => {
  if (value === null || value === undefined) return '-';
  return `${value.toFixed(decimals)}%`;
};

// Форматирование статуса
export const formatStatus = (status) => {
  const statusMap = {
    online: 'Онлайн',
    offline: 'Офлайн',
    error: 'Ошибка',
    recording: 'Запись',
    idle: 'Ожидание',
    active: 'Активен',
    inactive: 'Неактивен',
    pending: 'В ожидании',
    completed: 'Завершен',
    failed: 'Ошибка',
    processing: 'Обработка',
  };
  return statusMap[status] || status;
};

// Форматирование типа события
export const formatEventType = (eventType) => {
  const typeMap = {
    motion: 'Движение',
    intrusion: 'Проникновение',
    line_cross: 'Пересечение линии',
    object_left: 'Оставленный объект',
    object_removed: 'Удаленный объект',
    face_detection: 'Обнаружение лица',
    license_plate: 'Распознавание номера',
    audio_detection: 'Звуковое событие',
    system: 'Системное',
    manual: 'Ручное',
  };
  return typeMap[eventType] || eventType;
};

// Форматирование типа записи
export const formatRecordingType = (type) => {
  const typeMap = {
    continuous: 'Непрерывная',
    motion: 'По движению',
    event: 'По событию',
    manual: 'Ручная',
  };
  return typeMap[type] || type;
};

// Форматирование роли пользователя
export const formatRole = (role) => {
  const roleMap = {
    admin: 'Администратор',
    operator: 'Оператор',
    viewer: 'Наблюдатель',
  };
  return roleMap[role] || role;
};

// Получение цвета для статуса
export const getStatusColor = (status) => {
  const colorMap = {
    online: 'success',
    offline: 'danger',
    error: 'danger',
    recording: 'primary',
    idle: 'warning',
    active: 'success',
    inactive: 'warning',
    pending: 'warning',
    completed: 'success',
    failed: 'danger',
    processing: 'primary',
  };
  return colorMap[status] || 'default';
};

// Получение цвета для типа события
export const getEventTypeColor = (eventType) => {
  const colorMap = {
    motion: 'warning',
    intrusion: 'danger',
    line_cross: 'danger',
    object_left: 'warning',
    object_removed: 'warning',
    face_detection: 'primary',
    license_plate: 'primary',
    audio_detection: 'info',
    system: 'default',
    manual: 'default',
  };
  return colorMap[eventType] || 'default';
};

// Форматирование диапазона дат
export const formatDateRange = (startDate, endDate) => {
  const start = dayjs(startDate);
  const end = dayjs(endDate);

  if (start.isSame(end, 'day')) {
    return start.format('DD.MM.YYYY');
  }

  if (start.isSame(end, 'month')) {
    return `${start.format('DD')} - ${end.format('DD.MM.YYYY')}`;
  }

  if (start.isSame(end, 'year')) {
    return `${start.format('DD.MM')} - ${end.format('DD.MM.YYYY')}`;
  }

  return `${start.format('DD.MM.YYYY')} - ${end.format('DD.MM.YYYY')}`;
};

// Форматирование времени для таймлайна
export const formatTimelineTime = (date) => {
  return dayjs(date).format('HH:mm:ss');
};

// Парсинг длительности из строки (например, "01:30:45" в секунды)
export const parseDuration = (durationString) => {
  const parts = durationString.split(':').map(Number);
  if (parts.length === 3) {
    return parts[0] * 3600 + parts[1] * 60 + parts[2];
  }
  if (parts.length === 2) {
    return parts[0] * 60 + parts[1];
  }
  return parts[0] || 0;
};

// Получение текущей даты в нужном формате
export const getCurrentDate = (format = 'YYYY-MM-DD') => {
  return dayjs().format(format);
};

// Получение текущего времени в нужном формате
export const getCurrentTime = (format = 'HH:mm:ss') => {
  return dayjs().format(format);
};

// Получение текущей даты и времени
export const getCurrentDateTime = (format = 'YYYY-MM-DD HH:mm:ss') => {
  return dayjs().format(format);
};

// Получение начала дня
export const getStartOfDay = (date = new Date()) => {
  return dayjs(date).startOf('day').format('YYYY-MM-DD HH:mm:ss');
};

// Получение конца дня
export const getEndOfDay = (date = new Date()) => {
  return dayjs(date).endOf('day').format('YYYY-MM-DD HH:mm:ss');
};

// Получение начала месяца
export const getStartOfMonth = (date = new Date()) => {
  return dayjs(date).startOf('month').format('YYYY-MM-DD HH:mm:ss');
};

// Получение конца месяца
export const getEndOfMonth = (date = new Date()) => {
  return dayjs(date).endOf('month').format('YYYY-MM-DD HH:mm:ss');
};

// Получение даты N дней назад
export const getDateDaysAgo = (days) => {
  return dayjs().subtract(days, 'day').format('YYYY-MM-DD HH:mm:ss');
};

// Получение даты N дней вперед
export const getDateDaysAhead = (days) => {
  return dayjs().add(days, 'day').format('YYYY-MM-DD HH:mm:ss');
};
