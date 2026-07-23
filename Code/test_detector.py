import cv2

from detector import PersonDetector
from tracker import PersonTracker

detector = PersonDetector()
tracker = PersonTracker()

cap = cv2.VideoCapture("../Input_Videos/sample.mp4")

while True:

    ret, frame = cap.read()

    if not ret:
        break

    result = detector.detect(frame)

    tracked = tracker.update(result)

    print("-" * 40)

    print(f"Tracked Persons: {len(tracked)}")

    for tracker_id, box in zip(tracked.tracker_id, tracked.xyxy):

        print(
            f"ID: {tracker_id} | "
            f"BBox: {box.astype(int)}"
        )

    # Test only first 5 frames
    break

cap.release()

print("Tracker test completed.")