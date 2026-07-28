# core/alert_manager.py - Decides when to raise alerts based on crowd stats

import time
from utils import setup_logger

logger = setup_logger("AlertManager")


class AlertManager:
    """
    Checks crowd stats each frame and triggers alerts when thresholds are crossed.

    Two types of alerts:
        HIGH_DENSITY - too many people at the bus stop
        LONG_WAIT    - someone has been standing still for too long
    """

    # The two kinds of alerts this system can raise
    ALERT_TYPES = ["HIGH_DENSITY", "LONG_WAIT"]

    def __init__(self, crowd_threshold=15, wait_threshold=30.0, cooldown_seconds=60.0):
        self.crowd_threshold   = crowd_threshold    # people count that triggers alert
        self.wait_threshold    = wait_threshold      # seconds before wait alert
        self.cooldown_seconds  = cooldown_seconds    # gap between repeated alerts

        # Stores when each alert type was last triggered (wall clock time)
        self.last_triggered = {}

        logger.info(
            f"AlertManager ready. Crowd limit: {crowd_threshold}, "
            f"Wait limit: {wait_threshold}s, Cooldown: {cooldown_seconds}s"
        )

    def check(self, stats):
        """
        Look at the current frame's stats and return a list of new alerts.
        Each alert is a plain dict with details about what happened.

        Parameters:
            stats: dict returned by CrowdAnalyzer.analyze()

        Returns:
            list of alert dicts (empty list if no new alerts)
        """
        new_alerts   = []
        current_time = time.time()

        # --- Check for HIGH DENSITY alert ---
        if stats["crowd_count"] >= self.crowd_threshold:
            if self._can_fire("HIGH_DENSITY", current_time):

                # Decide severity based on how far over the limit we are
                if stats["crowd_count"] >= self.crowd_threshold * 1.5:
                    severity = "CRITICAL"
                else:
                    severity = "WARNING"

                alert = {
                    "alert_type":    "HIGH_DENSITY",
                    "severity":      severity,
                    "message":       f"HIGH DENSITY: {stats['crowd_count']} people (limit: {self.crowd_threshold})",
                    "frame_no":      stats["frame_no"],
                    "timestamp":     stats["timestamp"],
                    "crowd_count":   stats["crowd_count"],
                    "snapshot_path": None,
                }
                new_alerts.append(alert)
                self.last_triggered["HIGH_DENSITY"] = current_time
                logger.warning(alert["message"])

        # --- Check for LONG WAIT alert ---
        if len(stats["waiting_ids"]) > 0:
            if self._can_fire("LONG_WAIT", current_time):

                num_waiting = len(stats["waiting_ids"])
                alert = {
                    "alert_type":    "LONG_WAIT",
                    "severity":      "WARNING",
                    "message":       f"LONG WAIT: {num_waiting} person(s) waiting over {self.wait_threshold:.0f}s",
                    "frame_no":      stats["frame_no"],
                    "timestamp":     stats["timestamp"],
                    "crowd_count":   stats["crowd_count"],
                    "snapshot_path": None,
                }
                new_alerts.append(alert)
                self.last_triggered["LONG_WAIT"] = current_time
                logger.warning(alert["message"])

        return new_alerts

    def is_active(self, alert_type):
        """
        Return True if an alert is still 'active' (within its cooldown window).
        This is used to keep the alert banner visible on screen for a while.
        """
        last_time = self.last_triggered.get(alert_type)
        if last_time is None:
            return False
        return (time.time() - last_time) < self.cooldown_seconds

    def any_alert_active(self):
        """Return True if any alert is currently active."""
        for alert_type in self.ALERT_TYPES:
            if self.is_active(alert_type):
                return True
        return False

    def _can_fire(self, alert_type, current_time):
        """Return True if enough time has passed since the last alert of this type."""
        last_time = self.last_triggered.get(alert_type)
        if last_time is None:
            return True
        return (current_time - last_time) >= self.cooldown_seconds
