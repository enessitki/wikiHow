# import matplotlib.pyplot as plt
import numpy as np
# from scipy.interpolate import griddata
from scipy.spatial.transform import Rotation as R
# from mpl_toolkits.mplot3d.axes3d import *
# import pyqtgraph
# fig1 = plt.figure(1)
#
# ar = Axes3D(fig1)#fig1.gca()#

import pyqtgraph.opengl as gl
from pyqtgraph.Qt import QtCore, QtGui


app = QtGui.QApplication([])
w = gl.GLViewWidget()
w.opts['distance'] = 20
w.show()
w.setWindowTitle('pyqtgraph example: GLScatterPlotItem')

g = gl.GLGridItem()
w.addItem(g)

sp3 = gl.GLScatterPlotItem(color=(1,1,1,.3), size=0.1, pxMode=False)

w.addItem(sp3)


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

        out = np.empty((0, 3), int)
        for i in range(0, len(ptss), 1):
            if ptss[i][2] < 0.2:
                p = r.apply(ptss[i])
                p = np.array(p)
                p = p + np.array(pose[0])

                out = np.append(out, p)

                sp3.setData(pos=out)


            # if (ptss[i][2] < 1.5 and ptss[i][1] > -1 and ptss[i][1] < 2):
            # if not 0 in ptss[i]:
                # x.append(p[0] + pose[0][0])
                #
                # y.append(p[1] + pose[0][1])
                #
                # z.append(p[2] + pose[0][2])

        # xj = np.asarray(x)
        #
        # yj = np.asarray(z)
        #
        # zj = np.asarray(y)
