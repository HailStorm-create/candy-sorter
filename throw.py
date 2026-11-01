"""Throw a candy: wind up -> full-speed swing -> gripper opens mid-swing -> glide back to rest.

Record these with record_pose.py first:
  windup  - arm cocked back, gripper CLOSED on the candy
  follow  - where the swing ends, gripper WIDE OPEN
Then:
  python throw.py         release 15% of the way through the swing (the gripper takes ~0.1 s to open)
  python throw.py 0.45    release earlier (candy flies higher)
  python throw.py 0.75    release later (candy flies flatter / lower)

Grab first, then throw: list pickup poses before the number, e.g.
  python throw.py above_bowl grab lift
"""
import json
import sys
import time
from pathlib import Path

from so101_connect import connect

poses = json.loads(Path(__file__).with_name("poses.json").read_text())
args = sys.argv[1:]
nums = [a for a in args if a.replace(".", "", 1).isdigit()]
pickup = [a for a in args if a not in nums]  # poses played (1 s each) before the windup
missing = [p for p in ["rest", "windup", "follow", *pickup] if p not in poses]
if missing:
    raise SystemExit(f"Record these first with record_pose.py: {missing}")
rest, windup, follow = poses["rest"], poses["windup"], poses["follow"]
release_at = min(max(float(nums[0]) if nums else 0.15, 0.05), 0.95)

# the joint that moves the most between windup and follow times the release
swing = max((k for k in windup if k != "gripper.pos"), key=lambda k: abs(follow[k] - windup[k]))
start, end = windup[swing], follow[swing]
print(f"Swing joint: {swing} ({start:.0f} -> {end:.0f}), releasing at {release_at:.0%}")

# No relative cap here: the swing has to go full speed. Both targets are poses you set by hand.
robot = connect(max_relative_target=None, p_gain=32)  # snappier servos for the swing


def now():
    return {k: v for k, v in robot.get_observation().items() if k.endswith(".pos")}


def glide(target, seconds):
    s0 = now()
    steps = int(seconds * 50)
    for i in range(1, steps + 1):
        a = i / steps
        e = a * a * (3 - 2 * a)
        robot.send_action({k: s0[k] + (target[k] - s0[k]) * e for k in s0})
        time.sleep(0.02)


try:
    for name in pickup:
        print(f"-> {name}")
        glide(poses[name], 1.0)
        time.sleep(0.3)
    print("-> windup")
    glide(windup, 1.5)
    time.sleep(0.6)

    robot.send_action({**follow, "gripper.pos": windup["gripper.pos"]})  # swing, still holding
    t0, released = time.time(), False
    while time.time() - t0 < 1.5:
        frac = (now()[swing] - start) / (end - start)
        if not released and frac >= release_at:
            robot.send_action(follow)  # same targets, gripper opens
            released = True
            print(f"Released at {frac:.0%} ({(time.time() - t0) * 1000:.0f} ms into the swing)")
        if released and frac > 0.97:
            break
    if not released:
        robot.send_action(follow)
        print("Swing never reached the release point; opened at the end.")

    time.sleep(0.6)
    glide(rest, 2.0)
    print("Back at rest.")
finally:
    robot.disconnect()
