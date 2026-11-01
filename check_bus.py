"""Ping every servo and read its voltage/temperature. Touches nothing: torque stays off."""
import time

from lerobot.motors import Motor, MotorNormMode
from lerobot.motors.feetech import FeetechMotorsBus

names = ["shoulder_pan", "shoulder_lift", "elbow_flex", "wrist_flex", "wrist_roll", "gripper"]
bus = FeetechMotorsBus(
    port="COM3",
    motors={n: Motor(i + 1, "sts3215", MotorNormMode.RANGE_M100_100) for i, n in enumerate(names)},
)
bus.connect(handshake=False)
try:
    for rnd in range(3):
        print(f"--- round {rnd + 1} ---")
        for n in names:
            model = bus.ping(n, num_retry=2)
            if model is None:
                print(f"{bus.motors[n].id} {n:14s} NO ANSWER")
                continue
            v = bus.read("Present_Voltage", n, normalize=False, num_retry=2) / 10
            t = bus.read("Present_Temperature", n, normalize=False, num_retry=2)
            print(f"{bus.motors[n].id} {n:14s} ok   {v:.1f} V   {t} C")
        time.sleep(0.5)
finally:
    bus.disconnect(disable_torque=False)
