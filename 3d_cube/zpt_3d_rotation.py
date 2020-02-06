from PyQt5 import QtWidgets
from PyQt5 import QtGui
from PyQt5 import QtCore
import sys
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
from matplotlib import pyplot
from stl import mesh
from mpl_toolkits import mplot3d
import random


class Window(QtWidgets.QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("3D ZPT")
        self.setGeometry(0, 0, 500, 500)

        layout = QtWidgets.QVBoxLayout()
        self.plot = PlotCanvas()
        self.resetButton = QtWidgets.QPushButton("Reset")
        self.resetButton.clicked.connect(self.reset_plot)
        layout.addWidget(self.plot)
        layout.addWidget(self.resetButton)
        self.setLayout(layout)
        self.show()

    def reset_plot(self):
        self.plot.reset_figure()
        self.plot.update_plot([1, 2, 3, 4, 5])


class PlotCanvas(FigureCanvas):
    def __init__(self):
        figure = pyplot.figure()
        axes = mplot3d.Axes3D(figure)
        FigureCanvas.__init__(self, figure)
        # Load the STL files and add the vectors to the plot
        your_mesh = mesh.Mesh.from_file('m113.STL')
        collection = mplot3d.art3d.Poly3DCollection(your_mesh.vectors)
        collection.set_facecolor([0.3] * 3)
        collection.set_edgecolor([0.4] * 3)
        axes.add_collection3d(collection)

        # Auto scale to the mesh size
        scale = your_mesh.points.flatten("C")
        axes.auto_scale_xyz(scale, scale, scale)

        # Show the plot to the screen
        self.draw()

    # def __init__(self, parent=None, width=5, height=4, dpi=100):
    #     self.fig = Figure(figsize=(width, height), dpi=dpi)
    #     self.axes = self.fig.add_subplot(111)
    #
    #     FigureCanvas.__init__(self, self.fig)
    #     self.setParent(parent)
    #
    #     FigureCanvas.setSizePolicy(self,
    #             QtWidgets.QSizePolicy.Expanding,
    #             QtWidgets.QSizePolicy.Expanding)
    #     FigureCanvas.updateGeometry(self)
    #     self.plot()
    #
    # def plot(self):
    #     data = [random.random() for i in range(25)]
    #     self.axes.plot(data, 'r-')
    #     self.draw()
    #
    # def update_plot(self, data):
    #     self.axes.plot(data, 'r-')
    #     self.draw()
    #
    # def reset_figure(self):
    #     self.axes.clear()



app = QtWidgets.QApplication(sys.argv)
w = Window()
app.exec_()
sys.exit()

#
# # Create a new plot
# figure = pyplot.figure()
# axes = mplot3d.Axes3D(figure)
#
# # Load the STL files and add the vectors to the plot
# your_mesh = mesh.Mesh.from_file('m113.STL')
# print(dir(your_mesh))
# print(your_mesh.vectors)
# # print(your_mesh.v1)
# # print(your_mesh.v2)
# #axes.plot_trisurf(your_mesh.x, your_mesh.y, your_mesh.z, linewidth=0.2, antialiased=True)
# collection = mplot3d.art3d.Poly3DCollection(your_mesh.vectors)
# collection.set_facecolor([0.3]*3)
# collection.set_edgecolor([0.4]*3)
# axes.add_collection3d(collection)
# print(dir(axes))
#
# # Auto scale to the mesh size
# scale = your_mesh.points.flatten('C')
# axes.auto_scale_xyz(scale, scale, scale)
#
# # Show the plot to the screen
# pyplot.show()
