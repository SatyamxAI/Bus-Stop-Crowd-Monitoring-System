"""
alerts.py

Generates alerts based on crowd analytics.
"""

from config import WAITING_THRESHOLD


class AlertManager:

    def __init__(self):
        pass

    def check_alerts(self, analytics):

        alerts = []

        # High Crowd Alert
        if analytics["density"] == "HIGH":
            alerts.append("HIGH CROWD")

        # Long Waiting Alert
        long_wait = 0

        for waiting_time in analytics["waiting_times"].values():

            if waiting_time >= WAITING_THRESHOLD:
                long_wait += 1

        if long_wait > 0:
            alerts.append(
                f"{long_wait} People Waiting Too Long"
            )

        return alerts