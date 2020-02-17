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
        # self.z += 0.1
        # print(self.z)
        self.roll += roll
        self.pitch += pitch
        self.yaw += yaw

        self.roll = self.roll % 360
        self.pitch = self.pitch % 360
        self.yaw = self.yaw % 360
        self.camera.SetRoll(self.yaw)
        self.camera.Azimuth(pitch)

        # self.camera.UpdateViewport()
        # self.camera.SetRoll(self.yaw * numpy.pi / 180)

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
        # if camera_position[2] >= 0:
        #     self.upView[1] = 1
        # else:
        #     self.upView[1] = -1

        vpl.view(camera_position=camera_position, up_view=self.upView)
        self.update()
        # if not roll == 0:
        #     self.zptMesh.rotate([1, 0, 0], math.radians(roll), self.mid_point)
        # if not pitch == 0:
        #     self.zptMesh.rotate([0, 1, 0], math.radians(pitch), self.mid_point)
        # if not yaw == 0:
        #     self.zptMesh.rotate([0, 0, 1], math.radians(yaw), self.mid_point)
        # self.repaint()
        # # vpl.mesh_plot(self.zptMesh, color="green")
        # self.update()
        # print(self.camera.DirectionOfProjection)
        print(dir(self.camera))

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


# class PlotCanvas(FigureCanvas):
#     def __init__(self):
#         # self.roll = 0
#         # self.pitch = 0
#         # self.yaw = 0
#         self.mid_point = numpy.array([17.5, 11, 8])
#         self.view_ang = 0
#         figure = pyplot.figure()
#         self.stlAxes = mplot3d.Axes3D(figure)
#         FigureCanvas.__init__(self, figure)
#         FigureCanvas.setSizePolicy(self,
#                                    QtWidgets.QSizePolicy.Expanding,
#                                    QtWidgets.QSizePolicy.Expanding)
#         FigureCanvas.updateGeometry(self)
#
#         self.reset_rotation()
#
#     def rotate(self, roll=0, pitch=0, yaw=0):
#         t0 = time.time()
#         # self.roll += roll
#         # self.pitch += pitch
#         # self.yaw += yaw
#         #
#         # print(self.roll, self.pitch, self.yaw)
#
#         self.stlAxes.cla()
#         self.stlAxes.set_xlim(-25, 10)
#         self.stlAxes.set_ylim(35, 70)
#         self.stlAxes.set_zlim(-25, 0)
#
#         if not roll == 0:
#             self.your_mesh.rotate([1, 0, 0], math.radians(roll), self.mid_point)
#         if not pitch == 0:
#             self.your_mesh.rotate([0, 1, 0], math.radians(pitch), self.mid_point)
#         if not yaw == 0:
#             self.your_mesh.rotate([0, 0, 1], math.radians(yaw), self.mid_point)
#         self.collection = mplot3d.art3d.Poly3DCollection(self.your_mesh.vectors)
#         ls = LightSource(azdeg=225.0, altdeg=45.0)
#
#         min = numpy.min(ls.shade_normals(self.your_mesh.normals, fraction=1.0))  # min shade value
#         max = numpy.max(ls.shade_normals(self.your_mesh.normals, fraction=1.0))  # max shade value
#         diff = max - min
#         newMin = 0.3
#         newMax = 0.95
#         newdiff = newMax - newMin
#         colourRGB = numpy.array((0.3, 0.3, 0.3, 1.0))
#         rgbNew = numpy.array([colourRGB * (newMin + newdiff * ((shade - min) / diff)) for shade in
#                            ls.shade_normals(self.your_mesh.normals, fraction=1.0)])
#
#         print(rgbNew)
#         # print(len(self.your_mesh.normals))
#         print(numpy.array([[x / 375] * 4 for x in range(0, 375)]))
#         self.collection.set_facecolors([(0.1, 0.1, 0.1, 0.1),(0.8, 0.8, 0.8, 0.8)])
#         # self.collection.set_facecolors(numpy.array([[0.1, 0.1, 0.1, 0.1], [0.8, 0.8, 0.8, 0.8]]))
#         # self.collection.set_facecolors(numpy.array([[x/375]*3 +[0.62] for x in range(0, 375)]))
#         self.collection.set_facecolor(rgbNew)
#         # self.collection.set_facecolor([0.2] * 3)
#         # self.collection.set_edgecolor([0.5] * 3)
#         # print(dir(self.collection))
#         self.stlAxes.add_collection3d(self.collection)
#         pyplot.axis("off")
#         self.draw()
#         print(time.time() - t0)
#
#     def reset_rotation(self):
#         self.your_mesh = mesh.Mesh.from_file('m113.STL')
#         # print(self.your_mesh.data)
#         # mesh.Mesh.remove_duplicate_polygons(self.your_mesh.data)
#         # mesh.Mesh.remove_empty_areas(self.your_mesh.data)
#         # print(dir(self.your_mesh))
#
#         self.your_mesh.rotate([-1, 0, 0], math.radians(90), numpy.array([17.5, 11, 8]))
#         self.rotate(0, 0, 0)
#         self.draw()
#         # self.rotate(roll=360 - (self.roll % 360),
#         #             pitch=360 - (self.pitch % 360),
#         #             yaw=-360 - (self.yaw % 360))
#         # self.roll = 0
#         # self.pitch = 0
#         # self.yaw = 0


app = QtWidgets.QApplication(sys.argv)
w = Window()
app.exec_()
sys.exit()
