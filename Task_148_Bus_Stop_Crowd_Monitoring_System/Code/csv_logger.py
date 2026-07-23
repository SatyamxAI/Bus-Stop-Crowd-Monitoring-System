"""
csv_logger.py

Logs crowd analytics to a CSV file.
"""

import csv
from pathlib import Path
from datetime import datetime

from config import CSV_PATH


class CSVLogger:

    def __init__(self):

        Path(CSV_PATH).parent.mkdir(
            parents=True,
            exist_ok=True
        )

        self.header = [
            "Timestamp",
            "Crowd_Count",
            "Density",
            "Unique_People",
            "Alerts"
        ]

        # Create CSV file with header
        if not Path(CSV_PATH).exists():

            with open(
                CSV_PATH,
                mode="w",
                newline=""
            ) as file:

                writer = csv.writer(file)

                writer.writerow(self.header)

    def log(self, analytics, alerts):

        timestamp = datetime.now().strftime(
            "%Y-%m-%d %H:%M:%S"
        )

        with open(
            CSV_PATH,
            mode="a",
            newline=""
        ) as file:

            writer = csv.writer(file)

            writer.writerow([

                timestamp,

                analytics["crowd_count"],

                analytics["density"],

                analytics["unique_people"],

                ", ".join(alerts)

            ])