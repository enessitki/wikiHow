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


def calDist(point1,point2):
    x1, y1 = point1
    x2, y2 = point2
    dist = math.sqrt((x2-x1)**2+(y2-y1)**2)
    return dist


def calAngle(point1, point2, point3):
    x1, y1 = point1
    x2, y2 = point2
    x3, y3 = point3
    ang = math.degrees(math.atan2(y3 - y2, x3 - x2) - math.atan2(y1 - y2, x1 - x2))
    if ang <0:
        ang =ang + 360
        if ang > 180:
            ang = 360-ang
        return ang
    else:
        if ang > 180:
            ang = 360 - ang
        return ang


def maxDist(point1, point2):
    dist = calDist(point1,point2)
    if dist > 20:
        return False
    else:
        return True


def minDist(point1, point2):
    dist = calDist(point1, point2)
    if dist < 2.5:
        return False
    else:
        return True


def maxAngle(point1, point2, point3):
    angle = calAngle(point1, point2, point3)
    if angle < 30:          #ignore angle
        return True
    else:
        return False


def minAngle(point1, point2, point3):
    angle = calAngle(point1, point2, point3)
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
    zed=math.atan(z)
    zedx=math.degrees(zed)
    print("angle", zedx)
    print(z)
    print(m)
    return m
coordinates = [(x[0]*100, x[1]*100) for x in numpy.random.rand(45, 2)]
print(coordinates)
codes= [
    Path.MOVETO, Path.LINETO, Path.LINETO, Path.LINETO, Path.LINETO,
    Path.MOVETO, Path.LINETO, Path.LINETO, Path.LINETO, Path.LINETO,
    Path.LINETO, Path.LINETO, Path.LINETO, Path.LINETO, Path.LINETO,
    Path.LINETO, Path.LINETO, Path.LINETO, Path.LINETO, Path.LINETO,
    Path.LINETO, Path.LINETO, Path.LINETO, Path.LINETO, Path.LINETO,
    Path.LINETO, Path.LINETO, Path.LINETO, Path.LINETO, Path.LINETO,
    Path.LINETO, Path.LINETO, Path.LINETO, Path.LINETO, Path.LINETO,
    Path.LINETO, Path.LINETO, Path.LINETO, Path.LINETO, Path.LINETO,
    Path.LINETO, Path.LINETO, Path.LINETO, Path.LINETO, Path.LINETO
]
l1=len(coordinates)
#orginal path
path=Path(coordinates, codes)

fig, ax=plt.subplots()
patch= patches.PathPatch(path, facecolor='none', lw=2)
ax.add_patch(patch)
ax.set_xlim(0, 100)
ax.set_ylim(0, 100)

#3-dot elimination
x1=int((l1)/2)-1
coor2=[]
coor2.append(coordinates[0])
codes2=[]
codes2.append((codes[0]))

for i in range(0, x1):
    coor2.append(coordinates[2*i+1])
    codes2.append(codes[2*i+1])
coor2.append(coordinates[l1-1])
codes2.append((codes[l1-1]))
path2 = Path(coor2, codes2)

fig2, ax2 = plt.subplots()
patch2= patches.PathPatch(path2, facecolor='none', lw=2)
ax2.add_patch(patch)
ax2.set_xlim(0, 100)
ax2.set_ylim(0, 100)

#----------------------------------------------
#Burası Karıştı.Hepsini burda toplamaya çalıştım ancak max distance kontrolü 1den fazla yerde yapılması gerektiğini farkettim.
test=[]
test.append(coordinates[0])
testCode=[]
testCode.append(Path.MOVETO)
for i in range(2,l1-1):
    tfmin=minDist(coordinates[i-1],coordinates[i])
    tfmax=maxDist(coordinates[i-1], coordinates[i])
    if tfmax == True:
        if tfmin== True:
            tfMinAngle = minAngle(coordinates[i-2], coordinates[i-1], coordinates[i])
            tfMaxAngle = maxAngle(coordinates[i-2], coordinates[i-1], coordinates[i])
            if tfMinAngle < True and tfMaxAngle > True:
                test.appent(coordinates[i])
    else:
        test.append(coordinates[i])
ltest=len(test)
for i in range(1,ltest):
    testCode.append(Path.LINETO)

for i in range(1, l1):
    dist = calDist(coordinates[i], coordinates[k])
    if dist > 2.5:
        test.append(coordinates[i])
        testCode.append(Path.LINETO)
        k = i
path3 = Path(test, testCode)
fig3, ax3 = plt.subplots()
patch3 = patches.PathPatch(path3, facecolor='none', lw=2)
ax3.add_patch(patch3)
ax3.set_xlim(0, 100)
ax3.set_ylim(0, 100)
#-------------------------------------------------------

#both check minAngle and minDistance
testAng=[]
testAng.append(coordinates[0])
testAng.append(coordinates[1])
testCodeAng=[]
testCodeAng.append(Path.MOVETO)
testCodeAng.append(Path.LINETO)

for i in range(1, l1):
    if i+2 < l1:
        if minDist(coordinates[i-1], coordinates[i]) == True:
            angThree = calAngle(coordinates[i-1], coordinates[i], coordinates[i+1])
            if angThree > 10:
                if maxDist(coordinates[i-1], coordinates[i]) == True:
                    testAng.append(coordinates[i+2])
                    testCodeAng.append(Path.LINETO)
path4=Path(testAng, testCodeAng)
fig4, ax4 = plt.subplots()
patch4 = patches.PathPatch(path4, facecolor='none', lw=2)
ax4.add_patch(patch4)
ax4.set_xlim(0, 100)
ax4.set_ylim(0, 100)