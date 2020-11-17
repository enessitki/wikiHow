import matplotlib.pyplot as plt
import numpy as np
# from scipy.interpolate import griddata
from scipy.spatial.transform import Rotation as R
from mpl_toolkits.mplot3d.axes3d import *
# import pyqtgraph
fig1 = plt.figure(1)

ar = Axes3D(fig1)#fig1.gca()#


class MapBuilder:
    def __init__(self):
        pass

    def add_to_map(self, frames, pose):
        points = frames[1]

        x = []

        y = []

        z = []
        # print(dir(points))
        # print(type(points.data))

        v, t = points.get_vertices(), points.get_texture_coordinates()

        verts = np.asanyarray(v).view(np.float32).reshape(-1, 3)  # xyz

        ptss = np.asanyarray(v).view(np.float32).reshape(len(verts), 3)

        r = R.from_euler("xyz", pose[1])

        for i in range(0, len(ptss), 1):
            if ptss[i][2] < 0.2:

            # if (ptss[i][2] < 1.5 and ptss[i][1] > -1 and ptss[i][1] < 2):
            # if not 0 in ptss[i]:
                p = r.apply(ptss[i])
                x.append(p[0] + pose[0][0])

                y.append(p[1] + pose[0][1])

                z.append(p[2] + pose[0][2])

        xj = np.asarray(x)

        yj = np.asarray(z)

        zj = np.asarray(y)
        # print(xj)
        # print(yj)
        # print(zj)

        plt.scatter(xj, yj, zs=zj, s=20, zdir="z", c='r', marker="o")
        plt.xlim(-1, 1)
        plt.ylim(-1, 1)
        # plt.set_zlim(-1, 1)

        # xi = np.linspace(min(xj), max(xj))
        #
        # yi = np.linspace(min(yj), max(yj))
        #
        # X, Y = np.meshgrid(xi, yi)
        #
        # print(len(xj))
        #
        # Z = griddata((xj, yj), zj, (X, Y), method='nearest')
        #
        # ar.contour(X, Y, Z)
        #
        # surf = ar.scatter(xj, yj, zj, s=1, c='r')
        #
        # ar.set_xlabel('Horizontal - axis')
        #
        # ar.set_ylabel('Depth  - axis')
        #
        # ar.set_zlabel('Vertical - axis')
        #
        plt.pause(0.0001)
        #
        # surf.remove()
        #
        # ar.clear()
        # plt.cla()


        # x = []
        #
        # y = []
        #
        # z = []


