#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""11.7 六自由度机械臂视觉小场景搬运（气动吸取）。

摄像头识别红/蓝工件 -> 经 11.6 标定的仿射映射换算成机械臂坐标 -> 抓取并放置到置物区。
"""
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
        self.vacuum_gripper = webots.robot.getDevice("0x21")
        super().__init__(*M, 0.065, 0.150, 0.150, 0.08, 0.075, 0.09)
        C.boost_joint_torque(webots)

    def pick(self, x, y, z):
        self.joint_space_interpolated_motion(
            self.inverse_kinematics(x, y, z + 0.15, -pi, 0, -pi / 2, 2), duration=2)
        webots.sleep(0.5)
        self.joint_space_interpolated_motion(
            self.inverse_kinematics(x, y, z, -pi, 0, -pi / 2, 2), duration=1)
        webots.sleep(0.5)
        self.vacuum_gripper.turnOn()
        webots.sleep(1.5)
        self.joint_space_interpolated_motion(
            self.inverse_kinematics(x, y, z + 0.15, -pi, 0, -pi / 2, 2), duration=1)
        webots.sleep(0.5)

    def place(self, x, y, z):
        self.joint_space_interpolated_motion(
            self.inverse_kinematics(x, y, z + 0.15, -pi, 0, -pi / 2, 2), duration=2)
        webots.sleep(0.5)
        self.joint_space_interpolated_motion(
            self.inverse_kinematics(x, y, z, -pi, 0, -pi / 2, 2), duration=1)
        webots.sleep(1)
        self.vacuum_gripper.turnOff()
        webots.sleep(1.5)
        self.joint_space_interpolated_motion(
            self.inverse_kinematics(x, y, z + 0.15, -pi, 0, -pi / 2, 2), duration=2)
        webots.sleep(0.5)


def read_scene():
    try:
        lines = C.read_shared('scene.txt').strip().splitlines()
        t = float(lines[0])
        d = {}
        for ln in lines[1:]:
            k, a, b = ln.split()
            d[k] = (float(a), float(b))
        return t, d
    except (OSError, ValueError):
        return 0.0, {}


def wait_target(color, timeout=120):
    """等待摄像头的稳定识别（连续 3 帧同一目标）。"""
    start = webots.time()
    last = None
    hits = 0
    while webots.time() - start < timeout:
        webots.sleep(0.2)
        _, d = read_scene()
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
arm.vacuum_gripper.enablePresence(webots.time_step)
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
    arm.pick(x, y, 0.05)
    px, py = PLACES[color]
    arm.place(px, py, 0.05)
    print('%s 放置完成' % color)

arm.home(2)
arm.vacuum_gripper.disablePresence()
print('all done')

while True:
    if webots.sleep(1) == -1:
        break