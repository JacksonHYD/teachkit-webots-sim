#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""10.2 仿真直线模块基本控制（手册关键代码）"""
from robodyno.components import SliderModule
from robodyno.interfaces import Webots

webots = Webots()
slider = SliderModule(webots, 0x10)

slider.motor.position_track_mode(5, 10, 10)
slider.enable()
slider.set_pos(-0.1)

while True:
    print(f'pos: {slider.get_pos():.2f}, vel: {slider.motor.get_vel():.2f}')
    if webots.sleep(0.5) == -1:
        break