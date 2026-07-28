# storage/video_writer.py - Saves the annotated video frames to an MP4 file

import os
import cv2
from utils import setup_logger

logger = setup_logger("VideoWriter")


class VideoWriter:
    """
    Wraps OpenCV's VideoWriter to save annotated frames as an MP4 video file.
    """

    def __init__(self, output_path, fps, width, height):
        # Make sure the output folder exists
        output_folder = os.path.dirname(output_path)
        if output_folder:
            os.makedirs(output_folder, exist_ok=True)

        # mp4v is a common codec that works on most systems
        fourcc = cv2.VideoWriter_fourcc(*"mp4v")
        self._writer = cv2.VideoWriter(output_path, fourcc, fps, (width, height))

        if not self._writer.isOpened():
            raise RuntimeError(f"Could not create video file: {output_path}")

        self.output_path = output_path
        logger.info(f"Video output: {output_path}  ({width}x{height} @ {fps:.1f}fps)")

    def write_frame(self, frame):
        """Write one BGR frame to the video file."""
        self._writer.write(frame)

    def close(self):
        """Finish writing and close the video file."""
        if self._writer.isOpened():
            self._writer.release()
            logger.info(f"Video saved: {self.output_path}")

    def __del__(self):
        self.close()
