from pathlib import Path
import numpy as np
# ===========================
# PROJECT PATHS
# ===========================

ROI=np.array(
[[ 835 , 223],
 [ 809 , 556],
 [1241 , 515],
 [1237 , 140]]
)

ROOT = Path(__file__).resolve().parent.parent

MODEL_PATH = ROOT / "Models" / "yolov8n.pt"

INPUT_VIDEO = ROOT / "Input_Videos" / "sample.mp4"

OUTPUT_VIDEO = ROOT / "Outputs" / "output_videos" / "output.mp4"

SNAPSHOT_DIR = ROOT / "Outputs" / "evidence_snapshots"

ANALYTICS_DIR = ROOT / "Outputs" / "analytics"

CSV_PATH = ROOT / "CSV" / "report.csv"

# ===========================
# DETECTION SETTINGS
# ===========================

CONFIDENCE_THRESHOLD = 0.40

PERSON_CLASS_ID = 0

# ===========================
# TRACKING SETTINGS
# ===========================

TRACKER_CONFIG = "bytetrack.yaml"

TRACK_ACTIVATION_THRESHOLD = 0.25

MIN_MATCHING_THRESHOLD = 0.8

LOST_TRACK_BUFFER = 30

# ===========================
# CROWD SETTINGS
# ===========================

LOW_DENSITY = 5

MEDIUM_DENSITY = 15

HIGH_DENSITY = 25

WAITING_THRESHOLD = 60

SNAPSHOT_INTERVAL = 15

# ===========================
# DISPLAY SETTINGS
# ===========================

FONT_SCALE = 0.8

THICKNESS = 2