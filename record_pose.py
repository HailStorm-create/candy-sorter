"""Record named poses by hand. Torque is OFF: move the arm yourself, press ENTER, it saves to poses.json.

    python record_pose.py
"""
import json
from pathlib import Path

from so101_connect import connect

POSES = Path(__file__).with_name("poses.json")

robot = connect(max_relative_target=None)
robot.bus.disable_torque()  # limp, so you can move it by hand
poses = json.loads(POSES.read_text()) if POSES.exists() else {}

try:
    while True:
        name = input("\nPose name to record (e.g. rest, up), or just ENTER to quit: ").strip()
        if not name:
            break
        input(f"Hold the arm in '{name}' (it will want to fall), then press ENTER... ")
        obs = robot.get_observation()
        pos = {k: round(v, 1) for k, v in obs.items() if k.endswith(".pos")}
        poses[name] = pos
        POSES.write_text(json.dumps(poses, indent=2))
        print(f"Saved '{name}': {pos}")
finally:
    robot.disconnect()
    print(f"\nAll poses in {POSES.name}: {list(poses)}")
