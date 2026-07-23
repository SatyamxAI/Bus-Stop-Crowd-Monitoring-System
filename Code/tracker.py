"""
tracker.py

This module handles multi-object tracking using ByteTrack.
"""

import supervision as sv


class PersonTracker:
    """
    Tracks detected persons and assigns unique IDs.
    """

    def __init__(self):
        self.tracker = sv.ByteTrack()

    def update(self, result):
        """
        Parameters
        ----------
        result : ultralytics.engine.results.Results

        Returns
        -------
        supervision.Detections
        """

        detections = sv.Detections.from_ultralytics(result)

        tracked_detections = self.tracker.update_with_detections(
            detections
        )

        return tracked_detections