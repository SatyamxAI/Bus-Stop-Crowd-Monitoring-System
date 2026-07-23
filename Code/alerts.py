"""
alerts.py

Generates alerts based on crowd analytics.
"""

from config import (
    ALERT_THRESHOLD,
    WAITING_THRESHOLD
)


class AlertManager:

    def __init__(self):
        pass

    def check_alerts(self, analytics):

        alerts = []

        # Crowd Alert
        if analytics["crowd_count"] >= ALERT_THRESHOLD:

            alerts.append("HIGH CROWD")

        # Waiting Time Alert
        for person_id, waiting_time in analytics["waiting_times"].items():

            if waiting_time >= WAITING_THRESHOLD:

                alerts.append(
                    f"LONG WAIT : Person {int(person_id)}"
                )

        return alerts