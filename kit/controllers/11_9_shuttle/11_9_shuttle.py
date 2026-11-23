#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""11.9 大场景传送带端（Supervisor）。

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
Z = 0.046
HALF_H = 0.02


def step():
    if sup.step(ts) == -1:
        raise SystemExit


def wait_done(name, timeout=150):
    t0 = sup.getTime()
    while sup.getTime() - t0 < timeout:
        result = C.read_shared('done.txt').strip()
        if result == 'failed ' + name:
            return False
        if result == name:
            C.write_atomic('done.txt', '')
            return True
        step()
    return False


nodes = []
for name in BLOCKS:
    nd = sup.getFromDef(name)
    if nd is None:
        print('missing', name)
        continue
    tf = nd.getField('translation')
    nodes.append((name, nd, tf, tf.getSFVec3f()[0]))

C.write_atomic('belt.txt', '')
C.write_atomic('done.txt', '')
for index, (name, _, _, _) in enumerate(nodes):
    motor.setVelocity(BELT_SPEED)
    while nodes[index][3] < STOP_X:
        travel = min(STOP_X - nodes[index][3], BELT_SPEED * ts / 1000.0)
        for pending in range(index, len(nodes)):
            block_name, node, translation, x = nodes[pending]
            x += travel
            translation.setSFVec3f([x, Y, Z])
            node.resetPhysics()
            nodes[pending] = (block_name, node, translation, x)
        step()
    motor.setVelocity(0)
    z_tcp = Z + HALF_H
    C.write_atomic('belt.txt', 'ready %s %.3f %.3f %.3f' % (name, STOP_X, Y, z_tcp))
    print('ready %s at (%.3f, %.3f, %.3f)' % (name, STOP_X, Y, z_tcp), flush=True)
    if not wait_done(name):
        print('%s 未确认抓取成功，停止送料' % name, flush=True)
        while True:
            step()
    print('%s 被取走，继续送料' % name)

C.write_atomic('belt.txt', 'end')
print('all blocks delivered')
while True:
    if sup.step(ts) == -1:
        break
