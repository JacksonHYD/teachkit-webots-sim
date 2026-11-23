#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""11.6 手眼标定：摄像头识别 + Supervisor 移动标定方块，拟合像素->机械臂仿射映射。

流程同手册：把红块沿 x/y 网格移动，记录像素中心，用最小二乘拟合
    x_arm = a*px + b*py + c,  y_arm = d*px + e*py + f
结果写入 kit/shared/eye2arm.json，供 11.7/11.8 使用。
"""
import json
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'common'))
import cv2
import numpy as np
from controller import Supervisor
import robokit_common as C

sup = Supervisor()
ts = int(sup.getBasicTimeStep())
cam = sup.getDevice("camera")
cam.enable(ts)
cube = sup.getFromDef('red_block')
cube_tf = cube.getField('translation')

XS = [0.05, 0.10, 0.15, 0.20, 0.25]
YS = [-0.05, 0.0, 0.05, 0.10]
ROWS = []


def grab():
    raw = cam.getImage()
    img = np.frombuffer(raw, np.uint8).reshape((cam.getHeight(), cam.getWidth(), 4))
    bgr = cv2.cvtColor(img, cv2.COLOR_BGRA2BGR)
    return C.detect_red(bgr)


for x in XS:
    for y in YS:
        cube_tf.setSFVec3f([x, y, 0.0125])
        cube.resetPhysics()
        for _ in range(10):
            sup.step(ts)
        px, py = grab()
        if px is None:
            for _ in range(30):
                sup.step(ts)
                px, py = grab()
                if px is not None:
                    break
        if px is None:
            print('skip (%0.2f, %0.2f): no detection' % (x, y))
            continue
        ROWS.append((x, y, px, py))
        print('x=%0.2f y=%0.2f -> px=%0.1f py=%0.1f' % (x, y, px, py))

if len(ROWS) >= 6:
    arr = np.array(ROWS, dtype=float)
    A = np.c_[arr[:, 2], arr[:, 3], np.ones(len(arr))]
    cx, *_ = np.linalg.lstsq(A, arr[:, 0], rcond=None)
    cy, *_ = np.linalg.lstsq(A, arr[:, 1], rcond=None)
    model = {'x': list(cx), 'y': list(cy), 'rows': len(ROWS)}
    with open(C.shared_path('eye2arm.json'), 'w', encoding='utf-8') as f:
        json.dump(model, f, ensure_ascii=False, indent=1)
    print('eye2arm.json written:', model)
else:
    print('not enough points:', len(ROWS))

# 标定完成后把方块放回工作区，保持仿真运行
cube_tf.setSFVec3f([0.15, 0.0, 0.0125])
cube.resetPhysics()
while True:
    if sup.step(ts) == -1:
        break
