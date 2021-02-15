import sys
import time
from classes.SickS300 import SickS300
import matplotlib.pyplot as plt
from drawnow import *

plt.ion()
plt.style.use('seaborn')

def plot_values():
    plt.polar()


xCoord = []
zCoord = []
lidar = SickS300(max_distance=1, start_angle=85, end_angle=85.6)
while True:

    time1 = time.time()
    measurement = lidar.update()
    time2 = time.time()
    # xCoord.append(0)
    # zCoord.append(0)
    for x in measurement:
        xCoord.append(x[1]*100)
        zCoord.append(x[3]*100)
    time3 = time.time()
    if(len(xCoord)+len(zCoord) > 0):
        drawnow(plot_values)
        print(xCoord, zCoord)
    time4 = time.time()

    xCoord.clear()
    zCoord.clear()


