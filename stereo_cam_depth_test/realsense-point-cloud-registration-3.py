import pyqtgraph.opengl as gl
from pyqtgraph.Qt import QtCore, QtWidgets
import numpy as np
import sys
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
        self.inverseSensitivity = 100
        self.filterHash = {}

        self.show()

        self.timer = QtCore.QTimer()
        self.timer.setInterval(10)
        self.timer.timeout.connect(self.run)
        self.timer.start()

    def run(self):
        self.vertsMem = np.empty((0, 3), float)

        verts, texcoords, color_image = self.d435.update_frames()
        translation, rotation = self.t265.update_frames()
        translation = np.array(translation)
        r = R.from_euler("xyz", rotation, degrees=True)
        if verts is not None:
            for vert in verts:
                if vert[2] < 0.3:
                    # print("1", vert)
                    vert = r.apply(vert)
                    # print("2", vert)
                    # print(translation)
                    vert += translation
                    vert[1], vert[2] = vert[2], -vert[1]
                    vert[0] = int(vert[0]*self.inverseSensitivity)
                    vert[1] = int(vert[1]*self.inverseSensitivity)
                    vert[2] = int(vert[2]*self.inverseSensitivity)
                    self.vertsMem = np.append(self.vertsMem, np.array([vert]), axis=0)
                    # try:
                    #     if self.filterHash[str(vert)] > 5:
                    #         pass
                        #     alone_index = 0
                        #     for n in range(30):
                        #         for m in range(30):
                        #             try:
                        #                 if self.filterHash[str(vert[n] + m -15)] > -1:
                        #                     alone_index += 1
                        #             except:
                        #                 pass
                        #     # print(alone_index)
                        #     if alone_index > -1:
                        #         self.vertsMem = np.append(self.vertsMem, np.array([vert]), axis=0)
                        # else:
                        #     self.filterHash[str(vert)] += 1
                        #     print(self.filterHash[str(vert)])
                    # except:
                    #     self.filterHash[str(vert)] = 0
                    #     self.vertsMem = np.append(self.vertsMem, np.array([vert]), axis=0)

            # verts2 = np.array(verts2)
            # color = [(0.7, 0.7, 0.7, 1)] * (len(self.vertsMem) )
            color = []
            print(color_image.shape)
            for tex in texcoords:
                x = int(min(max(tex[0] + 0.5, 0), 639))
                y = int(min(max(tex[1] + 0.5, 0), 479))
                color.append(color_image[y, x, :]/255)

            color = np.array(color)
            print(color)
            print(len(self.vertsMem) )
            if len(self.vertsMem)  > 1:
                self.sp.setData(pos=self.vertsMem*(10/self.inverseSensitivity), color=color, size=0.1)

            # cw, ch = color_image.shape[:2][::-1]
            # v, u = (texcoords * (cw, ch) + 0.5).astype(np.uint32).T
            # print(v.shape)
            # clip texcoords to image
            # np.clip(u, 0, ch - 1, out=u)
            # np.clip(v, 0, cw - 1, out=v)

            # color = np.empty((cw, ch), dtype=np.uint32)
            # perform uv-mapping
            # color = []
            #
            # for n in range(19200):
            #     print("-------", texcoords[n, 0], texcoords[n, 1])
            #     _x = int(texcoords[n, 0] * cw + 0.5)
            #     _y = int(texcoords[n, 1] * ch + 0.5)
            #     print(_x, _y)
            #     if 0 <= _x < cw and 0 <= _y < ch:
            #         # r = color_image[_y, _x, 0] / 255
            #         # g = color_image[_y, _x, 1] / 255
            #         # b = color_image[_y, _x, 2] / 255
            #         r, g, b = 0.7, 0.7, 0.7
            #         a = 1
            #         color.append((r, g, b, a))
            # color = np.array(color)
            # print(color, type(color), color.shape)
    # @staticmethod
    # def view(v):
    #     """apply view transformation on vector array"""
    #     return np.dot(v, state.rotation) + state.pivot - state.translation




app = QtWidgets.QApplication(sys.argv)
w = Window()
app.exec_()
sys.exit()
