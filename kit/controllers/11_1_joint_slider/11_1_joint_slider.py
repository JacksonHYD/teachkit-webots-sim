#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""11.1 六自由度机械臂结构设计与仿真驱动（关节空间滑动条，手册关键代码）"""
from math import pi
import os
import sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'common'))
import robokit_common as C
import tkinter as tk
from robodyno.components import Motor
from robodyno.interfaces import Webots
from robodyno.robots.six_dof_collaborative_robot import SixDoFCollabRobot

slider_window = tk.Tk()
slider_window.title("Robot Arm Control")
slider_window.geometry("400x400")
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
        super().__init__(M1, M2, M3, M4, M5, M6, 0.065, 0.150, 0.150, 0.08, 0.075, 0.045)
        C.boost_joint_torque(webots)
        self.feedback_job = None

        self.descartes_slider = [
            tk.Scale(slider_window, from_=-2 * pi, to=2 * pi, orient='horizontal',
                     label='Joint1', length=300, resolution=0.01,
                     command=lambda _: arm.update_values()),
            tk.Scale(slider_window, from_=-2 * pi, to=2 * pi, orient='horizontal',
                     label='Joint2', length=300, resolution=0.01,
                     command=lambda _: arm.update_values()),
            tk.Scale(slider_window, from_=-2 * pi, to=2 * pi, orient='horizontal',
                     label='Joint3', length=300, resolution=0.01,
                     command=lambda _: arm.update_values()),
            tk.Scale(slider_window, from_=-2 * pi, to=2 * pi, orient='horizontal',
                     label='Joint4', length=300, resolution=0.01,
                     command=lambda _: arm.update_values()),
            tk.Scale(slider_window, from_=-2 * pi, to=2 * pi, orient='horizontal',
                     label='Joint5', length=300, resolution=0.01,
                     command=lambda _: arm.update_values()),
            tk.Scale(slider_window, from_=-2 * pi, to=2 * pi, orient='horizontal',
                     label='Joint6', length=300, resolution=0.01,
                     command=lambda _: arm.update_values()),
        ]

    def create_slider(self, poses):
        for id, slider in enumerate(self.descartes_slider):
            slider.pack()
            slider.set(poses[id])

    def update_values(self):
        if self.feedback_job is not None:
            slider_window.after_cancel(self.feedback_job)
            self.feedback_job = None
        targets = [slider.get() for slider in self.descartes_slider]
        self.joint_space_interpolated_motion(targets)
        self.feedback_job = slider_window.after(60, self.report_position, targets, 30)

    def report_position(self, targets, retries):
        joint_poses = self.get_joints_poses()
        if retries and any(abs(actual - target) > 0.03 for actual, target in zip(joint_poses, targets)):
            self.feedback_job = slider_window.after(60, self.report_position, targets, retries - 1)
            return
        self.feedback_job = None
        print(f"角度: {[round(angle, 2) for angle in joint_poses]}")
        print(f"位置: {[round(value, 2) for value in self.forward_kinematics(joint_poses)]}", flush=True)


arm = MySixDoFArm()

arm.enable()
arm.init()

print('six dof arm inited')

# 生成关节拖条
arm.create_slider((0, 0, 0, 0, 0, 0))
# 运行窗口
slider_window.mainloop()
