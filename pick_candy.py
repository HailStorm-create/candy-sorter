import json
import logging
import math
import sys
import time
from pathlib import Path

import cv2

from capture import OUT_DIR, grab, open_camera
from ik import ik, to_servo
from pixel_to_arm import pixel_to_arm
from so101_connect import connect

GRAB_Z = 0.5
HOVER_Z = 5.0
DROP_Z = 11.0
GRAB_ALONG, GRAB_SIDE = 1.5, 0.0
TRAVEL_Z = 14.0
OPEN, CLOSED = 35.0, 0.0
CLOSE_SECONDS = 1.0
SPEED = 1.0
REACH = (6.0, 28.0)
HZ = 50

poses = json.loads(Path(__file__).with_name("poses.json").read_text())


def look(cam=None):
    img = grab(cam)
    hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)

    tape, tape_px = None, None
    mask = cv2.inRange(hsv, (5, 40, 120), (25, 200, 255))
    for c in sorted(cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)[0], key=cv2.contourArea)[::-1]:
        if cv2.contourArea(c) < 6000:
            break
        (u, v), rad = cv2.minEnclosingCircle(c)
        x, y = pixel_to_arm(u, v)
        if x > 5 and math.hypot(x, y) < 26:
            tape, tape_px = (x, y), (u, v, rad)
            break

    mask = cv2.inRange(hsv, (0, 110, 70), (180, 255, 255))
    mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN, cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (5, 5)))
    candies, far = [], []
    for c in cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)[0]:
        if not 300 < cv2.contourArea(c) < 5000:
            continue
        m = cv2.moments(c)
        u, v = m["m10"] / m["m00"], m["m01"] / m["m00"]
        if tape_px and math.hypot(u - tape_px[0], v - tape_px[1]) < tape_px[2] * 1.15:
            continue
        x, y = pixel_to_arm(u, v)
        if x < 5:
            continue
        if REACH[0] < math.hypot(x, y) < REACH[1]:
            candies.append((x, y, u, v))
        elif math.hypot(x, y) < 31:
            far.append((x, y, u, v))

    out = img.copy()
    if tape_px:
        cv2.circle(out, (int(tape_px[0]), int(tape_px[1])), int(tape_px[2]), (255, 0, 255), 3)
        cv2.putText(out, f"tape ({tape[0]:.1f},{tape[1]:.1f})", (int(tape_px[0]) - 80, int(tape_px[1])), 0, 0.8, (255, 0, 255), 2)
    for color, found in (((0, 200, 0), candies), ((0, 0, 255), far)):
        for x, y, u, v in found:
            cv2.circle(out, (int(u), int(v)), 30, color, 3)
            cv2.putText(out, f"({x:.1f},{y:.1f})", (int(u) + 32, int(v)), 0, 0.7, color, 2)
    OUT_DIR.mkdir(exist_ok=True)
    cv2.imwrite(str(OUT_DIR / "look.jpg"), out)
    if far:
        print(f"   {len(far)} candy out of reach (red in look.jpg): move within {REACH[1]:.0f} cm of the base")
    return candies, tape


if __name__ == "__main__":
    robot = connect(max_relative_target=30.0)
    logging.getLogger().addFilter(lambda r: "had to be clamped" not in r.getMessage())

    def current():
        return {k: v for k, v in robot.get_observation().items() if k.endswith(".pos")}

    def go(target, seconds=1.5):
        start = current()
        steps = int(seconds * HZ)
        for i in range(1, steps + 1):
            a = i / steps
            s = a * a * (3 - 2 * a)
            robot.send_action({k: start[k] + (target[k] - start[k]) * s for k in start})
            time.sleep(1 / HZ)
        for _ in range(HZ // 6):
            robot.send_action(target)
            time.sleep(1 / HZ)

    def at(x, y, z, gripper):
        return {**to_servo(*ik(x, y, z)), "wrist_roll.pos": 0.0, "gripper.pos": gripper}

    def high(x, y, z, gripper):
        for pitch in range(-90, -20, 10):
            try:
                return {**to_servo(*ik(x, y, z, pitch)), "wrist_roll.pos": 0.0, "gripper.pos": gripper}
            except ValueError:
                continue
        raise ValueError(f"can't get up to {z} cm at ({x:.1f}, {y:.1f})")

    def plan(x, y, tape):
        a = math.atan2(y, x)
        x += GRAB_ALONG * math.cos(a) - GRAB_SIDE * math.sin(a)
        y += GRAB_ALONG * math.sin(a) + GRAB_SIDE * math.cos(a)
        grabbed = at(x, y, GRAB_Z, CLOSED)
        return [
            (high(x, y, TRAVEL_Z, OPEN), 1.0),
            (at(x, y, HOVER_Z, OPEN), 0.6),
            (at(x, y, GRAB_Z, OPEN), 0.6),
            (grabbed, CLOSE_SECONDS),
            (grabbed, 0.3),
            (at(x, y, HOVER_Z, CLOSED), 0.5),
            (high(x, y, TRAVEL_Z, CLOSED), 0.5),
            (high(*tape, TRAVEL_Z, CLOSED), 0.8),
            (high(*tape, DROP_Z, CLOSED), 0.4),
            (high(*tape, DROP_Z, OPEN), 0.4),
            (high(*tape, TRAVEL_Z, OPEN), 0.4),
        ]

    cam = open_camera()
    try:
        go(poses["up"], 2.0)
        if "--look" in sys.argv:
            candies, tape = look(cam)
            print(f"tape roll: {tape}")
            print(f"{len(candies)} candies: {[(round(x, 1), round(y, 1)) for x, y, _, _ in candies]}")
            print("Saved photos/look.jpg")
        else:
            done, t_start = 0, time.time()
            while True:
                candies, tape = look(cam)
                if tape is None:
                    raise SystemExit("Can't see the tape roll within reach. Put it 10-20 cm from the base.")
                jobs = []
                for x, y, _, _ in sorted(candies, key=lambda c: math.hypot(c[0], c[1])):
                    try:
                        jobs.append((x, y, plan(x, y, tape)))
                    except ValueError as e:
                        print(f"   can't grab ({x:.1f}, {y:.1f}): {e}")
                if not jobs:
                    print(f"No grabbable candy left. {done} in the tape in {time.time() - t_start:.0f} s.")
                    break
                for x, y, moves in jobs:
                    print(f"-> candy at ({x:.1f}, {y:.1f})")
                    for target, seconds in moves:
                        go(target, seconds * SPEED)
                    done += 1
                go(poses["up"], 1.2)
        go(poses["rest"], 2.0)
    finally:
        cam.release()
        robot.disconnect()
