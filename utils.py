# utils.py - Helper functions used across the project

import os
import time
import yaml
import logging


# -------------------------------------------------------
# Logger setup
# -------------------------------------------------------

def setup_logger(name):
    """Create and return a simple logger that prints to the console."""
    logger = logging.getLogger(name)

    # Only add a handler if one doesn't already exist
    if not logger.handlers:
        handler = logging.StreamHandler()
        formatter = logging.Formatter(
            "[%(asctime)s] %(levelname)s - %(name)s: %(message)s",
            datefmt="%H:%M:%S"
        )
        handler.setFormatter(formatter)
        logger.addHandler(handler)

    logger.setLevel(logging.INFO)
    return logger


# -------------------------------------------------------
# Config loader
# -------------------------------------------------------

def load_config(config_path):
    """Read a YAML config file and return it as a Python dictionary."""
    with open(config_path, "r") as f:
        config = yaml.safe_load(f)
    return config


# -------------------------------------------------------
# Directory helpers
# -------------------------------------------------------

def make_output_folders(config):
    """
    Create all output folders (videos, snapshots, reports).
    Returns a dict with the folder paths.
    """
    base_dir = config.get("output_dir", "output")

    folders = {
        "videos":    os.path.join(base_dir, config.get("video_subdir",    "videos")),
        "snapshots": os.path.join(base_dir, config.get("snapshot_subdir", "snapshots")),
        "reports":   os.path.join(base_dir, config.get("report_subdir",   "reports")),
    }

    for path in folders.values():
        os.makedirs(path, exist_ok=True)

    return folders


# -------------------------------------------------------
# Timestamp helpers
# -------------------------------------------------------

def get_timestamp_string():
    """Return the current time as a string like '20240723_143000'."""
    return time.strftime("%Y%m%d_%H%M%S")


def get_date_string():
    """Return today's date as a string like '2024-07-23'."""
    return time.strftime("%Y-%m-%d")


# -------------------------------------------------------
# Geometry helpers
# -------------------------------------------------------

def get_center_of_box(x1, y1, x2, y2):
    """Return the (cx, cy) center point of a bounding box."""
    cx = int((x1 + x2) / 2)
    cy = int((y1 + y2) / 2)
    return cx, cy


def get_distance(point1, point2):
    """Return the Euclidean distance between two (x, y) points."""
    dx = point1[0] - point2[0]
    dy = point1[1] - point2[1]
    return (dx * dx + dy * dy) ** 0.5
