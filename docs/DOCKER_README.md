# Docker Compose для VMS системы

## Обзор

Этот проект содержит полную Docker Compose конфигурацию для Video Management System (VMS), включающую все необходимые сервисы для разработки и production.

## Структура файлов

```
.
├── docker-compose.yml           # Основной Docker Compose файл
├── docker-compose.dev.yml       # Конфигурация для разработки
├── docker-compose.prod.yml      # Конфигурация для production
├── .env                         # Переменные окружения
├── .env.example                 # Пример переменных окружения
├── nginx/
│   ├── nginx.conf             # Конфигурация Nginx reverse proxy
│   └── ssl/                    # Директория для SSL сертификатов
├── prometheus/
│   └── prometheus.yml          # Конфигурация Prometheus
├── grafana/
│   ├── provisioning/
│   │   ├── datasources/       # Источники данных Grafana
│   │   └── dashboards/         # Конфигурация дашбордов
│   └── dashboards/
│       └── vms-overview.json  # Пример дашборда VMS
└── telegram-bot/
    ├── Dockerfile              # Dockerfile для Telegram бота
    ├── main.py                # Основной файл бота
    └── requirements.txt       # Зависимости Python
```

## Сервисы

| Сервис | Описание | Порты |
|--------|----------|-------|
| **backend** | FastAPI backend | 8000 |
| **frontend** | React frontend (Nginx) | 3000 |
| **postgres** | PostgreSQL база данных | 5432 |
| **redis** | Redis для кэша и очередей | 6379 |
| **telegram-bot** | Telegram бот | - |
| **prometheus** | Мониторинг | 9090 |
| **grafana** | Дашборды | 3001 |
| **nginx** | Reverse proxy | 80, 443 |

## Быстрый старт

### 1. Настройка переменных окружения

Скопируйте пример и отредактируйте:

```bash
cp .env.example .env
```

Отредактируйте `.env` файл, установив необходимые значения:

- `POSTGRES_PASSWORD` - пароль для PostgreSQL
- `SECRET_KEY` - секретный ключ для JWT токенов
- `TELEGRAM_BOT_TOKEN` - токен Telegram бота (если используется)
- `TELEGRAM_CHAT_ID` - ID чата для уведомлений (если используется)

### 2. Запуск в режиме разработки

```bash
docker-compose -f docker-compose.yml -f docker-compose.dev.yml up -d
```

Режим разработки включает:
- Hot reload для backend и frontend
- Debug порты
- Отключенный мониторинг (Prometheus/Grafana)

### 3. Запуск в режиме production

```bash
docker-compose -f docker-compose.yml -f docker-compose.prod.yml up -d
```

Режим production включает:
- Все сервисы оптимизированы
- Мониторинг (Prometheus/Grafana)
- Nginx reverse proxy
- Resource limits

### 4. Запуск с мониторингом (dev)

```bash
docker-compose -f docker-compose.yml -f docker-compose.dev.yml --profile monitoring up -d
```

### 5. Запуск с Nginx proxy (dev)

```bash
docker-compose -f docker-compose.yml -f docker-compose.dev.yml --profile proxy up -d
```

## Управление контейнерами

### Просмотр статуса

```bash
docker-compose ps
```

### Просмотр логов

```bash
# Все сервисы
docker-compose logs -f

# Конкретный сервис
docker-compose logs -f backend
```

### Остановка

```bash
# Остановка контейнеров
docker-compose stop

# Остановка и удаление контейнеров
docker-compose down

# Остановка и удаление контейнеров и volumes
docker-compose down -v
```

### Пересборка

```bash
# Пересборка всех сервисов
docker-compose build

# Пересборка конкретного сервиса
docker-compose build backend

# Пересборка и запуск
docker-compose up -d --build
```

## Доступ к сервисам

После запуска сервисы будут доступны по следующим адресам:

| Сервис | URL | Логин/Пароль |
|--------|-----|--------------|
| Frontend | http://localhost:3000 | - |
| Backend API | http://localhost:8000 | - |
| API Docs | http://localhost:8000/docs | - |
| Prometheus | http://localhost:9090 | - |
| Grafana | http://localhost:3001 | admin / (из .env) |

## SSL сертификаты

Для production режима с HTTPS:

1. Получите SSL сертификаты (например, через Let's Encrypt):

```bash
certbot certonly --standalone -d your-domain.com
```

2. Скопируйте сертификаты в директорию `nginx/ssl/`:

```bash
cp /etc/letsencrypt/live/your-domain.com/fullchain.pem nginx/ssl/
cp /etc/letsencrypt/live/your-domain.com/privkey.pem nginx/ssl/
cp /etc/letsencrypt/live/your-domain.com/chain.pem nginx/ssl/
```

3. Обновите `NGINX_SERVER_NAME` в `.env` файле:

```env
NGINX_SERVER_NAME=your-domain.com
```

## Telegram Bot

### Настройка

1. Создайте бота через [@BotFather](https://t.me/BotFather)
2. Получите токен бота
3. Добавьте токен в `.env` файл:

```env
TELEGRAM_BOT_TOKEN=your_bot_token_here
TELEGRAM_CHAT_ID=your_chat_id_here
```

### Команды бота

- `/start` - Главное меню
- `/help` - Справка
- `/status` - Статус системы
- `/cameras` - Список камер
- `/events` - Последние события
- `/recordings` - Последние записи
- `/start_camera <id>` - Запустить камеру
- `/stop_camera <id>` - Остановить камеру
- `/snapshot <id>` - Получить снимок

## Мониторинг

### Prometheus

- URL: http://localhost:9090
- Конфигурация: [`prometheus/prometheus.yml`](prometheus/prometheus.yml)
- Метрики собираются каждые 15 секунд

### Grafana

- URL: http://localhost:3001
- Дашборды: [`grafana/dashboards/`](grafana/dashboards/)
- Данные: Автоматически подтягиваются из Prometheus

## Volume'ы

Следующие named volumes используются для персистентных данных:

- `vms_postgres_data` - Данные PostgreSQL
- `vms_redis_data` - Данные Redis
- `vms_storage_data` - Хранилище видео
- `vms_models_data` - AI модели
- `vms_prometheus_data` - Данные Prometheus
- `vms_grafana_data` - Данные Grafana
- `vms_nginx_logs` - Логи Nginx

## Health Checks

Все сервисы имеют health checks:

```bash
# Проверка health status
docker-compose ps

# Проверка конкретного сервиса
docker inspect vms-backend | grep -A 10 Health
```

## Troubleshooting

### Проблемы с портом

Если порт уже занят, измените его в `.env` файле:

```env
BACKEND_PORT=8001
FRONTEND_PORT=3001
```

### Проблемы с базой данных

```bash
# Пересоздать базу данных
docker-compose down -v
docker-compose up -d postgres
```

### Проблемы с памятью

Увеличьте resource limits в [`docker-compose.prod.yml`](docker-compose.prod.yml):

```yaml
deploy:
  resources:
    limits:
      memory: 8G
```

### Просмотр логов

```bash
# Все логи
docker-compose logs

# Логи конкретного сервиса
docker-compose logs backend

# Последние 100 строк
docker-compose logs --tail=100 backend

# Логи в реальном времени
docker-compose logs -f backend
```

## Production рекомендации

1. **Безопасность**
   - Измените все пароли по умолчанию
   - Используйте сложный `SECRET_KEY`
   - Включите HTTPS
   - Настройте firewall

2. **Мониторинг**
   - Настройте алерты в Prometheus
   - Добавьте больше метрик
   - Настройте бэкап данных

3. **Производительность**
   - Настройте resource limits
   - Используйте внешнее хранилище для видео
   - Оптимизируйте конфигурацию Nginx

4. **Бэкап**
   - Регулярно бэкапите базу данных
   - Бэкапите Grafana дашборды
   - Бэкапите конфигурационные файлы

## Дополнительные команды

### Выполнение команд в контейнере

```bash
# Backend
docker-compose exec backend bash

# PostgreSQL
docker-compose exec postgres psql -U vms_user -d vms

# Redis
docker-compose exec redis redis-cli
```

### Миграции базы данных

```bash
docker-compose exec backend alembic upgrade head
```

### Очистка

```bash
# Удалить все контейнеры, volumes и сети
docker-compose down -v --remove-orphans

# Удалить неиспользуемые образы
docker image prune -a

# Удалить неиспользуемые volumes
docker volume prune
```

## Поддержка

Для получения помощи или сообщения о проблемах, пожалуйста, создайте issue в репозитории проекта.
