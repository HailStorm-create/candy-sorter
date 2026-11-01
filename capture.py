import sys
import time
from datetime import datetime
from pathlib import Path

import cv2

CAM_INDEX = 0
OUT_DIR = Path(__file__).with_name("photos")


def open_camera():
    cap = cv2.VideoCapture(CAM_INDEX, cv2.CAP_DSHOW)
    cap.set(cv2.CAP_PROP_FOURCC, cv2.VideoWriter_fourcc(*"MJPG"))
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1920)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 1080)
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
        for _ in range(5):
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
