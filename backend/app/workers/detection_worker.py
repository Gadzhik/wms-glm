"""Detection worker for AI person detection"""
import asyncio
from typing import Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.camera import Camera
from app.models.event import Event
from app.services.detection_service import detection_service
from app.services.notification_service import notification_service
from app.config import settings


class DetectionWorker:
    """Background worker for AI detection"""
    
    def __init__(self, db: AsyncSession):
        """Initialize detection worker
        
        Args:
            db: Database session
        """
        self.db = db
        self._running = False
        self._task: Optional[asyncio.Task] = None
    
    async def start(self) -> None:
        """Start detection worker"""
        if self._running:
            return
        
        self._running = True
        self._task = asyncio.create_task(self._process_detections())
    
    async def stop(self) -> None:
        """Stop detection worker"""
        self._running = False
        if self._task:
            self._task.cancel()
            try:
                await self._task
            except asyncio.CancelledError:
                pass
    
    async def _process_detections(self) -> None:
        """Process detections for all cameras"""
        while self._running:
            try:
                await self._detect_persons()
                await asyncio.sleep(settings.DETECTION_INTERVAL_SECONDS)
            except asyncio.CancelledError:
                break
            except Exception as e:
                print(f"Detection worker error: {e}")
                await asyncio.sleep(60)
    
    async def _detect_persons(self) -> None:
        """Detect persons in camera streams"""
        result = await self.db.execute(
            select(Camera).where(
                (Camera.status == "online") &
                (Camera.detection_enabled == 1)
            )
        )
        cameras = list(result.scalars().all())
        
        for camera in cameras:
            try:
                # Get latest frame from stream (simplified)
                # In real implementation, would get frame from FFmpeg stream
                # For now, just simulate detection
                if self._should_detect(camera):
                    await self._simulate_detection(camera)
            
            except Exception as e:
                print(f"Error detecting for camera {camera.id}: {e}")
    
    def _should_detect(self, camera: Camera) -> bool:
        """Check if detection should run for camera
        
        Args:
            camera: Camera object
            
        Returns:
            True if should detect
        """
        # Only detect if camera is online and detection is enabled
        if not camera.is_online():
            return False
        
        if not camera.is_detection_enabled():
            return False
        
        return True
    
    async def _simulate_detection(self, camera: Camera) -> None:
        """Simulate person detection (placeholder for real implementation)
        
        Args:
            camera: Camera object
        """
        # In real implementation, would:
        # 1. Get frame from RTSP stream
        # 2. Run detection_service.detect_persons(frame)
        # 3. Create event if persons detected
        # 4. Send notification
        
        # For now, just create a random detection event
        import random
        
        detected = random.random() < 0.1  # 10% chance
        
        if detected:
            event = Event(
                event_type=Event.EVENT_TYPE_PERSON_DETECTED,
                camera_id=camera.id,
                details={
                    "confidence": random.uniform(0.7, 0.95),
                    "bbox": {"x": 100, "y": 100, "width": 50, "height": 100},
                },
                timestamp=datetime.utcnow().isoformat(),
                status="new",
            )
            
            self.db.add(event)
            await self.db.commit()
            
            # Send notification
            await notification_service.send_person_detected_notification(
                camera.name,
                random.uniform(0.7, 0.95),
                datetime.utcnow().isoformat(),
            )
    
    async def process_frame(
        self,
        camera_id: int,
        frame,
        db: AsyncSession,
    ) -> dict:
        """Process a single frame for detection
        
        Args:
            camera_id: Camera ID
            frame: Video frame
            db: Database session
            
        Returns:
            Detection results
        """
        detections = await detection_service.process_frame(frame, camera_id)
        
        # Create events for detected persons
        if detections["person_count"] > 0:
            for person in detections["persons"]:
                event = Event(
                    event_type=Event.EVENT_TYPE_PERSON_DETECTED,
                    camera_id=camera_id,
                    details={
                        "confidence": person["confidence"],
                        "bbox": person["bbox"],
                    },
                    timestamp=person["timestamp"],
                    status="new",
                )
                
                self.db.add(event)
                await self.db.commit()
        
        return detections
