#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""11.6 标定端：Supervisor 把红色方块依次移动到网格点，
读取摄像头像素中心，拟合 像素->机械臂坐标 的仿射映射，写入 shared/eye2arm.json。
"""
import json
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'common'))
import numpy as np
from controller import Supervisor
import robokit_common as C

sup = Supervisor()
ts = int(sup.getBasicTimeStep())
block = sup.getFromDef('red_block')
trans = block.getField('translation')

XS = [0.05, 0.10, 0.15, 0.20, 0.25]
YS = [-0.05, 0.0, 0.05, 0.10]
ROWS = []


def read_cam():
    txt = C.read_shared('cam.txt').strip()
    t, px, py = txt.split()
    return float(t), (None if px == 'None' else float(px)), (None if py == 'None' else float(py))


for x in XS:
    for y in YS:
        trans.setSFVec3f([x, y, 0.025])
        block.resetPhysics()
        t0 = sup.getTime()
        sup.step(ts)
        # 等摄像头刷出比移动时刻更新的检测
        for _ in range(60):
            sup.step(ts)
            tc, px, py = read_cam()
            if tc > t0 + 0.1:
                break
        if px is None:
            print('skip (%0.2f, %0.2f): no detection' % (x, y))
            continue
        ROWS.append((x, y, px, py))
        print('x=%.2f y=%.2f  px=%.1f py=%.1f' % (x, y, px, py))

with open(C.shared_path('calib.csv'), 'w', encoding='utf-8') as f:
    f.write('x,y,px,py\n')
    for r in ROWS:
        f.write('%.3f,%.3f,%.1f,%.1f\n' % r)

if len(ROWS) >= 4:
    P = np.array([[r[2], r[3], 1.0] for r in ROWS])
    X = np.array([r[0] for r in ROWS])
    Y = np.array([r[1] for r in ROWS])
    cx, res_x, *_ = np.linalg.lstsq(P, X, rcond=None)
    cy, res_y, *_ = np.linalg.lstsq(P, Y, rcond=None)
    model = {
        'x': [float(v) for v in cx],
        'y': [float(v) for v in cy],
        'res_x': float(res_x[0]) if len(res_x) else 0.0,
        'res_y': float(res_y[0]) if len(res_y) else 0.0,
        'n': len(ROWS),
    }
    with open(C.shared_path('eye2arm.json'), 'w', encoding='utf-8') as f:
        json.dump(model, f, ensure_ascii=False, indent=2)
    print('fit: x = %.6f*px + %.6f*py + %.6f' % tuple(cx))
    print('     y = %.6f*px + %.6f*py + %.6f' % tuple(cy))
else:
    print('NOT ENOUGH POINTS: %d' % len(ROWS))

while True:
    sup.step(ts)