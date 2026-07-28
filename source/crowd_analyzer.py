# core/crowd_analyzer.py - Figures out how many people are present and who is waiting

from utils import setup_logger, get_distance

logger = setup_logger("CrowdAnalyzer")


class CrowdAnalyzer:
    """
    Analyzes each frame to count people and detect who is waiting (stationary).

    A person is considered "waiting" if they haven't moved much for
    several seconds (based on the waiting_time_threshold setting).
    """

    def __init__(self, frame_width, frame_height, stationary_pixels=25, fps=25.0, wait_seconds=30.0):
        self.frame_width       = frame_width
        self.frame_height      = frame_height
        self.stationary_pixels = stationary_pixels  # max movement to be called "still"
        self.fps               = max(fps, 1.0)
        self.wait_seconds      = wait_seconds        # seconds before a person is flagged as waiting

        # Tracks how many frames each person has been stationary
        # Key: track_id (int), Value: frame count (int)
        self.stationary_frame_count = {}

        logger.info(
            f"CrowdAnalyzer ready. Frame size: {frame_width}x{frame_height}, "
            f"FPS: {fps}, Wait threshold: {wait_seconds}s"
        )

    def analyze(self, frame_no, timestamp, detections, trail_history):
        """
        Process one frame and return crowd statistics as a plain dict.

        Parameters:
            frame_no     : current frame number (int)
            timestamp    : time in seconds from video start (float)
            detections   : list of person dicts from the tracker
            trail_history: dict of track_id -> list of (cx, cy) positions

        Returns a dict with:
            frame_no, timestamp, crowd_count, waiting_ids,
            avg_wait, max_wait, detections
        """

        # Collect IDs of all people currently visible
        active_ids = set()
        for person in detections:
            if person["track_id"] is not None:
                active_ids.add(person["track_id"])

        # Total crowd count is just how many people we can see
        crowd_count = len(active_ids)

        # Update how long each person has been standing still
        self._update_stationary_counts(active_ids, trail_history)

        # Find out who has been waiting long enough to be flagged
        waiting_ids = []
        wait_times  = []

        for tid in active_ids:
            frames_still = self.stationary_frame_count.get(tid, 0)
            seconds_waiting = frames_still / self.fps

            if seconds_waiting >= self.wait_seconds:
                waiting_ids.append(tid)
                wait_times.append(seconds_waiting)

        # Calculate average and max wait time
        if wait_times:
            avg_wait = sum(wait_times) / len(wait_times)
            max_wait = max(wait_times)
        else:
            avg_wait = 0.0
            max_wait = 0.0

        # Remove tracking data for people who left the frame
        left_ids = set(self.stationary_frame_count.keys()) - active_ids
        for tid in left_ids:
            del self.stationary_frame_count[tid]

        # Return all stats as a plain dictionary
        stats = {
            "frame_no":    frame_no,
            "timestamp":   timestamp,
            "crowd_count": crowd_count,
            "waiting_ids": waiting_ids,
            "avg_wait":    avg_wait,
            "max_wait":    max_wait,
            "detections":  detections,
        }

        return stats

    def _update_stationary_counts(self, active_ids, trail_history):
        """
        For each active person, check if they moved or stayed still.
        Increment or reset their stationary frame counter accordingly.
        """
        for tid in active_ids:
            history = trail_history.get(tid, [])

            # Need at least 2 positions to check movement
            if len(history) < 2:
                # First time seeing them — start their counter at 0
                if tid not in self.stationary_frame_count:
                    self.stationary_frame_count[tid] = 0
                continue

            # Measure how far they moved since last frame
            last_pos = history[-1]
            prev_pos = history[-2]
            movement = get_distance(last_pos, prev_pos)

            if movement <= self.stationary_pixels:
                # They barely moved — add one frame to their still count
                self.stationary_frame_count[tid] = self.stationary_frame_count.get(tid, 0) + 1
            else:
                # They moved — reset their still count
                self.stationary_frame_count[tid] = 0

    def get_wait_time_in_seconds(self, track_id):
        """Return how many seconds a person (by track_id) has been waiting."""
        frames = self.stationary_frame_count.get(track_id, 0)
        return frames / self.fps
