#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""公共小工具：共享文件夹、摄像头色块识别、原子写文件。"""
import os
import time

SHARED = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', 'shared'))
os.makedirs(SHARED, exist_ok=True)


def shared_path(name):
    return os.path.join(SHARED, name)


def write_atomic(name, text):
    """原子写；Windows 上读端可能短暂占用文件，替换失败时重试。"""
    p = shared_path(name)
    tmp = p + '.tmp'
    with open(tmp, 'w', encoding='utf-8') as f:
        f.write(text)
    for _ in range(40):
        try:
            os.replace(tmp, p)
            return
        except PermissionError:
            time.sleep(0.005)
    try:
        os.remove(tmp)
    except OSError:
        pass


def read_shared(name, default=''):
    try:
        with open(shared_path(name), 'r', encoding='utf-8') as f:
            return f.read()
    except OSError:
        return default


def detect_color(bgr, lower, upper, min_area=400, max_area=20000):
    """返回该类颜色最大色块的中心 (px, py)；没有则 (None, None)。"""
    import cv2
    hsv = cv2.cvtColor(bgr, cv2.COLOR_BGR2HSV)
    mask = cv2.inRange(hsv, lower, upper)
    kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (5, 5))
    mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, kernel, iterations=2)
    mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN, kernel, iterations=1)
    cnts = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    cnts = cnts[0] if len(cnts) == 2 else cnts[1]
    best = None
    best_area = 0
    for c in cnts:
        area = cv2.contourArea(c)
        if min_area < area < max_area and area > best_area:
            x, y, w, h = cv2.boundingRect(c)
            best = (x + w / 2, y + h / 2)
            best_area = area
    if best is None:
        return (None, None)
    return best


RED_LO = (0, 100, 80)
RED_HI = (10, 255, 255)
RED2_LO = (170, 100, 80)
RED2_HI = (179, 255, 255)
BLUE_LO = (100, 120, 60)
BLUE_HI = (130, 255, 255)


def detect_red(bgr, min_area=400, max_area=20000):
    """红色跨两个 HSV 区间（0-10 与 170-179），合并后取最大色块中心。"""
    import cv2
    hsv = cv2.cvtColor(bgr, cv2.COLOR_BGR2HSV)
    m1 = cv2.inRange(hsv, RED_LO, RED_HI)
    m2 = cv2.inRange(hsv, RED2_LO, RED2_HI)
    mask = cv2.bitwise_or(m1, m2)
    kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (5, 5))
    mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, kernel, iterations=2)
    mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN, kernel, iterations=1)
    cnts = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    cnts = cnts[0] if len(cnts) == 2 else cnts[1]
    best, best_area = (None, None), 0
    for c in cnts:
        area = cv2.contourArea(c)
        if min_area < area < max_area and area > best_area:
            x, y, w, h = cv2.boundingRect(c)
            best = (x + w / 2, y + h / 2)
            best_area = area
    return best

def boost_joint_torque(webots, ids=range(0x10, 0x16)):
    """把关节电机的可用力矩设到设备上限，避免启动阶段整臂在重力下下沉/漂移。"""
    for i in ids:
        dev = webots.robot.getDevice('0x%02X::motor' % i)
        if dev is not None:
            try:
                dev.setAvailableTorque(dev.getMaxTorque())
            except Exception:
                pass


def write_carry(hold, name, tcp):
    """写夹持状态：hold=0 未夹持；hold=1 时 name 为工件名，tcp 为末端世界坐标。"""
    if hold:
        write_atomic('carry.txt', '1 %s %.4f %.4f %.4f' % (name, tcp[0], tcp[1], tcp[2]))
    else:
        write_atomic('carry.txt', '0 - 0 0 0')


def read_carry():
    try:
        parts = read_shared('carry.txt').strip().split()
        if len(parts) >= 5 and parts[0] == '1':
            return parts[1], (float(parts[2]), float(parts[3]), float(parts[4]))
    except (OSError, ValueError):
        pass
    return None, None
