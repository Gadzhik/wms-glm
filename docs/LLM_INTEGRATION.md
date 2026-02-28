# Интеграция с LM Studio и Ollama

Документация по интеграции системы видеонаблюдения VMS с LLM (Large Language Models) через OpenAI-compatible API.

## Содержание

- [Обзор](#обзор)
- [Поддерживаемые провайдеры](#поддерживаемые-провайдеры)
- [Настройка](#настройка)
- [Функциональность](#функциональность)
- [Использование](#использование)
- [CPU-оптимизация](#cpu-оптимизация)
- [Безопасность](#безопасность)
- [Troubleshooting](#troubleshooting)

---

## Обзор

Система VMS поддерживает интеграцию с LLM для:

- 🧠 Генерации текстовых описаний событий
- 🔎 Семантического поиска через embeddings
- 📋 Автоматических ежедневных отчётов
- 🗣️ Интерпретации голосовых команд

### Graceful Fallback

Система продолжает работать корректно даже при недоступности LLM:
- Автоматическое переключение на fallback-логику
- Базовые описания и отчёты без LLM
- Никаких падений или зависаний

---

## Поддерживаемые провайдеры

### LM Studio

```env
LLM_PROVIDER=lmstudio
LLM_BASE_URL=http://localhost:1234/v1
```

**Установка LM Studio:**
1. Скачайте с [lmstudio.ai](https://lmstudio.ai)
2. Запустите сервер: `Server` → `Start Server`
3. Убедитесь, что порт 1234 доступен

### Ollama

```env
LLM_PROVIDER=ollama
LLM_BASE_URL=http://localhost:11434/v1
```

**Установка Ollama:**
```bash
# Linux/macOS
curl -fsSL https://ollama.ai/install.sh | sh

# Windows
# Скачайте установщик с ollama.ai

# Запуск модели
ollama run llama2
```

---

## Настройка

### 1. Переменные окружения

Добавьте в `.env` файл:

```env
# ==============================
# LLM Settings (LM Studio / Ollama)
# ==============================
LLM_ENABLED=true
LLM_PROVIDER=lmstudio
LLM_BASE_URL=http://localhost:1234/v1
LLM_MODEL=local-model
LLM_TIMEOUT=30
LLM_MAX_RETRIES=3
LLM_MIN_DELAY_SECONDS=5
LLM_MAX_CONCURRENT_CALLS=1
LLM_EMBEDDING_MODEL=nomic-embed-text
LLM_EMBEDDING_DIMENSION=768
LLM_HEALTH_CHECK_ENABLED=true
LLM_HEALTH_CHECK_TIMEOUT=5
LLM_CACHE_ENABLED=true
LLM_CACHE_TTL_SECONDS=3600
LLM_MAX_REQUEST_SIZE=10000
```

### 2. Установка зависимостей

```bash
cd backend
pip install -r requirements.txt
```

### 3. Миграция базы данных

```bash
# Для PostgreSQL
alembic upgrade head

# Для SQLite (автоматически при запуске)
# Миграция создаст необходимые поля
```

### 4. Инициализация LLM Bridge

LLM Bridge автоматически инициализируется при запуске приложения в [`backend/app/main.py`](backend/app/main.py):

```python
from app.services import initialize_llm_bridge, shutdown_llm_bridge

@app.on_event("startup")
async def startup_event():
    await initialize_llm_bridge()

@app.on_event("shutdown")
async def shutdown_event():
    await shutdown_llm_bridge()
```

---

## Функциональность

### 1. Генерация описаний событий

Автоматическое создание понятных описаний событий из JSON метаданных.

**Использование:**

```python
from app.services import get_llm_bridge

llm = get_llm_bridge()

event_data = {
    "event_type": "motion_detected",
    "camera_name": "Front Door",
    "timestamp": "2026-02-28T12:00:00",
    "confidence": 0.85,
    "metadata": {
        "motion_detected": True,
        "detected_objects": ["person"],
        "region": "entrance"
    }
}

description = await llm.generate_event_description(event_data)
# Результат: "Обнаружено движение на камере Front Door в 12:00. Уверенность: 85%."
```

**Fallback без LLM:**
```
"motion_detected на камере 'Front Door' в 2026-02-28T12:00:00"
```

### 2. Семантический поиск

Генерация embeddings для событий и пользовательских запросов.

**Использование:**

```python
# Генерация embedding для события
event_text = "Обнаружено движение на входе"
embedding = await llm.generate_embedding(event_text)

# Сохранение в БД
event.embedding = embedding
await db.commit()

# Поиск похожих событий
from sqlalchemy import func
from pgvector.sqlalchemy import cosine_distance

query_embedding = await llm.generate_embedding("поиск движения")

similar_events = await db.execute(
    select(Event)
    .order_by(cosine_distance(Event.embedding, query_embedding))
    .limit(10)
)
```

### 3. Автоматические отчёты

Генерация ежедневных сводок активности камер.

**Использование:**

```python
from datetime import datetime, timedelta

# Получение событий за день
yesterday = datetime.now() - timedelta(days=1)
events = await get_events_by_date(yesterday)

# Генерация отчёта
report = await llm.generate_daily_report(events, yesterday)
```

**Пример отчёта:**
```
Отчёт за 2026-02-27

Обзор активности:
Всего зафиксировано 45 событий на 5 камерах.

Основные события:
- Обнаружено движение: 32 события
- Обнаружен человек: 12 событий
- Камера оффлайн: 1 событие

Рекомендации:
- Обратите внимание на камеру "Backyard" - высокая активность ночью
- Проверьте камеру "Garage" - была офлайн 27 февраля
```

### 4. Интерпретация голосовых команд

Обработка распознанного текста и преобразование в команды системы.

**Использование:**

```python
# Распознанный текст от Whisper
command_text = "начать запись на камере Front Door"

# Интерпретация
result = await llm.interpret_voice_command(command_text)

# Результат:
# {
#     "action": "start_recording",
#     "camera_name": "Front Door",
#     "parameters": {},
#     "confidence": 0.9
# }

# Выполнение команды
if result["action"] == "start_recording":
    await start_recording(result["camera_name"])
```

**Поддерживаемые команды:**
- `start_recording` - начать запись
- `stop_recording` - остановить запись
- `show_camera` - показать камеру
- `search_events` - поиск событий
- `show_events` - показать события
- `export_recording` - экспорт записи
- `list_cameras` - список камер

---

## CPU-оптимизация

Система оптимизирована для работы на CPU-only конфигурациях:

### Rate Limiting

Минимальная задержка между запросами (по умолчанию 5 секунд):

```env
LLM_MIN_DELAY_SECONDS=5
```

### Concurrency Control

Ограничение одновременных запросов (по умолчанию 1):

```env
LLM_MAX_CONCURRENT_CALLS=1
```

### Кэширование

Кэширование ответов LLM для уменьшения количества запросов:

```env
LLM_CACHE_ENABLED=true
LLM_CACHE_TTL_SECONDS=3600
```

### Таймауты

Защита от зависания LLM:

```env
LLM_TIMEOUT=30
LLM_HEALTH_CHECK_TIMEOUT=5
```

### Retry Logic

Автоматический повтор при ошибках:

```env
LLM_MAX_RETRIES=3
```

---

## Безопасность

### Ограничение размера запроса

```env
LLM_MAX_REQUEST_SIZE=10000
```

Запросы превышающие лимит отклоняются с ошибкой [`LLMRequestTooLargeError`](backend/app/services/llm_bridge.py:65).

### Не отправлять видео

Система отправляет только JSON метаданные, никогда не отправляет:
- Видео файлы
- Изображения
- Аудиофайлы (кроме текста от Whisper)

### Логирование ошибок

Все ошибки LLM логируются в [`backend/logs/ai.log`](backend/logs/ai.log):

```
2026-02-28 12:00:00 - ERROR - LLM request failed: timeout
2026-02-28 12:00:05 - WARNING - LLM unavailable, using fallback
```

### Health Check

Автоматическая проверка доступности LLM при запуске:

```env
LLM_HEALTH_CHECK_ENABLED=true
```

---

## Использование

### В API endpoints

```python
from app.services import get_llm_bridge
from fastapi import APIRouter, Depends

router = APIRouter()

@router.post("/events/{event_id}/describe")
async def describe_event(event_id: int):
    llm = get_llm_bridge()
    
    event = await get_event(event_id)
    event_data = event.to_dict()
    
    description = await llm.generate_event_description(event_data)
    
    event.description = description
    await db.commit()
    
    return {"description": description}
```

### В workers

```python
from app.services import get_llm_bridge

async def process_event(event_data):
    llm = get_llm_bridge()
    
    # Генерация описания
    description = await llm.generate_event_description(event_data)
    
    # Генерация embedding
    embedding = await llm.generate_embedding(description)
    
    return {
        "description": description,
        "embedding": embedding
    }
```

### Проверка доступности

```python
from app.services import get_llm_bridge

llm = get_llm_bridge()

if llm.is_available:
    print("LLM доступен")
else:
    print(f"LLM недоступен: {llm.status}")
```

### Получение статистики

```python
stats = llm.get_stats()

# {
#     "enabled": true,
#     "provider": "lmstudio",
#     "status": "enabled",
#     "model": "local-model",
#     "concurrent_requests": 0,
#     "cache_size": 15,
#     "health_checked": true
# }
```

---

## Troubleshooting

### LLM недоступен

**Проблема:** `LLMStatus.UNAVAILABLE`

**Решения:**
1. Проверьте, что LLM запущен:
   ```bash
   # LM Studio
   curl http://localhost:1234/v1/models
   
   # Ollama
   curl http://localhost:11434/v1/models
   ```

2. Проверьте настройки в `.env`:
   ```env
   LLM_BASE_URL=http://localhost:1234/v1
   LLM_TIMEOUT=30
   ```

3. Проверьте логи:
   ```
   tail -f backend/logs/ai.log
   ```

### Таймаут запроса

**Проблема:** `LLMTimeoutError`

**Решения:**
1. Увеличьте таймаут:
   ```env
   LLM_TIMEOUT=60
   ```

2. Уменьшите размер запроса:
   ```env
   LLM_MAX_REQUEST_SIZE=5000
   ```

3. Используйте более быструю модель

### Медленная работа

**Проблема:** Долгое время ответа

**Решения:**
1. Включите кэширование:
   ```env
   LLM_CACHE_ENABLED=true
   LLM_CACHE_TTL_SECONDS=7200
   ```

2. Уменьшите задержку между запросами:
   ```env
   LLM_MIN_DELAY_SECONDS=3
   ```

3. Используйте более легкую модель

### Ошибки pgvector

**Проблема:** Ошибка при работе с embeddings

**Решения:**
1. Убедитесь, что PostgreSQL установлен:
   ```bash
   psql --version
   ```

2. Включите расширение pgvector:
   ```sql
   CREATE EXTENSION IF NOT EXISTS vector;
   ```

3. Проверьте миграцию:
   ```bash
   alembic current
   ```

### SQLite вместо PostgreSQL

Система работает с SQLite, но pgvector не поддерживается:

```python
# Embeddings будут храниться как TEXT (JSON массив)
# Семантический поиск не будет работать
```

Для полной функциональности используйте PostgreSQL.

---

## Тестирование

Запуск тестов LLM интеграции:

```bash
cd backend
pytest tests/test_llm_integration.py -v
```

Запуск конкретного теста:

```bash
pytest tests/test_llm_integration.py::TestEventDescriptionGeneration::test_generate_description_success -v
```

---

## API Reference

### LLMBridge

Основной класс для работы с LLM.

#### Методы

##### `async initialize() -> None`
Инициализация сервиса и health check.

##### `async shutdown() -> None`
Очистка ресурсов.

##### `async generate_event_description(event_data: Dict[str, Any]) -> str`
Генерация описания события.

##### `async generate_embedding(text: str) -> Optional[List[float]]`
Генерация embedding.

##### `async generate_daily_report(events: List[Dict[str, Any]], date: datetime) -> str`
Генерация ежедневного отчёта.

##### `async interpret_voice_command(command: str) -> Dict[str, Any]`
Интерпретация голосовой команды.

##### `get_stats() -> Dict[str, Any]`
Получение статистики сервиса.

#### Свойства

##### `status: LLMStatus`
Текущий статус LLM.

##### `is_available: bool`
Доступен ли LLM.

---

## Константы

### LLMProvider

```python
class LLMProvider(str, Enum):
    LMSTUDIO = "lmstudio"
    OLLAMA = "ollama"
```

### LLMStatus

```python
class LLMStatus(str, Enum):
    ENABLED = "enabled"
    DISABLED = "disabled"
    UNAVAILABLE = "unavailable"
    ERROR = "error"
```

---

## Дополнительные ресурсы

- [LM Studio Documentation](https://lmstudio.ai/docs)
- [Ollama Documentation](https://ollama.ai/docs)
- [OpenAI API Reference](https://platform.openai.com/docs/api-reference)
- [pgvector Documentation](https://github.com/pgvector/pgvector)

---

## Лицензия

Часть проекта VMS. См. LICENSE файл.
