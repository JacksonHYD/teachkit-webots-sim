#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""11.10 大场景传送带端（Supervisor）。

传送带模型（Webots Track）对块体摩擦驱动不稳定，这里由 Supervisor 按皮带速度
移动工件、到抓取点停下并通知机械臂；等到 done 信号后送下一件。
"""
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'common'))
from controller import Supervisor
import robokit_common as C

sup = Supervisor()
ts = int(sup.getBasicTimeStep())
motor = sup.getDevice('0x22')
motor.setPosition(float('inf'))
motor.setVelocity(0)

BLOCKS = ['cube_a', 'cube_b']
BELT_SPEED = 0.12
STOP_X = 0.16
Y = 0.25
Z = 0.036
BELT_FILE = 'belt_11_10.txt'
DONE_FILE = 'done_11_10.txt'


def step():
    if sup.step(ts) == -1:
        raise SystemExit


def wait_done(name, timeout=150):
    t0 = sup.getTime()
    while sup.getTime() - t0 < timeout:
        result = C.read_shared(DONE_FILE).split()
        if len(result) == 3 and result[0] == name:
            return float(result[1]), float(result[2])
        step()
    return None


nodes = []
for name in BLOCKS:
    nd = sup.getFromDef(name)
    if nd is None:
        print('missing', name)
        continue
    field = nd.getField('translation')
    nodes.append((name, nd, field))

C.write_atomic(BELT_FILE, '')
C.write_atomic(DONE_FILE, '')
positions = [field.getSFVec3f()[0] for _, _, field in nodes]
for _ in range(round(1.5 * 1000 / ts)):
    step()

for index, (name, node, _) in enumerate(nodes):
    motor.setVelocity(BELT_SPEED)
    print('履带送料：%s' % name, flush=True)
    while positions[index] < STOP_X:
        distance = min(STOP_X - positions[index], BELT_SPEED * ts / 1000.0)
        for pending in range(index, len(nodes)):
            _, block, field = nodes[pending]
            positions[pending] += distance
            field.setSFVec3f([positions[pending], Y, Z])
            block.resetPhysics()
        step()
    motor.setVelocity(0)
    step()
    C.write_atomic(BELT_FILE, 'ready %s %.3f %.3f %.3f' % (name, STOP_X, Y, Z))
    print('ready %s at (%.3f, %.3f, %.3f)' % (name, STOP_X, Y, Z), flush=True)
    target = wait_done(name)
    x, y, z = node.getPosition()
    if target is None or abs(x - target[0]) > 0.03 or abs(y - target[1]) > 0.03 or not 0.015 < z < 0.03:
        C.write_atomic(BELT_FILE, 'failed')
        print('%s 未到达放置区，停止送料' % name, flush=True)
        break
    print('%s 搬运完成，继续送料' % name, flush=True)
else:
    C.write_atomic(BELT_FILE, 'end')
    print('all blocks delivered', flush=True)

while True:
    step()
