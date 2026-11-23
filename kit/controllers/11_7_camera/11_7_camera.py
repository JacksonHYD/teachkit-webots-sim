#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""11.7/11.8 摄像头端：识别红、蓝工件，把像素中心写入 shared/scene.txt。

行格式：red <px> <py> / blue <px> <py>，未识别为 -1 -1。
"""
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

while robot.step(ts) != -1:
    raw = cam.getImage()
    img = np.frombuffer(raw, np.uint8).reshape((cam.getHeight(), cam.getWidth(), 4))
    bgr = cv2.cvtColor(img, cv2.COLOR_BGRA2BGR)
    rx, ry = C.detect_red(bgr)
    bx, by = C.detect_color(bgr, C.BLUE_LO, C.BLUE_HI)
    def fmt(v):
        return '%.1f' % v if v is not None else '-1'
    C.write_atomic('scene.txt', '%.4f\nred %s %s\nblue %s %s\n'
                   % (robot.getTime(), fmt(rx), fmt(ry), fmt(bx), fmt(by)))