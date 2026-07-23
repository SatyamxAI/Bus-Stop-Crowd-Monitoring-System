"""
detector.py

This module handles person detection using the YOLO model.

Responsibilities:
- Load the YOLO model
- Run inference on each frame
- Filter only person detections
- Return clean detection results
"""

from ultralytics import YOLO
from config import (
    MODEL_PATH,
    CONFIDENCE_THRESHOLD,
    PERSON_CLASS_ID
)


class PersonDetector:
    """
    YOLO Person Detector
    """

    def __init__(self):
        """
        Load YOLO model once.
        """

        self.model = YOLO(MODEL_PATH)

    def detect(self, frame):
       """
       Detect persons in a frame.

        Returns
        -------
        ultralytics.engine.results.Results
       """

       results = self.model(
          frame,
          conf=CONFIDENCE_THRESHOLD,
          classes=[PERSON_CLASS_ID],
          verbose=False
      )

       return results[0]