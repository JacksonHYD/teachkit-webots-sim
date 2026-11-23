#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""11.3 六轴机械臂模拟画圆（手册关键代码）"""
from math import pi, cos, sin
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'common'))
import robokit_common as C
from robodyno.components import Motor
from robodyno.interfaces import Webots
from robodyno.robots.six_dof_collaborative_robot import SixDoFCollabRobot

webots = Webots()
pen = webots.robot.getDevice('pencil')
pen.write(False)


class MySixDoFArm(SixDoFCollabRobot):
    def __init__(self):
        M1 = Motor(webots, 0x10)
        M2 = Motor(webots, 0x11)
        M3 = Motor(webots, 0x12)
        M4 = Motor(webots, 0x13)
        M5 = Motor(webots, 0x14)
        M6 = Motor(webots, 0x15)
        super().__init__(M1, M2, M3, M4, M5, M6, 0.065, 0.150, 0.150, 0.08, 0.075, 0.045)
        C.boost_joint_torque(webots)
        self.start_theta = pi

    def circle(self, xo, yo, zo, r, num=50, sn=True):
        """robot arm draw circle"""
        if sn:
            self.start_theta -= 2 * pi / num
            if self.start_theta < 0:
                self.start_theta += 2 * pi
        else:
            self.start_theta += 2 * pi / num
            if self.start_theta > 2 * pi:
                self.start_theta -= 2 * pi

        x = xo + r * cos(self.start_theta)
        y = yo + r * sin(self.start_theta)
        z = zo
        angles = self.inverse_kinematics(x, y, z, -pi, 0, -pi / 2, 2)
        return angles


arm = MySixDoFArm()

print('six dof arm inited')

arm.enable()
arm.init()

# 画圆
arm.joint_space_interpolated_motion(
    arm.inverse_kinematics(0.28, 0.0, 0.193, -pi, 0, -pi / 2, 2), duration=5)
arm.joint_space_interpolated_motion(arm.circle(0.28, 0.0, 0.193, 0.05, 50, False), duration=1)
webots.sleep(0.5)
pen.write(True)
print('开始画圆（顺时针 200 步）')
for i in range(200):
    arm.joint_space_interpolated_motion(arm.circle(0.28, 0.0, 0.193, 0.05, 50, False))
    webots.sleep(0.01)
print('开始画圆（逆时针 200 步）')
for j in range(200):
    arm.joint_space_interpolated_motion(arm.circle(0.28, 0.0, 0.193, 0.05, 50, True))
    webots.sleep(0.01)
pen.write(False)

while True:
    if webots.sleep(1) == -1:
        break
