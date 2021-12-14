from firmware import InitializeSerial
from firmware import MoveMotors
from firmware import CenterGantry
from firmware import ZeroGantry
import time
import math

arduino = InitializeSerial()
ZeroGantry(arduino)
CenterGantry(arduino)

center = (185,205)
offset = 125

center_x = 185
center_y = 205
num_spots = 6
angle = 0
for i in range(num_spots):
    x = int(center_x + offset*math.cos(angle))
    y = int(center_y + offset*math.sin(angle))
    print(x,y)
    angle += 2*math.pi/(num_spots)
    time.sleep(.5)
    MoveMotors(arduino,(x,y))
    



# MoveMotors(arduino,(185+offset,205+offset))
# time.sleep(.5)
# MoveMotors(arduino,(185-offset,205+offset))
# time.sleep(.5)
# MoveMotors(arduino,(185-offset,205-offset))
# time.sleep(.5)
# MoveMotors(arduino,(185+offset,205-offset))
