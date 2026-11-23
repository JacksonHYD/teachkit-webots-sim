#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""11.2 六轴机械臂运动学算法的仿真应用（笛卡尔滑动条 + 逆运动学，手册关键代码）"""
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

        self.descartes_slider = [
            tk.Scale(slider_window, from_=-0.4, to=0.4, orient='horizontal',
                     label='X', length=300, resolution=0.001,
                     command=lambda _: arm.update_values()),
            tk.Scale(slider_window, from_=-0.4, to=0.4, orient='horizontal',
                     label='Y', length=300, resolution=0.001,
                     command=lambda _: arm.update_values()),
            tk.Scale(slider_window, from_=0.0, to=0.3, orient='horizontal',
                     label='Z', length=300, resolution=0.001,
                     command=lambda _: arm.update_values()),
            tk.Scale(slider_window, from_=-2 * pi, to=2 * pi, orient='horizontal',
                     label='Roll', length=300, resolution=0.01,
                     command=lambda _: arm.update_values()),
            tk.Scale(slider_window, from_=-2 * pi, to=2 * pi, orient='horizontal',
                     label='Pitch', length=300, resolution=0.01,
                     command=lambda _: arm.update_values()),
            tk.Scale(slider_window, from_=-2 * pi, to=2 * pi, orient='horizontal',
                     label='Yaw', length=300, resolution=0.01,
                     command=lambda _: arm.update_values()),
        ]

    def create_slider(self, poses):
        for id, slider in enumerate(self.descartes_slider):
            slider.pack()
            slider.set(poses[id])

    def update_values(self):
        arm_poses = []
        for slider in self.descartes_slider:
            arm_poses.append(slider.get())
        print(f"角度: {[round(i, 2) for i in self.get_joints_poses()]}")
        print(f"位置: x={arm_poses[0]}, y={arm_poses[1]}, z={arm_poses[2]} "
              f"roll={arm_poses[3]}, pitch={arm_poses[4]}, yaw={arm_poses[5]}")
        self.joint_space_interpolated_motion(self.inverse_kinematics(*arm_poses))


arm = MySixDoFArm()

arm.enable()
arm.init()

print(arm.forward_kinematics((0, 0, pi / 2, 0, pi / 2, 0)))
arm.joint_space_interpolated_motion(
    arm.inverse_kinematics(0.225, -0.08, 0.17, -pi, 0, -pi / 2), duration=2)
print('six dof arm inited')
# 生成笛卡尔拖条
arm.create_slider((0.225, -0.080, 0.17, -pi, 0, -pi / 2))
# 运行窗口
slider_window.mainloop()