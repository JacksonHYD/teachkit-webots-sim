#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""11.8 六自由度机械臂视觉小场景搬运（夹爪抓取）。"""
import json
import os
import sys
from math import pi

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'common'))
import robokit_common as C
from robodyno.components import Motor
from robodyno.interfaces import Webots
from robodyno.robots.six_dof_collaborative_robot import SixDoFCollabRobot

webots = Webots()
webots.sleep(1)

model = json.load(open(C.shared_path('eye2arm.json'), encoding='utf-8'))
MA, MB, MC = model['x']
MD, ME, MF = model['y']


def px2arm(px, py):
    return (MA * px + MB * py + MC, MD * px + ME * py + MF)


class MySixDoFArm(SixDoFCollabRobot):
    def __init__(self):
        M = [Motor(webots, i) for i in range(0x10, 0x16)]
        G1 = Motor(webots, 0x1A)
        G1.position_mode()
        self.right_finger = webots.robot.getDevice('0x1A::right')
        super().__init__(*M, 0.065, 0.150, 0.150, 0.08, 0.075, 0.045, G1)
        C.boost_joint_torque(webots)

    def pick(self, x, y):
        self.joint_space_interpolated_motion(
            self.inverse_kinematics(x, y, 0.22, -pi, 0, -pi / 2, 2), duration=2)
        webots.sleep(0.5)
        self.joint_space_interpolated_motion(
            self.inverse_kinematics(x, y, 0.10, -pi, 0, -pi / 2, 2), duration=1.5)
        webots.sleep(0.5)
        self.end_effector.set_pos(10)
        if self.right_finger:
            self.right_finger.setPosition(10)   # 合拢抓取
        webots.sleep(1)
        self.joint_space_interpolated_motion(
            self.inverse_kinematics(x, y, 0.22, -pi, 0, -pi / 2, 2), duration=1.5)
        webots.sleep(0.5)

    def place(self, x, y):
        self.joint_space_interpolated_motion(
            self.inverse_kinematics(x, y, 0.22, -pi, 0, -pi / 2, 2), duration=2)
        webots.sleep(0.5)
        self.joint_space_interpolated_motion(
            self.inverse_kinematics(x, y, 0.11, -pi, 0, -pi / 2, 2), duration=1.5)
        webots.sleep(0.5)
        self.end_effector.set_pos(25)
        if self.right_finger:
            self.right_finger.setPosition(25)   # 张开释放
        webots.sleep(1)
        self.joint_space_interpolated_motion(
            self.inverse_kinematics(x, y, 0.22, -pi, 0, -pi / 2, 2), duration=1.5)
        webots.sleep(0.5)


def read_scene():
    try:
        lines = C.read_shared('scene.txt').strip().splitlines()
        d = {}
        for ln in lines[1:]:
            k, a, b = ln.split()
            d[k] = (float(a), float(b))
        return d
    except (OSError, ValueError):
        return {}


def wait_target(color, timeout=120):
    start = webots.time()
    last = None
    hits = 0
    while webots.time() - start < timeout:
        webots.sleep(0.2)
        d = read_scene()
        p = d.get(color)
        if p and p[0] > 0:
            if last and abs(p[0] - last[0]) < 12 and abs(p[1] - last[1]) < 12:
                hits += 1
            else:
                hits = 0
            last = p
            if hits >= 3:
                return p
    return None


arm = MySixDoFArm()
arm.init()
arm.enable()
arm.end_effector.enable()
arm.end_effector.set_pos(25)
if arm.right_finger:
    arm.right_finger.setPosition(25)
print('six dof arm inited')

PLACES = {'red': (0.0, 0.2), 'blue': (0.06, 0.2)}

for color in ('red', 'blue'):
    target = wait_target(color)
    if target is None:
        print('%s: 未识别到工件，跳过' % color)
        continue
    x, y = px2arm(*target)
    x = max(0.08, min(0.27, x))
    y = max(-0.10, min(0.24, y))
    print('%s 像素(%.1f, %.1f) -> 机械臂(%.3f, %.3f)' % (color, target[0], target[1], x, y))
    arm.pick(x, y)
    px, py = PLACES[color]
    arm.place(px, py)
    print('%s 放置完成' % color)

arm.end_effector.set_pos(0)
if arm.right_finger:
    arm.right_finger.setPosition(0)
arm.home(2)
print('all done')

while True:
    if webots.sleep(1) == -1:
        break