#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""11.10 六自由度机械臂视觉大场景搬运（夹爪抓取）。"""
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

COLOR_OF = {'cube_a': 'red', 'cube_b': 'blue'}
PLACES = {'red': (0.0, 0.14), 'blue': (0.08, 0.14)}
GRIPPER_CENTER_OFFSET = 0.066
BELT_FILE = 'belt_11_10.txt'
DONE_FILE = 'done_11_10.txt'


class MySixDoFArm(SixDoFCollabRobot):
    def __init__(self):
        M = [Motor(webots, i) for i in range(0x10, 0x16)]
        G1 = Motor(webots, 0x1A)
        G1.position_mode()
        self.right_finger = webots.robot.getDevice('0x1A::right')
        super().__init__(*M, 0.065, 0.150, 0.150, 0.08, 0.075, 0.045, G1)
        C.boost_joint_torque(webots)

    def pick(self, x, y, z):
        z += GRIPPER_CENTER_OFFSET
        self.joint_space_interpolated_motion(
            self.inverse_kinematics(x, y, z + 0.12, -pi, 0, -pi / 2, 2), duration=2)
        webots.sleep(0.5)
        self.joint_space_interpolated_motion(
            self.inverse_kinematics(x, y, z, -pi, 0, -pi / 2, 2), duration=1.5)
        webots.sleep(0.5)
        self.end_effector.set_pos(10)
        if self.right_finger:
            self.right_finger.setPosition(10)
        webots.sleep(1)
        self.joint_space_interpolated_motion(
            self.inverse_kinematics(x, y, z + 0.12, -pi, 0, -pi / 2, 2), duration=1.5)
        webots.sleep(0.5)

    def place(self, x, y):
        self.joint_space_interpolated_motion(
            self.inverse_kinematics(x, y, 0.22, -pi, 0, -pi / 2, 2), duration=2)
        webots.sleep(0.5)
        self.joint_space_interpolated_motion(
            self.inverse_kinematics(x, y, 0.10, -pi, 0, -pi / 2, 2), duration=1.5)
        webots.sleep(0.5)
        self.end_effector.set_pos(25)
        if self.right_finger:
            self.right_finger.setPosition(25)
        webots.sleep(1)
        self.joint_space_interpolated_motion(
            self.inverse_kinematics(x, y, 0.22, -pi, 0, -pi / 2, 2), duration=1.5)
        webots.sleep(0.5)


def read_scene():
    try:
        lines = C.read_shared('scene_11_10.txt').strip().splitlines()
        d = {}
        for ln in lines[1:]:
            k, a, b = ln.split()
            d[k] = (float(a), float(b))
        return d
    except (OSError, ValueError):
        return {}


arm = MySixDoFArm()
arm.init()
arm.enable()
arm.end_effector.enable()
arm.end_effector.set_pos(25)
if arm.right_finger:
    arm.right_finger.setPosition(25)
print('six dof arm inited')

while True:
    webots.sleep(0.5)
    line = C.read_shared(BELT_FILE).strip()
    if not line:
        continue
    if line in ('end', 'failed'):
        break
    parts = line.split()
    if parts[0] != 'ready':
        continue
    name = parts[1]
    x, y, z = (float(v) for v in parts[2:5])
    color = COLOR_OF.get(name, 'red')
    seen = read_scene().get(color)
    print('%s 到位 (%.3f, %.3f, %.3f)，摄像头 %s: %s' % (name, x, y, z, color, seen))
    C.write_atomic(BELT_FILE, 'picking')
    arm.pick(x, y, z)
    px, py = PLACES[color]
    arm.place(px, py)
    C.write_atomic(DONE_FILE, '%s %.3f %.3f' % (name, px, py))

arm.end_effector.set_pos(0)
if arm.right_finger:
    arm.right_finger.setPosition(0)
arm.home(2)
if line == 'end':
    print('all done', flush=True)

while True:
    if webots.sleep(1) == -1:
        break
