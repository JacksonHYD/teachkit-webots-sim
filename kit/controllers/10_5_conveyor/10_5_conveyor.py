"""10.5 传送带速度控制和非物理工件演示。"""
from controller import Supervisor

robot = Supervisor()
time_step = int(robot.getBasicTimeStep())
motor = robot.getDevice('0x22')
motor.setPosition(float('inf'))
workpieces = robot.getFromDef('WORKPIECES').getField('translation')

speed = 0.2
start_time = robot.getTime()
last_phase = None

while True:
    cycle_time = (robot.getTime() - start_time) % 8.0
    if cycle_time < 3.0:
        phase, velocity, travel_time = '正转', speed, cycle_time
    elif cycle_time < 4.0:
        phase, velocity, travel_time = '停止', 0.0, 3.0
    elif cycle_time < 7.0:
        phase, velocity, travel_time = '反转', -speed, 7.0 - cycle_time
    else:
        phase, velocity, travel_time = '停止', 0.0, 0.0

    if phase != last_phase:
        motor.setVelocity(velocity)
        print(f'传送带{phase} {velocity:g}', flush=True)
        last_phase = phase
    workpieces.setSFVec3f([speed * travel_time, 0.0, 0.0])
    if robot.step(time_step) == -1:
        break
