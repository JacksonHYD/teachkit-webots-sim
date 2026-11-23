#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""11.4 六自由度机械臂定点搬运（气动吸取，手册关键代码）"""
from math import pi
import os
import sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'common'))
import robokit_common as C
from robodyno.components import Motor
from robodyno.interfaces import Webots
from robodyno.robots.six_dof_collaborative_robot import SixDoFCollabRobot

webots = Webots()
webots.sleep(1)


class MySixDoFArm(SixDoFCollabRobot):
    def __init__(self):
        M1 = Motor(webots, 0x10)
        M2 = Motor(webots, 0x11)
        M3 = Motor(webots, 0x12)
        M4 = Motor(webots, 0x13)
        M5 = Motor(webots, 0x14)
        M6 = Motor(webots, 0x15)
        self.vacuum_gripper = webots.robot.getDevice("0x21")
        # 0.09m 代表机械臂末端 L56 与气动长度和
        super().__init__(M1, M2, M3, M4, M5, M6, 0.065, 0.150, 0.150, 0.08, 0.075, 0.09)
        C.boost_joint_torque(webots)

    def pick(self, x, y, z):
        self.joint_space_interpolated_motion(
            self.inverse_kinematics(x, y, z + 0.15, -pi, 0, -pi / 2, 2), duration=2)
        webots.sleep(1)
        self.joint_space_interpolated_motion(
            self.inverse_kinematics(x, y, z, -pi, 0, -pi / 2, 2), duration=1)
        webots.sleep(1)
        self.vacuum_gripper.turnOn()
        webots.sleep(2)
        self.joint_space_interpolated_motion(
            self.inverse_kinematics(x, y, z + 0.15, -pi, 0, -pi / 2, 2), duration=1)
        webots.sleep(1)

    def place(self, x, y, z):
        self.joint_space_interpolated_motion(
            self.inverse_kinematics(x, y, z + 0.15, -pi, 0, -pi / 2, 2), duration=2)
        webots.sleep(1)
        self.joint_space_interpolated_motion(
            self.inverse_kinematics(x, y, z, -pi, 0, -pi / 2, 2), duration=1)
        webots.sleep(2)
        self.vacuum_gripper.turnOff()
        webots.sleep(2)
        self.joint_space_interpolated_motion(
            self.inverse_kinematics(x, y, z + 0.15, -pi, 0, -pi / 2, 2), duration=2)
        webots.sleep(1)


arm = MySixDoFArm()

print('six dof arm inited')
arm.init()
arm.enable()
arm.vacuum_gripper.enablePresence(webots.time_step)

"""
参数备注：
机械臂坐标默认为(0,0,0)，底板上黑色点与点距离为0.05m；可以把工件放在点的正上方，便于调试；
红色工件的大小为（0.05,0.05,0.05）
当把红色工件沿着X轴方向移动4个距离点，则红色工件的位置为（0.15,0,0.05)
以此类推，计算出工件的目标位置；
"""
red_pick_pos = [0.15, 0, 0.05]     # 红色物块的抓取位置(x,y,z)
red_place_pos = [0, 0.2, 0.05]     # 红色物块的放置位置(x,y,z)
blue_pick_pos = [0.15, 0.1, 0.05]  # 蓝色物块的抓取位置(x,y,z)
blue_place_pos = [0, 0.2, 0.1]     # 蓝色物块的放置位置(x,y,z)

# 功能1：机械臂抓取红色物块
print('red pick')
arm.pick(red_pick_pos[0], red_pick_pos[1], red_pick_pos[2])

# 机械臂放置红色物块
print('red place')
arm.place(red_place_pos[0], red_place_pos[1], red_place_pos[2])

# 功能2：机械臂抓取蓝色物块
print('blue pick')
arm.pick(blue_pick_pos[0], blue_pick_pos[1], blue_pick_pos[2])

# 机械臂放置蓝色物块
print('blue place')
arm.place(blue_place_pos[0], blue_place_pos[1], blue_place_pos[2])

# 机械臂回到初始位置
arm.home(2)
arm.vacuum_gripper.disablePresence()
print('done')

while True:
    if webots.sleep(1) == -1:
        break