"""Grab one frame from the overhead USB webcam and save it.

    python capture.py              -> photos/2026-10-31_153012.jpg
    python capture.py crosses      -> photos/crosses.jpg
"""
import sys
import time
from datetime import datetime
from pathlib import Path

import cv2

CAM_INDEX = 0  # USB webcam (1 is the laptop's built-in one)
OUT_DIR = Path(__file__).with_name("photos")


def grab():
    cap = cv2.VideoCapture(CAM_INDEX, cv2.CAP_DSHOW)
    cap.set(cv2.CAP_PROP_FOURCC, cv2.VideoWriter_fourcc(*"MJPG"))  # needed for 1080p over USB
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1920)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 1080)
    try:
        # first frames are black / still auto-exposing: keep reading for ~2 s, keep the last one
        frame, t0 = None, time.time()
        while time.time() - t0 < 2:
            ok, f = cap.read()
            if ok:
                frame = f
    finally:
        cap.release()
    if frame is None or frame.mean() < 5:
        raise SystemExit("No picture. Is another app using the webcam?")
    return frame


if __name__ == "__main__":
    name = sys.argv[1] if len(sys.argv) > 1 else datetime.now().strftime("%Y-%m-%d_%H%M%S")
    OUT_DIR.mkdir(exist_ok=True)
    path = OUT_DIR / f"{name}.jpg"
    cv2.imwrite(str(path), grab())
    print(f"Saved {path}")
