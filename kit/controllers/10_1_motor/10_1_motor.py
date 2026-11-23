#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""10.1 仿真转动关节模块基本控制。

在手册关键代码基础上加了往复运动（0 <-> 31.4 rad），方便观察转动过程。
"""
from robodyno.components import Motor
from robodyno.interfaces import Webots

webots = Webots()
motor = Motor(webots, 0x10)

motor.position_track_mode(5, 2, 2)
motor.enable()

while True:
    print('目标位置 31.4 rad（5 圈）')
    motor.set_pos(31.4)
    for _ in range(12):
        print(f'pos: {motor.get_pos():.2f}, vel: {motor.get_vel():.2f}')
        if webots.sleep(0.5) == -1:
            raise SystemExit
    print('目标位置 0 rad（回到原点）')
    motor.set_pos(0)
    for _ in range(12):
        print(f'pos: {motor.get_pos():.2f}, vel: {motor.get_vel():.2f}')
        if webots.sleep(0.5) == -1:
            raise SystemExit