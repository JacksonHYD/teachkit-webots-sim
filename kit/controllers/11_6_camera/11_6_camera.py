#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""11.6 摄像头端：采集标定用红色方块的像素中心，写入 shared/cam.txt。"""
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
    px, py = C.detect_red(bgr)
    C.write_atomic('cam.txt', '%.4f %s %s' % (robot.getTime(), px, py))