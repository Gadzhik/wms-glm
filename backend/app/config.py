"""Application configuration using Pydantic Settings"""
from functools import lru_cache
from typing import Optional, List
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field, validator


class Settings(BaseSettings):
    """Application settings loaded from environment variables"""
    
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore"
    )
    
    # Application
    APP_NAME: str = Field(default="VMS Backend", description="Application name")
    APP_VERSION: str = Field(default="1.0.0", description="Application version")
    DEBUG: bool = Field(default=False, description="Debug mode")
    API_V1_PREFIX: str = Field(default="/api/v1", description="API v1 prefix")
    
    # Security
    SECRET_KEY: str = Field(
        default="your-secret-key-change-in-production",
        description="Secret key for JWT tokens"
    )
    ALGORITHM: str = Field(default="HS256", description="JWT algorithm")
    ACCESS_TOKEN_EXPIRE_MINUTES: int = Field(
        default=30,
        description="Access token expiration time in minutes"
    )
    REFRESH_TOKEN_EXPIRE_DAYS: int = Field(
        default=7,
        description="Refresh token expiration time in days"
    )
    
    # Database (SQLite for embedded deployment)
    DATABASE_URL: str = Field(
        default="sqlite+aiosqlite:///./data/vms.db",
        description="Database connection URL"
    )
    
    # Redis
    REDIS_URL: str = Field(
        default="redis://localhost:6379/0",
        description="Redis connection URL"
    )
    REDIS_MAX_CONNECTIONS: int = Field(
        default=10,
        description="Maximum Redis connections"
    )
    
    # Storage
    STORAGE_PATH: str = Field(
        default="./data",
        description="Base storage path"
    )
    RECORDINGS_PATH: str = Field(
        default="./data/recordings",
        description="Recordings storage path"
    )
    ARCHIVE_PATH: str = Field(
        default="./data/archive",
        description="Archive storage path"
    )
    EXPORTS_PATH: str = Field(
        default="./data/exports",
        description="Exports storage path"
    )
    LIVE_STREAM_PATH: str = Field(
        default="./data/live",
        description="Live stream segments path"
    )
    RETENTION_DAYS: int = Field(
        default=30,
        description="Retention period in days"
    )
    MAX_DISK_USAGE_GB: int = Field(
        default=1000,
        description="Maximum disk usage in GB"
    )
    
    # Recording
    RECORDING_SEGMENT_DURATION_SECONDS: int = Field(
        default=300,
        description="Recording segment duration in seconds (5 minutes)"
    )
    MOTION_PRE_BUFFER_SECONDS: int = Field(
        default=5,
        description="Motion pre-buffer duration in seconds"
    )
    MOTION_POST_BUFFER_SECONDS: int = Field(
        default=5,
        description="Motion post-buffer duration in seconds"
    )
    
    # AI Detection
    YOLO_MODEL_PATH: str = Field(
        default="yolov8n.pt",
        description="YOLO model path"
    )
    DETECTION_CONFIDENCE_THRESHOLD: float = Field(
        default=0.5,
        ge=0.0,
        le=1.0,
        description="Detection confidence threshold"
    )
    DETECTION_ENABLED: bool = Field(
        default=True,
        description="Enable AI detection"
    )
    DETECTION_INTERVAL_SECONDS: int = Field(
        default=1,
        description="Detection interval in seconds"
    )
    
    # Streaming
    HLS_SEGMENT_DURATION: int = Field(
        default=2,
        description="HLS segment duration in seconds"
    )
    LIVE_STREAM_BITRATE_KBPS: int = Field(
        default=1000,
        description="Live stream bitrate in kbps"
    )
    LIVE_STREAM_FPS: int = Field(
        default=15,
        description="Live stream FPS"
    )
    LIVE_STREAM_RESOLUTION: str = Field(
        default="1280x720",
        description="Live stream resolution"
    )
    
    # FFmpeg
    FFMPEG_PATH: str = Field(
        default="ffmpeg",
        description="Path to FFmpeg executable"
    )
    FFPROBE_PATH: str = Field(
        default="ffprobe",
        description="Path to FFprobe executable"
    )
    HARDWARE_ACCELERATION: Optional[str] = Field(
        default=None,
        description="Hardware acceleration (qsv, cuda, vaapi, none)"
    )
    
    # Telegram
    TELEGRAM_BOT_TOKEN: Optional[str] = Field(
        default=None,
        description="Telegram bot token"
    )
    TELEGRAM_CHAT_ID: Optional[str] = Field(
        default=None,
        description="Telegram chat ID for notifications"
    )
    TELEGRAM_ENABLED: bool = Field(
        default=False,
        description="Enable Telegram notifications"
    )
    
    # CORS
    CORS_ORIGINS: List[str] = Field(
        default=["http://localhost:3000", "http://localhost:5173"],
        description="CORS allowed origins"
    )
    CORS_ALLOW_CREDENTIALS: bool = Field(
        default=True,
        description="Allow credentials in CORS"
    )
    CORS_ALLOW_METHODS: List[str] = Field(
        default=["*"],
        description="CORS allowed methods"
    )
    CORS_ALLOW_HEADERS: List[str] = Field(
        default=["*"],
        description="CORS allowed headers"
    )
    
    # Logging
    LOG_DIR: str = Field(
        default="./logs",
        description="Directory for log files"
    )
    LOG_LEVEL: str = Field(
        default="INFO",
        description="Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)"
    )
    LOG_FORMAT: str = Field(
        default="%(asctime)s - %(name)s - %(levelname)s - [%(filename)s:%(lineno)d] - %(message)s",
        description="Log format"
    )
    LOG_MAX_FILE_SIZE_MB: int = Field(
        default=50,
        description="Maximum size of a single log file in MB before rotation"
    )
    LOG_BACKUP_COUNT: int = Field(
        default=10,
        description="Number of backup files to keep"
    )
    LOG_COMPRESS: bool = Field(
        default=True,
        description="Compress rotated log files with gzip"
    )
    LOG_MAX_TOTAL_SIZE_MB: int = Field(
        default=2048,
        description="Maximum total size of all log files in MB"
    )
    LOG_DELETE_OLDEST_WHEN_EXCEED: bool = Field(
        default=True,
        description="Delete oldest archives when total size exceeds limit"
    )
    LOG_MAX_AGE_DAYS: int = Field(
        default=30,
        description="Maximum age of log files in days before cleanup"
    )
    
    # Rate Limiting
    RATE_LIMIT_ENABLED: bool = Field(
        default=True,
        description="Enable rate limiting"
    )
    RATE_LIMIT_REQUESTS_PER_MINUTE: int = Field(
        default=60,
        description="Rate limit requests per minute"
    )
    
    # WebSocket
    WS_MAX_CONNECTIONS: int = Field(
        default=100,
        description="Maximum WebSocket connections"
    )
    WS_HEARTBEAT_INTERVAL: int = Field(
        default=30,
        description="WebSocket heartbeat interval in seconds"
    )
    WS_TIMEOUT: int = Field(
        default=60,
        description="WebSocket timeout in seconds"
    )
    
    # Workers
    CAMERA_MONITOR_INTERVAL: int = Field(
        default=30,
        description="Camera monitor interval in seconds"
    )
    CLEANUP_INTERVAL_HOURS: int = Field(
        default=6,
        description="Cleanup interval in hours"
    )
    
    # LLM Settings (LM Studio / Ollama)
    LLM_ENABLED: bool = Field(
        default=False,
        description="Enable LLM integration"
    )
    LLM_PROVIDER: str = Field(
        default="lmstudio",
        description="LLM provider: lmstudio, ollama"
    )
    LLM_BASE_URL: str = Field(
        default="http://localhost:1234/v1",
        description="LLM API base URL (OpenAI-compatible)"
    )
    LLM_MODEL: str = Field(
        default="local-model",
        description="LLM model name"
    )
    LLM_TIMEOUT: int = Field(
        default=30,
        description="LLM request timeout in seconds"
    )
    LLM_MAX_RETRIES: int = Field(
        default=3,
        description="Maximum LLM request retries"
    )
    LLM_MIN_DELAY_SECONDS: int = Field(
        default=5,
        description="Minimum delay between LLM requests (CPU optimization)"
    )
    LLM_MAX_CONCURRENT_CALLS: int = Field(
        default=1,
        description="Maximum concurrent LLM calls (CPU optimization)"
    )
    LLM_EMBEDDING_MODEL: str = Field(
        default="nomic-embed-text",
        description="Embedding model name for semantic search"
    )
    LLM_EMBEDDING_DIMENSION: int = Field(
        default=768,
        description="Embedding vector dimension"
    )
    LLM_HEALTH_CHECK_ENABLED: bool = Field(
        default=True,
        description="Enable LLM health check on startup"
    )
    LLM_HEALTH_CHECK_TIMEOUT: int = Field(
        default=5,
        description="LLM health check timeout in seconds"
    )
    LLM_CACHE_ENABLED: bool = Field(
        default=True,
        description="Enable LLM response caching"
    )
    LLM_CACHE_TTL_SECONDS: int = Field(
        default=3600,
        description="LLM cache TTL in seconds"
    )
    LLM_MAX_REQUEST_SIZE: int = Field(
        default=10000,
        description="Maximum LLM request size in characters"
    )
    
    @validator("CORS_ORIGINS")
    def parse_cors_origins(cls, v):
        """Parse CORS origins from string or list"""
        if isinstance(v, str):
            return [origin.strip() for origin in v.split(",")]
        return v
    
    @validator("DATABASE_URL")
    def validate_database_url(cls, v):
        """Ensure database URL has correct format"""
        if not v.startswith("sqlite+aiosqlite:///"):
            raise ValueError("DATABASE_URL must start with 'sqlite+aiosqlite:///'")
        return v
    
    @property
    def database_path(self) -> str:
        """Get database file path"""
        return self.DATABASE_URL.replace("sqlite+aiosqlite:///", "")
    
    @property
    def jwt_secret_key(self) -> str:
        """Get JWT secret key"""
        return self.SECRET_KEY


@lru_cache()
def get_settings() -> Settings:
    """Get cached settings instance"""
    return Settings()


# Global settings instance
settings = get_settings()
