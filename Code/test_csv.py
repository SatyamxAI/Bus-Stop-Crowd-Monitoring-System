import cv2

from detector import PersonDetector
from tracker import PersonTracker
from analytics import CrowdAnalytics
from alerts import AlertManager
from csv_logger import CSVLogger

detector = PersonDetector()
tracker = PersonTracker()
analytics = CrowdAnalytics()
alerts = AlertManager()
csv_logger = CSVLogger()

cap = cv2.VideoCapture("../Input_Videos/sample.mp4")

frame_count = 0

while True:

    ret, frame = cap.read()

    if not ret:
        break

    result = detector.detect(frame)

    tracked = tracker.update(result)

    stats = analytics.update(tracked)

    current_alerts = alerts.check_alerts(stats)

    csv_logger.log(
        stats,
        current_alerts
    )

    frame_count += 1

    if frame_count == 5:
        break

cap.release()

print("CSV created successfully.")