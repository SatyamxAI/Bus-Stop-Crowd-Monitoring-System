# drawing/annotator.py - Draws bounding boxes, info panel, and alerts on each frame

import cv2
from utils import setup_logger

logger = setup_logger("Annotator")

# --- Colors (BGR format for OpenCV) ---
GREEN  = (60,  210,  60)   # low crowd
YELLOW = (30,  200, 230)   # medium crowd
RED    = (40,   40, 220)   # high crowd / alert
WHITE  = (255, 255, 255)
BLACK  = (0,   0,   0)
DARK   = (15,  15,  15)    # panel background

FONT       = cv2.FONT_HERSHEY_SIMPLEX
FONT_BOLD  = cv2.FONT_HERSHEY_DUPLEX


def pick_box_color(crowd_count, low_limit, high_limit):
    """Return a color based on how crowded it is."""
    if crowd_count < low_limit:
        return GREEN
    elif crowd_count < high_limit:
        return YELLOW
    else:
        return RED


class FrameAnnotator:
    """
    Draws all the visual elements on a video frame:
      - Bounding boxes around each person with their ID
      - HUD panel showing people count and alert status
      - Flashing alert banner when an alert is active
    """

    def __init__(self, frame_width, frame_height, crowd_threshold=15):
        self.frame_width     = frame_width
        self.frame_height    = frame_height
        self.crowd_threshold = crowd_threshold

    def draw(self, frame, stats, active_alert_types):
        """
        Draw everything on a copy of the frame and return it.

        Parameters:
            frame              : original BGR frame (numpy array)
            stats              : dict from CrowdAnalyzer.analyze()
            active_alert_types : list of alert type strings currently active
        """
        # Work on a copy so we never modify the original frame
        output_frame = frame.copy()

        # Step 1: Draw bounding boxes around each detected person
        output_frame = self._draw_boxes(output_frame, stats)

        # Step 2: Draw the info panel in the top-left corner
        output_frame = self._draw_hud(output_frame, stats)

        # Step 3: Draw a flashing alert banner if any alert is active
        if active_alert_types:
            output_frame = self._draw_alert_banner(output_frame, active_alert_types, stats["frame_no"])

        return output_frame

    # ------------------------------------------------------------------
    # Private helper methods below
    # ------------------------------------------------------------------

    def _draw_boxes(self, frame, stats):
        """Draw a rectangle and track ID label around each detected person."""
        crowd_count = stats["crowd_count"]
        low_limit   = self.crowd_threshold // 2
        high_limit  = self.crowd_threshold

        # Pick a single color for all boxes based on the current crowd level
        box_color = pick_box_color(crowd_count, low_limit, high_limit)

        for person in stats["detections"]:
            x1 = int(person["x1"])
            y1 = int(person["y1"])
            x2 = int(person["x2"])
            y2 = int(person["y2"])
            tid = person["track_id"]

            # Draw the bounding box
            cv2.rectangle(frame, (x1, y1), (x2, y2), box_color, 2)

            # Draw the track ID label above the box (e.g. "#3")
            if tid is not None:
                label = f"#{tid}"

                text_size, _ = cv2.getTextSize(label, FONT, 0.5, 1)
                text_w, text_h = text_size

                label_x = x1
                label_y = max(y1 - 5, text_h + 6)

                # Small filled background rectangle for readability
                cv2.rectangle(
                    frame,
                    (label_x, label_y - text_h - 4),
                    (label_x + text_w + 6, label_y + 2),
                    box_color, -1
                )
                cv2.putText(
                    frame, label,
                    (label_x + 3, label_y - 2),
                    FONT, 0.5, WHITE, 1, cv2.LINE_AA
                )

        return frame

    def _draw_hud(self, frame, stats):
        """Draw a clean info panel in the top-left corner of the frame."""
        crowd_count = stats["crowd_count"]

        # --- Fixed pixel positions ---
        panel_x  = 12
        panel_y  = 12
        panel_w  = 250
        panel_h  = 135    # tall enough so nothing gets clipped
        pad      = 16     # horizontal padding inside the panel

        # Row Y positions (absolute frame coordinates)
        y_title   = panel_y + 30   # "BUS STOP MONITOR" text baseline
        y_divider = panel_y + 42   # thin horizontal line
        y_label   = panel_y + 62   # small "PEOPLE" label
        y_count   = panel_y + 100  # large bold number
        dot_y     = panel_y + 93   # center of status dot

        # --- Draw dark semi-transparent background ---
        overlay = frame.copy()
        cv2.rectangle(
            overlay,
            (panel_x, panel_y),
            (panel_x + panel_w, panel_y + panel_h),
            DARK, -1
        )
        frame = cv2.addWeighted(overlay, 0.72, frame, 0.28, 0)

        # --- Colored border (changes with crowd level) ---
        border_color = pick_box_color(crowd_count, self.crowd_threshold // 2, self.crowd_threshold)
        cv2.rectangle(
            frame,
            (panel_x, panel_y),
            (panel_x + panel_w, panel_y + panel_h),
            border_color, 2
        )

        # --- Title ---
        cv2.putText(
            frame, "BUS STOP MONITOR",
            (panel_x + pad, y_title),
            FONT, 0.46, WHITE, 1, cv2.LINE_AA
        )

        # --- Divider line ---
        cv2.line(
            frame,
            (panel_x + pad, y_divider),
            (panel_x + panel_w - pad, y_divider),
            (70, 70, 70), 1
        )

        # --- "PEOPLE" small grey label ---
        cv2.putText(
            frame, "PEOPLE",
            (panel_x + pad, y_label),
            FONT, 0.40, (140, 140, 140), 1, cv2.LINE_AA
        )

        # --- Large bold count number ---
        count_color = pick_box_color(crowd_count, self.crowd_threshold // 2, self.crowd_threshold)
        cv2.putText(
            frame, str(crowd_count),
            (panel_x + pad, y_count),
            FONT_BOLD, 1.2, count_color, 2, cv2.LINE_AA
        )

        # --- Status dot + label (right of the number) ---
        if crowd_count >= self.crowd_threshold:
            status_text  = "CROWDED"
            status_color = RED
        elif crowd_count >= self.crowd_threshold // 2:
            status_text  = "MODERATE"
            status_color = YELLOW
        else:
            status_text  = "NORMAL"
            status_color = GREEN

        dot_x = panel_x + pad + 58
        cv2.circle(frame, (dot_x, dot_y), 6, status_color, -1)
        cv2.putText(
            frame, status_text,
            (dot_x + 14, dot_y + 5),
            FONT, 0.43, status_color, 1, cv2.LINE_AA
        )

        return frame

    def _draw_alert_banner(self, frame, active_alert_types, frame_no):
        """Draw a flashing red banner at the top-center of the frame."""
        # The banner flashes on/off every 15 frames
        is_visible = (frame_no // 15) % 2 == 0

        if is_visible:
            overlay = frame.copy()

            # Banner stretches across the center-top of the frame
            banner_x1 = self.frame_width // 4
            banner_y1 = 8
            banner_x2 = 3 * self.frame_width // 4
            banner_y2 = 48

            cv2.rectangle(overlay, (banner_x1, banner_y1), (banner_x2, banner_y2), RED, -1)
            frame = cv2.addWeighted(overlay, 0.82, frame, 0.18, 0)

            # Build a readable label from the active alert type names
            labels = [a.replace("_", " ") for a in active_alert_types]
            banner_text = "!! " + " | ".join(labels) + " !!"

            text_size, _ = cv2.getTextSize(banner_text, FONT, 0.58, 1)
            text_x = (self.frame_width - text_size[0]) // 2

            cv2.putText(
                frame, banner_text,
                (text_x, 35),
                FONT, 0.58, WHITE, 1, cv2.LINE_AA
            )

        return frame
