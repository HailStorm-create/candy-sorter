import json
import math

import cv2
import numpy as np

from pixel_to_arm import CALIB, pixel_to_arm

REACH = (6.0, 28.0)
MIN_AREA, MAX_AREA = 2000, 90000
MIN_SAT, MAX_VAL = 70, 90
EDGE = 4
BASE_CLEAR = 6.5
LINE_PX = 15
MIN_WIDTH_PX = 25
SOLID = 0.5
STAND_OUT = 25
WORK_AREA = (6.0, 32.0)


def base_area(h, w, _cache={}):
    if (h, w) not in _cache:
        H = np.array(json.loads(CALIB.read_text())["H"])
        uu, vv = np.meshgrid(np.arange(w, dtype=np.float32), np.arange(h, dtype=np.float32))
        xy = cv2.perspectiveTransform(np.dstack([uu, vv]).reshape(-1, 1, 2), H).reshape(h, w, 2)
        _cache[(h, w)] = np.hypot(xy[..., 0], xy[..., 1]) < BASE_CLEAR
    return _cache[(h, w)]


def find_candies(img, reach=REACH, empty=None):
    h, w = img.shape[:2]
    blur = cv2.GaussianBlur(img, (7, 7), 0)
    hsv = cv2.cvtColor(blur, cv2.COLOR_BGR2HSV)
    mask = cv2.bitwise_or(cv2.inRange(hsv[..., 1], MIN_SAT, 255), cv2.inRange(hsv[..., 2], 0, MAX_VAL))
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    bg = cv2.resize(cv2.medianBlur(cv2.resize(gray, None, fx=0.25, fy=0.25), 31), (w, h))
    mask = cv2.bitwise_or(mask, ((cv2.absdiff(gray, bg) > STAND_OUT) * 255).astype(np.uint8))
    if empty is not None:
        mask[cv2.absdiff(blur, cv2.GaussianBlur(empty, (7, 7), 0)).max(axis=2) <= STAND_OUT] = 0
    mask[base_area(h, w)] = 0
    mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN, cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (5, 5)))
    mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (21, 21)))
    mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN, cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (LINE_PX, LINE_PX)))
    found = []
    for c in cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)[0]:
        area = cv2.contourArea(c)
        if not MIN_AREA < area < MAX_AREA:
            continue
        bx, by, bw, bh = cv2.boundingRect(c)
        if bx <= EDGE or by <= EDGE or bx + bw >= w - EDGE or by + bh >= h - EDGE:
            continue
        (u, v), size, angle = cv2.minAreaRect(c)
        if min(size) < MIN_WIDTH_PX or area < SOLID * size[0] * size[1]:
            continue
        x, y = pixel_to_arm(u, v)
        if x < 5 or (reach and not reach[0] < math.hypot(x, y) < reach[1]):
            continue
        found.append({"u": u, "v": v, "x": x, "y": y, "box": (bx, by, bw, bh), "size": size, "angle": angle})
    return found, mask


def crop(img, c, pad=1.3, min_side=96):
    _, _, bw, bh = c["box"]
    side = int(max(bw, bh, min_side) * pad)
    u0 = max(int(c["u"]) - side // 2, 0)
    v0 = max(int(c["v"]) - side // 2, 0)
    return img[v0:v0 + side, u0:u0 + side]
