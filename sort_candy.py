import json
import logging
import math
import msvcrt
import sys
import time
from datetime import datetime
from pathlib import Path

import cv2

from capture import OUT_DIR, Recorder, open_camera
from classify import CandyModel
from detect import crop, find_candies
from ik import fk, from_servo, ik, to_servo
from pixel_to_arm import pixel_to_arm
from so101_connect import connect

DROPS = {"kitkat": "bin", "mm": "bin", "skittles": "dump_back", "twix": "bin", "smarties": "bin",
         "trolli": "bin", "lifesavers": "bin", "nerdsgummyclusters": "bin", "haribo": "bin", "milkyway": "bin", "butterfinger": "bin"}
POSES_FILE = Path(__file__).with_name("poses.json")
PILES = {"kitkat": (1.0, 23.0), "mm": (1.0, -23.0), "skittles": (32.0, 0.0)}
REACH = (6.0, 31.0)
BAR_OPEN, PACK_OPEN = 45.0, 100.0
CLOSED = 0.0
OPEN_DROP = 60.0
DROP_ABOVE = 8.0
ROLL_SIGN = -1
MIN_CONF = 0.8
GRAB_Z, HOVER_Z, TRAVEL_Z, PILE_Z = 0.5, 5.0, 14.0, 6.0
BAR_ALONG, PACK_ALONG = 2.5, 4.0
GRIP_MARGIN = 1.0
STILL = 0.6
PACKS = {"mm", "skittles", "trolli", "lifesavers", "nerdsgummyclusters", "haribo"}
PACK_Z = -0.8
CLOSE_SECONDS = 0.5
MAX_PICKS = 40
HZ = 50
POSTS = OUT_DIR / "posts"
EMPTY_TABLE = OUT_DIR / "empty_up.jpg"
COLORS = {"kitkat": (40, 40, 220), "mm": (30, 60, 110), "skittles": (40, 180, 60)}


class Quit(Exception):
    pass


def check_quit():
    while msvcrt.kbhit():
        if msvcrt.getwch().lower() == "q":
            raise Quit


def long_axis_angle(c):
    box = cv2.boxPoints(((c["u"], c["v"]), c["size"], c["angle"]))
    edges = [(box[i], box[(i + 1) % 4]) for i in range(2)]
    a, b = max(edges, key=lambda e: math.dist(e[0], e[1]))
    (x0, y0), (x1, y1) = pixel_to_arm(*a), pixel_to_arm(*b)
    return math.degrees(math.atan2(y1 - y0, x1 - x0))


def wrist_roll_for(c):
    pan = math.degrees(math.atan2(c["y"], c["x"]))
    d = (long_axis_angle(c) - pan) % 180 - 90
    return ROLL_SIGN * d


def pack_middle(c):
    corners = [pixel_to_arm(*p) for p in cv2.boxPoints(((c["u"], c["v"]), c["size"], c["angle"]))]
    cx = sum(p[0] for p in corners) / 4
    cy = sum(p[1] for p in corners) / 4
    pan = math.degrees(math.atan2(cy, cx))
    rolls = []
    for a, b in ((corners[0], corners[2]), (corners[1], corners[3])):
        diag = math.degrees(math.atan2(b[1] - a[1], b[0] - a[0]))
        rolls.append((diag - pan + 90) % 180 - 90)
    return cx, cy, ROLL_SIGN * min(rolls, key=abs)


def steady_pitch(x, y, zs):
    for pitch in range(-90, -20, 10):
        try:
            for z in zs:
                to_servo(*ik(x, y, z, pitch))
            return pitch
        except ValueError:
            continue
    raise ValueError(f"can't go straight down at ({x:.1f}, {y:.1f})")


def pose(x, y, z, gripper, roll=0.0, tilt=False, pitch=None):
    for pitch in ([pitch] if pitch is not None else range(-90, -20, 10) if tilt else [-90]):
        try:
            return {**to_servo(*ik(x, y, z, pitch)), "wrist_roll.pos": roll, "gripper.pos": gripper}
        except ValueError:
            continue
    raise ValueError(f"can't reach ({x:.1f}, {y:.1f}, {z})")


def line(x, y, z0, z1, gripper, roll, pitch, seconds):
    n = max(int(seconds * HZ), 2)
    zs = [z0 + (z1 - z0) * (lambda a: a * a * (3 - 2 * a))(i / (n - 1)) for i in range(n)]
    return [pose(x, y, z, gripper, roll, pitch=pitch) for z in zs]


def opening_for(name):
    return PACK_OPEN if name in PACKS else BAR_OPEN


def drop(name, opening, px, py):
    saved = json.loads(POSES_FILE.read_text())
    if DROPS.get(name) in saved:
        spot = saved[DROPS[name]]
        bx, by, bz = fk(*from_servo(spot))
        try:
            above = pose(bx, by, bz + DROP_ABOVE, CLOSED, spot["wrist_roll.pos"], tilt=True)
        except ValueError:
            above = {**saved["up"], "shoulder_pan.pos": spot["shoulder_pan.pos"], "gripper.pos": CLOSED}
        return [
            (above, 1.0),
            ({**spot, "gripper.pos": CLOSED}, 0.7),
            ({**spot, "gripper.pos": OPEN_DROP}, 0.4),
            ({**spot, "gripper.pos": OPEN_DROP}, 0.2),
            ({**above, "gripper.pos": OPEN_DROP}, 0.6),
        ]
    return [
        (pose(px, py, TRAVEL_Z, CLOSED, 0.0, tilt=True), 0.7),
        (pose(px, py, PILE_Z, CLOSED, 0.0, tilt=True), 0.4),
        (pose(px, py, PILE_Z, opening, 0.0, tilt=True), 0.3),
        (pose(px, py, TRAVEL_Z, opening, 0.0, tilt=True), 0.4),
    ]


def plan(c, name):
    opening = opening_for(name)
    if name in PACKS:
        tx, ty, roll = pack_middle(c)
        z = PACK_Z
    else:
        tx, ty, roll = c["x"], c["y"], wrist_roll_for(c)
        z = GRAB_Z
    a = math.atan2(ty, tx) + math.radians(ROLL_SIGN * roll)
    along = PACK_ALONG if name in PACKS else BAR_ALONG
    x, y = tx + along * math.cos(a), ty + along * math.sin(a)
    px, py = PILES.get(name, PILES["kitkat"])
    p = steady_pitch(x, y, (HOVER_Z, z))
    grabbed = pose(x, y, z, CLOSED, roll, pitch=p)
    return {
        "grab": [
            (pose(x, y, HOVER_Z, opening, roll, pitch=p), 0.9),
            (line(x, y, HOVER_Z, z, opening, roll, p, 0.5), 0),
            (grabbed, CLOSE_SECONDS),
            (grabbed, 0.1),
        ],
        "lift": [
            (line(x, y, z, HOVER_Z, CLOSED, roll, p, 0.4), 0),
        ],
        "carry": [
            (pose(x, y, TRAVEL_Z, CLOSED, roll, tilt=True), 0.4),
            *drop(name, opening, px, py),
        ],
        "miss": [(pose(x, y, z, opening, roll, pitch=p), 0.3), (line(x, y, z, HOVER_Z, opening, roll, p, 0.4), 0)],
    }


def look(rec, model, table=None):
    before, _ = find_candies(rec.frame(), reach=REACH, empty=table)
    img = rec.frame(0.4)
    found, _ = find_candies(img, reach=REACH, empty=table)
    found = [c for c in found if any(math.dist((c["x"], c["y"]), (b["x"], b["y"])) < STILL for b in before)]
    out, todo, marks = img.copy(), [], []
    for c in found:
        name, conf = model.predict(crop(img, c))
        if name == "nothing":
            continue
        bx, by, bw, bh = c["box"]
        color = COLORS.get(name, (0, 200, 0)) if conf >= MIN_CONF else (150, 150, 150)
        cv2.rectangle(out, (bx, by), (bx + bw, by + bh), color, 3)
        cv2.putText(out, f"{name} {conf:.0%}", (bx, by - 8), 0, 0.9, color, 2)
        marks.append(((bx, by, bw, bh), f"{name} {conf:.0%}", color))
        if conf >= MIN_CONF:
            todo.append((c, name, conf))
        else:
            print(f"   not sure about the one at ({c['x']:.1f}, {c['y']:.1f}): {name} {conf:.0%}, leaving it. Touching another candy? Spread them 3 cm apart")
    rec.marks = marks
    POSTS.mkdir(parents=True, exist_ok=True)
    cv2.imwrite(str(POSTS / f"sort_{datetime.now().strftime('%H%M%S')}.jpg"), out)
    return sorted(todo, key=lambda t: math.hypot(t[0]["x"], t[0]["y"]))


if __name__ == "__main__":
    model = CandyModel()
    poses = json.loads(Path(__file__).with_name("poses.json").read_text())
    robot = connect(max_relative_target=30.0)
    logging.getLogger().addFilter(lambda r: "had to be clamped" not in r.getMessage())
    stopping = False

    def current():
        return {k: v for k, v in robot.get_observation().items() if k.endswith(".pos")}

    def squeeze():
        return abs(int(robot.bus.read("Present_Load", "gripper", normalize=False)))

    def go(target, seconds=1.5):
        if isinstance(target, list):
            for t in target:
                if not stopping:
                    check_quit()
                robot.send_action(t)
                time.sleep(1 / HZ)
            return
        start = current()
        steps = max(int(seconds * HZ), 1)
        for i in range(1, steps + 1):
            if not stopping:
                check_quit()
            a = i / steps
            s = a * a * (3 - 2 * a)
            robot.send_action({k: start[k] + (target[k] - start[k]) * s for k in start})
            time.sleep(1 / HZ)
        for _ in range(HZ // 6):
            robot.send_action(target)
            time.sleep(1 / HZ)

    cam = open_camera()
    POSTS.mkdir(parents=True, exist_ok=True)
    video = POSTS / f"sort_{datetime.now().strftime('%H%M%S')}.mp4"
    rec = Recorder(cam, video)
    rec.start()
    sorted_count = {}
    misses = 0
    t0 = time.time()
    watch = "--watch" in sys.argv
    try:
        print("Press q any time to stop safely." + (" Watching: slide candy in whenever." if watch else ""))
        go({**poses["up"], "gripper.pos": CLOSED}, 2.0)
        time.sleep(0.5)
        empty = current()["gripper.pos"]
        empty_load = squeeze()
        print(f"   empty gripper: position {empty:.1f}, load {empty_load}")
        if "--empty" in sys.argv or not EMPTY_TABLE.exists():
            input("Clear all candy off the table for one empty photo, then press ENTER ")
            cv2.imwrite(str(EMPTY_TABLE), rec.frame(1.0))
            print(f"   saved {EMPTY_TABLE}")
        table = cv2.imread(str(EMPTY_TABLE))
        picks = 0
        errors = 0
        while watch or picks < MAX_PICKS:
            rec.status = f"sorted {sum(sorted_count.values())} | watching"
            todo = look(rec, model, table)
            if "--look" in sys.argv:
                print(f"would sort: {[(n, f'{p:.0%}', round(c['x'], 1), round(c['y'], 1)) for c, n, p in todo]}")
                break
            job = None
            for c, name, conf in todo:
                try:
                    job = (c, name, conf, plan(c, name))
                    break
                except ValueError as e:
                    print(f"   can't grab the {name} at ({c['x']:.1f}, {c['y']:.1f}): {e}")
            if job is None:
                if not watch:
                    break
                rec.marks = []
                for _ in range(10):
                    check_quit()
                    time.sleep(0.1)
                continue
            try:
                picks += 1
                c, name, conf, moves = job
                rec.marks = [(c["box"], f"{name} {conf:.0%}", COLORS.get(name, (0, 200, 0)))]
                rec.status = f"sorted {sum(sorted_count.values())} | {name} -> pile"
                print(f"-> {name} ({conf:.0%}) at ({c['x']:.1f}, {c['y']:.1f})")
                for target, seconds in moves["grab"]:
                    go(target, seconds)
                grip = current()["gripper.pos"]
                if grip < empty + GRIP_MARGIN:
                    print(f"   missed: jaws closed all the way (gripper {grip:.1f}). Backing off and looking again")
                    misses += 1
                    for target, seconds in moves["miss"]:
                        go(target, seconds)
                else:
                    for target, seconds in moves["lift"]:
                        go(target, seconds)
                    time.sleep(0.3)
                    lifted, load = current()["gripper.pos"], squeeze()
                    if lifted < empty + GRIP_MARGIN:
                        print(f"   not holding it (position {lifted:.1f}, load {load}). Opening and looking again")
                        misses += 1
                        go({**current(), "gripper.pos": opening_for(name)}, 0.4)
                    else:
                        print(f"   holding it (position {lifted:.1f}, load {load}) -> {DROPS.get(name, name + ' pile')}")
                        for target, seconds in moves["carry"]:
                            go(target, seconds)
                        sorted_count[name] = sorted_count.get(name, 0) + 1
                go(poses["up"], 1.2)
                errors = 0
            except (RuntimeError, ConnectionError) as e:
                errors += 1
                print(f"   servo hiccup ({e}), parking and carrying on")
                if errors >= 4:
                    raise
                time.sleep(1.0)
                go(poses["up"], 2.0)
        print(f"Done: {sorted_count}, {misses} missed grabs, {time.time() - t0:.0f} s")
    except Quit:
        stopping = True
        print("\nStopping: going back to rest.")
        go(poses["up"], 2.0)
    finally:
        stopping = True
        try:
            go(poses["rest"], 2.0)
        finally:
            rec.stop()
            print(f"Video saved: {rec.path}")
            cam.release()
            robot.disconnect()
