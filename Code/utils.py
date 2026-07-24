"""
utils.py

Drawing utilities for Bus Stop Crowd Monitoring.
"""

import cv2


def draw_boxes(frame, tracked):
    """
    Draw bounding boxes and tracker IDs.
    """

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
    """
    Draw analytics dashboard on frame.
    """

    x = 20
    y = 35

    # Background rectangle
    cv2.rectangle(
        frame,
        (10, 10),
        (330, 170),
        (40, 40, 40),
        -1
    )

    # Crowd Count
    cv2.putText(
        frame,
        f"Crowd Count : {analytics['crowd_count']}",
        (x, y),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.7,
        (255, 255, 255),
        2
    )

    y += 30

    # Density
    density = analytics["density"]

    if density == "LOW":
        color = (0, 255, 0)

    elif density == "MEDIUM":
        color = (0, 255, 255)

    else:
        color = (0, 0, 255)

    cv2.putText(
        frame,
        f"Density : {density}",
        (x, y),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.7,
        color,
        2
    )

    y += 30

    # Unique People
    cv2.putText(
        frame,
        f"Unique People : {analytics['unique_people']}",
        (x, y),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.7,
        (255, 255, 255),
        2
    )

    y += 40

    # Alerts
    if len(alerts) > 0:

        for alert in alerts:

            cv2.putText(
                frame,
                alert,
                (x, y),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.7,
                (0, 0, 255),
                2
            )

            y += 30

    else:

        cv2.putText(
            frame,
            "Status : NORMAL",
            (x, y),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.7,
            (0, 255, 0),
            2
        )

    return frame

def draw_roi(frame, roi):

    cv2.polylines(
        frame,
        [roi],
        True,
        (255, 0, 0),
        2
    )

    cv2.putText(
        frame,
        "Bus Stop ROI",
        tuple(roi[0]),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.7,
        (255,0,0),
        2
    )

    return frame