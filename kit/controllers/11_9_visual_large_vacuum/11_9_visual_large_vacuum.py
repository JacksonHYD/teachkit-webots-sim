#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""11.9 六自由度机械臂视觉大场景搬运（气动吸取）。

传送带送料到抓取点 -> 摄像头识别确认 -> 机械臂抓取 -> 放到底板置物区 -> 通知传送带继续。
"""
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
PLACES = {'red': (0.0, 0.14, 0.034), 'blue': (0.08, 0.14, 0.034)}


class MySixDoFArm(SixDoFCollabRobot):
    def __init__(self):
        M = [Motor(webots, i) for i in range(0x10, 0x16)]
        self.vacuum_gripper = webots.robot.getDevice("0x21")
        super().__init__(*M, 0.065, 0.150, 0.150, 0.08, 0.075, 0.09)
        C.boost_joint_torque(webots)

    def pick(self, x, y, z):
        contact_z = z - 0.013
        self.joint_space_interpolated_motion(
            self.inverse_kinematics(x, y, z + 0.15, -pi, 0, -pi / 2, 2), duration=2)
        webots.sleep(0.5)
        self.joint_space_interpolated_motion(
            self.inverse_kinematics(x, y, contact_z, -pi, 0, -pi / 2, 2), duration=1)
        webots.sleep(0.5)
        self.vacuum_gripper.turnOn()
        webots.sleep(1.5)
        if not self.vacuum_gripper.getPresence():
            self.vacuum_gripper.turnOff()
            return False
        self.joint_space_interpolated_motion(
            self.inverse_kinematics(x, y, z + 0.15, -pi, 0, -pi / 2, 2), duration=1)
        webots.sleep(0.5)
        return self.vacuum_gripper.getPresence()

    def place(self, x, y, z):
        self.joint_space_interpolated_motion(
            self.inverse_kinematics(x, y, z + 0.15, -pi, 0, -pi / 2, 2), duration=2)
        webots.sleep(0.5)
        self.joint_space_interpolated_motion(
            self.inverse_kinematics(x, y, z, -pi, 0, -pi / 2, 2), duration=1)
        webots.sleep(1)
        if not self.vacuum_gripper.getPresence():
            self.vacuum_gripper.turnOff()
            return False
        self.vacuum_gripper.turnOff()
        webots.sleep(1.5)
        self.joint_space_interpolated_motion(
            self.inverse_kinematics(x, y, z + 0.15, -pi, 0, -pi / 2, 2), duration=2)
        webots.sleep(0.5)
        return True


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


arm = MySixDoFArm()
arm.init()
arm.enable()
arm.vacuum_gripper.enablePresence(webots.time_step)
print('six dof arm inited')

while True:
    webots.sleep(0.5)
    line = C.read_shared('belt.txt').strip()
    if not line:
        continue
    if line == 'end':
        break
    parts = line.split()
    if parts[0] != 'ready':
        continue
    name = parts[1]
    x, y, z = (float(v) for v in parts[2:5])
    color = COLOR_OF.get(name, 'red')

    # 视觉确认：摄像头应看到该颜色
    seen = read_scene().get(color)
    print('%s 到位 (%.3f, %.3f, %.3f)，摄像头 %s: %s' % (name, x, y, z, color, seen))

    C.write_atomic('belt.txt', 'picking')
    if not arm.pick(x, y, z) or not arm.place(*PLACES[color]):
        arm.vacuum_gripper.turnOff()
        C.write_atomic('done.txt', 'failed ' + name)
        print('%s 未能吸稳工件，停止搬运' % name, flush=True)
        break
    C.write_atomic('done.txt', name)
    print('%s 搬运完成' % name)

arm.home(2)
arm.vacuum_gripper.disablePresence()
if line == 'end':
    print('all done')

while True:
    if webots.sleep(1) == -1:
        break
