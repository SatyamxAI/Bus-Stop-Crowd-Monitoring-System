"""
snapshot.py

This module saves evidence snapshots whenever an alert occurs.
"""

from pathlib import Path
from datetime import datetime
import time
import cv2

from config import (
    SNAPSHOT_DIR,
    SNAPSHOT_INTERVAL
)


class SnapshotManager:

  def __init__(self):
        Path(SNAPSHOT_DIR).mkdir(
            parents=True,
            exist_ok=True
        )
        self.previous_alert = False
        self.last_snapshot_time = 0

  def save_snapshot(self, frame, alerts):

    if len(alerts) == 0:
        self.previous_alert = False
        return None

    current_time = time.time()

    if (
        current_time - self.last_snapshot_time
        < SNAPSHOT_INTERVAL
    ):
        return None

    self.last_snapshot_time = current_time

    self.previous_alert = True

    timestamp = datetime.now().strftime(
        "%Y%m%d_%H%M%S"
    )

    filename = f"snapshot_{timestamp}.jpg"

    filepath = Path(SNAPSHOT_DIR) / filename

    cv2.imwrite(str(filepath), frame)

    return filepath