"""Inverse kinematics for the SO-101: table point (x, y, z) in cm -> joint angles, gripper pointing straight down.

    python ik.py      runs the self-test: fk(ik(p)) should land back on p
"""
import math

# cm, from so101_new_calib.urdf. Swap in your ruler numbers if they're off by more than ~3 mm.
L1 = 11.6  # shoulder -> elbow
L2 = 13.5  # elbow -> wrist
L3 = 16.05  # wrist -> jaw tips
SHOULDER_R = 3.0  # shoulder axis, forward of the pan axis
SHOULDER_Z = 11.7  # shoulder axis, above the desk

# math angle -> servo degrees: servo = ZERO + SIGN * math. Fitted 2026-10-31 from the touch_A..D poses.
SERVO_ZERO = {"shoulder_pan": 11.0, "shoulder_lift": 86.6, "elbow_flex": -66.2, "wrist_flex": -15.2}
SERVO_SIGN = {"shoulder_pan": 1, "shoulder_lift": -1, "elbow_flex": -1, "wrist_flex": -1}
# +/- deg the servo may go, from the calibration ranges minus a 1 deg margin
SERVO_LIMIT = {"shoulder_pan": 103.9, "shoulder_lift": 86.3, "elbow_flex": 96.7, "wrist_flex": 88.1}
JOINTS = list(SERVO_ZERO)


def ik(x, y, z, pitch=-90.0):
    """(x, y, z) in cm -> (pan, shoulder, elbow, wrist) math angles in degrees.

    pitch: gripper angle from horizontal, -90 = pointing straight down (default). Tilting it (e.g. -60) reaches higher/farther.
    """
    p = math.radians(pitch)
    # 1. pan: turn the base to face the target
    pan = math.atan2(y, x)
    # 2. r: how far out the target is from the pan axis
    r = math.hypot(x, y)
    # 3. dx, dz: from the shoulder to the wrist (the wrist is L3 back along the gripper from the target;
    #    for pitch -90 that's straight above it)
    dx = (r - L3 * math.cos(p)) - SHOULDER_R
    dz = (z - L3 * math.sin(p)) - SHOULDER_Z
    # 4. d: straight line shoulder -> wrist
    d = math.hypot(dx, dz)
    if not abs(L1 - L2) < d < L1 + L2:
        raise ValueError(f"({x}, {y}, {z}) out of reach: shoulder->wrist {d:.1f} cm, arm spans {L1 + L2:.1f}")
    # 5. theta: inside angle at the elbow (law of cosines, opposite side = d)
    theta = math.acos((L1**2 + L2**2 - d**2) / (2 * L1 * L2))
    # 6. shoulder = tilt of the line d + inside angle at the shoulder (opposite side = L2)
    phi = math.atan2(dz, dx)
    alpha = math.acos((L1**2 + d**2 - L2**2) / (2 * L1 * d))
    shoulder = phi + alpha  # + alpha = elbow-up
    # 7. elbow: how far the forearm bends down from the upper arm's line
    elbow = -(math.pi - theta)
    # 8. wrist: whatever makes the gripper end up at the pitch asked for (-90 = straight down)
    wrist = p - (shoulder + elbow)
    return tuple(math.degrees(a) for a in (pan, shoulder, elbow, wrist))


def fk(pan, shoulder, elbow, wrist):
    """Math angles in degrees -> fingertip (x, y, z) in cm. Used to test ik()."""
    # start at the shoulder, in the side view (r, z)
    r, z = SHOULDER_R, SHOULDER_Z
    # walk each link; every joint adds its angle to the ones before it
    a = 0.0
    for length, joint in ((L1, shoulder), (L2, elbow), (L3, wrist)):
        a += math.radians(joint)
        r += length * math.cos(a)
        z += length * math.sin(a)
    # side view r -> table x, y
    p = math.radians(pan)
    return r * math.cos(p), r * math.sin(p), z


def to_servo(pan, shoulder, elbow, wrist):
    """Math angles -> servo degrees, as {"shoulder_pan.pos": ...}. Raises ValueError past a joint's range."""
    out = {}
    for j, a in zip(JOINTS, (pan, shoulder, elbow, wrist)):
        s = SERVO_ZERO[j] + SERVO_SIGN[j] * a
        if abs(s) > SERVO_LIMIT[j]:
            raise ValueError(f"{j} would need {s:.1f} deg, limit is +/-{SERVO_LIMIT[j]}")
        out[f"{j}.pos"] = s
    return out


def from_servo(pose):
    """Servo degrees (a poses.json entry or robot observation) -> math angles, for fk()."""
    return tuple(SERVO_SIGN[j] * (pose[f"{j}.pos"] - SERVO_ZERO[j]) for j in JOINTS)


if __name__ == "__main__":
    print("ik(25, 0, 0) =", tuple(round(a, 1) for a in ik(25, 0, 0)), " expect about (0, 40.3, -53.8, -76.5)")

    worst, tested = 0.0, 0
    for x in range(10, 31, 5):
        for y in range(-15, 16, 5):
            for z in (0, 5):
                try:
                    angles = ik(x, y, z)
                except ValueError as e:
                    print("  skip:", e)
                    continue
                worst = max(worst, math.dist(fk(*angles), (x, y, z)))
                tested += 1
    print(f"{tested} targets, worst fk(ik(p)) error: {worst:.6f} cm  (pass: < 0.01)")

    worst = 0.0
    for pitch in (-90, -70, -50, -30):
        for x, y, z in ((12, 5, 8), (18, -6, 10), (15, 10, 14)):
            worst = max(worst, math.dist(fk(*ik(x, y, z, pitch)), (x, y, z)))
    print(f"tilted gripper: worst fk(ik(p, pitch)) error: {worst:.6f} cm")
