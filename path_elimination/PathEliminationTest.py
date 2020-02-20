import math
import matplotlib.pyplot as plt
from matplotlib.path import Path
import matplotlib.patches as patches
import numpy


class MyClass:
    def __init__(self):
        self.myVariable = 0

    def to_do(self, my_input):
        pass


def calc_dist(point1,point2):
    x1, y1 = point1
    x2, y2 = point2
    dist = math.sqrt((x2-x1)**2+(y2-y1)**2)
    return dist


def calc_angle(point1, point2, point3):
    x1, y1 = point1
    x2, y2 = point2
    x3, y3 = point3
    ang = math.degrees(math.atan2(y3 - y2, x3 - x2) - math.atan2(y1 - y2, x1 - x2))
    if ang < 0:
        ang = ang + 360
        if ang > 180:
            ang = 360-ang
        return ang
    else:
        if ang > 180:
            ang = 360 - ang
        return ang


def max_dist(point1, point2):
    dist = calc_dist(point1, point2)
    if dist > 20:
        return False
    else:
        return True


def min_dist(point1, point2):
    dist = calc_dist(point1, point2)
    if dist < 2.5:
        return False
    else:
        return True


def max_angle(point1, point2, point3):
    angle = calc_angle(point1, point2, point3)
    if angle > 160:          #ignore angle
        return True
    else:
        return False


def min_angle(point1, point2, point3):
    angle = calc_angle(point1, point2, point3)
    if angle < 10:          #little sharp angle
        return True
    else:
        return False


def cumulAngle(point1, point2, point3, lastAngle, cuAngle):
    cuAngle=cuAngle+lastAngle
    if cuAngle > 30:         #cumulative angle
        return False
    else:
        return True

def slope(point1, point2):
    xs1, ys1 = point1
    xs2, ys2 = point2
    m = (ys1-ys2) / (xs1-xs2)
    z = (ys2-ys1) / (xs2-xs1)
    zed = math.atan(z)
    zedx = math.degrees(zed)
    print("angle", zedx)
    print(z)
    print(m)
    return m
coordinates = [(x[0]*100, x[1]*100) for x in numpy.random.rand(45, 2)]
print(coordinates)
codes = []
codes.append(Path.MOVETO)
codes.append(Path.LINETO)
l1 = len(coordinates)
for i in range(0, l1-2):
    codes.append(Path.LINETO)

#orginal path
path = Path(coordinates, codes)

fig, ax = plt.subplots()
patch = patches.PathPatch(path, facecolor='none', lw=2)
ax.add_patch(patch)
ax.set_xlim(0, 100)
ax.set_ylim(0, 100)


test = []
test.append(coordinates[0])
test.append(coordinates[1])
testCode = []
testCode.append(Path.MOVETO)
testCode.append(Path.LINETO)
for i in range(2, l1-1):
    tf_max_dist = max_dist(coordinates[i - 1], coordinates[i])
    tf_max_dist2 = max_dist(coordinates[i - 2], coordinates[i])
    tf_min_dist = min_dist(coordinates[i - 1], coordinates[i])
    tf_max_ang = max_angle(coordinates[i - 2], coordinates[i - 1], coordinates[i])
    tf_min_ang = min_angle(coordinates[i - 2], coordinates[i - 1], coordinates[i])
    if tf_max_dist == True:
        if tf_min_dist == True:
            if tf_max_dist2 == True:
                if tf_max_ang == True or tf_min_ang == True:
                    test.append(coordinates[i])
                    testCode.append(Path.LINETO)
                else:
                    pass
            else:
                pass
        else:
            pass
    else:
        test.append(coordinates[i])
        testCode.append(Path.LINETO)
path3 = Path(test, testCode)
fig3, ax3 = plt.subplots()
patch3 = patches.PathPatch(path3, facecolor='none', lw=2)
ax3.add_patch(patch3)
ax3.set_xlim(0, 100)
ax3.set_ylim(0, 100)
#Use this for graphs
#plt.show()
