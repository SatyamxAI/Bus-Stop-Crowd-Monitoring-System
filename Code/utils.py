"""
utils.py

Drawing utilities for Bus Stop Crowd Monitoring.
"""

import cv2


def draw_boxes(frame, tracked):

    if tracked.tracker_id is None:
        return frame

    for tracker_id, box in zip(tracked.tracker_id, tracked.xyxy):

        x1, y1, x2, y2 = map(int, box)

        cv2.rectangle(
            frame,
            (x1, y1),
            (x2, y2),
            (0, 255, 0),
            2
        )

        cv2.putText(
            frame,
            f"ID {int(tracker_id)}",
            (x1, y1 - 8),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.6,
            (0, 255, 0),
            2
        )

    return frame


def draw_dashboard(frame, analytics, alerts):

    y = 30

    cv2.putText(
        frame,
        f"Crowd Count : {analytics['crowd_count']}",
        (20, y),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.7,
        (255, 255, 255),
        2
    )

    y += 30

    cv2.putText(
        frame,
        f"Density : {analytics['density']}",
        (20, y),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.7,
        (255, 255, 255),
        2
    )

    y += 30

    cv2.putText(
        frame,
        f"Unique People : {analytics['unique_people']}",
        (20, y),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.7,
        (255, 255, 255),
        2
    )

    y += 40

    if alerts:

        cv2.putText(
            frame,
            "ALERT!",
            (20, y),
            cv2.FONT_HERSHEY_SIMPLEX,
            1,
            (0, 0, 255),
            3
        )

    return frame