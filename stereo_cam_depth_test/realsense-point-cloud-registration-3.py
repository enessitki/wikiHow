import pyqtgraph.opengl as gl
from pyqtgraph.Qt import QtCore, QtWidgets
import numpy as np
import cv2
import sys
import time
from classes.D435 import D435
from classes.T265 import T265
from scipy.spatial.transform import Rotation as R
# notes
# https://github.com/yoshimasa1700/mono_vo_python
# http://campar.in.tum.de/files/saleh/final_pres_reconstruct.pdf
# https://github.com/filchy/slam-python
# https://docs.opencv.org/3.4/df/ddc/classcv_1_1rgbd_1_1Odometry.html
# import pyqtgraph.examples
# pyqtgraph.examples.run()


class Window(gl.GLViewWidget):
    def __init__(self, parent=None):
        super(Window, self).__init__(parent=parent)
        self.opts['distance'] = 20
        self.setWindowTitle('pyqtgraph example: GLScatterPlotItem')

        self.g = gl.GLGridItem()
        self.addItem(self.g)

        self.spAxis = gl.GLScatterPlotItem(pos=np.array([[0, 0, 0],
                                                         [1, 0, 0],
                                                         [0, 1, 0],
                                                         [0, 0, 1]]),
                                           color=np.array([(1, 1, 1, 1),
                                                           (1, 0, 0, 1),
                                                           (0, 1, 0, 1),
                                                           (0, 0, 1, 1)]),
                                           size=0.2,
                                           pxMode=False)
        # self.spAxis.translate(0, 0, 0)
        self.addItem(self.spAxis)

        self.sp = gl.GLScatterPlotItem(pxMode=False)
        # sp1 = gl.GLScatterPlotItem(pos=pos, size=size, color=color, pxMode=False)
        # self.sp.translate(0, 0, 0)
        self.addItem(self.sp)

        self.d435 = D435(clipping_distance_in_meters=1000)
        self.t265 = T265()

        self.vertsMem = np.empty((0, 3), float)
        self.filterHash = {}
        self.colorMem = np.empty((0, 4), float)
        self.inverseSensitivity = 100
        self.frameWidth = 640
        self.frameHeight = 480
        self.maxDistance = 1

        self.show()

        self.timer = QtCore.QTimer()
        self.timer.setInterval(10)
        self.timer.timeout.connect(self.run)
        self.timer.start()

    def run(self):
        # self.vertsMem = np.empty((0, 3), float)
        # self.colorMem = np.empty((0, 4), float)
        t0 = time.time()

        verts, texcoords, color_image = self.d435.update_frames()
        translation, rotation = self.t265.update_frames()
        translation = np.array(translation)
        r = R.from_euler("xyz", rotation, degrees=True)
        if verts is not None:
            k = -1
            for vert, tex in zip(verts, texcoords):
                k += 1
                if vert[2] < self.maxDistance:
                    vert = r.apply(vert)
                    vert += translation
                    vert[1], vert[2] = vert[2], -vert[1]
                    vert[0] = int(vert[0]*self.inverseSensitivity)
                    vert[1] = int(vert[1]*self.inverseSensitivity)
                    vert[2] = int(vert[2]*self.inverseSensitivity)

                    x = int(tex[0] * self.frameWidth + 0.5)
                    y = int(tex[1] * self.frameHeight + 0.5)

                    if 0 <= x < self.frameWidth and 0 <= y < self.frameHeight:
                        rgb = np.array([x for x in np.flip(color_image[y, x, :]) / 255] + [1])
                        # if rgb[0] > 0.8 and rgb[1] > 0.8 and rgb[2] > 0.8:
                        #     rgb = np.array([0, 0, 0, 0])
                    else:
                        rgb = np.array([0, 0, 0, 0])

                    key = str(vert)
                    if key not in self.filterHash:
                        self.vertsMem = np.append(self.vertsMem, np.array([vert]), axis=0)
                        self.colorMem = np.append(self.colorMem, np.array([rgb]), axis=0)
                        self.filterHash[key] = len(self.vertsMem) - 1
                    else:
                        self.colorMem[self.filterHash[key]] = (self.colorMem[self.filterHash[key]] + rgb*5)/6

            if len(self.vertsMem) > 1:
                self.sp.setData(pos=self.vertsMem*(10/self.inverseSensitivity), color=self.colorMem, size=10/self.inverseSensitivity)

        cv2.imshow("colored", color_image)
        # print(len(self.filterHash))
        print(time.time() - t0)


app = QtWidgets.QApplication(sys.argv)
w = Window()
app.exec_()
sys.exit()
