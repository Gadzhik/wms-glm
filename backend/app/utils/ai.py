"""AI utilities for person detection using YOLO"""
import asyncio
from typing import List, Optional, Dict, Any
from dataclasses import dataclass
from datetime import datetime


@dataclass
class DetectedObject:
    """Detected object information"""
    type: str
    confidence: float
    bbox: Dict[str, int]  # {x, y, width, height}
    timestamp: str
    tracking_id: Optional[int] = None


class PersonDetector:
    """Person detector using YOLO"""
    
    def __init__(
        self,
        model_path: str = "yolov8n.pt",
        confidence_threshold: float = 0.5,
        device: Optional[str] = None,
    ):
        """Initialize person detector
        
        Args:
            model_path: Path to YOLO model file
            confidence_threshold: Minimum confidence for detection
            device: Device to use (cpu, cuda, mps, etc.)
        """
        self.model_path = model_path
        self.confidence_threshold = confidence_threshold
        self.device = device
        self._model = None
        self._loaded = False
    
    @property
    def is_loaded(self) -> bool:
        """Check if model is loaded"""
        return self._loaded
    
    def load_model(self) -> bool:
        """Load YOLO model
        
        Returns:
            True if loaded successfully
        """
        try:
            from ultralytics import YOLO
            
            self._model = YOLO(self.model_path)
            self._loaded = True
            return True
            
        except ImportError:
            print("Ultralytics not installed. Install with: pip install ultralytics")
            return False
        except Exception as e:
            print(f"Failed to load YOLO model: {e}")
            return False
    
    def detect(
        self,
        image,
        classes: Optional[List[int]] = None,
    ) -> List[DetectedObject]:
        """Detect objects in image
        
        Args:
            image: Input image (numpy array or PIL Image)
            classes: List of class IDs to detect (None for all)
            
        Returns:
            List of detected objects
        """
        if not self._loaded:
            if not self.load_model():
                return []
        
        try:
            results = self._model(
                image,
                conf=self.confidence_threshold,
                classes=classes,
                verbose=False,
            )
            
            detections = []
            
            for result in results:
                boxes = result.boxes
                if boxes is not None:
                    for box in boxes:
                        # Get box coordinates
                        x1, y1, x2, y2 = box.xyxy[0].tolist()
                        confidence = float(box.conf[0])
                        class_id = int(box.cls[0])
                        
                        # Get class name
                        class_name = self._model.names[class_id]
                        
                        detections.append(DetectedObject(
                            type=class_name,
                            confidence=confidence,
                            bbox={
                                "x": int(x1),
                                "y": int(y1),
                                "width": int(x2 - x1),
                                "height": int(y2 - y1),
                            },
                            timestamp=datetime.utcnow().isoformat(),
                        ))
            
            return detections
            
        except Exception as e:
            print(f"Detection error: {e}")
            return []
    
    def detect_persons(self, image) -> List[DetectedObject]:
        """Detect only persons in image
        
        Args:
            image: Input image
            
        Returns:
            List of detected persons
        """
        # Person class ID in COCO dataset is 0
        return self.detect(image, classes=[0])
    
    async def detect_async(
        self,
        image,
        classes: Optional[List[int]] = None,
    ) -> List[DetectedObject]:
        """Detect objects in image (async wrapper)
        
        Args:
            image: Input image
            classes: List of class IDs to detect
            
        Returns:
            List of detected objects
        """
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(None, self.detect, image, classes)
    
    async def detect_persons_async(self, image) -> List[DetectedObject]:
        """Detect only persons in image (async wrapper)
        
        Args:
            image: Input image
            
        Returns:
            List of detected persons
        """
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(None, self.detect_persons, image)


# Global detector instance
_detector: Optional[PersonDetector] = None


def get_detector(
    model_path: str = "yolov8n.pt",
    confidence_threshold: float = 0.5,
    device: Optional[str] = None,
) -> PersonDetector:
    """Get or create global detector instance
    
    Args:
        model_path: Path to YOLO model file
        confidence_threshold: Minimum confidence for detection
        device: Device to use
        
    Returns:
        PersonDetector instance
    """
    global _detector
    
    if _detector is None:
        _detector = PersonDetector(model_path, confidence_threshold, device)
        _detector.load_model()
    
    return _detector


def load_yolo_model(
    model_path: str = "yolov8n.pt",
    confidence_threshold: float = 0.5,
    device: Optional[str] = None,
) -> PersonDetector:
    """Load YOLO model for detection
    
    Args:
        model_path: Path to YOLO model file
        confidence_threshold: Minimum confidence for detection
        device: Device to use
        
    Returns:
        PersonDetector instance
    """
    return get_detector(model_path, confidence_threshold, device)


async def detect_persons(
    image,
    model_path: str = "yolov8n.pt",
    confidence_threshold: float = 0.5,
) -> List[DetectedObject]:
    """Detect persons in image
    
    Args:
        image: Input image
        model_path: Path to YOLO model file
        confidence_threshold: Minimum confidence for detection
        
    Returns:
        List of detected persons
    """
    detector = get_detector(model_path, confidence_threshold)
    return await detector.detect_persons_async(image)


async def detect_objects(
    image,
    classes: Optional[List[int]] = None,
    model_path: str = "yolov8n.pt",
    confidence_threshold: float = 0.5,
) -> List[DetectedObject]:
    """Detect objects in image
    
    Args:
        image: Input image
        classes: List of class IDs to detect
        model_path: Path to YOLO model file
        confidence_threshold: Minimum confidence for detection
        
    Returns:
        List of detected objects
    """
    detector = get_detector(model_path, confidence_threshold)
    return await detector.detect_async(image, classes)


def get_class_names() -> Dict[int, str]:
    """Get COCO class names
    
    Returns:
        Dictionary mapping class IDs to names
    """
    return {
        0: "person",
        1: "bicycle",
        2: "car",
        3: "motorcycle",
        4: "airplane",
        5: "bus",
        6: "train",
        7: "truck",
        8: "boat",
        9: "traffic light",
        10: "fire hydrant",
        11: "stop sign",
        12: "parking meter",
        13: "bench",
        14: "bird",
        15: "cat",
        16: "dog",
        17: "horse",
        18: "sheep",
        19: "cow",
        20: "elephant",
        21: "bear",
        22: "zebra",
        23: "giraffe",
        24: "backpack",
        25: "umbrella",
        26: "handbag",
        27: "tie",
        28: "suitcase",
        29: "frisbee",
        30: "skis",
        31: "snowboard",
        32: "sports ball",
        33: "kite",
        34: "baseball bat",
        35: "baseball glove",
        36: "skateboard",
        37: "surfboard",
        38: "tennis racket",
        39: "bottle",
        40: "wine glass",
        41: "cup",
        42: "fork",
        43: "knife",
        44: "spoon",
        45: "bowl",
        46: "banana",
        47: "apple",
        48: "sandwich",
        49: "orange",
        50: "broccoli",
        51: "carrot",
        52: "hot dog",
        53: "pizza",
        54: "donut",
        55: "cake",
        56: "chair",
        57: "couch",
        58: "potted plant",
        59: "bed",
        60: "dining table",
        61: "toilet",
        62: "tv",
        63: "laptop",
        64: "mouse",
        65: "remote",
        66: "keyboard",
        67: "cell phone",
        68: "microwave",
        69: "oven",
        70: "toaster",
        71: "sink",
        72: "refrigerator",
        73: "book",
        74: "clock",
        75: "vase",
        76: "scissors",
        77: "teddy bear",
        78: "hair drier",
        79: "toothbrush",
    }
