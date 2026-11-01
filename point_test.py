"""Real-arm IK test: hover the closed gripper 2 cm above each tape cross, then go back to rest.

    python point_test.py          all crosses: A B C D E
    python point_test.py E        just E (the honest check: it was never touched)

Watch from the side: the jaw tips should stop ~2 cm straight above each dot (3 s pause there).
"""
import json
import logging
import sys
import time
from pathlib import Path

from ik import fk, from_servo, ik, to_servo
from so101_connect import connect

# Cross centers in the ARM frame (cm; origin under the pan axis, x forward, y left).
# A-D: fk() of the touch_ poses. E: estimated from the tape layout, never touched.
CROSSES = {"A": (9.7, 11.2), "B": (9.7, -14.2), "C": (18.8, 6.6), "D": (17.9, -8.6), "E": (14.0, -1.3)}
HIGH = 6.0  # cm: travel height between crosses
LOW = 2.0  # cm: test height above the dot
HAND = {"wrist_roll.pos": 0.0, "gripper.pos": 5.0}  # roll as in the touch poses, gripper closed
SECONDS_PER_MOVE = 2.0
HZ = 50

poses = json.loads(Path(__file__).with_name("poses.json").read_text())
names = [a.upper() for a in sys.argv[1:]] or list(CROSSES)

# plan every target before anything moves: unreachable or out-of-range stops the script here
plan = []
for n in names:
    x, y = CROSSES[n]
    high = {**to_servo(*ik(x, y, HIGH)), **HAND}
    low = {**to_servo(*ik(x, y, LOW)), **HAND}
    plan += [(f"{n} high", high), (f"{n} low", low), (f"{n} high", high)]

robot = connect(max_relative_target=30.0)  # safety net, same as move_pose.py
logging.getLogger().addFilter(lambda r: "had to be clamped" not in r.getMessage())


def current():
    return {k: v for k, v in robot.get_observation().items() if k.endswith(".pos")}


def go(target, seconds=SECONDS_PER_MOVE):
    start = current()
    steps = int(seconds * HZ)
    for i in range(1, steps + 1):
        a = i / steps
        s = a * a * (3 - 2 * a)  # smoothstep: ease in, ease out
        robot.send_action({k: start[k] + (target[k] - start[k]) * s for k in start})
        time.sleep(1 / HZ)
    for _ in range(HZ // 2):  # let it settle on the target
        robot.send_action(target)
        time.sleep(1 / HZ)


try:
    print("-> up")
    go(poses["up"])
    for label, target in plan:
        print(f"-> {label}")
        go(target)
        if label.endswith("low"):
            time.sleep(3)  # look from the side: how far is the tip from the dot?
            # did the servos actually get there? (gravity sag shows up here)
            now = current()
            lag = {k.split(".")[0]: round(now[k] - target[k], 1) for k in target if k in now and "gripper" not in k}
            x, y, z = fk(*from_servo(now))
            tx, ty = CROSSES[label[0]]
            print(f"   servo miss (deg): {lag}")
            print(f"   tip from the servos' real angles: ({x:.1f}, {y:.1f}, {z:.1f})  aimed ({tx}, {ty}, {LOW})")
    print("-> up -> rest")
    go(poses["up"])
    go(poses["rest"])
finally:
    robot.disconnect()
