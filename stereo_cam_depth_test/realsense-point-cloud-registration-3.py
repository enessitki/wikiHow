import pyqtgraph.opengl as gl
from pyqtgraph.Qt import QtCore, QtWidgets
import numpy as np
import sys
from classes.D435 import D435
from classes.T265 import T265


class Window(gl.GLViewWidget):
    def __init__(self, parent=None):
        super(Window, self).__init__(parent=parent)
        self.opts['distance'] = 20
        self.setWindowTitle('pyqtgraph example: GLScatterPlotItem')

        self.g = gl.GLGridItem()
        self.addItem(self.g)

        pos = np.array([[0, 0, 0], [0, 1, 0]])

        sp1 = gl.GLScatterPlotItem(pos=pos, size=np.array([1, 2]),
                                   color=np.array([(1, 1, 1, 1), (0.5, 0.5, 0.5, 1)]), pxMode=False)
        # sp1 = gl.GLScatterPlotItem(pos=pos, size=size, color=color, pxMode=False)
        sp1.translate(5, 5, 0)
        self.addItem(sp1)

        self.d435 = D435(clipping_distance_in_meters=1000)
        self.t265 = T265()

        self.show()

        self.timer = QtCore.QTimer()
        self.timer.setInterval(10)
        self.timer.timeout.connect(self.run)
        self.timer.start()

    def run(self):
        verts, texcoords = self.d435.get_last_frames()
        pose = self.t265.update_frames()
        print(verts.shape)



app = QtWidgets.QApplication(sys.argv)
w = Window()
app.exec_()
sys.exit()
