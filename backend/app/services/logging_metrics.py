"""
Сервис метрик логирования.

Предоставляет API для получения метрик системы логирования.
"""
from typing import Dict, List, Optional
from datetime import datetime, timedelta
from pathlib import Path

from app.config import settings
from app.core.logger import get_logging_metrics, get_log_files_info, cleanup_old_logs


class LoggingMetricsService:
    """Сервис для работы с метриками логирования."""
    
    def __init__(self):
        self.log_dir = Path(getattr(settings, 'LOG_DIR', './logs'))
        self.max_file_size_mb = getattr(settings, 'LOG_MAX_FILE_SIZE_MB', 50)
        self.backup_count = getattr(settings, 'LOG_BACKUP_COUNT', 10)
        self.compress = getattr(settings, 'LOG_COMPRESS', True)
        self.max_total_size_mb = getattr(settings, 'LOG_MAX_TOTAL_SIZE_MB', 2048)
        self.delete_oldest_when_exceed = getattr(
            settings, 'LOG_DELETE_OLDEST_WHEN_EXCEED', True
        )
    
    def get_metrics(self) -> Dict:
        """
        Получить метрики системы логирования.
        
        Returns:
            Словарь с метриками
        """
        metrics = get_logging_metrics()
        
        # Добавляем настройки
        metrics['settings'] = {
            'max_file_size_mb': self.max_file_size_mb,
            'backup_count': self.backup_count,
            'compress': self.compress,
            'max_total_size_mb': self.max_total_size_mb,
            'delete_oldest_when_exceed': self.delete_oldest_when_exceed,
        }
        
        # Добавляем статус использования диска
        metrics['disk_usage'] = {
            'total_limit_mb': self.max_total_size_mb,
            'current_usage_mb': metrics['total_size_mb'],
            'usage_percentage': round(
                (metrics['total_size_mb'] / self.max_total_size_mb) * 100, 2
            ) if self.max_total_size_mb > 0 else 0,
            'is_exceeded': metrics['total_size_mb'] > self.max_total_size_mb,
        }
        
        return metrics
    
    def get_files_info(self, category: Optional[str] = None) -> List[Dict]:
        """
        Получить информацию о файлах логов.
        
        Args:
            category: Фильтр по категории (backend, ai, system, security, audit)
            
        Returns:
            Список словарей с информацией о файлах
        """
        files_info = get_log_files_info()
        
        # Фильтруем по категории, если указана
        if category:
            files_info = [
                f for f in files_info 
                if f['name'].startswith(f'{category}.log')
            ]
        
        return files_info
    
    def get_category_metrics(self) -> Dict[str, Dict]:
        """
        Получить метрики по каждой категории логов.
        
        Returns:
            Словарь с метриками по категориям
        """
        categories = ['backend', 'ai', 'system', 'security', 'audit']
        category_metrics = {}
        
        for category in categories:
            files_info = self.get_files_info(category)
            
            total_size = sum(f['size_bytes'] for f in files_info)
            file_count = len(files_info)
            
            # Находим последний файл
            latest_file = None
            if files_info:
                latest_file = max(files_info, key=lambda x: x['modified'])
            
            category_metrics[category] = {
                'total_size_bytes': total_size,
                'total_size_mb': round(total_size / (1024 * 1024), 2),
                'file_count': file_count,
                'latest_file': latest_file,
                'has_compressed_files': any(f['is_compressed'] for f in files_info),
            }
        
        return category_metrics
    
    def cleanup_logs(self, max_age_days: Optional[int] = None) -> Dict:
        """
        Очистить старые логи.
        
        Args:
            max_age_days: Максимальный возраст логов в днях
            
        Returns:
            Словарь с результатом очистки
        """
        deleted_count = cleanup_old_logs(max_age_days)
        
        return {
            'deleted_count': deleted_count,
            'max_age_days': max_age_days or getattr(settings, 'LOG_MAX_AGE_DAYS', 30),
            'timestamp': datetime.now().isoformat(),
        }
    
    def get_health_status(self) -> Dict:
        """
        Получить статус здоровья системы логирования.
        
        Returns:
            Словарь со статусом
        """
        metrics = self.get_metrics()
        disk_usage = metrics['disk_usage']
        
        # Определяем статус
        if disk_usage['is_exceeded']:
            status = 'critical'
            message = 'Превышен лимит общего размера логов'
        elif disk_usage['usage_percentage'] > 80:
            status = 'warning'
            message = 'Близко к превышению лимита размера логов'
        else:
            status = 'healthy'
            message = 'Система логирования работает нормально'
        
        return {
            'status': status,
            'message': message,
            'timestamp': datetime.now().isoformat(),
            'metrics': metrics,
        }
    
    def get_error_statistics(self, hours: int = 24) -> Dict:
        """
        Получить статистику ошибок.
        
        Args:
            hours: Период в часах для анализа
            
        Returns:
            Словарь со статистикой ошибок
        """
        metrics = self.get_metrics()
        
        # Вычисляем примерное количество ошибок за указанный период
        errors_per_hour = metrics['errors_last_hour']
        estimated_errors = errors_per_hour * hours
        
        return {
            'errors_last_hour': metrics['errors_last_hour'],
            'total_errors': metrics['total_errors'],
            'estimated_errors_last_24h': estimated_errors,
            'errors_per_hour_avg': errors_per_hour,
            'period_hours': hours,
        }


# Глобальный экземпляр сервиса
logging_metrics_service = LoggingMetricsService()
