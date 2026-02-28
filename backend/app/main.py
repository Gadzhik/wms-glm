"""FastAPI application main entry point"""
import os
import logging
from contextlib import asynccontextmanager
from typing import Optional

from fastapi import FastAPI, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles

from app.config import settings
from app.database import init_db, close_db, check_db_connection, get_db_context
from app.api import (
    auth_router,
    users_router,
    cameras_router,
    recordings_router,
    events_router,
    streams_router,
    settings_router,
)
from app.workers.camera_worker import CameraWorker
from app.workers.recording_worker import RecordingWorker
from app.workers.detection_worker import DetectionWorker
from app.workers.cleanup_worker import CleanupWorker
from app.core.logger import init_logging, get_logger
from app.services import initialize_llm_bridge, shutdown_llm_bridge, get_llm_bridge

# Initialize centralized logging system
init_logging()
logger = get_logger('backend')

# Create FastAPI app
app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    debug=settings.DEBUG,
    docs_url=f"{settings.API_V1_PREFIX}/docs",
    redoc_url=f"{settings.API_V1_PREFIX}/redoc",
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=settings.CORS_ALLOW_CREDENTIALS,
    allow_methods=settings.CORS_ALLOW_METHODS,
    allow_headers=settings.CORS_ALLOW_HEADERS,
)

# Add debug middleware for logging requests
@app.middleware("http")
async def log_requests(request: Request, call_next):
    """Log all incoming requests with method, path and response status"""
    logger.info(f"REQUEST: {request.method} {request.url.path}")
    response = await call_next(request)
    logger.info(f"RESPONSE: {request.method} {request.url.path} - Status: {response.status_code}")
    return response

# Include routers
app.include_router(auth_router, prefix=settings.API_V1_PREFIX)
app.include_router(users_router, prefix=settings.API_V1_PREFIX)
app.include_router(cameras_router, prefix=settings.API_V1_PREFIX)
app.include_router(recordings_router, prefix=settings.API_V1_PREFIX)
app.include_router(events_router, prefix=settings.API_V1_PREFIX)
app.include_router(streams_router, prefix=settings.API_V1_PREFIX)
app.include_router(settings_router, prefix=settings.API_V1_PREFIX)

# Serve static files for HLS streams
if os.path.exists(settings.LIVE_STREAM_PATH):
    app.mount("/live", StaticFiles(directory=settings.LIVE_STREAM_PATH), name="live")


# Startup and shutdown events
workers = {
    "camera": None,
    "recording": None,
    "detection": None,
    "cleanup": None,
}


@app.on_event("startup")
async def startup_event():
    """Initialize services and start background workers"""
    logger.info("Starting up...")
    
    # Initialize database
    await init_db()
    
    # Check database connection
    db_ok = await check_db_connection()
    if db_ok:
        logger.info("Database connection: OK")
    else:
        logger.error("Database connection: FAILED")
    
    # Check Redis connection
    redis_ok = await check_redis_connection()
    if redis_ok:
        logger.info("Redis connection: OK")
    else:
        logger.error("Redis connection: FAILED")
    
    # Create storage directories
    os.makedirs(settings.STORAGE_PATH, exist_ok=True)
    os.makedirs(settings.RECORDINGS_PATH, exist_ok=True)
    os.makedirs(settings.ARCHIVE_PATH, exist_ok=True)
    os.makedirs(settings.EXPORTS_PATH, exist_ok=True)
    os.makedirs(settings.LIVE_STREAM_PATH, exist_ok=True)
    
    # Start background workers
    async with get_db_context() as db:
        workers["camera"] = CameraWorker(db)
        workers["recording"] = RecordingWorker(db)
        workers["detection"] = DetectionWorker(db)
        workers["cleanup"] = CleanupWorker(db)
        
        await workers["camera"].start()
        await workers["recording"].start()
        await workers["detection"].start()
        await workers["cleanup"].start()
        
        # Initialize LLM Bridge
        try:
            await initialize_llm_bridge()
            llm = get_llm_bridge()
            logger.info(f"LLM Bridge initialized: status={llm.status}, provider={llm._provider}")
        except Exception as e:
            logger.warning(f"LLM Bridge initialization failed: {e}, system will work without LLM")
        
        logger.info("Background workers started")


@app.on_event("shutdown")
async def shutdown_event():
    """Cleanup and stop background workers"""
    logger.info("Shutting down...")
    
    # Stop background workers
    if workers["camera"]:
        await workers["camera"].stop()
    if workers["recording"]:
        await workers["recording"].stop()
    if workers["detection"]:
        await workers["detection"].stop()
    if workers["cleanup"]:
        await workers["cleanup"].stop()
    
    # Close database
    await close_db()
    
    # Close notification service
    from app.services.notification_service import notification_service
    await notification_service.close()
    
    # Shutdown LLM Bridge
    try:
        await shutdown_llm_bridge()
        logger.info("LLM Bridge shutdown complete")
    except Exception as e:
        logger.warning(f"LLM Bridge shutdown failed: {e}")
    
    logger.info("Background workers stopped")


# Health check endpoint
@app.get("/health", tags=["Health"])
async def health_check():
    """Health check endpoint"""
    db_ok = await check_db_connection()
    redis_ok = await check_redis_connection()
    
    # Check LLM status
    llm = get_llm_bridge()
    llm_status = llm.status.value if llm else "not_initialized"
    
    status = "healthy" if (db_ok and redis_ok) else "unhealthy"
    
    return {
        "status": status,
        "version": settings.APP_VERSION,
        "database": "connected" if db_ok else "disconnected",
        "redis": "connected" if redis_ok else "disconnected",
        "llm": {
            "status": llm_status,
            "enabled": llm._enabled if llm else False,
            "provider": llm._provider.value if llm else None,
        }
    }


# Root endpoint
@app.get("/", tags=["Root"])
async def root():
    """Root endpoint"""
    return {
        "name": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "status": "running",
        "docs": f"{settings.API_V1_PREFIX}/docs",
    }


async def check_redis_connection() -> bool:
    """Check Redis connection
    
    Returns:
        True if Redis is available
    """
    try:
        import aioredis
        redis = aioredis.from_url(settings.REDIS_URL)
        await redis.ping()
        await redis.close()
        return True
    except Exception:
        return False


if __name__ == "__main__":
    import uvicorn
    
    logger.info(f"Starting {settings.APP_NAME} v{settings.APP_VERSION}")
    logger.info(f"Debug mode: {settings.DEBUG}")
    
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        log_level=settings.LOG_LEVEL.lower(),
    )
