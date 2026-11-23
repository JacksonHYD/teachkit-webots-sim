#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""10.6 摄像头模块基本控制（手册关键代码）

说明：Webots 的 camera.getImage() 返回 BGRA 四通道数据，
手册示例直接送进 cv2.cvtColor(..., COLOR_BGR2HSV) 会因通道数不符报错，
这里先 BGRA->BGR 再识别，其余逻辑与手册一致。
"""
import cv2
import numpy as np
from controller import Robot

webots_robot = Robot()

cv2.startWindowThread()
cv2.namedWindow("preview")


class RobotCamera(object):
    def __init__(self):
        self.time_step = int(webots_robot.getBasicTimeStep())
        self.red_lower_hsv = np.array([0, 43, 46])
        self.red_upper_hsv = np.array([10, 255, 255])
        self.blue_lower_hsv = np.array([100, 43, 46])
        self.blue_upper_hsv = np.array([124, 255, 255])
        self.camera = webots_robot.getDevice("camera")
        self.camera.enable(self.time_step)

    def find_obj_by_color(self, img, lower_hsv, upper_hsv):
        # 颜色遮罩
        hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
        mask = cv2.inRange(hsv, lower_hsv, upper_hsv)
        # 锐化
        sharpen_kernel = np.array([[-1, -1, -1], [-1, 9, -1], [-1, -1, -1]])
        sharpen = cv2.filter2D(mask, -1, sharpen_kernel)
        # 形态学变换
        kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (3, 3))
        close = cv2.morphologyEx(sharpen, cv2.MORPH_CLOSE, kernel, iterations=2)
        # 提取边缘
        cnts = cv2.findContours(close, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        cnts = cnts[0] if len(cnts) == 2 else cnts[1]

        # 640x480 下 5cm 方块约 60x60 像素，面积阈值放宽
        min_area = 1200
        max_area = 40000
        if len(cnts) > 0:
            for c in cnts:
                area = cv2.contourArea(c)
                if area > min_area and area < max_area:
                    x, y, w, h = cv2.boundingRect(c)
                    img = img.copy()
                    cv2.putText(img, "center: ({}, {})".format(x + w / 2, y + h / 2),
                                (x, y - 40), cv2.FONT_HERSHEY_COMPLEX, 0.5, (36, 12, 255), 1)
                    cv2.rectangle(img, (x, y), (x + w, y + h), (3, 218, 218), 2)
                    return (img, x + w / 2, y + h / 2)
        return (img, None, None)


robot_camera = RobotCamera()

while webots_robot.step(robot_camera.time_step) != -1:
    cameraData = robot_camera.camera.getImage()
    image = np.frombuffer(cameraData, np.uint8).reshape(
        (robot_camera.camera.getHeight(), robot_camera.camera.getWidth(), 4))
    image = cv2.cvtColor(image, cv2.COLOR_BGRA2BGR)
    image, object_x, object_y = robot_camera.find_obj_by_color(
        image, robot_camera.red_lower_hsv, robot_camera.red_upper_hsv)
    print('r, {}, {}'.format(object_x, object_y))
    image, object_x, object_y = robot_camera.find_obj_by_color(
        image, robot_camera.blue_lower_hsv, robot_camera.blue_upper_hsv)
    print('b, {}, {}'.format(object_x, object_y))
    cv2.imshow("preview", image)
    cv2.waitKey(robot_camera.time_step)