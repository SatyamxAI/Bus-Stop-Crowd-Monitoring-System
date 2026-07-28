# main.py - Bus Stop Crowd Monitoring System
#
# This is the main file. Run this to start the program.
#
# How to run:
#   python main.py                           # processes all videos in data/input/
#   python main.py --source data/input/v.mp4 # process one specific video
#   python main.py --no-preview              # run without showing the window
#   python main.py --dry-run                 # preview only, save nothing

import argparse
import glob
import os
import sys
import time

import cv2

from utils                   import load_config, make_output_folders, setup_logger, get_timestamp_string
from source.tracker          import PersonTracker
from source.crowd_analyzer   import CrowdAnalyzer
from source.alert_manager    import AlertManager
from source.evidence_store   import EvidenceStore
from source.csv_reporter     import CSVReporter
from source.video_writer     import VideoWriter
from source.annotator        import FrameAnnotator

# Logger for this file
logger = setup_logger("Main")

# Supported video file extensions
VIDEO_EXTENSIONS = [".mp4", ".avi", ".mov", ".mkv", ".wmv", ".flv"]

# Default input folder (videos go here)
DEFAULT_INPUT_FOLDER = "data/input"


# -------------------------------------------------------
# Step 1: Read command-line arguments
# -------------------------------------------------------

def get_arguments():
    """Read arguments passed in the terminal when running the script."""
    parser = argparse.ArgumentParser(
        description="Bus Stop Crowd Monitoring System"
    )

    parser.add_argument(
        "--source", "-s",
        default=DEFAULT_INPUT_FOLDER,
        help=f"Path to a video file or a folder of videos (default: {DEFAULT_INPUT_FOLDER}/)"
    )
    parser.add_argument(
        "--config", "-c",
        default="config.yaml",
        help="Path to the config file (default: config.yaml)"
    )
    parser.add_argument(
        "--no-preview",
        action="store_true",
        help="Don't show the live preview window"
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Run without saving any output files"
    )
    parser.add_argument(
        "--device",
        default="",
        help="Device for YOLO: '' (auto), 'cpu', or '0' for GPU"
    )

    return parser.parse_args()


# -------------------------------------------------------
# Step 2: Find video files to process
# -------------------------------------------------------

def find_video_files(source_path):
    """
    Given a file path or folder, return a sorted list of video files.
    Exits the program if nothing is found.
    """
    if os.path.isfile(source_path):
        return [source_path]

    if os.path.isdir(source_path):
        found_videos = []
        for ext in VIDEO_EXTENSIONS:
            found_videos += glob.glob(os.path.join(source_path, f"*{ext}"))
            found_videos += glob.glob(os.path.join(source_path, f"*{ext.upper()}"))

        found_videos = sorted(set(found_videos))

        if not found_videos:
            logger.error(f"No video files found in: {source_path}")
            sys.exit(1)

        return found_videos

    logger.error(f"Source not found: {source_path}")
    sys.exit(1)


# -------------------------------------------------------
# Step 3: Process one video file
# -------------------------------------------------------

def process_one_video(video_path, config, args, output_folders, run_id, video_number, total_videos):
    """
    Run the full pipeline on one video:
      - Open video → detect & track people → analyze → alert → annotate → save
    Returns a summary dict with stats for this video.
    """
    video_name = os.path.splitext(os.path.basename(video_path))[0]
    logger.info(f"--- [{video_number}/{total_videos}] {os.path.basename(video_path)} ---")

    # Open the video
    cap = cv2.VideoCapture(video_path)
    if not cap.isOpened():
        logger.error(f"Cannot open: {video_path}")
        return {}

    # Read video properties
    total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    source_fps   = cap.get(cv2.CAP_PROP_FPS) or 25.0
    frame_width  = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    frame_height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    output_fps   = config.get("output_fps", 0) or source_fps

    logger.info(f"  {frame_width}x{frame_height} @ {source_fps:.1f}fps  |  {total_frames} frames")

    # Create all processing modules
    tracker = PersonTracker(
        model_path = config.get("model", "models/yolov8n.pt"),
        confidence = config.get("confidence_threshold", 0.40),
        iou        = config.get("iou_threshold", 0.45),
        device     = args.device,
    )

    analyzer = CrowdAnalyzer(
        frame_width       = frame_width,
        frame_height      = frame_height,
        stationary_pixels = config.get("stationary_pixel_threshold", 25),
        fps               = source_fps,
        wait_seconds      = config.get("waiting_time_threshold", 30),
    )

    alert_mgr = AlertManager(
        crowd_threshold  = config.get("crowd_alert_threshold", 15),
        wait_threshold   = config.get("waiting_time_threshold", 30),
        cooldown_seconds = config.get("alert_cooldown_seconds", 60),
    )

    annotator = FrameAnnotator(
        frame_width     = frame_width,
        frame_height    = frame_height,
        crowd_threshold = config.get("crowd_alert_threshold", 15),
    )

    # Set up output writers (skip in dry-run mode)
    video_tag = f"{run_id}_{video_number:02d}_{video_name}"

    if not args.dry_run and config.get("snapshot_on_alert", True):
        snapshot_saver = EvidenceStore(output_folders.get("snapshots", "data/output/snapshots"))
    else:
        snapshot_saver = None

    if not args.dry_run:
        csv_log = CSVReporter(output_folders.get("reports", "data/output/reports"), run_id=video_tag)
    else:
        csv_log = None

    video_out = None
    if not args.dry_run and config.get("save_video", True):
        out_path = os.path.join(
            output_folders.get("videos", "data/output/videos"),
            f"output_{video_tag}.mp4"
        )
        video_out = VideoWriter(out_path, output_fps, frame_width, frame_height)

    # Preview window settings
    show_preview   = config.get("show_preview", True) and not args.no_preview and not args.dry_run
    preview_width  = config.get("preview_width",  1280)
    preview_height = config.get("preview_height",  720)
    window_title   = f"Bus Stop Monitor — {os.path.basename(video_path)}"

    # Frame loop
    frame_number = 0
    total_alerts = 0
    peak_count   = 0
    start_time   = time.time()

    while True:
        ret, frame = cap.read()
        if not ret:
            break

        timestamp  = frame_number / source_fps
        detections = tracker.update(frame)

        stats = analyzer.analyze(
            frame_no      = frame_number,
            timestamp     = timestamp,
            detections    = detections,
            trail_history = tracker.trail_history,
        )

        peak_count = max(peak_count, stats["crowd_count"])

        new_alerts   = alert_mgr.check(stats)
        total_alerts += len(new_alerts)

        active_alerts = [t for t in alert_mgr.ALERT_TYPES if alert_mgr.is_active(t)]

        annotated_frame = annotator.draw(
            frame             = frame,
            stats             = stats,
            active_alert_types = active_alerts,
        )

        for alert in new_alerts:
            if snapshot_saver:
                saved_path = snapshot_saver.save_snapshot(annotated_frame, alert, video_tag)
                alert["snapshot_path"] = saved_path
            if csv_log:
                csv_log.log_alert(alert)

        if video_out:
            video_out.write_frame(annotated_frame)

        if show_preview:
            display_frame = cv2.resize(annotated_frame, (preview_width, preview_height))
            cv2.imshow(window_title, display_frame)
            key = cv2.waitKey(1) & 0xFF
            if key == ord("q") or key == 27:
                logger.info("User stopped the preview.")
                break

        if frame_number % 100 == 0:
            elapsed  = time.time() - start_time
            percent  = (frame_number / total_frames * 100) if total_frames > 0 else 0
            fps_rate = frame_number / elapsed if elapsed > 0 else 0
            logger.info(
                f"  Frame {frame_number:>6}/{total_frames} ({percent:5.1f}%) | "
                f"People: {stats['crowd_count']:>3} | "
                f"Alerts: {total_alerts} | {fps_rate:.1f} fps"
            )

        frame_number += 1

    # Cleanup
    cap.release()
    if video_out:
        video_out.close()
    if csv_log:
        csv_log.close()
    if show_preview:
        cv2.destroyAllWindows()

    elapsed = time.time() - start_time
    summary = {
        "file":       os.path.basename(video_path),
        "frames":     frame_number,
        "time_sec":   elapsed,
        "fps_rate":   frame_number / elapsed if elapsed > 0 else 0,
        "alerts":     total_alerts,
        "peak_count": peak_count,
    }

    logger.info(
        f"  Done: {frame_number} frames in {elapsed:.1f}s "
        f"({summary['fps_rate']:.1f} fps) | "
        f"Peak: {peak_count} people | Alerts: {total_alerts}"
    )

    return summary


# -------------------------------------------------------
# Step 4: Main entry point
# -------------------------------------------------------

def main():
    """The main function — ties everything together."""
    args   = get_arguments()
    config = load_config(args.config)
    logger.info(f"Config: {args.config}")

    video_files = find_video_files(args.source)
    logger.info(f"Found {len(video_files)} video(s) to process:")
    for i, v in enumerate(video_files, 1):
        logger.info(f"  {i}. {os.path.basename(v)}")

    run_id = get_timestamp_string()

    if args.dry_run:
        output_folders = {}
        logger.info("Dry-run mode: no files will be saved.")
    else:
        output_folders = make_output_folders(config)

    all_summaries = []
    grand_start   = time.time()

    for index, video_path in enumerate(video_files, 1):
        summary = process_one_video(
            video_path     = video_path,
            config         = config,
            args           = args,
            output_folders = output_folders,
            run_id         = run_id,
            video_number   = index,
            total_videos   = len(video_files),
        )
        if summary:
            all_summaries.append(summary)

    grand_elapsed = time.time() - grand_start
    logger.info("=" * 55)
    logger.info(f"ALL DONE — {len(all_summaries)} video(s) in {grand_elapsed:.1f}s")
    logger.info("-" * 55)
    for s in all_summaries:
        logger.info(
            f"  {s['file']:<35} "
            f"peak={s['peak_count']:>3} people  "
            f"alerts={s['alerts']:>2}  "
            f"{s['fps_rate']:.1f} fps"
        )
    logger.info("=" * 55)

    if not args.dry_run:
        logger.info(f"Outputs saved to: {config.get('output_dir', 'data/output')}/")


if __name__ == "__main__":
    main()
