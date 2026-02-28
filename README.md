# VMS (Video Management System)

Система управления видеонаблюдением с поддержкой AI-детекции, облачного хранения и WebSocket потокового вещания.

## 📋 Описание проекта

![VMS Dashboard](screenshots/wms-dashboard.jpg)

VMS — это полнофункциональная система видеонаблюдения, включающая:

- **Управление камерами**: добавление, настройка, тестирование RTSP потоков
- **AI-детекция**: распознавание людей, транспортных средств, животных (YOLO)
- **Запись видео**: непрерывная, по движению, по расписанию
- **Архивация**: автоматическое удаление старых записей
- **Потоковое вещание**: HLS потоки в реальном времени
- **Уведомления**: Telegram бот для оповещений
- **LLM интеграция**: анализ событий через LM Studio / Ollama
- **WebSocket**: реальное время обновление событий

## 🏗️ Архитектура

```
┌─────────────────────────────────────────────────────────────────┐
│                         Frontend (React + Vite)          │
│                      http://localhost:3000                │
└────────────────────────┬────────────────────────────────────┘
                       │
                       │ Nginx proxy
                       │
┌───────────────────────┴────────────────────────────────────┐
│                  Backend (FastAPI)                      │
│                   http://localhost:8000                   │
│  ┌──────────────────────────────────────────────────────┐  │
│  │  Auth │ Users │ Cameras │ Events │ Settings │  │  │
│  └──────────────────────────────────────────────────────┘  │
│  ┌──────────────────────────────────────────────────────┐  │
│  │  Services (Auth, Camera, Recording, etc.)      │  │
│  └──────────────────────────────────────────────────────┘  │
│  ┌──────────────────────────────────────────────────────┐  │
│  │  Workers (Camera, Recording, Detection, Cleanup)  │  │
│  └──────────────────────────────────────────────────────┘  │
└──────────┬──────────────┬──────────────┬───────────────┘
           │              │              │
    ┌──────┴──────┐  ┌──┴──────┐  ┌──┴──────┐
    │ SQLite       │  │ Redis    │  │ Storage  │
    │ (data/)     │  │ (cache)  │  │ (/data)  │
    └─────────────┘  └───────────┘  └───────────┘
```

## 🚀 Быстрый старт

### Требования

- Docker и Docker Compose
- Node.js 18+ (для локальной разработки)
- Python 3.11+ (для локальной разработки)
- FFmpeg

### Установка и запуск

#### 1. Клонирование репозитория

```bash
git clone <repository-url>
cd project_name
```

#### 2. Настройка переменных окружения

Скопируйте файл примера и отредактируйте:

```bash
cp .env.example .env
```

Основные переменные в `.env`:

```env
# Backend
BACKEND_HOST=0.0.0.0
BACKEND_PORT=8000
SECRET_KEY=your-secret-key-change-in-production

# Frontend
VITE_API_URL=http://localhost:8000/api/v1
VITE_WS_URL=ws://localhost:8000/ws

# Database (по умолчанию SQLite)
DATABASE_URL=sqlite+aiosqlite:///./data/vms.db

# Redis (опционально)
REDIS_URL=redis://localhost:6379/0
```

#### 3. Запуск с Docker Compose (рекомендуется)

**Режим разработки:**

```bash
docker-compose -f docker-compose.dev.yml up -d
```

**Режим производства:**

```bash
docker-compose -f docker-compose.prod.yml up -d
```

**Полный запуск со всеми сервисами:**

```bash
docker-compose up -d
```

#### 4. Локальная разработка

**Backend:**

```bash
cd backend
python -m venv venv
source venv/bin/activate  # Linux/Mac
# venv\Scripts\activate  # Windows
pip install -r requirements.txt
python -m app.main
```

**Frontend:**

```bash
cd frontend
npm install
npm run dev
```

## 📁 Структура проекта

```
project_name/
├── backend/                 # FastAPI backend
│   ├── app/
│   │   ├── api/           # API endpoints
│   │   ├── core/          # Core functionality (security, logger, websocket)
│   │   ├── models/        # SQLAlchemy models
│   │   ├── schemas/       # Pydantic schemas
│   │   ├── services/       # Business logic
│   │   ├── utils/         # Utilities (AI, ONVIF, RTSP, video)
│   │   └── workers/       # Background workers
│   ├── data/              # SQLite database, recordings, streams
│   ├── logs/              # Application logs
│   ├── Dockerfile
│   └── requirements.txt
├── frontend/              # React + Vite frontend
│   ├── src/
│   │   ├── api/          # API client
│   │   ├── components/    # React components
│   │   └── main.jsx      # Entry point
│   ├── public/            # Static assets
│   ├── Dockerfile
│   ├── nginx.conf        # Nginx configuration
│   └── package.json
├── docs/                 # Документация
│   ├── ARCHITECTURE.md
│   ├── DATABASE_SCHEMA.md
│   ├── API.md
│   └── DEPLOYMENT.md
├── docker-compose.yml           # Полный стек
├── docker-compose.dev.yml       # Разработка
├── docker-compose.prod.yml      # Производство
├── .gitignore
├── .env.example
└── README.md
```

## 🔧 Конфигурация

### Backend

Конфигурация находится в `backend/app/config.py`:

| Переменная | Описание | По умолчанию |
|------------|-----------|----------------|
| `APP_NAME` | Название приложения | VMS Backend |
| `DEBUG` | Режим отладки | False |
| `API_V1_PREFIX` | Префикс API | /api/v1 |
| `DATABASE_URL` | URL базы данных | sqlite+aiosqlite:///./data/vms.db |
| `REDIS_URL` | URL Redis | redis://localhost:6379/0 |
| `SECRET_KEY` | Ключ для JWT | your-secret-key |
| `CORS_ORIGINS` | Разрешённые origins | http://localhost:3000,http://localhost:5173 |

### Frontend

Конфигурация находится в `frontend/.env.development` и `frontend/.env.production`:

| Переменная | Описание | По умолчанию |
|------------|-----------|----------------|
| `VITE_API_URL` | URL API backend | http://localhost:8000/api/v1 |
| `VITE_WS_URL` | URL WebSocket | ws://localhost:8000/ws |

## 🌐 API Endpoints

### Аутентификация

```
POST   /api/v1/auth/login          # Вход в систему
POST   /api/v1/auth/logout         # Выход
POST   /api/v1/auth/refresh        # Обновление токена
POST   /api/v1/auth/change-password # Смена пароля
GET    /api/v1/auth/me            # Текущий пользователь
```

### Камеры

```
GET    /api/v1/cameras              # Список камер
POST   /api/v1/cameras              # Создать камеру
GET    /api/v1/cameras/{id}         # Получить камеру
PUT    /api/v1/cameras/{id}         # Обновить камеру
DELETE /api/v1/cameras/{id}         # Удалить камеру
POST   /api/v1/cameras/{id}/test    # Тестирование RTSP
POST   /api/v1/cameras/discover     # ONVIF обнаружение
```

### Записи

```
GET    /api/v1/recordings              # Список записей
GET    /api/v1/recordings/{id}         # Получить запись
DELETE /api/v1/recordings/{id}         # Удалить запись
POST   /api/v1/recordings/export       # Экспорт записей
```

### События

```
GET    /api/v1/events                  # Список событий
GET    /api/v1/events/stats            # Статистика событий
POST   /api/v1/events/acknowledge      # Подтвердить события
```

### Настройки

```
GET    /api/v1/settings                # Список настроек
POST   /api/v1/settings                # Создать настройку
GET    /api/v1/settings/{key}        # Получить настройку
PUT    /api/v1/settings/{key}        # Обновить настройку
DELETE /api/v1/settings/{key}        # Удалить настройку
POST   /api/v1/settings/bulk          # Массовое обновление
```

## 👥 Пользователи

### Создание администратора

```bash
cd backend
python create_admin_simple.py
```

Введите имя пользователя, email и пароль при запросе.

### Роли пользователей

- **admin**: полный доступ ко всем функциям
- **viewer**: только просмотр (без управления)

## 📊 Мониторинг

### Health Check

```bash
curl http://localhost:8000/health
```

Ответ:

```json
{
  "status": "healthy",
  "version": "1.0.0",
  "database": "connected",
  "redis": "connected",
  "llm": {
    "status": "disabled",
    "enabled": false,
    "provider": "lmstudio"
  }
}
```

### API Documentation

- Swagger UI: http://localhost:8000/api/v1/docs
- ReDoc: http://localhost:8000/api/v1/redoc
- OpenAPI JSON: http://localhost:8000/openapi.json

## 🔒 Безопасность

### Аутентификация

- JWT токены (access + refresh)
- Время жизни access токена: 30 минут
- Время жизни refresh токена: 7 дней

### CORS

Разрешённые origins настраиваются через `CORS_ORIGINS` в `.env`.

### Rate Limiting

Включён по умолчанию (60 запросов в минуту).

## 🧪 Тестирование

### Запуск тестов

```bash
cd backend
pytest tests/
```

### Тестирование API

```bash
# Тест входа
curl -X POST http://localhost:3000/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username":"admin","password":"admin12345"}'

# Тест списка камер
curl http://localhost:3000/api/v1/cameras \
  -H "Authorization: Bearer <token>"
```

## 🐛 Troubleshooting

### Проблема: 405 Method Not Allowed при login

**Решение:**

1. Убедитесь, что `VITE_API_URL=/api/v1` в `.env`
2. Нажмите **Ctrl+F5** для очистки кэша браузера
3. Пересоберите frontend: `docker-compose -f docker-compose.dev.yml up -d --build frontend`

### Проблема: База данных не подключается

**Решение:**

```bash
# Проверьте права доступа к папке data/
chmod 755 backend/data
```

### Проблема: RTSP поток не работает

**Решение:**

1. Проверьте RTSP URL: `rtsp://user:password@ip:port/path`
2. Протестируйте поток с FFmpeg:
```bash
ffplay rtsp://user:password@ip:port/path
```

## 📝 Логи

### Backend

```bash
# Docker
docker logs vms-backend-dev -f

# Локально
tail -f backend/logs/backend.log
```

### Frontend

```bash
# Docker
docker logs vms-frontend-dev -f
```

## 🚢 Развертывание

### Production

```bash
# Сборка и запуск
docker-compose -f docker-compose.prod.yml up -d --build

# Мониторинг
docker-compose -f docker-compose.prod.yml logs -f
```

### Nginx Reverse Proxy

Пример конфигурации для production:

```nginx
server {
    listen 80;
    server_name your-domain.com;

    location /api/v1/ {
        proxy_pass http://backend:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    location /ws/ {
        proxy_pass http://backend:8000/ws/;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
    }

    location / {
        root /usr/share/nginx/html;
        try_files $uri $uri/ /index.html;
    }
}
```

## 🤝 Вклад

1. Fork проект
2. Создайте ветку (`git checkout -b feature/AmazingFeature`)
3. Commit изменения (`git commit -m 'Add some AmazingFeature'`)
4. Push в ветку (`git push origin feature/AmazingFeature`)
5. Откройте Pull Request

## 📄 Лицензия

MIT License

## 👥 Поддержка

Для вопросов и проблем:
- Создайте Issue в репозитории
- Проверьте документацию в папке `docs/`

## 🔗 Полезные ссылки

- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [React Documentation](https://react.dev/)
- [Vite Documentation](https://vitejs.dev/)
- [YOLO Documentation](https://github.com/ultralytics/yolov5)
- [FFmpeg Documentation](https://ffmpeg.org/documentation.html)
