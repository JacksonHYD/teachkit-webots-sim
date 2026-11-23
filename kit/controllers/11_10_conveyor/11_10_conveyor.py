#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""11.9 大场景传送带端：只负责把皮带按速度运转（送料由 11_9_shuttle 完成）。"""
from controller import Robot

robot = Robot()
ts = int(robot.getBasicTimeStep())
motor = robot.getDevice("0x22")
motor.setPosition(float('inf'))
motor.setVelocity(0.12)

while robot.step(ts) != -1:
    pass
