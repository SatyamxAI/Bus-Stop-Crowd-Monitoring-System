import cv2

from detector import PersonDetector
from tracker import PersonTracker
from analytics import CrowdAnalytics
from alerts import AlertManager

detector = PersonDetector()
tracker = PersonTracker()
analytics = CrowdAnalytics()
alerts = AlertManager()

cap = cv2.VideoCapture("../Input_Videos/sample.mp4")

frame = 0

while True:

    ret, img = cap.read()

    if not ret:
        break

    result = detector.detect(img)

    tracked = tracker.update(result)

    stats = analytics.update(tracked)

    current_alerts = alerts.check_alerts(stats)

    print("=" * 50)
    print(stats)
    print(current_alerts)

    frame += 1

    if frame == 5:
        break

cap.release()