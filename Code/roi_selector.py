"""
roi_selector.py

Select Bus Stop ROI using mouse clicks.
"""

import cv2
import numpy as np

points = []


def mouse_callback(event, x, y, flags, param):

    global points

    if event == cv2.EVENT_LBUTTONDOWN:

        points.append((x, y))

        print(f"Point {len(points)} : ({x}, {y})")


def select_roi(video_path):

    cap = cv2.VideoCapture(video_path)

    ret, frame = cap.read()

    if not ret:
        print("Cannot read video.")
        return None

    clone = frame.copy()

    cv2.namedWindow("Select ROI")

    cv2.setMouseCallback(
        "Select ROI",
        mouse_callback
    )

    while True:

        display = clone.copy()

        for p in points:

            cv2.circle(
                display,
                p,
                5,
                (0, 0, 255),
                -1
            )

        if len(points) > 1:

            cv2.polylines(
                display,
                [np.array(points)],
                False,
                (255, 0, 0),
                2
            )

        cv2.imshow(
            "Select ROI",
            display
        )

        key = cv2.waitKey(1)

        if key == ord("q"):
            break

        if len(points) == 4:
            break

    cv2.destroyAllWindows()

    cap.release()

    return np.array(points)