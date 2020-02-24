from geopy import distance
import math
import matplotlib.pyplot as plt
from matplotlib.path import Path
import matplotlib.patches as patches
import numpy


class PathTracker:
    def __init__(self, min_distance=1, max_distance=10, target_distance=5, tolerance_angle=None):
        self.minDistance = min_distance  # meter
        self.maxDistance = max_distance  # meter
        self.targetDistance = target_distance  # meter

        if tolerance_angle is None:
            self.sloopTolerance = min_distance / max_distance  # slope
        else:
            self.sloopTolerance = math.atan(tolerance_angle) * 180 / math.pi

        self.path = []
        self.isPathEmpty = True
        self.isPathHasNoLine = True

    def get_target_coordinate(self, lat, lon):
        self.add_new_coordinate(lat, lon)

        N = len(self.path)

        if N >= 1:
            return 0, 0
        else:
            self.path.pop(-1)
            return self.path[-1]

        # p2 = (lat, lon)
        #
        # N = len(self.path)
        # if N > 1:
        #     for idx in range(N):
        #         d = distance.distance(self.path[-1], p2).meters
        #         if d < self.minDistance:
        #             self.path.pop(-1)
        #         else:
        #             break
        # else:
        #     return 0, 0
        #
        # if len(self.path) > 0:
        #     return self.path[-1]
        # else:
        #     return 0, 0

    def add_new_coordinate(self, lat, lon):
        if self.isPathEmpty:
            self.path.append((lat, lon))
            self.isPathEmpty = False

        else:
            p2 = (lat, lon)
            d = distance.distance(self.path[-1], p2).meters

            if d < self.minDistance:
                pass
            elif d > self.maxDistance:
                self.path.append(p2)

            else:
                if self.isPathHasNoLine:
                    if len(self.path) >= 2:
                        self.isPathHasNoLine = False
                else:
                    p0 = self.path[-2]
                    p1 = self.path[-1]

                    dx0 = p0[0] - p1[0]
                    dx1 = p1[0] - p2[0]
                    dy0 = p0[1] - p1[1]
                    dy1 = p1[1] - p2[1]
                    if dx0 == 0 or dx1 == 0:
                        self.path.append(p2)

                    else:
                        if abs(dy0/dx0 - dy1/dx1) > self.sloopTolerance:
                            self.path.append(p2)
                        else:
                            self.path[-1] = p2

p1 = PathTracker()
coorX = []
coorY = []
file1 = open("MT.txt", "r")
while True:
    line = file1.readline()
    if len(line) < 1:
        break
    line = line.split(",")
    lat1 = float(line[1])
    coorX.append(lat1)
    lon1 = float(line[2])
    coorY.append(lon1)
    data = (lat1, lon1)
    #coordinates.append(data)
    p1.add_new_coordinate(lat1, lon1)
i=0
px = []
py = []
while True:
    if i == len(p1.path):
        break
    x, y = p1.path[i]
    px.append(x)
    py.append(y)
    i= i+1
#codes = [Path.MOVETO] + [Path.LINETO] * (len(coordinates) - 1 )
#codes2 = [Path.MOVETO] + [Path.LINETO] * (len(p1.path) - 1 )

#path = Path(coordinates, codes)
#patch = patches.PathPatch(path, facecolor='none', lw=2)

#path2 = Path(p1.path, codes2)
#patch2 = patches.PathPatch(path2,linestyle=':',edgecolor="red", facecolor='none', lw=2)

#fig, ax = plt.subplots()
#ax.add_patch(patch)
#ax.add_patch(patch2)
#ax.set_xlim(39.97, 39.98)
#ax.set_ylim(32.5, 33)
plt.plot(coorX, coorY, 'o-')
plt.plot(px, py, 'o-')
plt.show()






