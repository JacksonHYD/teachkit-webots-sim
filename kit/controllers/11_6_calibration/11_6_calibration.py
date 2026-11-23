#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""11.6 机械臂端：保持初始姿态即可（标定由 11_6_mover 完成）。"""
import os
import sys
from math import pi
import os
import sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'common'))
import robokit_common as C

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'common'))
from robodyno.components import Motor
from robodyno.interfaces import Webots
from robodyno.robots.six_dof_collaborative_robot import SixDoFCollabRobot

webots = Webots()
webots.sleep(1)


class MySixDoFArm(SixDoFCollabRobot):
    def __init__(self):
        M = [Motor(webots, i) for i in range(0x10, 0x16)]
        super().__init__(*M, 0.065, 0.150, 0.150, 0.08, 0.075, 0.045)
        C.boost_joint_torque(webots)


arm = MySixDoFArm()
arm.init()
arm.enable()
print('six dof arm inited (calibration scene)')

while True:
    if webots.sleep(1) == -1:
        break