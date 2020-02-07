from PyQt5 import QtWidgets
from PyQt5 import QtGui
from PyQt5 import QtCore
import sys
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
from matplotlib import pyplot
from stl import mesh
from mpl_toolkits import mplot3d
import math
import time
import numpy


class Window(QtWidgets.QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("3D ZPT")
        self.setGeometry(0, 0, 500, 500)

        layout = QtWidgets.QVBoxLayout()
        self.plot = PlotCanvas()

        self.rollButton = QtWidgets.QPushButton("roll +10")
        self.rollButton.clicked.connect(lambda: self.plot.rotate(roll=10))

        self.pitchButton = QtWidgets.QPushButton("pitch + 10")
        self.pitchButton.clicked.connect(lambda: self.plot.rotate(pitch=10))

        self.yawButton = QtWidgets.QPushButton("yaw + 10")
        self.yawButton.clicked.connect(lambda: self.plot.rotate(yaw=10))

        self.resetButton = QtWidgets.QPushButton("reset")
        self.resetButton.clicked.connect(self.plot.reset_rotation)

        layout.addWidget(self.plot)
        layout.addWidget(self.rollButton)
        layout.addWidget(self.pitchButton)
        layout.addWidget(self.yawButton)
        layout.addWidget(self.resetButton)
        self.setLayout(layout)
        self.show()


class PlotCanvas(FigureCanvas):
    def __init__(self):
        # self.roll = 0
        # self.pitch = 0
        # self.yaw = 0
        self.mid_point = numpy.array([17.5, 11, 8])
        self.view_ang = 0
        figure = pyplot.figure()
        self.stlAxes = mplot3d.Axes3D(figure)
        FigureCanvas.__init__(self, figure)
        FigureCanvas.setSizePolicy(self,
                                   QtWidgets.QSizePolicy.Expanding,
                                   QtWidgets.QSizePolicy.Expanding)
        FigureCanvas.updateGeometry(self)

        self.reset_rotation()

    def rotate(self, roll=0, pitch=0, yaw=0):
        t0 = time.time()
        # self.roll += roll
        # self.pitch += pitch
        # self.yaw += yaw
        #
        # print(self.roll, self.pitch, self.yaw)

        self.stlAxes.cla()
        self.stlAxes.set_xlim(-25, 10)
        self.stlAxes.set_ylim(35, 70)
        self.stlAxes.set_zlim(-25, 0)

        if not roll == 0:
            self.your_mesh.rotate([1, 0, 0], math.radians(roll), self.mid_point)
        if not pitch == 0:
            self.your_mesh.rotate([0, 1, 0], math.radians(pitch), self.mid_point)
        if not yaw == 0:
            self.your_mesh.rotate([0, 0, 1], math.radians(yaw), self.mid_point)
        self.collection = mplot3d.art3d.Poly3DCollection(self.your_mesh.vectors)
        self.collection.set_facecolor([0.2] * 3)
        self.collection.set_edgecolor([0.5] * 3)
        self.stlAxes.add_collection3d(self.collection)
        pyplot.axis("off")
        self.draw()
        print(time.time() - t0)

    def reset_rotation(self):
        self.your_mesh = mesh.Mesh.from_file('m113.STL')
        self.your_mesh.rotate([-1, 0, 0], math.radians(90), numpy.array([17.5, 11, 8]))
        self.rotate(0, 0, 0)
        self.draw()
        # self.rotate(roll=360 - (self.roll % 360),
        #             pitch=360 - (self.pitch % 360),
        #             yaw=-360 - (self.yaw % 360))
        # self.roll = 0
        # self.pitch = 0
        # self.yaw = 0


app = QtWidgets.QApplication(sys.argv)
w = Window()
app.exec_()
sys.exit()
