#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""10.3 仿真夹持器模块基本控制（手册关键代码）。

停顿必须边走时间步边等，否则仿真会被冻住、夹爪不会动。
"""
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'common'))
import robokit_common as C
from robodyno.components import Motor
from robodyno.interfaces import Webots

webots = Webots()
gripper = Motor(webots, 0x1A)
gripper.position_mode()
gripper.enable()

LOG = []


def hold(seconds):
    t0 = webots.time()
    while webots.time() - t0 < seconds:
        if webots.sleep(0.05) == -1:
            raise SystemExit
        LOG.append('%.2f pos=%.4f' % (webots.time(), gripper.get_pos()))
        C.write_atomic('hand.txt', '\n'.join(LOG[-200:]))


while True:
    print('夹爪合拢 set_pos(25)')
    gripper.set_pos(25)
    hold(2)
    print('  pos={:.2f}'.format(gripper.get_pos()))
    print('夹爪张开 set_pos(0)')
    gripper.set_pos(0)
    hold(2)
    print('  pos={:.2f}'.format(gripper.get_pos()))