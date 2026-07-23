import cv2

from detector import PersonDetector
from tracker import PersonTracker
from analytics import CrowdAnalytics
from alerts import AlertManager
from snapshot import SnapshotManager

detector = PersonDetector()
tracker = PersonTracker()
analytics = CrowdAnalytics()
alerts = AlertManager()
snapshot = SnapshotManager()

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

    path = snapshot.save_snapshot(
        frame,
        current_alerts
    )

    if path is not None:
        print("Snapshot saved:", path)

    frame_count += 1

    if frame_count == 5:
        break

cap.release()