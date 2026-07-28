# storage/evidence_store.py - Saves a screenshot of the frame when an alert happens

import os
import cv2
from utils import setup_logger

logger = setup_logger("EvidenceStore")


class EvidenceStore:
    """
    Saves a JPEG image of the annotated frame each time an alert is triggered.
    Images are saved to the snapshots folder inside the output directory.
    """

    def __init__(self, snapshot_folder, jpeg_quality=90):
        self.snapshot_folder = snapshot_folder
        self.jpeg_quality    = jpeg_quality

        # Create the folder if it doesn't exist
        os.makedirs(snapshot_folder, exist_ok=True)
        logger.info(f"Snapshots will be saved to: {snapshot_folder}")

    def save_snapshot(self, frame, alert, run_tag):
        """
        Save an annotated frame as a JPEG file.

        Parameters:
            frame   : the annotated BGR frame (numpy array)
            alert   : alert dict from AlertManager.check()
            run_tag : a string used in the filename for identification

        Returns the file path where the image was saved.
        """
        # Build a descriptive filename
        alert_type = alert["alert_type"]
        frame_num  = alert["frame_no"]
        filename   = f"snapshot_{run_tag}_{alert_type}_frame{frame_num:06d}.jpg"
        file_path  = os.path.join(self.snapshot_folder, filename)

        # Save the image with the specified JPEG quality
        encode_params = [cv2.IMWRITE_JPEG_QUALITY, self.jpeg_quality]
        success = cv2.imwrite(file_path, frame, encode_params)

        if success:
            logger.info(f"Snapshot saved: {filename}")
        else:
            logger.error(f"Failed to save snapshot: {file_path}")

        return file_path
