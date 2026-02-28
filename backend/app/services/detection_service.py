"""AI detection service for person detection"""
import asyncio
from typing import List, Optional
from datetime import datetime

from app.utils.ai import PersonDetector, DetectedObject, get_detector
from app.config import settings


class DetectionService:
    """AI detection service"""
    
    def __init__(self):
        """Initialize detection service"""
        self.detector: Optional[PersonDetector] = None
        self._detection_enabled = settings.DETECTION_ENABLED
        self._confidence_threshold = settings.DETECTION_CONFIDENCE_THRESHOLD
    
    def load_model(self) -> bool:
        """Load YOLO model
        
        Returns:
            True if loaded successfully
        """
        if self.detector is None:
            self.detector = get_detector(
                model_path=settings.YOLO_MODEL_PATH,
                confidence_threshold=self._confidence_threshold,
            )
        
        return self.detector.is_loaded
    
    async def detect_persons(self, image) -> List[DetectedObject]:
        """Detect persons in image
        
        Args:
            image: Input image (numpy array or PIL Image)
            
        Returns:
            List of detected persons
        """
        if not self._detection_enabled:
            return []
        
        if not self.load_model():
            return []
        
        return await self.detector.detect_persons_async(image)
    
    async def detect_objects(
        self,
        image,
        classes: Optional[List[int]] = None,
    ) -> List[DetectedObject]:
        """Detect objects in image
        
        Args:
            image: Input image
            classes: List of class IDs to detect
            
        Returns:
            List of detected objects
        """
        if not self._detection_enabled:
            return []
        
        if not self.load_model():
            return []
        
        return await self.detector.detect_async(image, classes)
    
    async def process_frame(
        self,
        frame,
        camera_id: int,
        timestamp: Optional[str] = None,
    ) -> dict:
        """Process a video frame for detection
        
        Args:
            frame: Video frame
            camera_id: Camera ID
            timestamp: Frame timestamp
            
        Returns:
            Detection results dictionary
        """
        if timestamp is None:
            timestamp = datetime.utcnow().isoformat()
        
        persons = await self.detect_persons(frame)
        
        return {
            "camera_id": camera_id,
            "timestamp": timestamp,
            "person_count": len(persons),
            "persons": [
                {
                    "type": p.type,
                    "confidence": p.confidence,
                    "bbox": p.bbox,
                    "timestamp": p.timestamp,
                }
                for p in persons
            ],
        }
    
    def set_confidence_threshold(self, threshold: float) -> None:
        """Set detection confidence threshold
        
        Args:
            threshold: Confidence threshold (0.0 - 1.0)
        """
        self._confidence_threshold = max(0.0, min(1.0, threshold))
        
        if self.detector:
            self.detector.confidence_threshold = self._confidence_threshold
    
    def get_confidence_threshold(self) -> float:
        """Get current confidence threshold
        
        Returns:
            Confidence threshold
        """
        return self._confidence_threshold
    
    def enable_detection(self) -> None:
        """Enable detection"""
        self._detection_enabled = True
    
    def disable_detection(self) -> None:
        """Disable detection"""
        self._detection_enabled = False
    
    def is_enabled(self) -> bool:
        """Check if detection is enabled
        
        Returns:
            True if enabled
        """
        return self._detection_enabled


# Global detection service instance
detection_service = DetectionService()


# Convenience functions
async def detect_persons(image) -> List[DetectedObject]:
    """Detect persons in image"""
    return await detection_service.detect_persons(image)


async def process_frame(
    frame,
    camera_id: int,
    timestamp: Optional[str] = None,
) -> dict:
    """Process video frame for detection"""
    return await detection_service.process_frame(frame, camera_id, timestamp)
