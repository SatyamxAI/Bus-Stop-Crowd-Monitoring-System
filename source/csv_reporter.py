# storage/csv_reporter.py - Writes alert events to a CSV log file

import csv
import os
import time
from utils import setup_logger, get_date_string

logger = setup_logger("CSVReporter")

# The columns in our CSV report
CSV_COLUMNS = [
    "wall_time",        # real clock time of the alert
    "video_time",       # position in the video (seconds)
    "frame_no",         # which frame it happened on
    "alert_type",       # e.g. HIGH_DENSITY or LONG_WAIT
    "severity",         # WARNING or CRITICAL
    "crowd_count",      # number of people at that moment
    "message",          # full description of the alert
    "snapshot_path",    # path to the saved screenshot (if any)
]


class CSVReporter:
    """
    Logs each alert to a CSV file so you can review events later.
    One CSV file is created per run.
    """

    def __init__(self, report_folder, run_id=""):
        os.makedirs(report_folder, exist_ok=True)

        # Build the filename using today's date and the run ID
        date     = get_date_string()
        suffix   = f"_{run_id}" if run_id else ""
        filename = f"report_{date}{suffix}.csv"
        self.file_path = os.path.join(report_folder, filename)

        # Open the file for appending (so we don't overwrite old data)
        is_new_file = not os.path.exists(self.file_path)
        self._file   = open(self.file_path, "a", newline="", encoding="utf-8")
        self._writer = csv.DictWriter(self._file, fieldnames=CSV_COLUMNS)

        # Write the header row only if this is a brand new file
        if is_new_file:
            self._writer.writeheader()
            self._file.flush()

        logger.info(f"Report file: {self.file_path}")

    def log_alert(self, alert):
        """Write one alert to the CSV file."""
        row = {
            "wall_time":     time.strftime("%Y-%m-%dT%H:%M:%S"),
            "video_time":    f"{alert['timestamp']:.2f}",
            "frame_no":      alert["frame_no"],
            "alert_type":    alert["alert_type"],
            "severity":      alert["severity"],
            "crowd_count":   alert["crowd_count"],
            "message":       alert["message"],
            "snapshot_path": alert.get("snapshot_path") or "",
        }
        self._writer.writerow(row)
        self._file.flush()  # Make sure data is written immediately

    def close(self):
        """Close the CSV file when we're done."""
        if not self._file.closed:
            self._file.close()
            logger.info(f"Report closed: {self.file_path}")

    def __del__(self):
        self.close()
