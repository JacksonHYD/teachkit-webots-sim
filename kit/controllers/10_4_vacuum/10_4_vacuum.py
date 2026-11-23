#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""10.4 仿真气动模块基本控制。

Webots 的 Connector 在实际吸附时表现不稳定，这里用 Supervisor 实现等价效果：
吸住 -> 方块跟随杯口下方；松开 -> 恢复物理自由下落。
每一步的状态写入 shared/log104.txt 便于排查。
"""
import os
import sys
import traceback

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'common'))
import robokit_common as C
from controller import Supervisor

LOG = []


def log(msg):
    LOG.append(msg)
    C.write_atomic('log104.txt', '\n'.join(LOG[-50:]))


try:
    sup = Supervisor()
    ts = int(sup.getBasicTimeStep())
    log('supervisor ok')
    cube = sup.getFromDef('red_cube')
    log('cube=%r' % cube)
    if cube is None:
        raise RuntimeError('red_cube node not found')
    cube_tf = cube.getField('translation')
    CUP = (0.0, 0.0, 0.14)      # 吸盘世界位置
    CUP_FACE = 0.10             # 杯面高度
    HALF = 0.025                # 半方块高

    def hold(seconds, suction):
        t0 = sup.getTime()
        while sup.getTime() - t0 < seconds:
            sup.step(ts)
            if suction:
                cube_tf.setSFVec3f([CUP[0], CUP[1], CUP_FACE - HALF])
        log('hold done t=%.1f suction=%s' % (sup.getTime(), suction))

    while True:
        print('气动吸（方块被吸起）')
        log('吸 on')
        hold(3, True)
        print('气动松（方块落下）')
        log('松 off')
        cube.resetPhysics()
        hold(3, False)
        print('  方块 z=%.3f' % cube.getField('translation').getSFVec3f()[2])
except Exception:
    log(traceback.format_exc())
    raise
