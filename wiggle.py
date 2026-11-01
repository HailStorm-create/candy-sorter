"""First-motion test for the SO-101 follower: opens and closes the gripper twice.

Run AFTER lerobot-calibrate. Start with the arm folded down, resting on the desk:
torque turns off when the script ends, and anything held up will drop.
"""
import time

from lerobot.robots.so_follower import SO101Follower, SO101FollowerConfig

PORT = "COM3"
ROBOT_ID = "snh_follower"  # must match --robot.id used in lerobot-calibrate

config = SO101FollowerConfig(port=PORT, id=ROBOT_ID, max_relative_target=10.0)  # max 10 units per step
robot = SO101Follower(config)
for attempt in range(3):  # Feetech buses occasionally drop one reply; retry the connect
    try:
        robot.connect(calibrate=False)
        break
    except ConnectionError as e:
        print(f"Connect attempt {attempt + 1} failed: {e}")
        if robot.bus.is_connected:
            robot.bus.disconnect(disable_torque=False)
        time.sleep(1)
else:
    raise SystemExit("Could not connect after 3 tries. Unplug power and tell Claude.")

try:
    start = robot.get_observation()
    hold = {k: v for k, v in start.items() if k.endswith(".pos")}  # every joint stays where it is
    print("Start positions:", {k: round(v, 1) for k, v in hold.items()})

    g0 = hold["gripper.pos"]
    target_open = min(g0 + 30, 95) if g0 < 50 else max(g0 - 30, 5)

    def move_gripper(target, seconds=1.5):
        end = time.time() + seconds
        while time.time() < end:
            robot.send_action({**hold, "gripper.pos": target})
            time.sleep(0.05)

    for i in range(2):
        print(f"Gripper move {i + 1}/2")
        move_gripper(target_open)
        move_gripper(g0)

    print("Done. Gripper back where it started.")
finally:
    robot.disconnect()
