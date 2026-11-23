#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""11.5 六自由度机械臂定点搬运（夹爪抓取，手册关键代码）"""
from math import pi
import os
import sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'common'))
import robokit_common as C
from robodyno.components import Motor
from robodyno.interfaces import Webots
from robodyno.robots.six_dof_collaborative_robot import SixDoFCollabRobot

# 初始化
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
        G1 = Motor(webots, 0x1A)
        G1.position_mode()
        self.right_finger = webots.robot.getDevice('0x1A::right')

        super().__init__(M1, M2, M3, M4, M5, M6, 0.065, 0.150, 0.150, 0.08, 0.075, 0.045, G1)
        C.boost_joint_torque(webots)

    # 抓红色工件
    def crab_palce_reb_object(self, red_source_pos, red_target_pos):
        self.joint_space_interpolated_motion(
            arm.inverse_kinematics(red_source_pos[0], red_source_pos[1], 0.22, -pi, 0, -pi / 2, 2),
            duration=2)
        webots.sleep(1)
        self.joint_space_interpolated_motion(
            arm.inverse_kinematics(red_source_pos[0], red_source_pos[1], 0.10, -pi, 0, -pi / 2, 2),
            duration=2)
        webots.sleep(1)
        self.end_effector.set_pos(10)  # 抓取
        if self.right_finger:
            self.right_finger.setPosition(10)
        webots.sleep(1)
        self.joint_space_interpolated_motion(
            arm.inverse_kinematics(red_source_pos[0], red_source_pos[1], 0.22, -pi, 0, -pi / 2, 2),
            duration=2)
        webots.sleep(1)

        self.joint_space_interpolated_motion(
            arm.inverse_kinematics(red_target_pos[0], red_target_pos[1], 0.22, -pi, 0, -pi / 2, 2),
            duration=2)  # 转到目标正上方
        webots.sleep(1)
        self.joint_space_interpolated_motion(
            arm.inverse_kinematics(red_target_pos[0], red_target_pos[1], 0.10, -pi, 0, -pi / 2, 2),
            duration=2)
        webots.sleep(1)
        self.end_effector.set_pos(25)  # 放置
        if self.right_finger:
            self.right_finger.setPosition(25)
        webots.sleep(1)
        self.joint_space_interpolated_motion(
            arm.inverse_kinematics(red_target_pos[0], red_target_pos[1], 0.22, -pi, 0, -pi / 2, 2),
            duration=2)
        webots.sleep(1)

    # 抓蓝色工件
    def crab_place_blue_object(self, blue_source_pos, blue_target_pos):
        self.joint_space_interpolated_motion(
            arm.inverse_kinematics(blue_source_pos[0], blue_source_pos[1], 0.22, -pi, 0, -pi / 2, 2),
            duration=2)
        webots.sleep(1)
        self.joint_space_interpolated_motion(
            arm.inverse_kinematics(blue_source_pos[0], blue_source_pos[1], 0.10, -pi, 0, -pi / 2, 2),
            duration=2)
        webots.sleep(1)
        self.end_effector.set_pos(10)  # 抓取
        if self.right_finger:
            self.right_finger.setPosition(10)
        webots.sleep(1)
        self.joint_space_interpolated_motion(
            arm.inverse_kinematics(blue_source_pos[0], blue_source_pos[1], 0.22, -pi, 0, -pi / 2, 2),
            duration=2)
        webots.sleep(1)

        self.joint_space_interpolated_motion(
            arm.inverse_kinematics(blue_target_pos[0], blue_target_pos[1], 0.22, -pi, 0, -pi / 2, 2),
            duration=2)  # 转到目标正上方
        webots.sleep(1)
        self.joint_space_interpolated_motion(
            arm.inverse_kinematics(blue_target_pos[0], blue_target_pos[1], 0.124, -pi, 0, -pi / 2, 2),
            duration=2)
        webots.sleep(1)
        self.end_effector.set_pos(25)  # 放置
        if self.right_finger:
            self.right_finger.setPosition(25)
        webots.sleep(1)
        self.joint_space_interpolated_motion(
            arm.inverse_kinematics(blue_target_pos[0], blue_target_pos[1], 0.22, -pi, 0, -pi / 2, 2),
            duration=2)
        webots.sleep(1)


"""
主程序开始
"""
red_source_pos = [0.2, 0]       # 红色物块的抓取位置(x,y)
red_target_pos = [0, 0.2]       # 红色物块的放置位置(x,y)
blue_source_pos = [0.2, 0.05]   # 蓝色物块的抓取位置(x,y)
blue_target_pos = [0, 0.2]      # 蓝色物块的放置位置(x,y)

arm = MySixDoFArm()
print('six dof arm inited')

arm.init()
arm.enable()
arm.end_effector.enable()
arm.end_effector.set_pos(25)
webots.sleep(1)

"""
功能1:抓取红色物块
"""
arm.crab_palce_reb_object(red_source_pos, red_target_pos)

"""
功能2:抓取蓝色物块
"""
arm.crab_place_blue_object(blue_source_pos, blue_target_pos)

# 复位工作
arm.end_effector.set_pos(0)
arm.home(2)
print('done')

while True:
    if webots.sleep(1) == -1:
        break
