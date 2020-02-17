from PyQt5 import QtWidgets
from PyQt5 import QtGui
from PyQt5 import QtCore
import sys
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
from matplotlib import pyplot
from stl import mesh
from mpl_toolkits import mplot3d
from matplotlib.colors import LightSource
import math
import time
import numpy
import vtkplotlib as vpl


class Window(QtWidgets.QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("3D ZPT")
        self.setGeometry(0, 0, 500, 500)

        layout = QtWidgets.QVBoxLayout()

        self.figure = ZptFigure()

        self.rollButton = QtWidgets.QPushButton("roll +10")
        self.rollButton.clicked.connect(lambda: self.figure.rotate(roll=10))

        self.pitchButton = QtWidgets.QPushButton("pitch + 10")
        self.pitchButton.clicked.connect(lambda: self.figure.rotate(pitch=10))

        self.yawButton = QtWidgets.QPushButton("yaw + 10")
        self.yawButton.clicked.connect(lambda: self.figure.rotate(yaw=10))

        self.resetButton = QtWidgets.QPushButton("reset")
        self.resetButton.clicked.connect(self.figure.reset_rotation)

        layout.addWidget(self.figure)
        layout.addWidget(self.rollButton)
        layout.addWidget(self.pitchButton)
        layout.addWidget(self.yawButton)
        layout.addWidget(self.resetButton)
        self.setLayout(layout)
        self.show()
        self.figure.show()


class ZptFigure(vpl.QtFigure):
    def __init__(self):
        super().__init__()
        self.mid_point = numpy.array([17.5, 11, 8])
        self.zptMesh = mesh.Mesh.from_file('m113.STL')
        vpl.mesh_plot(self.zptMesh, color="green")
        vpl.reset_camera(self)
        self.cameraPosition = numpy.array([0, 0, 1])
        self.upView = [0, 1, 0]
        self.roll = 5
        self.pitch = 0
        self.yaw = 0
        vpl.view(camera_position=self.cameraPosition, up_view=self.upView)
        self.camera.SetViewAngle(30)
        self.update()

    def rotate(self, roll=0, pitch=0, yaw=0):
        self.roll += roll
        self.pitch += pitch
        self.yaw += yaw

        self.roll = self.roll % 360
        self.pitch = self.pitch % 360
        self.yaw = self.yaw % 360
        print(self.roll, self.pitch, self.yaw)
        camera_position = self.eulerAnglesToRotationMatrix([self.roll * numpy.pi / 180,
                                                            self.pitch * numpy.pi / 180,
                                                            0 * numpy.pi / 180],
                                                           self.cameraPosition)
        print(camera_position)
        if 270 > self.roll > 90:
            self.upView[1] = -1
        else:
            self.upView[1] = 1

        vpl.view(camera_position=camera_position, up_view=self.upView)
        self.camera.SetRoll(self.yaw)
        self.update()

    def reset_rotation(self):
        self.roll = 0
        self.pitch = 0
        self.yaw = 0
        vpl.view(camera_position=self.cameraPosition, up_view=self.upView)
        self.update()

    # Calculates Rotation Matrix given euler angles.
    def eulerAnglesToRotationMatrix(self, theta, vec):
        R_x = numpy.array([[1, 0, 0],
                        [0, math.cos(theta[0]), -math.sin(theta[0])],
                        [0, math.sin(theta[0]), math.cos(theta[0])]
                        ])

        R_y = numpy.array([[math.cos(theta[1]), 0, math.sin(theta[1])],
                        [0, 1, 0],
                        [-math.sin(theta[1]), 0, math.cos(theta[1])]
                        ])

        R_z = numpy.array([[math.cos(theta[2]), -math.sin(theta[2]), 0],
                        [math.sin(theta[2]), math.cos(theta[2]), 0],
                        [0, 0, 1]
                        ])

        R = numpy.dot(R_z, numpy.dot(R_y, R_x))

        new_vec = numpy.dot(R, vec)

        return new_vec


app = QtWidgets.QApplication(sys.argv)
w = Window()
app.exec_()
sys.exit()
