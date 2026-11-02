import json
import logging
import sys
import time
from datetime import datetime
from pathlib import Path

import cv2

from capture import OUT_DIR, grab, open_camera
from detect import WORK_AREA, crop, find_candies
from so101_connect import connect

DATASET = Path(__file__).with_name("dataset")
POSTS = OUT_DIR / "posts"
HZ = 50

if len(sys.argv) < 2:
    raise SystemExit("python collect.py <candy_type>")
label = sys.argv[1].lower()
poses = json.loads(Path(__file__).with_name("poses.json").read_text())
robot = connect(max_relative_target=30.0)
logging.getLogger().addFilter(lambda r: "had to be clamped" not in r.getMessage())


def current():
    return {k: v for k, v in robot.get_observation().items() if k.endswith(".pos")}


def go(target, seconds=2.0):
    start = current()
    steps = int(seconds * HZ)
    for i in range(1, steps + 1):
        a = i / steps
        s = a * a * (3 - 2 * a)
        robot.send_action({k: start[k] + (target[k] - start[k]) * s for k in start})
        time.sleep(1 / HZ)
    for _ in range(HZ // 2):
        robot.send_action(target)
        time.sleep(1 / HZ)


cam = open_camera()
try:
    go(poses["up"])
    out = DATASET / label
    out.mkdir(parents=True, exist_ok=True)
    total = len(list(out.glob("*.jpg")))
    while True:
        if input(f"[{label}: {total} crops] spread them out, ENTER to shoot, q to stop: ").strip().lower() == "q":
            break
        img = grab(cam)
        found, _ = find_candies(img, reach=WORK_AREA)
        stamp = datetime.now().strftime("%H%M%S")
        preview = img.copy()
        for i, c in enumerate(found):
            cv2.imwrite(str(out / f"{stamp}_{i}.jpg"), crop(img, c))
            bx, by, bw, bh = c["box"]
            cv2.rectangle(preview, (bx, by), (bx + bw, by + bh), (0, 200, 0), 3)
        cv2.imwrite(str(OUT_DIR / "collect_preview.jpg"), preview)
        POSTS.mkdir(parents=True, exist_ok=True)
        cv2.imwrite(str(POSTS / f"{label}_{stamp}.jpg"), img)
        cv2.imwrite(str(POSTS / f"{label}_{stamp}_boxes.jpg"), preview)
        total += len(found)
        print(f"   {len(found)} found and saved. Check photos/collect_preview.jpg")
    go(poses["rest"])
finally:
    cam.release()
    robot.disconnect()
