import cv2

from detector import PersonDetector
from tracker import PersonTracker
from analytics import CrowdAnalytics
from alerts import AlertManager
from snapshot import SnapshotManager
from csv_logger import CSVLogger
from utils import draw_boxes, draw_dashboard
from utils import draw_boxes, draw_dashboard, draw_roi

from config import (
    INPUT_VIDEO,
    OUTPUT_VIDEO
)

detector = PersonDetector()
tracker = PersonTracker()
analytics = CrowdAnalytics()
alerts = AlertManager()
snapshot = SnapshotManager()
csv_logger = CSVLogger()

cap = cv2.VideoCapture(INPUT_VIDEO)

if not cap.isOpened():
    print("Cannot open input video.")
    exit()

width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
fps = cap.get(cv2.CAP_PROP_FPS)
if fps <= 0:
    fps = 30

print("INPUT_VIDEO :", INPUT_VIDEO)
print("OUTPUT_VIDEO:", OUTPUT_VIDEO)
print("Width :", width)
print("Height:", height)
print("FPS :", fps)
writer = cv2.VideoWriter(
    OUTPUT_VIDEO,
    cv2.VideoWriter_fourcc(*"mp4v"),
    fps,
    (width, height)
)
if not writer.isOpened():
    print("❌ Could not create output video.")
    exit()


frame_number = 0
while True:
    frame_number += 1

    if frame_number % 30 == 0:
         print(f"Processed {frame_number} frames...")
    ret, frame = cap.read()

    if not ret:
        break

    result = detector.detect(frame)

    tracked = tracker.update(result)

    # Crowd Count directly from YOLO
    crowd_count = len(result.boxes)

    stats = analytics.update(tracked,crowd_count)

    current_alerts = alerts.check_alerts(stats)

    draw_boxes(frame, tracked)
    tracker.draw_roi(frame)
    from utils import draw_roi

    draw_roi(
    frame,
    tracker.roi
    )
    draw_dashboard(
      frame,
      stats,
      current_alerts
    )

    snapshot.save_snapshot(
       frame,
       current_alerts
    )

    csv_logger.log(
      stats,
      current_alerts
   )

    writer.write(frame)

cap.release()
writer.release()

print("=" * 60)
print("Processing Completed")
print(f"Frames Processed : {frame_number}")
print(f"Output Saved : {OUTPUT_VIDEO}")
print("=" * 60)