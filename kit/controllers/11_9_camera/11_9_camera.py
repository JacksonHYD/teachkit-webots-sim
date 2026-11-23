#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""11.9 大场景摄像头端：识别传送带上的工件颜色，供机械臂确认。"""
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'common'))
import cv2
import numpy as np
from controller import Robot
import robokit_common as C

robot = Robot()
ts = int(robot.getBasicTimeStep())
cam = robot.getDevice("camera")
cam.enable(ts)
preview = '11.9 Conveyor Camera'
cv2.namedWindow(preview, cv2.WINDOW_NORMAL)
cv2.resizeWindow(preview, 480, 360)

while robot.step(ts) != -1:
    raw = cam.getImage()
    if raw is None:
        continue
    img = np.frombuffer(raw, np.uint8).reshape((cam.getHeight(), cam.getWidth(), 4))
    bgr = cv2.cvtColor(img, cv2.COLOR_BGRA2BGR)
    rx, ry = C.detect_red(bgr)
    bx, by = C.detect_color(bgr, C.BLUE_LO, C.BLUE_HI)
    def fmt(v):
        return '%.1f' % v if v is not None else '-1'
    C.write_atomic('scene.txt', '%.4f\nred %s %s\nblue %s %s\n'
                   % (robot.getTime(), fmt(rx), fmt(ry), fmt(bx), fmt(by)))
    for label, x, y, color in (('red', rx, ry, (0, 0, 255)),
                               ('blue', bx, by, (255, 128, 0))):
        if x is None or y is None:
            continue
        center = (int(x), int(y))
        cv2.drawMarker(bgr, center, color, cv2.MARKER_CROSS, 20, 2)
        cv2.putText(bgr, label, (center[0] + 12, center[1] - 8),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.55, color, 2)
    cv2.imshow(preview, bgr)
    cv2.waitKey(1)
