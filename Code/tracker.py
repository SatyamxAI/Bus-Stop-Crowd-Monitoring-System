"""
tracker.py

This module handles multi-object tracking using ByteTrack.
"""

import cv2
import numpy as np
import supervision as sv

from config import ROI


class PersonTracker:
    """
    Tracks detected persons and keeps only those inside the ROI.
    """

    def __init__(self):

        self.tracker = sv.ByteTrack()

        self.roi = ROI

    def update(self, result):

        detections = sv.Detections.from_ultralytics(result)

        tracked_detections = self.tracker.update_with_detections(
            detections
        )

        filtered_boxes = []
        filtered_ids = []

        if tracked_detections.tracker_id is not None:

            for tracker_id, box in zip(
                tracked_detections.tracker_id,
                tracked_detections.xyxy
            ):

                x1, y1, x2, y2 = box

                cx = int((x1 + x2) / 2)
                cy = int((y1 + y2) / 2)

                inside = (
                    cv2.pointPolygonTest(
                        self.roi.astype(np.int32),
                        (cx, cy),
                        False
                    ) >= 0
                )

                if inside:

                    filtered_boxes.append(box)
                    filtered_ids.append(tracker_id)

        # Update detections with only ROI objects
        if len(filtered_boxes) > 0:

            tracked_detections.xyxy = np.array(filtered_boxes)

            tracked_detections.tracker_id = np.array(filtered_ids)

        else:

            tracked_detections.xyxy = np.empty((0, 4))

            tracked_detections.tracker_id = np.array([])

        return tracked_detections

    def draw_roi(self, frame):

        cv2.polylines(
            frame,
            [self.roi.astype(np.int32)],
            True,
            (255, 0, 0),
            2
        )

        cv2.putText(
            frame,
            "Bus Stop ROI",
            tuple(self.roi[0]),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.7,
            (255, 0, 0),
            2
        )

        return frame