"""
LLM Bridge Service - Интеграция с LM Studio и Ollama через OpenAI-compatible API

Этот модуль обеспечивает:
- Генерацию текстовых описаний событий
- Семантический поиск через embeddings
- Автоматические отчёты
- Интерпретацию голосовых команд
- Graceful fallback при недоступности LLM
- CPU-оптимизацию (очереди, таймауты, кэширование)
"""

import asyncio
import json
import time
import hashlib
from datetime import datetime, timedelta
from typing import Optional, Dict, List, Any, Tuple
from enum import Enum
from dataclasses import dataclass, field

import httpx
from pydantic import BaseModel, Field

from app.config import settings
from app.core.logger import get_logger

logger = get_logger(__name__)


class LLMProvider(str, Enum):
    """Поддерживаемые LLM провайдеры"""
    LMSTUDIO = "lmstudio"
    OLLAMA = "ollama"


class LLMStatus(str, Enum):
    """Статус LLM сервиса"""
    ENABLED = "enabled"
    DISABLED = "disabled"
    UNAVAILABLE = "unavailable"
    ERROR = "error"


@dataclass
class LLMCacheEntry:
    """Запись в кэше LLM"""
    key: str
    value: Any
    created_at: datetime = field(default_factory=datetime.now)
    expires_at: Optional[datetime] = None
    
    def is_expired(self) -> bool:
        """Проверить истечение срока действия"""
        if self.expires_at is None:
            return False
        return datetime.now() > self.expires_at


class LLMRequestError(Exception):
    """Ошибка запроса к LLM"""
    pass


class LLMUnavailableError(Exception):
    """LLM недоступен"""
    pass


class LLMTimeoutError(Exception):
    """Таймаут запроса к LLM"""
    pass


class LLMRequestTooLargeError(Exception):
    """Запрос слишком большой"""
    pass


class LLMBridge:
    """
    Сервис для интеграции с LM Studio и Ollama
    
    Особенности:
    - Graceful fallback при недоступности
    - CPU-оптимизация через очереди и задержки
    - Кэширование ответов
    - Retry логика
    - Таймауты для защиты от зависаний
    """
    
    def __init__(self):
        self._enabled: bool = settings.LLM_ENABLED
        self._provider: LLMProvider = LLMProvider(settings.LLM_PROVIDER)
        self._base_url: str = settings.LLM_BASE_URL
        self._model: str = settings.LLM_MODEL
        self._timeout: int = settings.LLM_TIMEOUT
        self._max_retries: int = settings.LLM_MAX_RETRIES
        self._min_delay: float = settings.LLM_MIN_DELAY_SECONDS
        self._max_concurrent: int = settings.LLM_MAX_CONCURRENT_CALLS
        self._embedding_model: str = settings.LLM_EMBEDDING_MODEL
        self._embedding_dimension: int = settings.LLM_EMBEDDING_DIMENSION
        self._health_check_enabled: bool = settings.LLM_HEALTH_CHECK_ENABLED
        self._health_check_timeout: int = settings.LLM_HEALTH_CHECK_TIMEOUT
        self._cache_enabled: bool = settings.LLM_CACHE_ENABLED
        self._cache_ttl: int = settings.LLM_CACHE_TTL_SECONDS
        self._max_request_size: int = settings.LLM_MAX_REQUEST_SIZE
        
        # Внутреннее состояние
        self._status: LLMStatus = LLMStatus.DISABLED
        self._last_request_time: float = 0.0
        self._concurrent_requests: int = 0
        self._request_lock = asyncio.Lock()
        self._cache: Dict[str, LLMCacheEntry] = {}
        self._client: Optional[httpx.AsyncClient] = None
        self._health_checked: bool = False
        
        logger.info(
            f"LLMBridge initialized: provider={self._provider}, "
            f"enabled={self._enabled}, model={self._model}"
        )
    
    async def initialize(self) -> None:
        """Инициализация сервиса"""
        if not self._enabled:
            logger.info("LLM integration is disabled")
            self._status = LLMStatus.DISABLED
            return
        
        try:
            # Создаём HTTP клиент
            self._client = httpx.AsyncClient(
                timeout=self._timeout,
                limits=httpx.Limits(max_connections=1, max_keepalive_connections=1)
            )
            
            # Проверяем доступность если включено
            if self._health_check_enabled:
                await self._health_check()
            else:
                self._status = LLMStatus.ENABLED
                logger.info("LLM health check disabled, assuming available")
            
        except Exception as e:
            logger.error(f"Failed to initialize LLMBridge: {e}")
            self._status = LLMStatus.ERROR
            # Graceful fallback - не падаем, продолжаем работу без LLM
    
    async def shutdown(self) -> None:
        """Очистка ресурсов"""
        if self._client:
            await self._client.aclose()
            self._client = None
        
        # Очищаем кэш
        self._cache.clear()
        logger.info("LLMBridge shutdown complete")
    
    async def _health_check(self) -> bool:
        """
        Проверка доступности LLM
        
        Returns:
            True если LLM доступен, False иначе
        """
        if not self._client:
            logger.warning("LLM client not initialized")
            return False
        
        try:
            logger.info(f"Performing LLM health check to {self._base_url}")
            
            # Проверяем через /models endpoint (OpenAI-compatible)
            response = await self._client.get(
                f"{self._base_url}/models",
                timeout=self._health_check_timeout
            )
            
            if response.status_code == 200:
                self._status = LLMStatus.ENABLED
                self._health_checked = True
                logger.info("LLM health check passed")
                return True
            else:
                logger.warning(f"LLM health check failed: status={response.status_code}")
                self._status = LLMStatus.UNAVAILABLE
                return False
                
        except httpx.TimeoutException:
            logger.warning("LLM health check timeout")
            self._status = LLMStatus.UNAVAILABLE
            return False
        except Exception as e:
            logger.error(f"LLM health check error: {e}")
            self._status = LLMStatus.ERROR
            return False
    
    @property
    def status(self) -> LLMStatus:
        """Текущий статус LLM"""
        return self._status
    
    @property
    def is_available(self) -> bool:
        """Доступен ли LLM для использования"""
        return self._enabled and self._status == LLMStatus.ENABLED
    
    async def _wait_for_rate_limit(self) -> None:
        """
        Ожидание для соблюдения rate limit (CPU-оптимизация)
        """
        now = time.time()
        time_since_last = now - self._last_request_time
        
        if time_since_last < self._min_delay:
            wait_time = self._min_delay - time_since_last
            logger.debug(f"Rate limit: waiting {wait_time:.2f}s")
            await asyncio.sleep(wait_time)
    
    async def _acquire_concurrent_slot(self) -> None:
        """
        Получение слота для конкурентного запроса
        """
        async with self._request_lock:
            while self._concurrent_requests >= self._max_concurrent:
                logger.debug("Waiting for concurrent LLM request slot")
                await asyncio.sleep(0.1)
            self._concurrent_requests += 1
    
    async def _release_concurrent_slot(self) -> None:
        """Освобождение слота"""
        async with self._request_lock:
            self._concurrent_requests = max(0, self._concurrent_requests - 1)
    
    def _get_cache_key(self, prompt: str, model: str) -> str:
        """Генерация ключа кэша"""
        content = f"{model}:{prompt}"
        return hashlib.md5(content.encode()).hexdigest()
    
    def _get_from_cache(self, key: str) -> Optional[Any]:
        """Получение из кэша"""
        if not self._cache_enabled:
            return None
        
        entry = self._cache.get(key)
        if entry and not entry.is_expired():
            logger.debug(f"Cache hit for key {key}")
            return entry.value
        
        # Удаляем истёкшие записи
        if entry and entry.is_expired():
            del self._cache[key]
        
        return None
    
    def _set_cache(self, key: str, value: Any) -> None:
        """Сохранение в кэш"""
        if not self._cache_enabled:
            return
        
        expires_at = datetime.now() + timedelta(seconds=self._cache_ttl)
        self._cache[key] = LLMCacheEntry(
            key=key,
            value=value,
            expires_at=expires_at
        )
        logger.debug(f"Cached response for key {key}")
    
    def _validate_request_size(self, text: str) -> None:
        """Проверка размера запроса"""
        if len(text) > self._max_request_size:
            raise LLMRequestTooLargeError(
                f"Request size {len(text)} exceeds maximum {self._max_request_size}"
            )
    
    async def _make_llm_request(
        self,
        messages: List[Dict[str, str]],
        model: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: Optional[int] = None
    ) -> str:
        """
        Выполнение запроса к LLM с retry логикой
        
        Args:
            messages: Список сообщений для LLM
            model: Модель (используется default если не указан)
            temperature: Температура генерации
            max_tokens: Максимальное количество токенов
            
        Returns:
            Сгенерированный текст
            
        Raises:
            LLMUnavailableError: Если LLM недоступен
            LLMTimeoutError: Если превышен таймаут
            LLMRequestError: При ошибке запроса
        """
        if not self.is_available:
            raise LLMUnavailableError("LLM is not available")
        
        model = model or self._model
        
        # Проверяем размер запроса
        total_text = " ".join(m.get("content", "") for m in messages)
        self._validate_request_size(total_text)
        
        # Проверяем кэш
        cache_key = self._get_cache_key(json.dumps(messages), model)
        cached = self._get_from_cache(cache_key)
        if cached is not None:
            return cached
        
        # Rate limiting и concurrency
        await self._wait_for_rate_limit()
        await self._acquire_concurrent_slot()
        
        start_time = time.time()
        last_error = None
        
        try:
            for attempt in range(self._max_retries):
                try:
                    logger.info(
                        f"LLM request attempt {attempt + 1}/{self._max_retries}, "
                        f"model={model}"
                    )
                    
                    payload = {
                        "model": model,
                        "messages": messages,
                        "temperature": temperature
                    }
                    
                    if max_tokens:
                        payload["max_tokens"] = max_tokens
                    
                    response = await self._client.post(
                        f"{self._base_url}/chat/completions",
                        json=payload,
                        timeout=self._timeout
                    )
                    
                    if response.status_code == 200:
                        data = response.json()
                        content = data["choices"][0]["message"]["content"]
                        
                        # Логируем время ответа
                        elapsed = time.time() - start_time
                        logger.info(
                            f"LLM request completed in {elapsed:.2f}s, "
                            f"response length={len(content)}"
                        )
                        
                        # Кэшируем результат
                        self._set_cache(cache_key, content)
                        
                        return content
                    else:
                        error_msg = f"LLM request failed: status={response.status_code}"
                        logger.warning(f"{error_msg}, response={response.text}")
                        last_error = error_msg
                        
                        if attempt < self._max_retries - 1:
                            # Экспоненциальный backoff
                            backoff = 2 ** attempt
                            logger.info(f"Retrying in {backoff}s...")
                            await asyncio.sleep(backoff)
                        
                except httpx.TimeoutException:
                    error_msg = f"LLM request timeout after {self._timeout}s"
                    logger.warning(error_msg)
                    last_error = error_msg
                    
                    if attempt < self._max_retries - 1:
                        await asyncio.sleep(2 ** attempt)
                
                except httpx.HTTPError as e:
                    error_msg = f"LLM HTTP error: {e}"
                    logger.error(error_msg)
                    last_error = error_msg
                    
                    if attempt < self._max_retries - 1:
                        await asyncio.sleep(2 ** attempt)
            
            # Все попытки неудачны
            raise LLMRequestError(f"LLM request failed after {self._max_retries} retries: {last_error}")
            
        finally:
            self._last_request_time = time.time()
            await self._release_concurrent_slot()
    
    async def generate_event_description(self, event_data: Dict[str, Any]) -> str:
        """
        Генерация текстового описания события из JSON метаданных
        
        Args:
            event_data: JSON данные события
            
        Returns:
            Понятное текстовое описание события
            
        Raises:
            LLMUnavailableError: Если LLM недоступен
        """
        if not self.is_available:
            # Graceful fallback - базовое описание
            return self._generate_fallback_description(event_data)
        
        try:
            # Формируем промпт
            prompt = self._build_event_description_prompt(event_data)
            
            messages = [
                {
                    "role": "system",
                    "content": "Ты - ассистент системы видеонаблюдения. Создавай понятные и информативные описания событий на основе JSON данных."
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ]
            
            description = await self._make_llm_request(
                messages=messages,
                temperature=0.5,
                max_tokens=200
            )
            
            logger.info(f"Generated event description: {description[:100]}...")
            return description
            
        except (LLMUnavailableError, LLMRequestError) as e:
            logger.warning(f"LLM description generation failed: {e}, using fallback")
            return self._generate_fallback_description(event_data)
    
    def _build_event_description_prompt(self, event_data: Dict[str, Any]) -> str:
        """Построение промпта для генерации описания события"""
        event_type = event_data.get("event_type", "неизвестное событие")
        camera_name = event_data.get("camera_name", "камера")
        timestamp = event_data.get("timestamp", datetime.now().isoformat())
        confidence = event_data.get("confidence", 0)
        metadata = event_data.get("metadata", {})
        
        # Извлекаем дополнительную информацию
        detected_objects = metadata.get("detected_objects", [])
        motion_detected = metadata.get("motion_detected", False)
        
        prompt = f"""
Создай краткое описание события (1-2 предложения) на русском языке:

Тип события: {event_type}
Камера: {camera_name}
Время: {timestamp}
Уверенность: {confidence:.2%}
Движение: {'да' if motion_detected else 'нет'}
Обнаруженные объекты: {', '.join(detected_objects) if detected_objects else 'нет'}

Дополнительные данные: {json.dumps(metadata, ensure_ascii=False)}
"""
        return prompt
    
    def _generate_fallback_description(self, event_data: Dict[str, Any]) -> str:
        """Генерация базового описания без LLM"""
        event_type = event_data.get("event_type", "Событие")
        camera_name = event_data.get("camera_name", "камера")
        timestamp = event_data.get("timestamp", datetime.now().isoformat())
        
        return f"{event_type} на камере '{camera_name}' в {timestamp}"
    
    async def generate_embedding(self, text: str) -> Optional[List[float]]:
        """
        Генерация embedding для семантического поиска
        
        Args:
            text: Текст для генерации embedding
            
        Returns:
            Вектор embedding или None если LLM недоступен
            
        Raises:
            LLMUnavailableError: Если LLM недоступен
        """
        if not self.is_available:
            logger.warning("LLM not available, embedding generation skipped")
            return None
        
        try:
            self._validate_request_size(text)
            
            # Проверяем кэш
            cache_key = self._get_cache_key(f"embed:{text}", self._embedding_model)
            cached = self._get_from_cache(cache_key)
            if cached is not None:
                return cached
            
            # Rate limiting
            await self._wait_for_rate_limit()
            await self._acquire_concurrent_slot()
            
            start_time = time.time()
            
            try:
                payload = {
                    "model": self._embedding_model,
                    "input": text
                }
                
                response = await self._client.post(
                    f"{self._base_url}/embeddings",
                    json=payload,
                    timeout=self._timeout
                )
                
                if response.status_code == 200:
                    data = response.json()
                    embedding = data["data"][0]["embedding"]
                    
                    elapsed = time.time() - start_time
                    logger.info(f"Embedding generated in {elapsed:.2f}s, dimension={len(embedding)}")
                    
                    # Кэшируем
                    self._set_cache(cache_key, embedding)
                    
                    return embedding
                else:
                    logger.warning(f"Embedding request failed: status={response.status_code}")
                    return None
                    
            except httpx.TimeoutException:
                logger.warning("Embedding request timeout")
                return None
            except httpx.HTTPError as e:
                logger.error(f"Embedding HTTP error: {e}")
                return None
                
            finally:
                self._last_request_time = time.time()
                await self._release_concurrent_slot()
                
        except LLMRequestTooLargeError as e:
            logger.warning(f"Embedding request too large: {e}")
            return None
    
    async def generate_daily_report(
        self,
        events: List[Dict[str, Any]],
        date: datetime
    ) -> str:
        """
        Генерация ежедневного отчёта активности камер
        
        Args:
            events: Список событий за день
            date: Дата отчёта
            
        Returns:
            Текст отчёта
        """
        if not self.is_available:
            return self._generate_fallback_report(events, date)
        
        try:
            # Формируем промпт
            prompt = self._build_daily_report_prompt(events, date)
            
            messages = [
                {
                    "role": "system",
                    "content": "Ты - ассистент системы видеонаблюдения. Создавай структурированные отчёты о активности камер."
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ]
            
            report = await self._make_llm_request(
                messages=messages,
                temperature=0.3,
                max_tokens=500
            )
            
            logger.info(f"Generated daily report for {date.date()}")
            return report
            
        except (LLMUnavailableError, LLMRequestError) as e:
            logger.warning(f"LLM report generation failed: {e}, using fallback")
            return self._generate_fallback_report(events, date)
    
    def _build_daily_report_prompt(self, events: List[Dict[str, Any]], date: datetime) -> str:
        """Построение промпта для генерации отчёта"""
        # Статистика
        total_events = len(events)
        events_by_type = {}
        events_by_camera = {}
        
        for event in events:
            event_type = event.get("event_type", "неизвестно")
            camera = event.get("camera_name", "неизвестно")
            
            events_by_type[event_type] = events_by_type.get(event_type, 0) + 1
            events_by_camera[camera] = events_by_camera.get(camera, 0) + 1
        
        # Формируем промпт
        prompt = f"""
Создай структурированный отчёт за {date.date()} на русском языке:

Общее количество событий: {total_events}

События по типам:
{chr(10).join(f'  - {t}: {c}' for t, c in events_by_type.items())}

События по камерам:
{chr(10).join(f'  - {c}: {e}' for c, e in events_by_camera.items())}

Детали событий (последние 10):
{json.dumps(events[-10:], ensure_ascii=False, indent=2)}

Отчёт должен включать:
1. Обзор активности
2. Основные события
3. Рекомендации по вниманию
"""
        return prompt
    
    def _generate_fallback_report(self, events: List[Dict[str, Any]], date: datetime) -> str:
        """Генерация базового отчёта без LLM"""
        total = len(events)
        
        events_by_type = {}
        for event in events:
            event_type = event.get("event_type", "неизвестно")
            events_by_type[event_type] = events_by_type.get(event_type, 0) + 1
        
        lines = [
            f"Отчёт за {date.date()}",
            f"Всего событий: {total}",
            "",
            "События по типам:"
        ]
        
        for event_type, count in events_by_type.items():
            lines.append(f"  - {event_type}: {count}")
        
        return "\n".join(lines)
    
    async def interpret_voice_command(self, command: str) -> Dict[str, Any]:
        """
        Интерпретация голосовой команды
        
        Args:
            command: Распознанный текст команды
            
        Returns:
            Словарь с интерпретацией команды (action, parameters)
        """
        if not self.is_available:
            return self._parse_fallback_command(command)
        
        try:
            self._validate_request_size(command)
            
            prompt = self._build_voice_command_prompt(command)
            
            messages = [
                {
                    "role": "system",
                    "content": """Ты - интерпретатор голосовых команд для системы видеонаблюдения.
Анализируй команду и возвращай JSON с полями:
- action: тип действия (start_recording, stop_recording, show_camera, search_events, etc.)
- camera_name: название камеры (если применимо)
- parameters: дополнительные параметры (словарь)
- confidence: уверенность в интерпретации (0-1)

Возвращай только JSON без дополнительного текста."""
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ]
            
            response = await self._make_llm_request(
                messages=messages,
                temperature=0.2,
                max_tokens=200
            )
            
            # Парсим JSON из ответа
            try:
                # Извлекаем JSON из текста (может быть обёрнут в markdown)
                json_start = response.find("{")
                json_end = response.rfind("}") + 1
                
                if json_start >= 0 and json_end > json_start:
                    json_str = response[json_start:json_end]
                    result = json.loads(json_str)
                    
                    logger.info(f"Interpreted voice command: {result}")
                    return result
                else:
                    logger.warning("No JSON found in LLM response")
                    return self._parse_fallback_command(command)
                    
            except json.JSONDecodeError as e:
                logger.warning(f"Failed to parse LLM response as JSON: {e}")
                return self._parse_fallback_command(command)
                
        except (LLMUnavailableError, LLMRequestError) as e:
            logger.warning(f"LLM command interpretation failed: {e}, using fallback")
            return self._parse_fallback_command(command)
    
    def _build_voice_command_prompt(self, command: str) -> str:
        """Построение промпта для интерпретации команды"""
        return f"""
Проанализируй следующую голосовую команду и определи действие:

Команда: "{command}"

Доступные действия:
- start_recording: начать запись на камере
- stop_recording: остановить запись
- show_camera: показать камеру
- search_events: поиск событий
- show_events: показать события
- export_recording: экспорт записи
- list_cameras: список камер

Верни JSON с интерпретацией.
"""
    
    def _parse_fallback_command(self, command: str) -> Dict[str, Any]:
        """Базовый парсинг команды без LLM"""
        command_lower = command.lower()
        
        result = {
            "action": "unknown",
            "camera_name": None,
            "parameters": {},
            "confidence": 0.3
        }
        
        # Простое ключевое слово matching
        if "запись" in command_lower or "запис" in command_lower:
            if "стоп" in command_lower or "останов" in command_lower:
                result["action"] = "stop_recording"
                result["confidence"] = 0.7
            else:
                result["action"] = "start_recording"
                result["confidence"] = 0.7
        
        elif "камер" in command_lower:
            if "покаж" in command_lower:
                result["action"] = "show_camera"
                result["confidence"] = 0.7
            else:
                result["action"] = "list_cameras"
                result["confidence"] = 0.7
        
        elif "событи" in command_lower:
            result["action"] = "search_events"
            result["confidence"] = 0.6
        
        return result
    
    def get_stats(self) -> Dict[str, Any]:
        """Получить статистику сервиса"""
        return {
            "enabled": self._enabled,
            "provider": self._provider.value,
            "status": self._status.value,
            "model": self._model,
            "concurrent_requests": self._concurrent_requests,
            "cache_size": len(self._cache),
            "health_checked": self._health_checked
        }


# Глобальный экземпляр сервиса
_llm_bridge: Optional[LLMBridge] = None


def get_llm_bridge() -> LLMBridge:
    """Получить глобальный экземпляр LLMBridge"""
    global _llm_bridge
    if _llm_bridge is None:
        _llm_bridge = LLMBridge()
    return _llm_bridge


async def initialize_llm_bridge() -> None:
    """Инициализировать глобальный LLMBridge"""
    bridge = get_llm_bridge()
    await bridge.initialize()


async def shutdown_llm_bridge() -> None:
    """Остановить глобальный LLMBridge"""
    global _llm_bridge
    if _llm_bridge:
        await _llm_bridge.shutdown()
        _llm_bridge = None
