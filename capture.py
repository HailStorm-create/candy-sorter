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


def open_camera():
    """Open the webcam and let it warm up. Keep it open to take many photos fast (pass it to grab)."""
    cap = cv2.VideoCapture(CAM_INDEX, cv2.CAP_DSHOW)
    cap.set(cv2.CAP_PROP_FOURCC, cv2.VideoWriter_fourcc(*"MJPG"))  # needed for 1080p over USB
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1920)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 1080)
    # first frames are black / still auto-exposing: keep reading for ~2 s
    t0 = time.time()
    while time.time() - t0 < 2:
        cap.read()
    return cap


def grab(cap=None):
    own = cap is None
    if own:
        cap = open_camera()
    try:
        frame = None
        for _ in range(5):  # skip frames buffered while the arm was moving: keep the newest
            ok, f = cap.read()
            if ok:
                frame = f
    finally:
        if own:
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
