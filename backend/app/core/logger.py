"""
Централизованная система логирования с ротацией файлов, сжатием и управлением размером.

Поддерживает:
- Ротацию по размеру файла
- Сжатие архивов в .gz
- Управление общим размером папки логов
- Разделение логов по категориям
- Метрики логирования
"""
import os
import gzip
import shutil
import logging
import logging.handlers
from pathlib import Path
from typing import Optional, Dict, List
from datetime import datetime, timedelta
from threading import Lock
import time

from app.config import settings


class GzipRotatingFileHandler(logging.handlers.RotatingFileHandler):
    """
    Обработчик файлов с ротацией по размеру и сжатием в gzip.
    
    При достижении максимального размера файла:
    1. Файл ротируется
    2. Архивируется в .gz
    3. Удаляются старые архивы при превышении общего размера
    """
    
    def __init__(
        self,
        filename: str,
        mode: str = 'a',
        maxBytes: int = 50 * 1024 * 1024,  # 50MB по умолчанию
        backupCount: int = 10,
        encoding: Optional[str] = None,
        delay: bool = False,
        max_total_size: int = 2 * 1024 * 1024 * 1024,  # 2GB по умолчанию
        compress: bool = True,
        delete_oldest_when_exceed: bool = True,
    ):
        """
        Инициализация обработчика.
        
        Args:
            filename: Путь к файлу логов
            mode: Режим открытия файла
            maxBytes: Максимальный размер файла в байтах
            backupCount: Количество сохраняемых архивов
            encoding: Кодировка файла
            delay: Задержка создания файла до первой записи
            max_total_size: Максимальный общий размер папки логов в байтах
            compress: Сжимать архивы в .gz
            delete_oldest_when_exceed: Удалять старые архивы при превышении размера
        """
        self.max_total_size = max_total_size
        self.compress = compress
        self.delete_oldest_when_exceed = delete_oldest_when_exceed
        self._lock = Lock()
        
        super().__init__(
            filename,
            mode=mode,
            maxBytes=maxBytes,
            backupCount=backupCount,
            encoding=encoding,
            delay=delay,
        )
    
    def doRollover(self):
        """Выполнить ротацию файла с сжатием и управлением размером."""
        with self._lock:
            # Получаем базовый путь и расширение
            base_path = Path(self.baseFilename)
            
            # Сжимаем существующие архивы перед ротацией
            if self.compress:
                self._compress_existing_archives(base_path)
            
            # Выполняем стандартную ротацию
            super().doRollover()
            
            # Сжимаем только что созданный архив
            if self.compress:
                self._compress_latest_archive(base_path)
            
            # Проверяем и очищаем старые архивы при необходимости
            if self.delete_oldest_when_exceed:
                self._cleanup_old_archives(base_path)
    
    def _compress_existing_archives(self, base_path: Path):
        """Сжать существующие несжатые архивы."""
        for i in range(self.backupCount - 1, 0, -1):
            archive_path = base_path.with_suffix(f'.{i}')
            if archive_path.exists() and not archive_path.suffix == '.gz':
                self._compress_file(archive_path)
    
    def _compress_latest_archive(self, base_path: Path):
        """Сжать последний архив после ротации."""
        archive_path = base_path.with_suffix('.1')
        if archive_path.exists() and not archive_path.suffix == '.gz':
            self._compress_file(archive_path)
    
    def _compress_file(self, file_path: Path):
        """Сжать файл в gzip."""
        try:
            compressed_path = file_path.with_suffix(file_path.suffix + '.gz')
            
            # Читаем исходный файл и сжимаем
            with open(file_path, 'rb') as f_in:
                with gzip.open(compressed_path, 'wb') as f_out:
                    shutil.copyfileobj(f_in, f_out)
            
            # Удаляем исходный файл
            file_path.unlink()
        except Exception as e:
            # Не прерываем логирование при ошибке сжатия
            print(f"Ошибка сжатия файла {file_path}: {e}")
    
    def _cleanup_old_archives(self, base_path: Path):
        """Удалить старые архивы при превышении общего размера."""
        log_dir = base_path.parent
        
        try:
            # Получаем общий размер всех логов
            total_size = self._get_total_log_size(log_dir)
            
            # Если размер превышен, удаляем старые архивы
            while total_size > self.max_total_size:
                oldest_archive = self._find_oldest_archive(log_dir)
                if oldest_archive:
                    oldest_size = oldest_archive.stat().st_size
                    oldest_archive.unlink()
                    total_size -= oldest_size
                else:
                    break
        except Exception as e:
            print(f"Ошибка очистки архивов: {e}")
    
    def _get_total_log_size(self, log_dir: Path) -> int:
        """Получить общий размер всех файлов логов в директории."""
        total_size = 0
        for file_path in log_dir.glob('*.log*'):
            if file_path.is_file():
                total_size += file_path.stat().st_size
        return total_size
    
    def _find_oldest_archive(self, log_dir: Path) -> Optional[Path]:
        """Найти самый старый архив."""
        archives = []
        for file_path in log_dir.glob('*.log.*'):
            if file_path.is_file():
                archives.append((file_path, file_path.stat().st_mtime))
        
        if not archives:
            return None
        
        # Сортируем по времени модификации и возвращаем самый старый
        archives.sort(key=lambda x: x[1])
        return archives[0][0]


class LoggingMetrics:
    """Метрики системы логирования."""
    
    def __init__(self):
        self._lock = Lock()
        self._error_count = 0
        self._error_timestamps: List[datetime] = []
        self._start_time = datetime.now()
    
    def record_error(self):
        """Зарегистрировать ошибку."""
        with self._lock:
            self._error_count += 1
            self._error_timestamps.append(datetime.now())
            
            # Удаляем записи старше 1 часа
            one_hour_ago = datetime.now() - timedelta(hours=1)
            self._error_timestamps = [
                ts for ts in self._error_timestamps if ts > one_hour_ago
            ]
    
    def get_errors_last_hour(self) -> int:
        """Получить количество ошибок за последний час."""
        with self._lock:
            one_hour_ago = datetime.now() - timedelta(hours=1)
            return sum(1 for ts in self._error_timestamps if ts > one_hour_ago)
    
    def get_total_errors(self) -> int:
        """Получить общее количество ошибок."""
        with self._lock:
            return self._error_count
    
    def get_uptime(self) -> float:
        """Получить время работы в секундах."""
        return (datetime.now() - self._start_time).total_seconds()


# Глобальный экземпляр метрик
_metrics = LoggingMetrics()


class ErrorCountingFilter(logging.Filter):
    """Фильтр для подсчета ошибок."""
    
    def filter(self, record: logging.LogRecord) -> bool:
        """Подсчитать ошибки."""
        if record.levelno >= logging.ERROR:
            _metrics.record_error()
        return True


def setup_logging(
    log_dir: Optional[str] = None,
    max_file_size_mb: Optional[int] = None,
    backup_count: Optional[int] = None,
    compress: Optional[bool] = None,
    max_total_size_mb: Optional[int] = None,
    delete_oldest_when_exceed: Optional[bool] = None,
    level: Optional[str] = None,
) -> Dict[str, logging.Logger]:
    """
    Настроить централизованную систему логирования.
    
    Args:
        log_dir: Директория для логов
        max_file_size_mb: Максимальный размер файла в МБ
        backup_count: Количество архивов
        compress: Сжимать архивы
        max_total_size_mb: Максимальный общий размер в МБ
        delete_oldest_when_exceed: Удалять старые архивы
        level: Уровень логирования
        
    Returns:
        Словарь логгеров по категориям
    """
    # Получаем настройки из config или используем значения по умолчанию
    log_dir = log_dir or getattr(settings, 'LOG_DIR', './logs')
    max_file_size_mb = max_file_size_mb or getattr(settings, 'LOG_MAX_FILE_SIZE_MB', 50)
    backup_count = backup_count or getattr(settings, 'LOG_BACKUP_COUNT', 10)
    compress = compress if compress is not None else getattr(settings, 'LOG_COMPRESS', True)
    max_total_size_mb = max_total_size_mb or getattr(settings, 'LOG_MAX_TOTAL_SIZE_MB', 2048)
    delete_oldest_when_exceed = delete_oldest_when_exceed if delete_oldest_when_exceed is not None else getattr(
        settings, 'LOG_DELETE_OLDEST_WHEN_EXCEED', True
    )
    level = level or getattr(settings, 'LOG_LEVEL', 'INFO')
    
    # Создаем директорию для логов
    log_path = Path(log_dir)
    log_path.mkdir(parents=True, exist_ok=True)
    
    # Формат логов
    log_format = getattr(
        settings,
        'LOG_FORMAT',
        '%(asctime)s - %(name)s - %(levelname)s - [%(filename)s:%(lineno)d] - %(message)s'
    )
    date_format = '%Y-%m-%d %H:%M:%S'
    
    # Создаем форматтер
    formatter = logging.Formatter(log_format, datefmt=date_format)
    
    # Создаем фильтр для подсчета ошибок
    error_filter = ErrorCountingFilter()
    
    # Определяем категории логов
    log_categories = {
        'backend': 'backend.log',
        'ai': 'ai.log',
        'system': 'system.log',
        'security': 'security.log',
        'audit': 'audit.log',
    }
    
    loggers = {}
    
    # Создаем логгеры для каждой категории
    for category, filename in log_categories.items():
        logger = logging.getLogger(category)
        logger.setLevel(getattr(logging, level.upper()))
        logger.handlers.clear()  # Очищаем существующие обработчики
        logger.propagate = False  # Не передаем логи родительским логгерам
        
        # Создаем обработчик с ротацией и сжатием
        file_handler = GzipRotatingFileHandler(
            filename=str(log_path / filename),
            maxBytes=max_file_size_mb * 1024 * 1024,
            backupCount=backup_count,
            encoding='utf-8',
            max_total_size=max_total_size_mb * 1024 * 1024,
            compress=compress,
            delete_oldest_when_exceed=delete_oldest_when_exceed,
        )
        file_handler.setFormatter(formatter)
        file_handler.addFilter(error_filter)
        
        # Добавляем обработчик в консоль для отладки
        if getattr(settings, 'DEBUG', False):
            console_handler = logging.StreamHandler()
            console_handler.setFormatter(formatter)
            console_handler.addFilter(error_filter)
            logger.addHandler(console_handler)
        
        logger.addHandler(file_handler)
        loggers[category] = logger
    
    # Настраиваем корневой логгер
    root_logger = logging.getLogger()
    root_logger.setLevel(getattr(logging, level.upper()))
    
    # Удаляем существующие обработчики
    for handler in root_logger.handlers[:]:
        root_logger.removeHandler(handler)
    
    # Добавляем обработчик для консоли
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)
    console_handler.addFilter(error_filter)
    root_logger.addHandler(console_handler)
    
    return loggers


def get_logger(category: str = 'backend') -> logging.Logger:
    """
    Получить логгер по категории.
    
    Args:
        category: Категория логов (backend, ai, system, security, audit)
        
    Returns:
        Логгер для указанной категории
    """
    return logging.getLogger(category)


def get_logging_metrics() -> Dict:
    """
    Получить метрики системы логирования.
    
    Returns:
        Словарь с метриками
    """
    log_dir = Path(getattr(settings, 'LOG_DIR', './logs'))
    
    # Получаем размер папки логов
    total_size = 0
    file_count = 0
    if log_dir.exists():
        for file_path in log_dir.glob('*.log*'):
            if file_path.is_file():
                total_size += file_path.stat().st_size
                file_count += 1
    
    return {
        'log_dir': str(log_dir),
        'total_size_bytes': total_size,
        'total_size_mb': round(total_size / (1024 * 1024), 2),
        'file_count': file_count,
        'errors_last_hour': _metrics.get_errors_last_hour(),
        'total_errors': _metrics.get_total_errors(),
        'uptime_seconds': _metrics.get_uptime(),
    }


def get_log_files_info() -> List[Dict]:
    """
    Получить информацию о файлах логов.
    
    Returns:
        Список словарей с информацией о файлах
    """
    log_dir = Path(getattr(settings, 'LOG_DIR', './logs'))
    files_info = []
    
    if log_dir.exists():
        for file_path in sorted(log_dir.glob('*.log*')):
            if file_path.is_file():
                stat = file_path.stat()
                files_info.append({
                    'name': file_path.name,
                    'path': str(file_path),
                    'size_bytes': stat.st_size,
                    'size_mb': round(stat.st_size / (1024 * 1024), 2),
                    'modified': datetime.fromtimestamp(stat.st_mtime).isoformat(),
                    'is_compressed': file_path.suffix == '.gz',
                })
    
    return files_info


def cleanup_old_logs(max_age_days: Optional[int] = None) -> int:
    """
    Очистить старые логи.
    
    Args:
        max_age_days: Максимальный возраст логов в днях
        
    Returns:
        Количество удаленных файлов
    """
    max_age_days = max_age_days or getattr(settings, 'LOG_MAX_AGE_DAYS', 30)
    log_dir = Path(getattr(settings, 'LOG_DIR', './logs'))
    
    if not log_dir.exists():
        return 0
    
    deleted_count = 0
    cutoff_time = datetime.now() - timedelta(days=max_age_days)
    
    for file_path in log_dir.glob('*.log*'):
        if file_path.is_file():
            file_time = datetime.fromtimestamp(file_path.stat().st_mtime)
            if file_time < cutoff_time:
                try:
                    file_path.unlink()
                    deleted_count += 1
                except Exception as e:
                    print(f"Ошибка удаления файла {file_path}: {e}")
    
    return deleted_count


# Инициализация логгеров при импорте
_loggers = None


def init_logging():
    """Инициализировать систему логирования."""
    global _loggers
    if _loggers is None:
        _loggers = setup_logging()
    return _loggers


# Автоматическая инициализация при импорте
init_logging()
