# core/tracker.py - Tracks people across video frames using YOLOv8 + ByteTrack

from collections import defaultdict
from ultralytics import YOLO
from utils import setup_logger, get_center_of_box

logger = setup_logger("Tracker")

# YOLOv8 class index for "person"
PERSON_CLASS = 0

# How many recent positions to remember per person
MAX_TRAIL_LENGTH = 100


class PersonTracker:
    """
    Loads a YOLOv8 model and tracks people in video frames.
    Each person gets a unique ID that stays the same across frames.
    """

    def __init__(self, model_path="yolov8n.pt", confidence=0.40, iou=0.45, device=""):
        logger.info(f"Loading model: {model_path}")
        self.model      = YOLO(model_path)
        self.confidence = confidence
        self.iou        = iou
        self.device     = device

        # Stores the recent center positions for each tracked person
        # Key: person ID, Value: list of (cx, cy) tuples
        self.trail_history = defaultdict(list)

        logger.info("Tracker ready.")

    def update(self, frame):
        """
        Run detection and tracking on one video frame.

        Returns a list of dicts, each representing one detected person:
            {
                "track_id": int or None,
                "x1": float, "y1": float, "x2": float, "y2": float,
                "confidence": float
            }
        """
        # Run YOLO tracking (detection + ByteTrack)
        results = self.model.track(
            source=frame,
            conf=self.confidence,
            iou=self.iou,
            classes=[PERSON_CLASS],
            device=self.device,
            persist=True,             # keep tracking state between frames
            tracker="bytetrack.yaml",
            verbose=False,
        )

        detections = []

        if not results:
            return detections

        result = results[0]

        if result.boxes is None or len(result.boxes) == 0:
            return detections

        # Get bounding boxes and confidence scores as numpy arrays
        boxes = result.boxes.xyxy.cpu().numpy()
        confs = result.boxes.conf.cpu().numpy()

        # Get track IDs (may be None if tracking lost a person)
        if result.boxes.id is not None:
            ids = result.boxes.id.cpu().numpy().astype(int)
        else:
            ids = [None] * len(boxes)

        # Build a simple dict for each detected person
        for box, conf, track_id in zip(boxes, confs, ids):
            x1, y1, x2, y2 = box

            person = {
                "track_id":   int(track_id) if track_id is not None else None,
                "x1":         float(x1),
                "y1":         float(y1),
                "x2":         float(x2),
                "y2":         float(y2),
                "confidence": float(conf),
            }
            detections.append(person)

            # Save the center position to the trail history
            if track_id is not None:
                tid = int(track_id)
                cx, cy = get_center_of_box(x1, y1, x2, y2)
                self.trail_history[tid].append((cx, cy))

                # Only keep the most recent positions (trim old ones)
                if len(self.trail_history[tid]) > MAX_TRAIL_LENGTH:
                    self.trail_history[tid].pop(0)

        return detections

    def reset(self):
        """Clear all tracking data (call this between different video files)."""
        self.trail_history.clear()
        logger.info("Tracker reset.")
