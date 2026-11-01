"""Move smoothly through saved poses, then always end at 'rest' (torque turns off when the script ends).

    python move_pose.py up rest        (3 s per move)
    python move_pose.py up rest 1      (faster: 1 s per move)
    python move_pose.py up rest 0.5    (fastest allowed; the servos top out around here at 5 V)
"""
import json
import logging
import sys
import time
from pathlib import Path

from so101_connect import connect

POSES = Path(__file__).with_name("poses.json")
SECONDS_PER_MOVE = 3.0
HZ = 50

poses = json.loads(POSES.read_text())
args = sys.argv[1:]
nums = [a for a in args if a.replace(".", "", 1).isdigit()]
if nums:
    SECONDS_PER_MOVE = max(float(nums[0]), 0.5)  # below ~0.5 s the servos can't keep up anyway; it only gets jerkier
seq = [a for a in args if a not in nums] or ["up", "rest"]
if seq[-1] != "rest":
    seq.append("rest")  # never end in the air: the arm drops when torque turns off
missing = [p for p in seq if p not in poses]
if missing:
    raise SystemExit(f"Not recorded yet: {missing}. Run record_pose.py first.")

robot = connect(max_relative_target=30.0)  # safety net: never command a joint >30 deg ahead of where it is
# hide LeRobot's "had to be clamped" spam; the cap still works, it just stops printing
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


print(f"{SECONDS_PER_MOVE:.1f} s per move: {' -> '.join(seq)}")
try:
    for name in seq:
        print(f"-> {name}")
        go(poses[name])
        time.sleep(0.5)
    print("Done, back at rest.")
finally:
    robot.disconnect()
