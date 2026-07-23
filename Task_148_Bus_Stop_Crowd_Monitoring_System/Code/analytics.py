"""
analytics.py

This module computes crowd analytics.

Features:
- Crowd Count
- Crowd Density
- Waiting Time
- Unique Persons
"""

import time

from config import (
    LOW_DENSITY,
    MEDIUM_DENSITY,
    HIGH_DENSITY
)


class CrowdAnalytics:

    def __init__(self):

        # Stores first appearance time of each tracked person
        self.entry_times = {}

    def update(self, tracked_detections):

        current_time = time.time()

        tracker_ids = tracked_detections.tracker_id

        # Handle case when no people are detected
        if tracker_ids is None:
            tracker_ids = []

        crowd_count = len(tracker_ids)

        waiting_times = {}

        # Record entry time for new IDs
        for person_id in tracker_ids:

            if person_id not in self.entry_times:

                self.entry_times[person_id] = current_time

            waiting_times[person_id] = round(
                current_time - self.entry_times[person_id],
                1
            )

        # Determine crowd density
        if crowd_count <= LOW_DENSITY:

            density = "LOW"

        elif crowd_count <= MEDIUM_DENSITY:

            density = "MEDIUM"

        else:

            density = "HIGH"

        return {

            "crowd_count": crowd_count,

            "density": density,

            "waiting_times": waiting_times,

            "unique_people": len(self.entry_times)
        }