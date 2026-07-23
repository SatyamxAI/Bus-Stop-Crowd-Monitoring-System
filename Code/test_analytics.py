import cv2

from detector import PersonDetector
from tracker import PersonTracker
from analytics import CrowdAnalytics

detector = PersonDetector()
tracker = PersonTracker()
analytics = CrowdAnalytics()

cap = cv2.VideoCapture("../Input_Videos/sample.mp4")

frame_count = 0

while True:

    ret, frame = cap.read()

    if not ret:
        break

    result = detector.detect(frame)

    tracked = tracker.update(result)

    stats = analytics.update(tracked)

    print(stats)

    frame_count += 1

    if frame_count == 5:
        break

cap.release()