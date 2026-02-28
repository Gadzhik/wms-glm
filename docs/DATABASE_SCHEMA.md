# VMS Database Schema

## Схема базы данных для Video Management System

**База данных:** SQLite 3.40+  
**Характеристики:** Встраиваемая, безсерверная, ACID транзакции  
**Масштаб:** 4-16 камер, 30 дней хранения записей

---

## 1. ER-диаграмма

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                              VMS Database Schema                            │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  ┌─────────────┐       ┌─────────────┐       ┌─────────────┐               │
│  │   users     │       │  cameras    │       │ recordings  │               │
│  │─────────────│       │─────────────│       │─────────────│               │
│  │ id (PK)     │       │ id (PK)     │       │ id (PK)     │               │
│  │ username    │       │ name        │       │ camera_id   │──────┐        │
│  │ email       │       │ rtsp_url    │       │ file_path   │      │        │
│  │ password_hash│      │ onvif_data  │       │ start_time  │      │        │
│  │ role        │       │ status      │       │ end_time    │      │        │
│  │ refresh_token│      │ recording_  │       │ file_size   │      │        │
│  │ created_at  │       │   settings  │       │ duration    │      │        │
│  │ last_login  │       │ detection_  │       │ is_encrypted│      │        │
│  └─────────────┘       │   settings  │       │ encryption_key│    │        │
│                         │ metadata    │       │ codec       │      │        │
│                         │ created_at  │       │ resolution  │      │        │
│                         │ updated_at  │       │ bitrate     │      │        │
│                         └──────┬──────┘       │ created_at  │      │        │
│                                │               └──────┬──────┘      │        │
│                                │                      │             │        │
│                                │                      │             │        │
│                                │               ┌──────▼──────┐      │        │
│                                │               │video_metadata│      │        │
│                                │               │──────────────│      │        │
│                                │               │ id (PK)      │      │        │
│                                │               │ recording_id │◄─────┘        │
│                                │               │ thumbnails   │               │
│                                │               │ detected_obj │               │
│                                │               │ motion_events│              │
│                                │               └──────────────┘               │
│                                │                                             │
│                         ┌────▼─────┐       ┌─────────────┐                 │
│                         │ schedules│       │   events    │                 │
│                         │───────────│       │─────────────│                 │
│                         │ id (PK)   │       │ id (PK)     │                 │
│                         │ camera_id │◄──────│ camera_id   │                 │
│                         │ days_of_  │       │ recording_id│                 │
│                         │   week     │       │ event_type  │                 │
│                         │ start_time│       │ timestamp   │                 │
│                         │ end_time  │       │ details     │                 │
│                         │ record_   │       │ status      │                 │
│                         │   type    │       │ push_sent   │                 │
│                         │ is_active │       └─────────────┘                 │
│                         └───────────┘                                      │
│                                                                             │
│  ┌─────────────┐       ┌─────────────┐                                     │
│  │    logs     │       │  settings   │                                     │
│  │─────────────│       │─────────────│                                     │
│  │ id (PK)     │       │ key (PK)    │                                     │
│  │ level       │       │ value       │                                     │
│  │ component   │       │ category    │                                     │
│  │ message     │       │ description │                                     │
│  │ details     │       │ updated_at  │                                     │
│  │ timestamp   │       └─────────────┘                                     │
│  └─────────────┘                                                           │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘

Типы связей:
─────────────────────────────────────────────────────────────────────────────
cameras → recordings        : 1:N (одна камера имеет много записей)
recordings → video_metadata : 1:1 (одна запись имеет метаданные)
cameras → schedules        : 1:N (одна камера имеет много расписаний)
cameras → events           : 1:N (одна камера генерирует много событий)
recordings → events        : 0:1 (событие может быть связано с записью)
users → (нет прямых связей): пользователи управляются через API
```

---

## 2. Детальное описание таблиц

### 2.1 Таблица: `users`

**Описание:** Хранит информацию о пользователях системы и их учетные данные.

| Колонка | Тип SQLite | Описание | Ограничения | Default |
|---------|------------|----------|-------------|---------|
| `id` | INTEGER | Уникальный идентификатор пользователя | PRIMARY KEY, AUTOINCREMENT | - |
| `username` | TEXT(50) | Имя пользователя для входа | NOT NULL, UNIQUE | - |
| `email` | TEXT(100) | Email адрес | NOT NULL, UNIQUE | - |
| `password_hash` | TEXT(255) | Хеш пароля (bcrypt) | NOT NULL | - |
| `role` | TEXT(20) | Роль пользователя | NOT NULL, CHECK(role IN ('admin', 'viewer')) | 'viewer' |
| `refresh_token` | TEXT(500) | JWT refresh токен | NULL | NULL |
| `created_at` | TEXT | Дата создания аккаунта | NOT NULL | CURRENT_TIMESTAMP |
| `last_login` | TEXT | Дата последнего входа | NULL | NULL |

**Индексы:**
- `idx_users_username` - для быстрого поиска по username при входе
- `idx_users_email` - для быстрого поиска по email

**Constraints:**
- `CHECK(role IN ('admin', 'viewer'))` - ограничение на допустимые роли

---

### 2.2 Таблица: `cameras`

**Описание:** Хранит информацию о IP камерах, их настройках и статусе.

| Колонка | Тип SQLite | Описание | Ограничения | Default |
|---------|------------|----------|-------------|---------|
| `id` | INTEGER | Уникальный идентификатор камеры | PRIMARY KEY, AUTOINCREMENT | - |
| `name` | TEXT(100) | Название камеры | NOT NULL | - |
| `rtsp_url` | TEXT(500) | RTSP URL для подключения | NOT NULL | - |
| `onvif_host` | TEXT(100) | ONVIF хост | NULL | NULL |
| `onvif_port` | INTEGER | ONVIF порт | NULL | 80 |
| `onvif_username` | TEXT(50) | ONVIF имя пользователя | NULL | NULL |
| `onvif_password` | TEXT(100) | ONVIF пароль (зашифрованный) | NULL | NULL |
| `status` | TEXT(20) | Статус камеры | NOT NULL, CHECK(status IN ('online', 'offline', 'error')) | 'offline' |
| `recording_mode` | TEXT(20) | Режим записи | NOT NULL, CHECK(recording_mode IN ('continuous', 'motion', 'scheduled')) | 'motion' |
| `detection_enabled` | INTEGER | Включена ли детекция (0/1) | NOT NULL | 1 |
| `detection_confidence` | REAL | Порог уверенности детекции (0.0-1.0) | NOT NULL, CHECK(detection_confidence >= 0 AND detection_confidence <= 1) | 0.5 |
| `resolution_width` | INTEGER | Ширина разрешения | NULL | NULL |
| `resolution_height` | INTEGER | Высота разрешения | NULL | NULL |
| `codec` | TEXT(20) | Видео кодек | NULL | NULL |
| `fps` | INTEGER | Кадров в секунду | NULL | NULL |
| `created_at` | TEXT | Дата добавления камеры | NOT NULL | CURRENT_TIMESTAMP |
| `updated_at` | TEXT | Дата последнего обновления | NOT NULL | CURRENT_TIMESTAMP |

**Индексы:**
- `idx_cameras_status` - для фильтрации камер по статусу
- `idx_cameras_name` - для поиска по названию

**Constraints:**
- `CHECK(status IN ('online', 'offline', 'error'))` - ограничение на статусы
- `CHECK(recording_mode IN ('continuous', 'motion', 'scheduled'))` - ограничение на режимы записи
- `CHECK(detection_confidence >= 0 AND detection_confidence <= 1)` - валидация порога уверенности

---

### 2.3 Таблица: `recordings`

**Описание:** Хранит информацию о записанных видеофайлах.

| Колонка | Тип SQLite | Описание | Ограничения | Default |
|---------|------------|----------|-------------|---------|
| `id` | INTEGER | Уникальный идентификатор записи | PRIMARY KEY, AUTOINCREMENT | - |
| `camera_id` | INTEGER | ID камеры (FK) | NOT NULL, REFERENCES cameras(id) ON DELETE CASCADE | - |
| `file_path` | TEXT(500) | Путь к файлу записи | NOT NULL | - |
| `recording_type` | TEXT(20) | Тип записи | NOT NULL, CHECK(recording_type IN ('continuous', 'motion', 'scheduled')) | 'motion' |
| `start_time` | TEXT | Время начала записи (ISO 8601) | NOT NULL | - |
| `end_time` | TEXT | Время окончания записи (ISO 8601) | NOT NULL | - |
| `file_size` | INTEGER | Размер файла в байтах | NOT NULL | 0 |
| `duration` | INTEGER | Длительность в секундах | NOT NULL | 0 |
| `is_encrypted` | INTEGER | Зашифрован ли файл (0/1) | NOT NULL | 0 |
| `encryption_key` | TEXT(255) | Ключ шифрования (если зашифрован) | NULL | NULL |
| `codec` | TEXT(20) | Видео кодек | NULL | NULL |
| `resolution_width` | INTEGER | Ширина разрешения | NULL | NULL |
| `resolution_height` | INTEGER | Высота разрешения | NULL | NULL |
| `bitrate` | INTEGER | Битрейт в kbps | NULL | NULL |
| `created_at` | TEXT | Дата создания записи | NOT NULL | CURRENT_TIMESTAMP |

**Индексы:**
- `idx_recordings_camera_id` - для поиска записей конкретной камеры
- `idx_recordings_start_time` - для поиска по времени начала (архив)
- `idx_recordings_camera_start` - составной индекс для архивных запросов
- `idx_recordings_recording_type` - для фильтрации по типу записи

**Constraints:**
- `CHECK(recording_type IN ('continuous', 'motion', 'scheduled'))` - ограничение на типы записи
- `CHECK(is_encrypted IN (0, 1))` - ограничение на флаг шифрования
- `FOREIGN KEY (camera_id) REFERENCES cameras(id) ON DELETE CASCADE` - каскадное удаление при удалении камеры

---

### 2.4 Таблица: `video_metadata`

**Описание:** Хранит метаданные для каждой записи (ключевые кадры, детекции, движение).

| Колонка | Тип SQLite | Описание | Ограничения | Default |
|---------|------------|----------|-------------|---------|
| `id` | INTEGER | Уникальный идентификатор метаданных | PRIMARY KEY, AUTOINCREMENT | - |
| `recording_id` | INTEGER | ID записи (FK) | NOT NULL, UNIQUE, REFERENCES recordings(id) ON DELETE CASCADE | - |
| `thumbnails` | TEXT | JSON с путями к ключевым кадрам | NULL | NULL |
| `detected_objects` | TEXT | JSON с детектированными объектами | NULL | NULL |
| `motion_events` | TEXT | JSON с событиями движения | NULL | NULL |

**Индексы:**
- `idx_video_metadata_recording_id` - для связи с записью (UNIQUE)

**Constraints:**
- `FOREIGN KEY (recording_id) REFERENCES recordings(id) ON DELETE CASCADE` - каскадное удаление

**JSON структура для `detected_objects`:**
```json
[
  {
    "timestamp": "2024-01-01T12:00:00Z",
    "type": "person",
    "confidence": 0.95,
    "bbox": {"x": 100, "y": 200, "width": 50, "height": 150}
  }
]
```

**JSON структура для `motion_events`:**
```json
[
  {
    "timestamp": "2024-01-01T12:00:00Z",
    "level": 0.75,
    "region": {"x": 0, "y": 0, "width": 640, "height": 480}
  }
]
```

---

### 2.5 Таблица: `events`

**Описание:** Хранит события системы (детекция, оффлайн камера, переполнение хранилища и т.д.).

| Колонка | Тип SQLite | Описание | Ограничения | Default |
|---------|------------|----------|-------------|---------|
| `id` | INTEGER | Уникальный идентификатор события | PRIMARY KEY, AUTOINCREMENT | - |
| `event_type` | TEXT(50) | Тип события | NOT NULL, CHECK(event_type IN ('motion_detected', 'person_detected', 'camera_offline', 'camera_error', 'storage_full', 'system_error')) | - |
| `camera_id` | INTEGER | ID камеры (FK) | NULL, REFERENCES cameras(id) ON DELETE SET NULL | NULL |
| `recording_id` | INTEGER | ID записи (FK) | NULL, REFERENCES recordings(id) ON DELETE SET NULL | NULL |
| `timestamp` | TEXT | Время события (ISO 8601) | NOT NULL | CURRENT_TIMESTAMP |
| `details` | TEXT | Дополнительные детали (JSON) | NULL | NULL |
| `status` | TEXT(20) | Статус события | NOT NULL, CHECK(status IN ('new', 'acknowledged', 'resolved')) | 'new' |
| `push_sent` | INTEGER | Отправлено ли push уведомление (0/1) | NOT NULL | 0 |

**Индексы:**
- `idx_events_camera_id` - для поиска событий камеры
- `idx_events_timestamp` - для поиска по времени
- `idx_events_event_type` - для фильтрации по типу события
- `idx_events_status` - для фильтрации по статусу
- `idx_events_camera_timestamp` - составной индекс для архивных запросов

**Constraints:**
- `CHECK(event_type IN ('motion_detected', 'person_detected', 'camera_offline', 'camera_error', 'storage_full', 'system_error'))` - ограничение на типы событий
- `CHECK(status IN ('new', 'acknowledged', 'resolved'))` - ограничение на статусы
- `CHECK(push_sent IN (0, 1))` - ограничение на флаг отправки

---

### 2.6 Таблица: `logs`

**Описание:** Хранит логи системы для отладки и мониторинга.

| Колонка | Тип SQLite | Описание | Ограничения | Default |
|---------|------------|----------|-------------|---------|
| `id` | INTEGER | Уникальный идентификатор лога | PRIMARY KEY, AUTOINCREMENT | - |
| `level` | TEXT(10) | Уровень логирования | NOT NULL, CHECK(level IN ('DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL')) | - |
| `component` | TEXT(50) | Компонент системы | NOT NULL | - |
| `message` | TEXT(1000) | Сообщение лога | NOT NULL | - |
| `details` | TEXT | Дополнительные детали (JSON) | NULL | NULL |
| `timestamp` | TEXT | Время лога (ISO 8601) | NOT NULL | CURRENT_TIMESTAMP |

**Индексы:**
- `idx_logs_level` - для фильтрации по уровню
- `idx_logs_component` - для фильтрации по компоненту
- `idx_logs_timestamp` - для поиска по времени
- `idx_logs_level_timestamp` - составной индекс для очистки старых логов

**Constraints:**
- `CHECK(level IN ('DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL'))` - ограничение на уровни логирования

---

### 2.7 Таблица: `settings`

**Описание:** Хранит настройки системы.

| Колонка | Тип SQLite | Описание | Ограничения | Default |
|---------|------------|----------|-------------|---------|
| `key` | TEXT(100) | Ключ настройки | PRIMARY KEY | - |
| `value` | TEXT | Значение настройки (JSON) | NOT NULL | - |
| `category` | TEXT(50) | Категория настройки | NOT NULL, CHECK(category IN ('storage', 'recording', 'detection', 'notification', 'system', 'auth')) | - |
| `description` | TEXT(500) | Описание настройки | NULL | NULL |
| `updated_at` | TEXT | Дата последнего обновления | NOT NULL | CURRENT_TIMESTAMP |

**Индексы:**
- `idx_settings_category` - для фильтрации по категории

**Constraints:**
- `CHECK(category IN ('storage', 'recording', 'detection', 'notification', 'system', 'auth'))` - ограничение на категории

**Примеры настроек:**
```json
{
  "storage.retention_days": "30",
  "storage.max_disk_usage_gb": "1000",
  "recording.continuous_fps": "15",
  "detection.confidence_threshold": "0.5",
  "notification.telegram_enabled": "true"
}
```

---

### 2.8 Таблица: `schedules`

**Описание:** Хранит расписания записей для камер.

| Колонка | Тип SQLite | Описание | Ограничения | Default |
|---------|------------|----------|-------------|---------|
| `id` | INTEGER | Уникальный идентификатор расписания | PRIMARY KEY, AUTOINCREMENT | - |
| `camera_id` | INTEGER | ID камеры (FK) | NOT NULL, REFERENCES cameras(id) ON DELETE CASCADE | - |
| `days_of_week` | TEXT | Дни недели (JSON array, 0-6) | NOT NULL | - |
| `start_time` | TEXT | Время начала (HH:MM) | NOT NULL | - |
| `end_time` | TEXT | Время окончания (HH:MM) | NOT NULL | - |
| `record_type` | TEXT(20) | Тип записи | NOT NULL, CHECK(record_type IN ('continuous', 'motion')) | 'continuous' |
| `is_active` | INTEGER | Активно ли расписание (0/1) | NOT NULL | 1 |

**Индексы:**
- `idx_schedules_camera_id` - для поиска расписаний камеры
- `idx_schedules_is_active` - для фильтрации активных расписаний

**Constraints:**
- `CHECK(record_type IN ('continuous', 'motion'))` - ограничение на типы записи
- `CHECK(is_active IN (0, 1))` - ограничение на флаг активности
- `FOREIGN KEY (camera_id) REFERENCES cameras(id) ON DELETE CASCADE` - каскадное удаление

**JSON структура для `days_of_week`:**
```json
[0, 1, 2, 3, 4]  // 0=воскресенье, 1=понедельник, ..., 6=суббота
```

---

## 3. SQL DDL скрипты

### 3.1 Создание таблиц

```sql
-- ============================================
-- VMS Database Schema - SQLite
-- Version: 1.0
-- ============================================

PRAGMA foreign_keys = ON;
PRAGMA journal_mode = WAL;
PRAGMA synchronous = NORMAL;
PRAGMA cache_size = -64000;  -- 64MB cache
PRAGMA temp_store = MEMORY;
PRAGMA mmap_size = 268435456;  -- 256MB mmap

-- ============================================
-- Table: users
-- ============================================
CREATE TABLE users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT(50) NOT NULL UNIQUE,
    email TEXT(100) NOT NULL UNIQUE,
    password_hash TEXT(255) NOT NULL,
    role TEXT(20) NOT NULL DEFAULT 'viewer' CHECK(role IN ('admin', 'viewer')),
    refresh_token TEXT(500),
    created_at TEXT NOT NULL DEFAULT (datetime('now')),
    last_login TEXT
);

-- ============================================
-- Table: cameras
-- ============================================
CREATE TABLE cameras (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT(100) NOT NULL,
    rtsp_url TEXT(500) NOT NULL,
    onvif_host TEXT(100),
    onvif_port INTEGER DEFAULT 80,
    onvif_username TEXT(50),
    onvif_password TEXT(100),
    status TEXT(20) NOT NULL DEFAULT 'offline' CHECK(status IN ('online', 'offline', 'error')),
    recording_mode TEXT(20) NOT NULL DEFAULT 'motion' CHECK(recording_mode IN ('continuous', 'motion', 'scheduled')),
    detection_enabled INTEGER NOT NULL DEFAULT 1 CHECK(detection_enabled IN (0, 1)),
    detection_confidence REAL NOT NULL DEFAULT 0.5 CHECK(detection_confidence >= 0 AND detection_confidence <= 1),
    resolution_width INTEGER,
    resolution_height INTEGER,
    codec TEXT(20),
    fps INTEGER,
    created_at TEXT NOT NULL DEFAULT (datetime('now')),
    updated_at TEXT NOT NULL DEFAULT (datetime('now'))
);

-- ============================================
-- Table: recordings
-- ============================================
CREATE TABLE recordings (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    camera_id INTEGER NOT NULL,
    file_path TEXT(500) NOT NULL,
    recording_type TEXT(20) NOT NULL DEFAULT 'motion' CHECK(recording_type IN ('continuous', 'motion', 'scheduled')),
    start_time TEXT NOT NULL,
    end_time TEXT NOT NULL,
    file_size INTEGER NOT NULL DEFAULT 0,
    duration INTEGER NOT NULL DEFAULT 0,
    is_encrypted INTEGER NOT NULL DEFAULT 0 CHECK(is_encrypted IN (0, 1)),
    encryption_key TEXT(255),
    codec TEXT(20),
    resolution_width INTEGER,
    resolution_height INTEGER,
    bitrate INTEGER,
    created_at TEXT NOT NULL DEFAULT (datetime('now')),
    FOREIGN KEY (camera_id) REFERENCES cameras(id) ON DELETE CASCADE
);

-- ============================================
-- Table: video_metadata
-- ============================================
CREATE TABLE video_metadata (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    recording_id INTEGER NOT NULL UNIQUE,
    thumbnails TEXT,
    detected_objects TEXT,
    motion_events TEXT,
    FOREIGN KEY (recording_id) REFERENCES recordings(id) ON DELETE CASCADE
);

-- ============================================
-- Table: events
-- ============================================
CREATE TABLE events (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    event_type TEXT(50) NOT NULL CHECK(event_type IN ('motion_detected', 'person_detected', 'camera_offline', 'camera_error', 'storage_full', 'system_error')),
    camera_id INTEGER,
    recording_id INTEGER,
    timestamp TEXT NOT NULL DEFAULT (datetime('now')),
    details TEXT,
    status TEXT(20) NOT NULL DEFAULT 'new' CHECK(status IN ('new', 'acknowledged', 'resolved')),
    push_sent INTEGER NOT NULL DEFAULT 0 CHECK(push_sent IN (0, 1)),
    FOREIGN KEY (camera_id) REFERENCES cameras(id) ON DELETE SET NULL,
    FOREIGN KEY (recording_id) REFERENCES recordings(id) ON DELETE SET NULL
);

-- ============================================
-- Table: logs
-- ============================================
CREATE TABLE logs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    level TEXT(10) NOT NULL CHECK(level IN ('DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL')),
    component TEXT(50) NOT NULL,
    message TEXT(1000) NOT NULL,
    details TEXT,
    timestamp TEXT NOT NULL DEFAULT (datetime('now'))
);

-- ============================================
-- Table: settings
-- ============================================
CREATE TABLE settings (
    key TEXT(100) PRIMARY KEY,
    value TEXT NOT NULL,
    category TEXT(50) NOT NULL CHECK(category IN ('storage', 'recording', 'detection', 'notification', 'system', 'auth')),
    description TEXT(500),
    updated_at TEXT NOT NULL DEFAULT (datetime('now'))
);

-- ============================================
-- Table: schedules
-- ============================================
CREATE TABLE schedules (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    camera_id INTEGER NOT NULL,
    days_of_week TEXT NOT NULL,
    start_time TEXT NOT NULL,
    end_time TEXT NOT NULL,
    record_type TEXT(20) NOT NULL DEFAULT 'continuous' CHECK(record_type IN ('continuous', 'motion')),
    is_active INTEGER NOT NULL DEFAULT 1 CHECK(is_active IN (0, 1)),
    FOREIGN KEY (camera_id) REFERENCES cameras(id) ON DELETE CASCADE
);
```

### 3.2 Создание индексов

```sql
-- ============================================
-- Indexes for users table
-- ============================================
CREATE INDEX idx_users_username ON users(username);
CREATE INDEX idx_users_email ON users(email);

-- ============================================
-- Indexes for cameras table
-- ============================================
CREATE INDEX idx_cameras_status ON cameras(status);
CREATE INDEX idx_cameras_name ON cameras(name);

-- ============================================
-- Indexes for recordings table
-- ============================================
CREATE INDEX idx_recordings_camera_id ON recordings(camera_id);
CREATE INDEX idx_recordings_start_time ON recordings(start_time);
CREATE INDEX idx_recordings_camera_start ON recordings(camera_id, start_time);
CREATE INDEX idx_recordings_recording_type ON recordings(recording_type);

-- ============================================
-- Indexes for video_metadata table
-- ============================================
CREATE INDEX idx_video_metadata_recording_id ON video_metadata(recording_id);

-- ============================================
-- Indexes for events table
-- ============================================
CREATE INDEX idx_events_camera_id ON events(camera_id);
CREATE INDEX idx_events_timestamp ON events(timestamp);
CREATE INDEX idx_events_event_type ON events(event_type);
CREATE INDEX idx_events_status ON events(status);
CREATE INDEX idx_events_camera_timestamp ON events(camera_id, timestamp);

-- ============================================
-- Indexes for logs table
-- ============================================
CREATE INDEX idx_logs_level ON logs(level);
CREATE INDEX idx_logs_component ON logs(component);
CREATE INDEX idx_logs_timestamp ON logs(timestamp);
CREATE INDEX idx_logs_level_timestamp ON logs(level, timestamp);

-- ============================================
-- Indexes for settings table
-- ============================================
CREATE INDEX idx_settings_category ON settings(category);

-- ============================================
-- Indexes for schedules table
-- ============================================
CREATE INDEX idx_schedules_camera_id ON schedules(camera_id);
CREATE INDEX idx_schedules_is_active ON schedules(is_active);
```

### 3.3 Комментарии к таблицам и колонкам

```sql
-- SQLite не поддерживает COMMENT ON TABLE/COLUMN напрямую
-- Используйте следующие SQL команды для просмотра схемы:
-- .schema [table_name]
-- PRAGMA table_info([table_name]);

-- Для документации используйте отдельный файл или комментарии в коде
```

---

## 4. Оптимизация

### 4.1 Индексы для частых запросов

**Запрос 1: Получение списка камер с фильтрацией по статусу**
```sql
-- Индекс: idx_cameras_status
SELECT * FROM cameras WHERE status = 'online';
```

**Запрос 2: Поиск записей для архива (по камере и времени)**
```sql
-- Индекс: idx_recordings_camera_start
SELECT * FROM recordings 
WHERE camera_id = ? 
  AND start_time >= ? 
  AND end_time <= ?
ORDER BY start_time;
```

**Запрос 3: Получение событий камеры за период**
```sql
-- Индекс: idx_events_camera_timestamp
SELECT * FROM events 
WHERE camera_id = ? 
  AND timestamp >= ? 
  AND timestamp <= ?
ORDER BY timestamp DESC;
```

**Запрос 4: Очистка старых логов**
```sql
-- Индекс: idx_logs_level_timestamp
DELETE FROM logs 
WHERE level IN ('DEBUG', 'INFO') 
  AND timestamp < datetime('now', '-7 days');
```

**Запрос 5: Получение активных расписаний**
```sql
-- Индекс: idx_schedules_is_active
SELECT s.*, c.name as camera_name 
FROM schedules s
JOIN cameras c ON s.camera_id = c.id
WHERE s.is_active = 1;
```

### 4.2 Оптимизация хранения больших объемов данных

**Для таблицы `recordings` (самая большая таблица):**

1. **WAL Mode (Write-Ahead Logging):**
   ```sql
   PRAGMA journal_mode = WAL;
   ```
   - Увеличивает производительность записи
   - Позволяет одновременное чтение и запись

2. **Размер кэша:**
   ```sql
   PRAGMA cache_size = -64000;  -- 64MB cache
   ```
   - Увеличивает кэш для частых запросов

3. **Memory-Mapped I/O:**
   ```sql
   PRAGMA mmap_size = 268435456;  -- 256MB mmap
   ```
   - Ускоряет доступ к файлу БД

4. **Очистка старых записей:**
   ```sql
   -- Удаление записей старше 30 дней
   DELETE FROM recordings 
   WHERE start_time < datetime('now', '-30 days');
   
   -- После удаления выполнить VACUUM для освобождения места
   VACUUM;
   ```

5. **Архивирование старых данных:**
   ```sql
   -- Создание таблицы для архива
   CREATE TABLE recordings_archive (
       -- такая же структура как recordings
   );
   
   -- Перенос старых записей в архив
   INSERT INTO recordings_archive
   SELECT * FROM recordings
   WHERE start_time < datetime('now', '-30 days');
   
   -- Удаление из основной таблицы
   DELETE FROM recordings
   WHERE start_time < datetime('now', '-30 days');
   ```

**Для таблицы `events`:**

1. **Ограничение количества событий:**
   ```sql
   -- Удаление событий старше 7 дней (кроме resolved)
   DELETE FROM events 
   WHERE status != 'resolved' 
     AND timestamp < datetime('now', '-7 days');
   ```

2. **Архивирование resolved событий:**
   ```sql
   CREATE TABLE events_archive (
       -- такая же структура как events
   );
   
   INSERT INTO events_archive
   SELECT * FROM events
   WHERE status = 'resolved'
     AND timestamp < datetime('now', '-30 days');
   
   DELETE FROM events
   WHERE status = 'resolved'
     AND timestamp < datetime('now', '-30 days');
   ```

**Для таблицы `logs`:**

1. **Ротация логов:**
   ```sql
   -- Удаление DEBUG и INFO логов старше 7 дней
   DELETE FROM logs 
   WHERE level IN ('DEBUG', 'INFO') 
     AND timestamp < datetime('now', '-7 days');
   
   -- Удаление WARNING логов старше 30 дней
   DELETE FROM logs 
   WHERE level = 'WARNING' 
     AND timestamp < datetime('now', '-30 days');
   
   -- ERROR и CRITICAL логи хранить всегда
   ```

### 4.3 VACUUM и оптимизация

**Регулярное выполнение VACUUM:**
```sql
-- Полная перестройка БД для освобождения места
VACUUM;

-- Анализ таблиц для оптимизации запросов
ANALYZE;
```

**Рекомендации по расписанию:**
- `VACUUM`: раз в неделю ночью (когда минимальная нагрузка)
- `ANALYZE`: после удаления большого количества данных

### 4.4 Оптимизация JSON полей

SQLite не имеет встроенной поддержки JSON, но может хранить JSON как TEXT.

**Для поиска в JSON полях используйте:**
- Python/приложение для парсинга JSON
- SQLite JSON1 extension (если доступна)

```sql
-- Включение JSON1 extension (если поддерживается)
SELECT json_extract(detected_objects, '$[0].type') 
FROM video_metadata 
WHERE recording_id = ?;
```

### 4.5 Резервное копирование

**Онлайн бэкап:**
```sql
-- Создание бэкапа без блокировки
.backup 'backup_vms_' || datetime('now', 'unixepoch') || '.db'
```

**Офлайн бэкап:**
```bash
# Копирование файла БД (когда приложение остановлено)
cp vms.db vms_backup_$(date +%Y%m%d_%H%M%S).db
```

---

## 5. Миграции

### 5.1 Рекомендации по инструменту миграций

**Alembic** - рекомендуемый инструмент для миграций в Python проектах.

**Почему Alembic:**
- Полная интеграция с SQLAlchemy ORM
- Автоматическая генерация миграций
- Поддержка отката миграций
- Версионирование миграций
- Отличная документация

**Альтернативы:**
- **SQLAlchemy-Migrate** - устаревший, не рекомендуется
- **Flyway** - Java-based, не для Python
- **Liquibase** - XML-based, сложнее в использовании

### 5.2 Установка Alembic

```bash
# Установка Alembic
pip install alembic

# Инициализация Alembic
alembic init alembic
```

### 5.3 Конфигурация Alembic

Файл `alembic.ini`:
```ini
# alembic.ini

[alembic]
script_location = alembic
file_template = %%(year)d%%(month).2d%%(day).2d_%%(hour).2d%%(minute).2d_%%(rev)s_%%(slug)s

sqlalchemy.url = sqlite:///./vms.db

[post_write_hooks]

[loggers]
keys = root,sqlalchemy,alembic

[handlers]
keys = console

[formatters]
keys = generic
```

Файл `alembic/env.py`:
```python
from logging.config import fileConfig
from sqlalchemy import engine_from_config, pool
from alembic import context
import sys
import os

# Добавляем путь к приложению
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from app.db.base import Base  # Базовый класс SQLAlchemy
from app.db.models import *   # Все модели

# this is the Alembic Config object
config = context.config

# Interpret the config file for Python logging
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# add your model's MetaData object here
target_metadata = Base.metadata

def run_migrations_offline() -> None:
    """Run migrations in 'offline' mode."""
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    """Run migrations in 'online' mode."""
    connectable = engine_from_config(
        config.get_section(config.config_ini_section, {}),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:
        context.configure(
            connection=connection, target_metadata=target_metadata
        )

        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
```

### 5.4 Пример начальной миграции

Файл `alembic/versions/001_initial_schema.py`:
```python
"""Initial VMS database schema

Revision ID: 001
Revises: 
Create Date: 2024-01-01 00:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import sqlite

# revision identifiers
revision = '001'
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Create users table
    op.create_table(
        'users',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('username', sa.String(length=50), nullable=False),
        sa.Column('email', sa.String(length=100), nullable=False),
        sa.Column('password_hash', sa.String(length=255), nullable=False),
        sa.Column('role', sa.String(length=20), nullable=False, server_default='viewer'),
        sa.Column('refresh_token', sa.String(length=500), nullable=True),
        sa.Column('created_at', sa.String(), nullable=False, server_default=sa.text("(datetime('now'))")),
        sa.Column('last_login', sa.String(), nullable=True),
        sa.CheckConstraint("role IN ('admin', 'viewer')", name='check_users_role'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('username'),
        sa.UniqueConstraint('email')
    )
    
    # Create cameras table
    op.create_table(
        'cameras',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('name', sa.String(length=100), nullable=False),
        sa.Column('rtsp_url', sa.String(length=500), nullable=False),
        sa.Column('onvif_host', sa.String(length=100), nullable=True),
        sa.Column('onvif_port', sa.Integer(), nullable=True, server_default='80'),
        sa.Column('onvif_username', sa.String(length=50), nullable=True),
        sa.Column('onvif_password', sa.String(length=100), nullable=True),
        sa.Column('status', sa.String(length=20), nullable=False, server_default='offline'),
        sa.Column('recording_mode', sa.String(length=20), nullable=False, server_default='motion'),
        sa.Column('detection_enabled', sa.Integer(), nullable=False, server_default='1'),
        sa.Column('detection_confidence', sa.Float(), nullable=False, server_default='0.5'),
        sa.Column('resolution_width', sa.Integer(), nullable=True),
        sa.Column('resolution_height', sa.Integer(), nullable=True),
        sa.Column('codec', sa.String(length=20), nullable=True),
        sa.Column('fps', sa.Integer(), nullable=True),
        sa.Column('created_at', sa.String(), nullable=False, server_default=sa.text("(datetime('now'))")),
        sa.Column('updated_at', sa.String(), nullable=False, server_default=sa.text("(datetime('now'))")),
        sa.CheckConstraint("status IN ('online', 'offline', 'error')", name='check_cameras_status'),
        sa.CheckConstraint("recording_mode IN ('continuous', 'motion', 'scheduled')", name='check_cameras_recording_mode'),
        sa.CheckConstraint("detection_confidence >= 0 AND detection_confidence <= 1", name='check_cameras_detection_confidence'),
        sa.PrimaryKeyConstraint('id')
    )
    
    # Create recordings table
    op.create_table(
        'recordings',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('camera_id', sa.Integer(), nullable=False),
        sa.Column('file_path', sa.String(length=500), nullable=False),
        sa.Column('recording_type', sa.String(length=20), nullable=False, server_default='motion'),
        sa.Column('start_time', sa.String(), nullable=False),
        sa.Column('end_time', sa.String(), nullable=False),
        sa.Column('file_size', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('duration', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('is_encrypted', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('encryption_key', sa.String(length=255), nullable=True),
        sa.Column('codec', sa.String(length=20), nullable=True),
        sa.Column('resolution_width', sa.Integer(), nullable=True),
        sa.Column('resolution_height', sa.Integer(), nullable=True),
        sa.Column('bitrate', sa.Integer(), nullable=True),
        sa.Column('created_at', sa.String(), nullable=False, server_default=sa.text("(datetime('now'))")),
        sa.CheckConstraint("recording_type IN ('continuous', 'motion', 'scheduled')", name='check_recordings_recording_type'),
        sa.CheckConstraint("is_encrypted IN (0, 1)", name='check_recordings_is_encrypted'),
        sa.ForeignKeyConstraint(['camera_id'], ['cameras.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    
    # Create video_metadata table
    op.create_table(
        'video_metadata',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('recording_id', sa.Integer(), nullable=False),
        sa.Column('thumbnails', sa.String(), nullable=True),
        sa.Column('detected_objects', sa.String(), nullable=True),
        sa.Column('motion_events', sa.String(), nullable=True),
        sa.ForeignKeyConstraint(['recording_id'], ['recordings.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('recording_id')
    )
    
    # Create events table
    op.create_table(
        'events',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('event_type', sa.String(length=50), nullable=False),
        sa.Column('camera_id', sa.Integer(), nullable=True),
        sa.Column('recording_id', sa.Integer(), nullable=True),
        sa.Column('timestamp', sa.String(), nullable=False, server_default=sa.text("(datetime('now'))")),
        sa.Column('details', sa.String(), nullable=True),
        sa.Column('status', sa.String(length=20), nullable=False, server_default='new'),
        sa.Column('push_sent', sa.Integer(), nullable=False, server_default='0'),
        sa.CheckConstraint("event_type IN ('motion_detected', 'person_detected', 'camera_offline', 'camera_error', 'storage_full', 'system_error')", name='check_events_event_type'),
        sa.CheckConstraint("status IN ('new', 'acknowledged', 'resolved')", name='check_events_status'),
        sa.CheckConstraint("push_sent IN (0, 1)", name='check_events_push_sent'),
        sa.ForeignKeyConstraint(['camera_id'], ['cameras.id'], ondelete='SET NULL'),
        sa.ForeignKeyConstraint(['recording_id'], ['recordings.id'], ondelete='SET NULL'),
        sa.PrimaryKeyConstraint('id')
    )
    
    # Create logs table
    op.create_table(
        'logs',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('level', sa.String(length=10), nullable=False),
        sa.Column('component', sa.String(length=50), nullable=False),
        sa.Column('message', sa.String(length=1000), nullable=False),
        sa.Column('details', sa.String(), nullable=True),
        sa.Column('timestamp', sa.String(), nullable=False, server_default=sa.text("(datetime('now'))")),
        sa.CheckConstraint("level IN ('DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL')", name='check_logs_level'),
        sa.PrimaryKeyConstraint('id')
    )
    
    # Create settings table
    op.create_table(
        'settings',
        sa.Column('key', sa.String(length=100), nullable=False),
        sa.Column('value', sa.String(), nullable=False),
        sa.Column('category', sa.String(length=50), nullable=False),
        sa.Column('description', sa.String(length=500), nullable=True),
        sa.Column('updated_at', sa.String(), nullable=False, server_default=sa.text("(datetime('now'))")),
        sa.CheckConstraint("category IN ('storage', 'recording', 'detection', 'notification', 'system', 'auth')", name='check_settings_category'),
        sa.PrimaryKeyConstraint('key')
    )
    
    # Create schedules table
    op.create_table(
        'schedules',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('camera_id', sa.Integer(), nullable=False),
        sa.Column('days_of_week', sa.String(), nullable=False),
        sa.Column('start_time', sa.String(), nullable=False),
        sa.Column('end_time', sa.String(), nullable=False),
        sa.Column('record_type', sa.String(length=20), nullable=False, server_default='continuous'),
        sa.Column('is_active', sa.Integer(), nullable=False, server_default='1'),
        sa.CheckConstraint("record_type IN ('continuous', 'motion')", name='check_schedules_record_type'),
        sa.CheckConstraint("is_active IN (0, 1)", name='check_schedules_is_active'),
        sa.ForeignKeyConstraint(['camera_id'], ['cameras.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    
    # Create indexes
    op.create_index('idx_users_username', 'users', ['username'])
    op.create_index('idx_users_email', 'users', ['email'])
    
    op.create_index('idx_cameras_status', 'cameras', ['status'])
    op.create_index('idx_cameras_name', 'cameras', ['name'])
    
    op.create_index('idx_recordings_camera_id', 'recordings', ['camera_id'])
    op.create_index('idx_recordings_start_time', 'recordings', ['start_time'])
    op.create_index('idx_recordings_camera_start', 'recordings', ['camera_id', 'start_time'])
    op.create_index('idx_recordings_recording_type', 'recordings', ['recording_type'])
    
    op.create_index('idx_video_metadata_recording_id', 'video_metadata', ['recording_id'])
    
    op.create_index('idx_events_camera_id', 'events', ['camera_id'])
    op.create_index('idx_events_timestamp', 'events', ['timestamp'])
    op.create_index('idx_events_event_type', 'events', ['event_type'])
    op.create_index('idx_events_status', 'events', ['status'])
    op.create_index('idx_events_camera_timestamp', 'events', ['camera_id', 'timestamp'])
    
    op.create_index('idx_logs_level', 'logs', ['level'])
    op.create_index('idx_logs_component', 'logs', ['component'])
    op.create_index('idx_logs_timestamp', 'logs', ['timestamp'])
    op.create_index('idx_logs_level_timestamp', 'logs', ['level', 'timestamp'])
    
    op.create_index('idx_settings_category', 'settings', ['category'])
    
    op.create_index('idx_schedules_camera_id', 'schedules', ['camera_id'])
    op.create_index('idx_schedules_is_active', 'schedules', ['is_active'])


def downgrade() -> None:
    # Drop indexes
    op.drop_index('idx_schedules_is_active', 'schedules')
    op.drop_index('idx_schedules_camera_id', 'schedules')
    op.drop_index('idx_settings_category', 'settings')
    op.drop_index('idx_logs_level_timestamp', 'logs')
    op.drop_index('idx_logs_timestamp', 'logs')
    op.drop_index('idx_logs_component', 'logs')
    op.drop_index('idx_logs_level', 'logs')
    op.drop_index('idx_events_camera_timestamp', 'events')
    op.drop_index('idx_events_status', 'events')
    op.drop_index('idx_events_event_type', 'events')
    op.drop_index('idx_events_timestamp', 'events')
    op.drop_index('idx_events_camera_id', 'events')
    op.drop_index('idx_video_metadata_recording_id', 'video_metadata')
    op.drop_index('idx_recordings_recording_type', 'recordings')
    op.drop_index('idx_recordings_camera_start', 'recordings')
    op.drop_index('idx_recordings_start_time', 'recordings')
    op.drop_index('idx_recordings_camera_id', 'recordings')
    op.drop_index('idx_cameras_name', 'cameras')
    op.drop_index('idx_cameras_status', 'cameras')
    op.drop_index('idx_users_email', 'users')
    op.drop_index('idx_users_username', 'users')
    
    # Drop tables
    op.drop_table('schedules')
    op.drop_table('settings')
    op.drop_table('logs')
    op.drop_table('events')
    op.drop_table('video_metadata')
    op.drop_table('recordings')
    op.drop_table('cameras')
    op.drop_table('users')
```

### 5.5 Команды Alembic

```bash
# Создание новой миграции (автоматическая генерация)
alembic revision --autogenerate -m "description of changes"

# Применение миграций
alembic upgrade head

# Откат последней миграции
alembic downgrade -1

# Откат до конкретной версии
alembic downgrade <revision_id>

# Просмотр истории миграций
alembic history

# Просмотр текущей версии
alembic current

# Создание пустой миграции (для ручного написания)
alembic revision -m "description"
```

### 5.6 Примеры миграций

**Добавление новой колонки:**
```python
def upgrade() -> None:
    op.add_column('cameras', sa.Column('ptz_enabled', sa.Integer(), nullable=False, server_default='0'))

def downgrade() -> None:
    op.drop_column('cameras', 'ptz_enabled')
```

**Изменение типа колонки:**
```python
def upgrade() -> None:
    op.alter_column('recordings', 'duration', type_=sa.Integer())

def downgrade() -> None:
    op.alter_column('recordings', 'duration', type_=sa.Integer())
```

**Добавление новой таблицы:**
```python
def upgrade() -> None:
    op.create_table(
        'new_table',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.PrimaryKeyConstraint('id')
    )

def downgrade() -> None:
    op.drop_table('new_table')
```

---

## 6. Best Practices для SQLite

### 6.1 Производительность

1. **Используйте WAL mode:**
   ```sql
   PRAGMA journal_mode = WAL;
   ```

2. **Увеличьте размер кэша:**
   ```sql
   PRAGMA cache_size = -64000;  -- 64MB
   ```

3. **Используйте транзакции для массовых операций:**
   ```sql
   BEGIN TRANSACTION;
   INSERT INTO recordings (...) VALUES (...);
   INSERT INTO recordings (...) VALUES (...);
   COMMIT;
   ```

4. **Используйте подготовленные выражения (prepared statements):**
   - В Python: используйте `session.execute()` с параметрами
   - Это предотвращает SQL injection и улучшает производительность

### 6.2 Безопасность

1. **Всегда используйте параметризованные запросы:**
   ```python
   # Правильно
   session.execute("SELECT * FROM cameras WHERE id = ?", (camera_id,))
   
   # Неправильно (SQL injection)
   session.execute(f"SELECT * FROM cameras WHERE id = {camera_id}")
   ```

2. **Шифруйте чувствительные данные:**
   - Пароли: используйте bcrypt
   - ONVIF пароли: шифруйте перед сохранением
   - Ключи шифрования видео: храните в переменных окружения

3. **Ограничьте права доступа к файлу БД:**
   ```bash
   chmod 600 vms.db
   ```

### 6.3 Резервное копирование

1. **Регулярные бэкапы:**
   - Полный бэкап: раз в день ночью
   - Инкрементальный бэкап: раз в час

2. **Храните бэкапы в разных местах:**
   - Локальный диск
   - Облачное хранилище (S3, Google Drive)
   - Внешний диск

3. **Тестируйте восстановление:**
   - Регулярно проверяйте бэкапы
   - Проводите тестовые восстановления

### 6.4 Мониторинг

1. **Мониторинг размера БД:**
   ```bash
   ls -lh vms.db
   ```

2. **Мониторинг количества записей:**
   ```sql
   SELECT COUNT(*) FROM recordings;
   SELECT COUNT(*) FROM events;
   SELECT COUNT(*) FROM logs;
   ```

3. **Мониторинг производительности:**
   ```sql
   PRAGMA cache_size;
   PRAGMA page_size;
   PRAGMA user_version;
   ```

---

## 7. SQLAlchemy ORM модели

### 7.1 Примеры моделей

```python
from sqlalchemy import Column, Integer, String, Float, Text, ForeignKey, DateTime, Boolean
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship

Base = declarative_base()

class User(Base):
    __tablename__ = 'users'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    username = Column(String(50), unique=True, nullable=False)
    email = Column(String(100), unique=True, nullable=False)
    password_hash = Column(String(255), nullable=False)
    role = Column(String(20), nullable=False, default='viewer')
    refresh_token = Column(String(500), nullable=True)
    created_at = Column(Text, nullable=False, default=lambda: datetime.now().isoformat())
    last_login = Column(Text, nullable=True)


class Camera(Base):
    __tablename__ = 'cameras'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(100), nullable=False)
    rtsp_url = Column(String(500), nullable=False)
    onvif_host = Column(String(100), nullable=True)
    onvif_port = Column(Integer, default=80, nullable=True)
    onvif_username = Column(String(50), nullable=True)
    onvif_password = Column(String(100), nullable=True)
    status = Column(String(20), nullable=False, default='offline')
    recording_mode = Column(String(20), nullable=False, default='motion')
    detection_enabled = Column(Integer, nullable=False, default=1)
    detection_confidence = Column(Float, nullable=False, default=0.5)
    resolution_width = Column(Integer, nullable=True)
    resolution_height = Column(Integer, nullable=True)
    codec = Column(String(20), nullable=True)
    fps = Column(Integer, nullable=True)
    created_at = Column(Text, nullable=False, default=lambda: datetime.now().isoformat())
    updated_at = Column(Text, nullable=False, default=lambda: datetime.now().isoformat())
    
    # Relationships
    recordings = relationship("Recording", back_populates="camera", cascade="all, delete-orphan")
    schedules = relationship("Schedule", back_populates="camera", cascade="all, delete-orphan")
    events = relationship("Event", back_populates="camera")


class Recording(Base):
    __tablename__ = 'recordings'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    camera_id = Column(Integer, ForeignKey('cameras.id', ondelete='CASCADE'), nullable=False)
    file_path = Column(String(500), nullable=False)
    recording_type = Column(String(20), nullable=False, default='motion')
    start_time = Column(Text, nullable=False)
    end_time = Column(Text, nullable=False)
    file_size = Column(Integer, nullable=False, default=0)
    duration = Column(Integer, nullable=False, default=0)
    is_encrypted = Column(Integer, nullable=False, default=0)
    encryption_key = Column(String(255), nullable=True)
    codec = Column(String(20), nullable=True)
    resolution_width = Column(Integer, nullable=True)
    resolution_height = Column(Integer, nullable=True)
    bitrate = Column(Integer, nullable=True)
    created_at = Column(Text, nullable=False, default=lambda: datetime.now().isoformat())
    
    # Relationships
    camera = relationship("Camera", back_populates="recordings")
    video_metadata = relationship("VideoMetadata", back_populates="recording", uselist=False, cascade="all, delete-orphan")
    events = relationship("Event", back_populates="recording")


class VideoMetadata(Base):
    __tablename__ = 'video_metadata'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    recording_id = Column(Integer, ForeignKey('recordings.id', ondelete='CASCADE'), unique=True, nullable=False)
    thumbnails = Column(Text, nullable=True)
    detected_objects = Column(Text, nullable=True)
    motion_events = Column(Text, nullable=True)
    
    # Relationships
    recording = relationship("Recording", back_populates="video_metadata")


class Event(Base):
    __tablename__ = 'events'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    event_type = Column(String(50), nullable=False)
    camera_id = Column(Integer, ForeignKey('cameras.id', ondelete='SET NULL'), nullable=True)
    recording_id = Column(Integer, ForeignKey('recordings.id', ondelete='SET NULL'), nullable=True)
    timestamp = Column(Text, nullable=False, default=lambda: datetime.now().isoformat())
    details = Column(Text, nullable=True)
    status = Column(String(20), nullable=False, default='new')
    push_sent = Column(Integer, nullable=False, default=0)
    
    # Relationships
    camera = relationship("Camera", back_populates="events")
    recording = relationship("Recording", back_populates="events")


class Log(Base):
    __tablename__ = 'logs'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    level = Column(String(10), nullable=False)
    component = Column(String(50), nullable=False)
    message = Column(String(1000), nullable=False)
    details = Column(Text, nullable=True)
    timestamp = Column(Text, nullable=False, default=lambda: datetime.now().isoformat())


class Setting(Base):
    __tablename__ = 'settings'
    
    key = Column(String(100), primary_key=True)
    value = Column(Text, nullable=False)
    category = Column(String(50), nullable=False)
    description = Column(String(500), nullable=True)
    updated_at = Column(Text, nullable=False, default=lambda: datetime.now().isoformat())


class Schedule(Base):
    __tablename__ = 'schedules'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    camera_id = Column(Integer, ForeignKey('cameras.id', ondelete='CASCADE'), nullable=False)
    days_of_week = Column(Text, nullable=False)
    start_time = Column(String(5), nullable=False)
    end_time = Column(String(5), nullable=False)
    record_type = Column(String(20), nullable=False, default='continuous')
    is_active = Column(Integer, nullable=False, default=1)
    
    # Relationships
    camera = relationship("Camera", back_populates="schedules")
```

---

## 8. Заключение

Данная схема базы данных спроектирована для VMS системы с учетом следующих требований:

- **Масштаб:** 4-16 камер, 30 дней хранения записей
- **База данных:** SQLite 3.40+ (встраиваемая, безсерверная)
- **Производительность:** Оптимизированные индексы, WAL mode, кэширование
- **Безопасность:** Шифрование паролей, параметризованные запросы
- **Масштабируемость:** Возможность миграции на PostgreSQL при необходимости
- **Резервное копирование:** Простое копирование файла БД

**Преимущества SQLite для VMS:**
- Простота деплоя (отсутствие отдельного сервера БД)
- Низкие накладные расходы
- Отличная производительность для 4-16 камер
- Простое резервное копирование (копирование файла)
- ACID транзакции

**Ограничения SQLite:**
- Нет параллельной записи (один писатель в момент времени)
- Ограниченный набор типов данных
- Нет встроенной репликации

Для больших установок (>16 камер) рекомендуется миграция на PostgreSQL.
