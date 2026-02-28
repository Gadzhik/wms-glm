# Video Management System (VMS) - Архитектурный проект

## 1. Общая архитектура

### 1.1 Архитектурный паттерн

**Модульный монолит (Modular Monolith)**

**Обоснование:**
- Для частного дома (обычно 4-16 камер) микросервисы избыточны
- Модульный монолит обеспечивает простоту деплоя и обслуживания
- Легкая миграция на микросервисы при необходимости
- Минимальные накладные расходы на межсервисное взаимодействие
- Единая точка деплоя через Docker Compose

### 1.2 Компоненты системы

```
┌─────────────────────────────────────────────────────────────────────┐
│                         VMS System                                    │
├─────────────────────────────────────────────────────────────────────┤
│                                                                      │
│  ┌──────────────────┐  ┌──────────────────┐  ┌──────────────────┐  │
│  │  Web Frontend    │  │  Telegram Bot    │  │  Mobile App      │  │
│  │  (React + Vite)  │  │  (aiogram 3.x)   │  │  (PWA)           │  │
│  └────────┬─────────┘  └────────┬─────────┘  └────────┬─────────┘  │
│           │                     │                     │            │
│           └─────────────────────┼─────────────────────┘            │
│                                 │                                  │
│                    ┌────────────▼────────────┐                      │
│                    │   API Gateway / Nginx   │                      │
│                    │   (Reverse Proxy + SSL) │                      │
│                    └────────────┬────────────┘                      │
│                                 │                                  │
│           ┌─────────────────────┼─────────────────────┐            │
│           │                     │                     │            │
│  ┌────────▼─────────┐  ┌────────▼─────────┐  ┌────────▼─────────┐  │
│  │  HTTP API        │  │  WebSocket       │  │  Notification    │  │
│  │  (FastAPI)       │  │  Server          │  │  Service        │  │
│  └────────┬─────────┘  └────────┬─────────┘  └────────┬─────────┘  │
│           │                     │                     │            │
│           └─────────────────────┼─────────────────────┘            │
│                                 │                                  │
│                    ┌────────────▼────────────┐                      │
│                    │   Business Logic Layer  │                      │
│                    └────────────┬────────────┘                      │
│                                 │                                  │
│  ┌──────────────────────────────┼──────────────────────────────┐  │
│  │                              │                              │  │
│  │  ┌──────────────────────┐   │   ┌──────────────────────┐  │  │
│  │  │ Camera Manager       │   │   │ Recording Manager    │  │  │
│  │  │ - RTSP Connection    │   │   │ - Continuous Record  │  │  │
│  │  │ - ONVIF Discovery    │   │   │ - Motion Detection   │  │  │
│  │  │ - Reconnect Logic    │   │   │ - Schedule Record    │  │  │
│  │  └──────────┬───────────┘   │   └──────────┬───────────┘  │  │
│  │             │               │              │              │  │
│  │  ┌──────────▼───────────┐   │   ┌──────────▼───────────┐  │  │
│  │  │ Stream Processor     │   │   │ Storage Manager     │  │  │
│  │  │ - Transcoding        │   │   │ - File Management   │  │  │
│  │  │ - Segmenting         │   │   │ - Retention Policy  │  │  │
│  │  │ - Buffering          │   │   │ - Disk Monitoring   │  │  │
│  │  └──────────┬───────────┘   │   └──────────┬───────────┘  │  │
│  │             │               │              │              │  │
│  │  ┌──────────▼───────────┐   │   ┌──────────▼───────────┐  │  │
│  │  │ AI Detection Engine  │   │   │ Archive Manager      │  │  │
│  │  │ - Person Detection   │   │   │ - Timeline Query     │  │  │
│  │  │ - Object Tracking    │   │   │ - Export Video       │  │  │
│  │  │ - Event Generation   │   │   │ - Encryption         │  │  │
│  │  └──────────┬───────────┘   │   └──────────┬───────────┘  │  │
│  │             │               │              │              │  │
│  └─────────────┼───────────────┴──────────────┼──────────────┘  │
│                │                              │                 │
│  ┌─────────────▼──────────────────────────────▼─────────────┐    │
│  │                    Data Access Layer                     │    │
│  └─────────────┬──────────────────────────────┬─────────────┘    │
│                │                              │                 │
│  ┌─────────────▼──────────┐    ┌──────────────▼────────────┐   │
│  │ PostgreSQL Database    │    │ Redis Cache & Queue       │   │
│  │ - Cameras              │    │ - Session Store           │   │
│  │ - Users                │    │ - Event Queue             │   │
│  │ - Recordings           │    │ - Stream Metadata        │   │
│  │ - Events               │    │ - Rate Limiting           │   │
│  │ - Settings             │    │ - Pub/Sub                 │   │
│  └────────────────────────┘    └───────────────────────────┘   │
│                                                                 │
│  ┌───────────────────────────────────────────────────────────┐  │
│  │                    Storage Layer                          │  │
│  │  /data/recordings/                                        │  │
│  │  /data/archive/                                           │  │
│  │  /data/exports/                                           │  │
│  └───────────────────────────────────────────────────────────┘  │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────┐
│                    Infrastructure & Monitoring                   │
├─────────────────────────────────────────────────────────────────┤
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐          │
│  │ Prometheus   │  │ Grafana      │  │ Alertmanager │          │
│  │ (Metrics)    │  │ (Dashboards) │  │ (Alerts)     │          │
│  └──────────────┘  └──────────────┘  └──────────────┘          │
│                                                                 │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐          │
│  │ Watchdog     │  │ Backup       │  │ Health Check │          │
│  │ Service      │  │ Service      │  │ Service      │          │
│  └──────────────┘  └──────────────┘  └──────────────┘          │
└─────────────────────────────────────────────────────────────────┘
```

### 1.3 Поток данных

```mermaid
graph TD
    A[IP Cameras] -->|RTSP Stream| B[Camera Manager]
    B -->|Raw Stream| C[Stream Processor]
    C -->|Transcoded Stream| D[Recording Manager]
    C -->|Live Stream| E[WebSocket Server]
    D -->|Video Segments| F[Storage Manager]
    C -->|Frames| G[AI Detection Engine]
    G -->|Detection Events| H[Event Queue - Redis]
    H --> I[Notification Service]
    I -->|Push Notification| J[Telegram Bot]
    I -->|WebSocket Event| E
    F -->|Metadata| K[PostgreSQL]
    G -->|Metadata| K
    K -->|Query Results| L[HTTP API]
    L --> M[Web Frontend]
    E -->|Live Video| M
    F -->|Archive Files| N[Archive Manager]
    N -->|Video Stream| L
```

### 1.4 Масштабируемость

**Горизонтальное масштабирование:**
- WebSocket серверы могут масштабироваться через Redis Pub/Sub
- HTTP API могут масштабироваться за балансировщиком
- AI Detection Engine может быть вынесен в отдельный сервис

**Вертикальное масштабирование:**
- Увеличение CPU для большего количества камер
- Увеличение RAM для буферизации стримов
- Увеличение дискового пространства для хранения

### 1.5 Потенциальные узкие места

| Узкое место | Решение |
|-------------|---------|
| Транскодинг видео (CPU) | Аппаратное ускорение (Intel QSV, NVIDIA NVENC), ограничение FPS |
| AI детекция (GPU/CPU) | Аппаратное ускорение (CUDA, OpenVINO), периодическая детекция |
| Дисковые операции при записи | SSD для активных записей, HDD для архива, отдельные диски |
| WebSocket соединения | Redis Pub/Sub для масштабирования, ограничение одновременных просмотров |
| База данных при большом количестве событий | Партиционирование таблиц, индексация, очистка старых событий |

### 1.6 Оптимизация CPU и RAM

**CPU оптимизация:**
- Использование FFmpeg с аппаратным ускорением
- Лимитирование FPS для записи (15-30 FPS вместо 60)
- Оптимизация параметров кодирования (preset, CRF)
- Пул воркеров для AI детекции
- Приоритизация задач (live > recording > detection)

**RAM оптимизация:**
- Кольцевой буфер для стриминга (не более 5-10 секунд)
- Ленивая загрузка метаданных архива
- Пагинация при запросах к БД
- Очистка неиспользуемых кэшей
- Использование потоков вместо процессов там, где возможно

---

## 2. Диаграмма компонентов

### 2.1 Структура компонентов

```
VMS System
│
├── Presentation Layer
│   ├── Web Frontend (React + Vite)
│   │   ├── Live View Module
│   │   ├── Archive Player Module
│   │   ├── Camera Management Module
│   │   ├── Settings Module
│   │   └── Authentication Module
│   │
│   └── Telegram Bot (aiogram 3.x)
│       ├── Notification Handler
│       ├── Command Handler
│       └── Callback Handler
│
├── API Gateway
│   ├── Nginx Reverse Proxy
│   ├── SSL/TLS Termination
│   ├── Rate Limiting
│   └── Request Routing
│
├── Application Layer
│   ├── HTTP API (FastAPI)
│   │   ├── Auth Endpoints
│   │   ├── Camera Endpoints
│   │   ├── Recording Endpoints
│   │   ├── Archive Endpoints
│   │   ├── Settings Endpoints
│   │   └── System Endpoints
│   │
│   └── WebSocket Server
│       ├── Stream Publisher
│       ├── Event Broadcaster
│       └── Connection Manager
│
├── Business Logic Layer
│   ├── Camera Manager
│   │   ├── RTSP Client (ffmpeg-python)
│   │   ├── ONVIF Client (onvif-zeep)
│   │   ├── Connection Pool
│   │   └── Health Monitor
│   │
│   ├── Stream Processor
│   │   ├── Transcoder (FFmpeg)
│   │   ├── Segmenter
│   │   ├── Buffer Manager
│   │   └── Quality Adapter
│   │
│   ├── Recording Manager
│   │   ├── Continuous Recorder
│   │   ├── Motion Detector (OpenCV)
│   │   ├── Scheduler
│   │   └── Segment Manager
│   │
│   ├── Storage Manager
│   │   ├── File Writer
│   │   ├── Retention Policy
│   │   ├── Disk Monitor
│   │   └── Cleanup Service
│   │
│   ├── AI Detection Engine
│   │   ├── Person Detector (YOLOv8 / Ultralytics)
│   │   ├── Object Tracker
│   │   ├── Event Classifier
│   │   └── Confidence Filter
│   │
│   └── Archive Manager
│       ├── Timeline Builder
│       ├── Video Exporter
│       ├── Encryption Service
│       └── Thumbnail Generator
│
├── Data Access Layer
│   ├── PostgreSQL Repository
│   │   ├── Camera Repository
│   │   ├── User Repository
│   │   ├── Recording Repository
│   │   ├── Event Repository
│   │   └── Settings Repository
│   │
│   └── Redis Cache
│       ├── Session Store
│       ├── Event Queue
│       ├── Stream Metadata
│       └── Pub/Sub Broker
│
├── Notification Service
│   ├── Push Notification Manager
│   ├── Telegram Integration
│   └── Email Notification (опционально)
│
└── Infrastructure Services
    ├── Watchdog Service
    ├── Backup Service
    ├── Health Check Service
    ├── Metrics Collector (Prometheus)
    └── Log Aggregator
```

### 2.2 Связи между компонентами

```
Web Frontend <--HTTP/REST--> HTTP API <----> Business Logic Layer
Web Frontend <--WebSocket----> WebSocket Server <----> Business Logic Layer
Telegram Bot <--HTTP/REST----> HTTP API <----> Business Logic Layer
Telegram Bot <--Direct-------> Notification Service

IP Cameras <--RTSP----------> Camera Manager <--ONVIF--> Camera Manager
Camera Manager <--Raw Stream--> Stream Processor <--Frames--> AI Detection Engine
Stream Processor <--Segments--> Recording Manager <--Files--> Storage Manager
Recording Manager <--Events----> Event Queue (Redis)
Event Queue <--Events--------> Notification Service
Notification Service <--Notifications--> Telegram Bot

Business Logic Layer <--SQL--> PostgreSQL Repository <--SQL--> PostgreSQL
Business Logic Layer <--Cache--> Redis Cache <--Pub/Sub--> WebSocket Server
Business Logic Layer <--Files--> Storage Manager <--Files--> File System

Watchdog Service <--Monitors--> All Services
Health Check Service <--Checks--> All Services
Backup Service <--Backups--> PostgreSQL
Metrics Collector <--Metrics--> All Services --> Prometheus
```

---

## 3. Выбор технологий

### 3.1 Backend Framework

**Выбор: FastAPI (Python 3.11+)**

**Обоснование:**
- **Асинхронность**: Нативная поддержка async/await для обработки множества WebSocket соединений
- **Производительность**: Сравнима с Node.js и Go благодаря Starlette и Uvicorn
- **Типизация**: Автоматическая генерация OpenAPI документации, Pydantic для валидации
- **Экосистема**: Отличные библиотеки для видео (ffmpeg-python, opencv-python), AI (ultralytics, torch)
- **Разработка**: Быстрый старт, меньше шаблонного кода чем в Spring Boot
- **Мониторинг**: Встроенная поддержка Prometheus metrics через starlette-exporter
- **WebSocket**: Нативная поддержка WebSocket без дополнительных библиотек

**Альтернатива (отклонена): Node.js (Express/NestJS)**
- Плюсы: Отличная поддержка WebSocket (Socket.io), быстрая работа с I/O
- Минусы: Меньше готовых библиотек для AI/Computer Vision, сложнее интеграция с FFmpeg

### 3.2 Frontend Framework

**Выбор: React 18 + Vite**

**Обоснование:**
- **Экосистема**: Огромное количество библиотек для видео плееров (video.js, plyr)
- **Производительность**: Vite обеспечивает мгновенный HMR, быструю сборку
- **Компоненты**: Material-UI или Ant Design для быстрой разработки UI
- **State Management**: Zustand или Redux Toolkit для управления состоянием
- **WebSocket**: Отличные библиотеки (socket.io-client, native WebSocket API)
- **PWA**: Поддержка Progressive Web App для мобильных устройств
- **TypeScript**: Полная типизация для надежности

**Альтернатива (отклонена): Vue 3**
- Плюсы: Простой синтаксис, отличная документация
- Минусы: Меньше библиотек для специфических задач видео стриминга

### 3.3 База данных

**Выбор: PostgreSQL 15+**

**Обоснование:**
- **Надежность**: ACID транзакции, отличная репликация для backup
- **Производительность**: JSONB для гибких метаданных, индексы для быстрых запросов
- **Масштабируемость**: Партиционирование таблиц для больших объемов данных
- **Функциональность**: Full-text search, геометрические типы (для зон детекции)
- **Мониторинг**: Отличные инструменты (pgAdmin, pgbadger)
- **Backup**: pg_dump для надежных бэкапов

**Для SQLite (опционально для небольших установок):**
- Использовать только для < 4 камер
- Простой деплой без отдельного контейнера
- Ограничения: нет параллельной записи, нет репликации

### 3.4 Очереди сообщений

**Выбор: Redis 7+**

**Обоснование:**
- **Скорость**: In-memory хранилище, минимальная задержка
- **Многофункциональность**: Кэш, очередь, Pub/Sub, сессии в одном сервисе
- **Простота**: Легкий деплой, минимальная конфигурация
- **Масштабируемость**: Redis Cluster для горизонтального масштабирования
- **Постоянство**: RDB/AOF для сохранения данных при рестарте

**Альтернатива (отклонена): Kafka**
- Плюсы: Отличная для event sourcing, высокая пропускная способность
- Минусы: Избыточна для VMS, сложная настройка и обслуживание

### 3.5 Брокер для WebSocket

**Выбор: Redis Pub/Sub**

**Обоснование:**
- **Интеграция**: Уже используется для кэша и очередей
- **Производительность**: Миллионы сообщений в секунду
- **Простота**: Нативная поддержка в FastAPI через aioredis
- **Масштабируемость**: Позволяет масштабировать WebSocket серверы

### 3.6 Библиотеки для RTSP стриминга

**Выбор: FFmpeg + ffmpeg-python**

**Обоснование:**
- **FFmpeg**: Индустриальный стандарт для обработки видео
  - Поддержка RTSP, RTMP, HLS, DASH
  - Аппаратное ускорение (Intel QSV, NVIDIA NVENC, VAAPI)
  - Транскодинг H.264/H.265
  - Сегментация видео
- **ffmpeg-python**: Pythonic wrapper для FFmpeg
  - Простое создание пайплайнов
  - Асинхронное выполнение
  - Обработка потоков в реальном времени

**Альтернативы:**
- **OpenCV**: Для чтения RTSP стримов (cv2.VideoCapture)
- **PyAV**: Python bindings для FFmpeg (более низкоуровневый)

### 3.7 Библиотеки для AI детекции

**Выбор: Ultralytics YOLOv8**

**Обоснование:**
- **Производительность**: Оптимизированная модель для real-time детекции
- **Точность**: State-of-the-art результаты на COCO датасете
- **Простота**: Простой API, автоматическая загрузка моделей
- **Поддержка**: CPU, GPU (CUDA, MPS для Apple Silicon), TensorRT, ONNX
- **Функциональность**: Детекция, трекинг, сегментация, классификация
- **Размеры**: nano, small, medium, large модели для разных ресурсов

**Альтернативы:**
- **OpenCV DNN**: Для CPU без зависимостей от PyTorch
- **TensorRT**: Для максимальной производительности на NVIDIA GPU
- **OpenVINO**: Для Intel CPU/GPU

### 3.8 Библиотеки для ONVIF

**Выбор: onvif-zeep**

**Обоснование:**
- **Полная поддержка**: Все ONVIF спецификации (Device, PTZ, Imaging, Analytics)
- **Авто-дискавери**: SSDP протокол для поиска камер в сети
- **Типизация**: Автоматическая генерация Python классов из WSDL
- **Надежность**: Активно поддерживаемый проект

**Альтернативы:**
- **python-onvif**: Более старый, менее функциональный

### 3.9 Библиотеки для обработки видео

**Выбор: OpenCV (opencv-python) + FFmpeg**

**Обоснование:**
- **OpenCV**:
  - Детекция движения (MOG2, KNN background subtraction)
  - Обработка кадров (resize, crop, rotate)
  - Фильтры и морфологические операции
  - Интеграция с YOLO для детекции
- **FFmpeg**:
  - Транскодинг и сжатие
  - Сегментация видео
  - Экспорт фрагментов
  - Генерация превью

### 3.10 Дополнительные технологии

| Компонент | Технология | Обоснование |
|-----------|------------|-------------|
| Контейнеризация | Docker + Docker Compose | Единая среда, простой деплой |
| Reverse Proxy | Nginx | SSL termination, rate limiting, static files |
| SSL/TLS | Let's Encrypt (Certbot) | Бесплатные сертификаты, автообновление |
| Мониторинг | Prometheus + Grafana | Индустриальный стандарт, богатые дашборды |
| Логи | Loki + Promtail | Легковесный, интеграция с Grafana |
| Health Checks | встроенные в FastAPI | /health endpoint, readiness/liveness probes |
| Backup | pg_dump + cron | Надежные бэкапы PostgreSQL |
| Шифрование | cryptography (Fernet) | AES-256 для архива |
| Telegram Bot | aiogram 3.x | Асинхронный, современный API |
| Тестирование | pytest + pytest-asyncio | Асинхронные тесты, fixtures |
| Code Quality | ruff, mypy | Быстрый линтер, статическая типизация |

---

## 4. Поток данных

### 4.1 Поток данных от камер

```
1. Камера (RTSP)
   ↓
2. Camera Manager (ffmpeg-python)
   - Установление RTSP соединения
   - Аутентификация (Digest/Basic)
   - Получение SDP (Session Description Protocol)
   ↓
3. Stream Processor (FFmpeg)
   - Декодирование H.264/H.265 потока
   - Декодирование аудио (AAC/PCM)
   ↓
4. Разделение на два потока:
   
   Поток A: Live Streaming
   ↓
   - Транскодирование в H.264 (если нужно)
   - Сегментация в HLS (2-3 секунды)
   - Запись в /tmp/live/<camera_id>/
   - Публикация через WebSocket
   
   Поток B: Recording
   ↓
   - Буферизация в кольцевой буфер (5-10 секунд)
   - Детекция движения (OpenCV)
   - Запись в /data/recordings/<camera_id>/<date>/
   - Сегментация каждые 5-10 минут
```

### 4.2 Обработка и запись

```
1. Stream Processor получает кадры
   ↓
2. Motion Detection (OpenCV)
   - Сравнение текущего кадра с фоном
   - Вычисление разницы (absdiff)
   - Пороговая фильтрация
   - Морфологические операции (erode, dilate)
   - Подсчет контуров
   ↓
3. Если движение обнаружено:
   - Активация записи по движению
   - Запись пре-буфера (5 секунд до события)
   - Запись пост-буфера (5 секунд после события)
   ↓
4. Recording Manager
   - Получает сегменты от Stream Processor
   - Записывает в файл с метаданными:
     * Timestamp начала/конца
     * Камера
     * Тип записи (continuous/motion/schedule)
     * Длительность
     * Размер файла
   ↓
5. Storage Manager
   - Сохраняет файл на диск
   - Обновляет метаданные в PostgreSQL
   - Проверяет свободное место
   - Применяет политику хранения
```

### 4.3 Передача данных на фронтенд

```
1. HTTP API (FastAPI)
   - REST endpoints для:
     * Список камер
     * Метаданные записей
     * Настройки
     * События
   - JWT аутентификация
   - Пагинация и фильтрация
   ↓
2. WebSocket Server
   - Подключение клиента
   - Аутентификация через JWT token
   - Подписка на:
     * Live stream камеры
     * События детекции
     * Статус системы
   ↓
3. Live Streaming
   - Stream Processor генерирует HLS сегменты
   - Сегменты записываются в /tmp/live/<camera_id>/
   - WebSocket уведомляет о новых сегментах
   - Frontend запрашивает сегменты через HTTP
   - Video.js воспроизводит HLS поток
```

### 4.4 Live Streaming

```
Архитектура Live Streaming:

┌─────────────┐
│ IP Camera   │
│ (RTSP)      │
└──────┬──────┘
       │
       ▼
┌─────────────────────┐
│ FFmpeg Transcoder  │
│ - H.264 → H.264     │
│ - Resize: 1280x720  │
│ - FPS: 15          │
│ - Bitrate: 1Mbps   │
└──────┬──────────────┘
       │
       ▼
┌─────────────────────┐
│ HLS Segmenter       │
│ - Segment: 2 sec    │
│ - Playlist: .m3u8   │
│ - Location: /tmp/live/
└──────┬──────────────┘
       │
       ▼
┌─────────────────────┐
│ WebSocket Server    │
│ - Notify clients    │
│ - Stream metadata   │
└──────┬──────────────┘
       │
       ▼
┌─────────────────────┐
│ Nginx (Static)      │
│ - Serve .ts files   │
│ - Serve .m3u8       │
└──────┬──────────────┘
       │
       ▼
┌─────────────────────┐
│ Web Frontend        │
│ - Video.js Player   │
│ - HLS.js            │
└─────────────────────┘

Оптимизации:
- Аппаратное ускорение транскодинга
- Адаптивный битрейт (ABR)
- Кэширование сегментов в Redis
- Prefetching сегментов на клиенте
```

### 4.5 Архив

```
1. Запрос архива (Frontend → HTTP API)
   ↓
2. Archive Manager
   - Запрос к PostgreSQL:
     SELECT * FROM recordings 
     WHERE camera_id = ? 
       AND start_time >= ? 
       AND end_time <= ?
     ORDER BY start_time
   ↓
3. Построение таймлайна
   - Группировка по дате
   - Определение интервалов с записью
   - Генерация превью (thumbnails)
   ↓
4. Воспроизведение
   - Запрос видеофрагмента
   - Проверка прав доступа
   - Расшифровка (если зашифровано)
   - Стриминг через HTTP Range requests
   ↓
5. Экспорт
   - FFmpeg: вырезка фрагмента
   - Транскодирование (если нужно)
   - Запись в /data/exports/
   - Генерация ссылки для скачивания
```

---

## 5. Оптимизация производительности

### 5.1 Оптимизация CPU

#### 5.1.1 Транскодинг видео

**Аппаратное ускорение:**

```bash
# Intel Quick Sync Video (QSV)
ffmpeg -hwaccel qsv -c:v h264_qsv ...

# NVIDIA NVENC
ffmpeg -hwaccel cuda -c:v h264_nvenc ...

# VAAPI (AMD/Intel)
ffmpeg -hwaccel vaapi -c:v h264_vaapi ...
```

**Оптимизация параметров кодирования:**

| Параметр | Значение | Обоснование |
|----------|----------|-------------|
| Preset | faster/veryfast | Баланс скорости и качества |
| CRF | 23-28 | Константное качество, меньший размер |
| FPS | 15-30 | Достаточно для surveillance |
| Resolution | 1280x720 или 1920x1080 | Баланс качества и нагрузки |
| GOP | 30-60 | Размер группы кадров |
| B-frames | 0-2 | Уменьшение задержки для live streaming |

**Пул воркеров:**
- Количество воркеров = min(CPU cores, количество камер)
- Приоритет: Live > Recording > Detection
- Очередь задач с приоритетами

#### 5.1.2 AI детекция

**Оптимизации:**

1. **Периодическая детекция:**
   - Не каждый кадр, а каждый N-й (например, каждый 5-й)
   - Детекция только при наличии движения
   - Детекция в зоне интереса (ROI)

2. **Модель:**
   - YOLOv8n (nano) для CPU
   - YOLOv8s/m для GPU
   - TensorRT оптимизация для NVIDIA GPU
   - ONNX Runtime для CPU

3. **Batch processing:**
   - Группировка кадров для batch inference
   - Размер batch: 4-8 кадров

4. **Асинхронная обработка:**
   - Отдельный процесс для детекции
   - Очередь кадров через Redis
   - Неблокирующая обработка

#### 5.1.3 Дополнительные оптимизации

- **CPU affinity:** Привязка процессов к конкретным ядрам
- **Priority:** Приоритет real-time для critical задач
- **C-states:** Отключение глубоких C-states для снижения задержки
- **Governor:** Performance governor вместо powersave

### 5.2 Оптимизация RAM

#### 5.2.1 Буферизация видео

**Кольцевой буфер:**
- Размер: 5-10 секунд видео
- Реализация: collections.deque с ограничением
- Автоматическая очистка старых кадров

```python
from collections import deque
import numpy as np

class CircularBuffer:
    def __init__(self, max_size: int, fps: int, duration: int):
        self.max_frames = fps * duration
        self.buffer = deque(maxlen=self.max_frames)
    
    def add_frame(self, frame: np.ndarray):
        self.buffer.append(frame)
    
    def get_frames(self, count: int) -> list:
        return list(self.buffer)[-count:]
```

#### 5.2.2 Управление памятью

**Стратегии:**

1. **Ленивая загрузка:**
   - Загрузка метаданных по запросу
   - Пагинация для больших списков
   - Virtual scrolling на фронтенде

2. **Очистка кэшей:**
   - TTL для Redis кэша (1-5 минут)
   - Очистка неиспользуемых WebSocket соединений
   - Сборка мусора Python (gc.collect())

3. **Оптимизация структур данных:**
   - Использование __slots__ для классов
   - numpy arrays вместо list для изображений
   - Генераторы вместо list comprehensions

4. **Мониторинг:**
   - Лимиты на контейнеры Docker
   - Оповещения при высоком потреблении RAM
   - Автоматический перезапуск при утечках

### 5.3 Оптимизация дисковых операций

#### 5.3.1 Стратегия хранения

**Разделение дисков:**

```
/data/
├── live/          # SSD или RAM disk (tmpfs)
│   └── <camera_id>/
│       ├── stream.m3u8
│       └── segment_*.ts
│
├── recordings/     # SSD для активных записей
│   └── <camera_id>/
│       └── <date>/
│           └── <timestamp>.mp4
│
├── archive/        # HDD для долгосрочного хранения
│   └── <camera_id>/
│       └── <date>/
│           └── <timestamp>.mp4
│
└── exports/        # SSD для временных файлов
    └── <export_id>.mp4
```

#### 5.3.2 Оптимизации записи

1. **Буферизация:**
   - Запись блоками (1-4 MB)
   - fsync только при закрытии файла
   - O_DIRECT для прямого I/O (опционально)

2. **Сегментация:**
   - Размер сегмента: 5-10 минут
   - Автоматическое закрытие файлов
   - Асинхронная запись

3. **Файловая система:**
   - ext4 или XFS для Linux
   - noatime для уменьшения метаданных
   - Выделенный inode для большого количества файлов

4. **Мониторинг диска:**
   - Проверка свободного места каждые 5 минут
   - Оповещения при < 10% свободного места
   - Автоматическая очистка при критическом уровне

### 5.4 Оптимизация сетевых операций

#### 5.4.1 RTSP соединения

**Оптимизации:**

1. **TCP буферы:**
   ```python
   sock.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, 1)
   sock.setsockopt(socket.SOL_SOCKET, socket.SO_RCVBUF, 1024*1024)
   ```

2. **Keep-alive:**
   - Периодические RTSP OPTIONS запросы
   - Автоматическое переподключение при обрыве
   - Экспоненциальный backoff

3. **Мультиплексирование:**
   - Один FFmpeg процесс на несколько камер (если позволяет CPU)
   - Асинхронное чтение потоков

#### 5.4.2 WebSocket

**Оптимизации:**

1. **Сжатие:**
   - Per-message deflate (WebSocket Extension)
   - Отключение для бинарных данных (видео)

2. **Пулинг соединений:**
   - Ограничение одновременных подключений
   - Таймаут неактивных соединений (30 секунд)
   - Heartbeat каждые 10 секунд

3. **Redis Pub/Sub:**
   - Локальный кэш для частых данных
   - Batch отправка событий
   - Фильтрация на сервере

#### 5.4.3 HTTP API

**Оптимизации:**

1. **Кэширование:**
   - HTTP Cache-Control заголовки
   - Redis кэш для частых запросов
   - ETag для условных запросов

2. **Сжатие:**
   - Gzip для JSON ответов
   - Отключение для бинарных данных (видео)

3. **Rate limiting:**
   - Redis-based rate limiting
   - Пределы по endpoint
   - Whitelist для trusted IP

---

## 6. Безопасность

### 6.1 Шифрование трафика (HTTPS)

**Реализация:**

1. **SSL/TLS сертификаты:**
   - Let's Encrypt через Certbot
   - Автоматическое обновление
   - HSTS (HTTP Strict Transport Security)

2. **Nginx конфигурация:**
   ```nginx
   server {
       listen 443 ssl http2;
       server_name vms.local;
       
       ssl_certificate /etc/letsencrypt/live/vms.local/fullchain.pem;
       ssl_certificate_key /etc/letsencrypt/live/vms.local/privkey.pem;
       
       ssl_protocols TLSv1.2 TLSv1.3;
       ssl_ciphers ECDHE-ECDSA-AES128-GCM-SHA256:ECDHE-RSA-AES128-GCM-SHA256;
       ssl_prefer_server_ciphers off;
       
       # HSTS
       add_header Strict-Transport-Security "max-age=31536000" always;
   }
   ```

3. **WebSocket через WSS:**
   - Nginx проксирование WebSocket
   - Заголовок Upgrade: websocket
   - Заголовок Connection: Upgrade

### 6.2 Шифрование архива

**Реализация:**

1. **Алгоритм:**
   - AES-256-GCM (Galois/Counter Mode)
   - Ключ шифрования: 256 бит
   - IV (Initialization Vector): 96 бит, уникальный для каждого файла

2. **Библиотека:**
   ```python
   from cryptography.fernet import Fernet
   from cryptography.hazmat.primitives.ciphers.aead import AESGCM
   
   class VideoEncryption:
       def __init__(self, key: bytes):
           self.aesgcm = AESGCM(key)
       
       def encrypt(self, data: bytes, nonce: bytes) -> bytes:
           return self.aesgcm.encrypt(nonce, data, None)
       
       def decrypt(self, ciphertext: bytes, nonce: bytes) -> bytes:
           return self.aesgcm.decrypt(nonce, ciphertext, None)
   ```

3. **Управление ключами:**
   - Хранение ключей в переменных окружения
   - Ключ шифрования: AES-256 ключ для шифрования ключей файлов
   - Периодическая смена ключей (каждые 30 дней)

4. **Процесс шифрования:**
   - Шифрование при записи (опционально)
   - Расшифровка при воспроизведении
   - Шифрование при экспорте

### 6.3 Аутентификация и авторизация

#### 6.3.1 Аутентификация

**JWT (JSON Web Tokens):**

```python
from datetime import datetime, timedelta
from jose import JWTError, jwt

SECRET_KEY = "your-secret-key"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

def create_access_token(data: dict):
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

def verify_token(token: str):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except JWTError:
        return None
```

**Хеширование паролей:**

```python
from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def hash_password(password: str) -> str:
    return pwd_context.hash(password)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)
```

#### 6.3.2 Авторизация

**Роли и права:**

| Роль | Права |
|------|-------|
| admin | Полный доступ ко всем функциям |
| viewer | Просмотр live stream и архива |
| operator | Просмотр + управление камерами |

**Реализация в FastAPI:**

```python
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

security = HTTPBearer()

async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)):
    token = credentials.credentials
    payload = verify_token(token)
    if not payload:
        raise HTTPException(status_code=401, detail="Invalid token")
    return payload

async def require_admin(user: dict = Depends(get_current_user)):
    if user.get("role") != "admin":
        raise HTTPException(status_code=403, detail="Admin required")
    return user
```

### 6.4 Защита от атак

#### 6.4.1 Защита API

1. **Rate Limiting:**
   ```python
   from slowapi import Limiter
   from slowapi.util import get_remote_address
   
   limiter = Limiter(key_func=get_remote_address)
   
   @app.get("/api/cameras")
   @limiter.limit("10/minute")
   async def get_cameras():
       pass
   ```

2. **Input Validation:**
   - Pydantic модели для всех запросов
   - Санитизация пользовательского ввода
   - Проверка типов и диапазонов

3. **SQL Injection Prevention:**
   - Использование SQLAlchemy ORM
   - Параметризованные запросы
   - Никаких прямых SQL запросов

4. **XSS Prevention:**
   - Экранирование вывода на фронтенде
   - CSP (Content Security Policy) заголовки
   - Sanitization HTML

#### 6.4.2 Защита WebSocket

1. **Аутентификация при подключении:**
   ```python
   @app.websocket("/ws/stream/{camera_id}")
   async def websocket_endpoint(websocket: WebSocket, camera_id: str, token: str):
       user = verify_token(token)
       if not user:
           await websocket.close(code=1008)
           return
       await websocket.accept()
   ```

2. **Валидация сообщений:**
   - Проверка формата JSON
   - Проверка прав доступа
   - Логирование подозрительной активности

3. **Ограничение частоты сообщений:**
   - Максимум N сообщений в секунду
   - Отключение при превышении лимита

#### 6.4.3 Защита от brute-force

1. **Блокировка IP:**
   - Redis store для попыток входа
   - Блокировка на 15 минут после 5 неудачных попыток
   - CAPTCHA после 3 неудачных попыток

2. **Логирование:**
   - Все попытки аутентификации
   - Подозрительная активность
   - Оповещения через Telegram

#### 6.4.4 Дополнительные меры

1. **Безопасность контейнеров:**
   - Запуск от непривилегированного пользователя
   - Read-only файловая система где возможно
   - Ограничение ресурсов (CPU, RAM)

2. **Безопасность сети:**
   - Изоляция в отдельной VLAN
   - Firewall правила (только необходимые порты)
   - VPN для удаленного доступа

3. **Регулярные обновления:**
   - Автоматические обновления security patches
   - Мониторинг уязвимостей (Trivy, Snyk)
   - Регулярные security audit

---

## 7. Структура проекта

### 7.1 Дерево файлов проекта

```
vms-glm/
│
├── ARCHITECTURE.md              # Архитектурный документ
├── README.md                    # Документация проекта
├── .env.example                 # Пример переменных окружения
├── .gitignore                   # Git ignore
├── docker-compose.yml           # Docker Compose конфигурация
├── Makefile                     # Полезные команды
│
├── backend/                     # Backend (FastAPI)
│   ├── Dockerfile               # Docker образ для backend
│   ├── requirements.txt         # Python зависимости
│   ├── pyproject.toml           # Проект конфигурация (Poetry)
│   ├── .env                     # Переменные окружения (не в git)
│   │
│   ├── app/                     # Главный пакет приложения
│   │   ├── __init__.py
│   │   ├── main.py              # Точка входа FastAPI
│   │   ├── config.py            # Конфигурация (Pydantic Settings)
│   │   ├── dependencies.py      # Зависимости для DI
│   │   ├── security.py          # JWT, хеширование паролей
│   │   │
│   │   ├── api/                 # API endpoints
│   │   │   ├── __init__.py
│   │   │   ├── deps.py          # Зависимости для endpoints
│   │   │   ├── v1/              # API v1
│   │   │   │   ├── __init__.py
│   │   │   │   ├── auth.py      # Auth endpoints
│   │   │   │   ├── cameras.py   # Camera endpoints
│   │   │   │   ├── recordings.py# Recording endpoints
│   │   │   │   ├── archive.py   # Archive endpoints
│   │   │   │   ├── events.py    # Event endpoints
│   │   │   │   ├── settings.py  # Settings endpoints
│   │   │   │   └── system.py    # System endpoints
│   │   │   └── websocket.py     # WebSocket endpoints
│   │   │
│   │   ├── core/                # Core бизнес-логика
│   │   │   ├── __init__.py
│   │   │   ├── camera_manager.py# Управление камерами
│   │   │   ├── stream_processor.py# Обработка стримов
│   │   │   ├── recording_manager.py# Управление записью
│   │   │   ├── storage_manager.py# Управление хранилищем
│   │   │   ├── ai_detection.py  # AI детекция
│   │   │   ├── archive_manager.py# Управление архивом
│   │   │   └── notification_service.py# Уведомления
│   │   │
│   │   ├── models/              # Pydantic модели
│   │   │   ├── __init__.py
│   │   │   ├── camera.py        # Camera модели
│   │   │   ├── user.py          # User модели
│   │   │   ├── recording.py     # Recording модели
│   │   │   ├── event.py         # Event модели
│   │   │   └── settings.py      # Settings модели
│   │   │
│   │   ├── schemas/             # Pydantic схемы для API
│   │   │   ├── __init__.py
│   │   │   ├── camera.py        # Camera схемы
│   │   │   ├── user.py          # User схемы
│   │   │   ├── recording.py     # Recording схемы
│   │   │   ├── event.py         # Event схемы
│   │   │   └── settings.py      # Settings схемы
│   │   │
│   │   ├── db/                  # База данных
│   │   │   ├── __init__.py
│   │   │   ├── base.py          # Base SQLAlchemy класс
│   │   │   ├── session.py       # Database session
│   │   │   ├── models.py        # SQLAlchemy ORM модели
│   │   │   │   ├── camera.py
│   │   │   │   ├── user.py
│   │   │   │   ├── recording.py
│   │   │   │   ├── event.py
│   │   │   │   └── settings.py
│   │   │   └── repositories.py  # Repository паттерн
│   │   │       ├── camera.py
│   │   │       ├── user.py
│   │   │       ├── recording.py
│   │   │       ├── event.py
│   │   │       └── settings.py
│   │   │
│   │   ├── services/            # Сервисы
│   │   │   ├── __init__.py
│   │   │   ├── auth_service.py  # Auth сервис
│   │   │   ├── camera_service.py# Camera сервис
│   │   │   ├── recording_service.py# Recording сервис
│   │   │   ├── archive_service.py# Archive сервис
│   │   │   └── notification_service.py# Notification сервис
│   │   │
│   │   ├── utils/               # Утилиты
│   │   │   ├── __init__.py
│   │   │   ├── ffmpeg.py        # FFmpeg wrapper
│   │   │   ├── onvif.py         # ONVIF client
│   │   │   ├── encryption.py    # Шифрование
│   │   │   ├── video.py         # Video утилиты
│   │   │   └── logger.py        # Logger конфигурация
│   │   │
│   │   ├── workers/             # Фоновые задачи
│   │   │   ├── __init__.py
│   │   │   ├── camera_worker.py # Camera connection worker
│   │   │   ├── recording_worker.py# Recording worker
│   │   │   ├── detection_worker.py# AI detection worker
│   │   │   └── cleanup_worker.py# Cleanup worker
│   │   │
│   │   └── middleware/          # Middleware
│   │       ├── __init__.py
│   │       ├── auth.py          # Auth middleware
│   │       ├── logging.py       # Logging middleware
│   │       └── error_handler.py # Error handler
│   │
│   ├── tests/                   # Тесты
│   │   ├── __init__.py
│   │   ├── conftest.py          # Pytest конфигурация
│   │   ├── test_api/            # API тесты
│   │   │   ├── test_auth.py
│   │   │   ├── test_cameras.py
│   │   │   └── test_recordings.py
│   │   ├── test_core/           # Core тесты
│   │   │   ├── test_camera_manager.py
│   │   │   ├── test_stream_processor.py
│   │   │   └── test_ai_detection.py
│   │   └── test_services/       # Service тесты
│   │       ├── test_auth_service.py
│   │       └── test_camera_service.py
│   │
│   ├── scripts/                 # Скрипты
│   │   ├── init_db.py           # Инициализация БД
│   │   ├── create_admin.py      # Создание admin пользователя
│   │   ├── backup_db.py         # Backup БД
│   │   └── restore_db.py        # Restore БД
│   │
│   └── alembic/                 # Database migrations
│       ├── env.py
│       ├── script.py.mako
│       └── versions/
│           ├── 001_initial.py
│           └── ...
│
├── frontend/                    # Frontend (React + Vite)
│   ├── Dockerfile               # Docker образ для frontend
│   ├── package.json             # Node зависимости
│   ├── vite.config.ts           # Vite конфигурация
│   ├── tsconfig.json            # TypeScript конфигурация
│   ├── .env                     # Переменные окружения (не в git)
│   │
│   ├── src/
│   │   ├── main.tsx             # Точка входа
│   │   ├── App.tsx              # Главный компонент
│   │   ├── vite-env.d.ts        # Vite типы
│   │   │
│   │   ├── assets/              # Статические файлы
│   │   │   ├── images/
│   │   │   └── fonts/
│   │   │
│   │   ├── components/          # React компоненты
│   │   │   ├── common/          # Общие компоненты
│   │   │   │   ├── Button.tsx
│   │   │   │   ├── Input.tsx
│   │   │   │   ├── Modal.tsx
│   │   │   │   └── ...
│   │   │   ├── layout/          # Layout компоненты
│   │   │   │   ├── Header.tsx
│   │   │   │   ├── Sidebar.tsx
│   │   │   │   └── Layout.tsx
│   │   │   ├── camera/          # Camera компоненты
│   │   │   │   ├── CameraList.tsx
│   │   │   │   ├── CameraCard.tsx
│   │   │   │   ├── CameraForm.tsx
│   │   │   │   └── CameraSettings.tsx
│   │   │   ├── video/           # Video компоненты
│   │   │   │   ├── LivePlayer.tsx
│   │   │   │   ├── ArchivePlayer.tsx
│   │   │   │   ├── Timeline.tsx
│   │   │   │   └── VideoControls.tsx
│   │   │   ├── events/          # Event компоненты
│   │   │   │   ├── EventList.tsx
│   │   │   │   ├── EventCard.tsx
│   │   │   │   └── EventFilters.tsx
│   │   │   └── settings/        # Settings компоненты
│   │   │       ├── SettingsPanel.tsx
│   │   │       ├── StorageSettings.tsx
│   │   │       └── UserSettings.tsx
│   │   │
│   │   ├── pages/               # Страницы
│   │   │   ├── Login.tsx
│   │   │   ├── Dashboard.tsx
│   │   │   ├── LiveView.tsx
│   │   │   ├── Archive.tsx
│   │   │   ├── Events.tsx
│   │   │   ├── Cameras.tsx
│   │   │   └── Settings.tsx
│   │   │
│   │   ├── hooks/               # React hooks
│   │   │   ├── useAuth.ts
│   │   │   ├── useCameras.ts
│   │   │   ├── useRecordings.ts
│   │   │   ├── useWebSocket.ts
│   │   │   └── useEvents.ts
│   │   │
│   │   ├── services/            # API сервисы
│   │   │   ├── api.ts           # Axios конфигурация
│   │   │   ├── auth.ts          # Auth API
│   │   │   ├── cameras.ts       # Camera API
│   │   │   ├── recordings.ts    # Recording API
│   │   │   ├── archive.ts       # Archive API
│   │   │   └── events.ts        # Event API
│   │   │
│   │   ├── store/               # State management (Zustand)
│   │   │   ├── index.ts
│   │   │   ├── authStore.ts
│   │   │   ├── cameraStore.ts
│   │   │   └── eventStore.ts
│   │   │
│   │   ├── types/               # TypeScript типы
│   │   │   ├── camera.ts
│   │   │   ├── user.ts
│   │   │   ├── recording.ts
│   │   │   └── event.ts
│   │   │
│   │   ├── utils/               # Утилиты
│   │   │   ├── date.ts
│   │   │   ├── video.ts
│   │   │   └── validation.ts
│   │   │
│   │   └── styles/              # Стили
│   │       ├── global.css
│   │       └── variables.css
│   │
│   ├── public/                  # Публичные файлы
│   │   ├── favicon.ico
│   │   └── robots.txt
│   │
│   └── tests/                   # Тесты
│       ├── setup.ts
│       ├── components/
│       └── pages/
│
├── telegram-bot/                # Telegram Bot (aiogram)
│   ├── Dockerfile               # Docker образ для bot
│   ├── requirements.txt         # Python зависимости
│   ├── .env                     # Переменные окружения (не в git)
│   │
│   ├── bot/
│   │   ├── __init__.py
│   │   ├── main.py              # Точка входа
│   │   ├── config.py            # Конфигурация
│   │   │
│   │   ├── handlers/            # Handlers
│   │   │   ├── __init__.py
│   │   │   ├── commands.py      # Command handlers (/start, /help)
│   │   │   ├── callbacks.py     # Callback query handlers
│   │   │   └── notifications.py # Notification handlers
│   │   │
│   │   ├── keyboards/           # Keyboards
│   │   │   ├── __init__.py
│   │   │   ├── main.py
│   │   │   └── camera.py
│   │   │
│   │   ├── services/            # Сервисы
│   │   │   ├── __init__.py
│   │   │   ├── auth_service.py  # Auth сервис
│   │   │   └── notification_service.py# Notification сервис
│   │   │
│   │   └── utils/               # Утилиты
│   │       ├── __init__.py
│   │       └── logger.py
│   │
│   └── tests/                   # Тесты
│       ├── __init__.py
│       └── test_handlers.py
│
├── nginx/                       # Nginx конфигурация
│   ├── Dockerfile
│   ├── nginx.conf               # Главный конфиг
│   ├── ssl.conf                 # SSL конфиг
│   └── conf.d/
│       ├── frontend.conf
│       ├── backend.conf
│       └── websocket.conf
│
├── prometheus/                  # Prometheus конфигурация
│   ├── Dockerfile
│   ├── prometheus.yml           # Prometheus конфиг
│   └── alerts.yml               # Alert rules
│
├── grafana/                     # Grafana конфигурация
│   ├── Dockerfile
│   ├── dashboards/              # Дашборды
│   │   ├── system.json
│   │   ├── cameras.json
│   │   └── recordings.json
│   └── provisioning/
│       ├── datasources/
│       │   └── prometheus.yml
│       └── dashboards/
│           └── dashboards.yml
│
├── scripts/                     # Скрипты для деплоя
│   ├── deploy.sh                # Деплой скрипт
│   ├── backup.sh                # Backup скрипт
│   ├── restore.sh               # Restore скрипт
│   └── init.sh                  # Инициализация скрипт
│
├── docs/                        # Документация
│   ├── api.md                   # API документация
│   ├── deployment.md            # Деплой гайд
│   └── troubleshooting.md       # Troubleshooting гайд
│
└── data/                        # Данные (volume mounts)
    ├── postgres/                # PostgreSQL данные
    ├── redis/                   # Redis данные
    ├── recordings/              # Записи
    ├── archive/                 # Архив
    ├── exports/                 # Экспортированные видео
    └── logs/                    # Логи
```

### 7.2 Описание каталогов и файлов

#### Backend

| Каталог/Файл | Назначение |
|--------------|------------|
| `backend/app/main.py` | Точка входа FastAPI приложения |
| `backend/app/config.py` | Конфигурация приложения (Pydantic Settings) |
| `backend/app/dependencies.py` | Зависимости для Dependency Injection |
| `backend/app/security.py` | JWT токены, хеширование паролей |
| `backend/app/api/` | API endpoints |
| `backend/app/core/` | Core бизнес-логика |
| `backend/app/models/` | Pydantic модели для валидации |
| `backend/app/schemas/` | Pydantic схемы для API |
| `backend/app/db/` | База данных (SQLAlchemy) |
| `backend/app/services/` | Сервисный слой |
| `backend/app/utils/` | Утилиты (FFmpeg, ONVIF, шифрование) |
| `backend/app/workers/` | Фоновые задачи |
| `backend/app/middleware/` | Middleware (auth, logging) |
| `backend/tests/` | Тесты |
| `backend/scripts/` | Скрипты для инициализации и backup |
| `backend/alembic/` | Database migrations |

#### Frontend

| Каталог/Файл | Назначение |
|--------------|------------|
| `frontend/src/main.tsx` | Точка входа React приложения |
| `frontend/src/App.tsx` | Главный компонент |
| `frontend/src/components/` | React компоненты |
| `frontend/src/pages/` | Страницы приложения |
| `frontend/src/hooks/` | React hooks |
| `frontend/src/services/` | API сервисы (Axios) |
| `frontend/src/store/` | State management (Zustand) |
| `frontend/src/types/` | TypeScript типы |
| `frontend/src/utils/` | Утилиты |
| `frontend/src/styles/` | Стили |
| `frontend/tests/` | Тесты |

#### Telegram Bot

| Каталог/Файл | Назначение |
|--------------|------------|
| `telegram-bot/bot/main.py` | Точка входа бота |
| `telegram-bot/bot/handlers/` | Handlers для команд и событий |
| `telegram-bot/bot/keyboards/` | Inline keyboards |
| `telegram-bot/bot/services/` | Сервисы (auth, notifications) |
| `telegram-bot/tests/` | Тесты |

#### Инфраструктура

| Каталог/Файл | Назначение |
|--------------|------------|
| `docker-compose.yml` | Docker Compose конфигурация |
| `nginx/` | Nginx конфигурация |
| `prometheus/` | Prometheus конфигурация |
| `grafana/` | Grafana конфигурация и дашборды |
| `scripts/` | Скрипты для деплоя |
| `docs/` | Документация |
| `data/` | Данные (volume mounts) |

---

## Приложение A: Docker Compose конфигурация

```yaml
version: '3.8'

services:
  # PostgreSQL Database
  postgres:
    image: postgres:15-alpine
    container_name: vms-postgres
    environment:
      POSTGRES_USER: ${POSTGRES_USER}
      POSTGRES_PASSWORD: ${POSTGRES_PASSWORD}
      POSTGRES_DB: ${POSTGRES_DB}
    volumes:
      - ./data/postgres:/var/lib/postgresql/data
    ports:
      - "5432:5432"
    restart: unless-stopped
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U ${POSTGRES_USER}"]
      interval: 10s
      timeout: 5s
      retries: 5

  # Redis Cache & Queue
  redis:
    image: redis:7-alpine
    container_name: vms-redis
    command: redis-server --appendonly yes
    volumes:
      - ./data/redis:/data
    ports:
      - "6379:6379"
    restart: unless-stopped
    healthcheck:
      test: ["CMD", "redis-cli", "ping"]
      interval: 10s
      timeout: 5s
      retries: 5

  # Backend API
  backend:
    build:
      context: ./backend
      dockerfile: Dockerfile
    container_name: vms-backend
    environment:
      - DATABASE_URL=postgresql+asyncpg://${POSTGRES_USER}:${POSTGRES_PASSWORD}@postgres:5432/${POSTGRES_DB}
      - REDIS_URL=redis://redis:6379/0
      - SECRET_KEY=${SECRET_KEY}
      - JWT_SECRET_KEY=${JWT_SECRET_KEY}
      - STORAGE_PATH=/data
    volumes:
      - ./data:/data
      - ./backend/app:/app/app
    ports:
      - "8000:8000"
    depends_on:
      postgres:
        condition: service_healthy
      redis:
        condition: service_healthy
    restart: unless-stopped
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8000/health"]
      interval: 30s
      timeout: 10s
      retries: 3

  # Frontend
  frontend:
    build:
      context: ./frontend
      dockerfile: Dockerfile
    container_name: vms-frontend
    ports:
      - "3000:80"
    depends_on:
      - backend
    restart: unless-stopped

  # Telegram Bot
  telegram-bot:
    build:
      context: ./telegram-bot
      dockerfile: Dockerfile
    container_name: vms-telegram-bot
    environment:
      - BOT_TOKEN=${TELEGRAM_BOT_TOKEN}
      - API_URL=http://backend:8000
    depends_on:
      - backend
    restart: unless-stopped

  # Nginx Reverse Proxy
  nginx:
    image: nginx:alpine
    container_name: vms-nginx
    volumes:
      - ./nginx/nginx.conf:/etc/nginx/nginx.conf:ro
      - ./nginx/ssl.conf:/etc/nginx/ssl.conf:ro
      - ./nginx/conf.d:/etc/nginx/conf.d:ro
      - ./data:/data:ro
      - ./certbot/conf:/etc/letsencrypt:ro
      - ./certbot/www:/var/www/certbot:ro
    ports:
      - "80:80"
      - "443:443"
    depends_on:
      - frontend
      - backend
    restart: unless-stopped

  # Prometheus Metrics
  prometheus:
    image: prom/prometheus:latest
    container_name: vms-prometheus
    volumes:
      - ./prometheus/prometheus.yml:/etc/prometheus/prometheus.yml:ro
      - ./prometheus/alerts.yml:/etc/prometheus/alerts.yml:ro
      - ./data/prometheus:/prometheus
    ports:
      - "9090:9090"
    command:
      - '--config.file=/etc/prometheus/prometheus.yml'
      - '--storage.tsdb.path=/prometheus'
    restart: unless-stopped

  # Grafana Dashboards
  grafana:
    image: grafana/grafana:latest
    container_name: vms-grafana
    environment:
      - GF_SECURITY_ADMIN_USER=${GRAFANA_USER}
      - GF_SECURITY_ADMIN_PASSWORD=${GRAFANA_PASSWORD}
    volumes:
      - ./grafana/dashboards:/etc/grafana/provisioning/dashboards:ro
      - ./grafana/provisioning:/etc/grafana/provisioning:ro
      - ./data/grafana:/var/lib/grafana
    ports:
      - "3001:3000"
    depends_on:
      - prometheus
    restart: unless-stopped

  # Certbot for SSL
  certbot:
    image: certbot/certbot:latest
    container_name: vms-certbot
    volumes:
      - ./certbot/conf:/etc/letsencrypt
      - ./certbot/www:/var/www/certbot
    entrypoint: "/bin/sh -c 'trap exit TERM; while :; do certbot renew; sleep 12h & wait $${!}; done;'"
    restart: unless-stopped

volumes:
  postgres:
  redis:
  prometheus:
  grafana:
```

---

## Заключение

Данный архитектурный проект описывает production-ready Video Management System для частного дома с учетом всех требований:

- **Модульный монолит** обеспечивает баланс между простотой и масштабируемостью
- **FastAPI + React** обеспечивают современную технологическую базу
- **PostgreSQL + Redis** обеспечивают надежное хранение данных
- **FFmpeg + YOLOv8** обеспечивают качественную обработку видео и AI детекцию
- **Docker Compose** обеспечивает простой деплой и масштабирование
- **Prometheus + Grafana** обеспечивают мониторинг и alerting
- **Комплексная безопасность** через HTTPS, шифрование, JWT и rate limiting

Архитектура спроектирована с учетом оптимизации CPU, RAM, дисковых и сетевых операций, что обеспечивает стабильную работу даже при большом количестве камер.
