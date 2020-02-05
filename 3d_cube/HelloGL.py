from PyQt5 import QtCore      # core Qt functionality
from PyQt5 import QtGui       # extends QtCore with GUI functionality
from PyQt5 import QtOpenGL    # provides QGLWidget, a special OpenGL QWidget
from PyQt5 import QtWidgets
from PyQt5.QtWidgets import (QApplication, QWidget, QLCDNumber, QSlider, QVBoxLayout)
from PyQt5.QtCore import Qt
import OpenGL.GL as gl        # python wrapping of OpenGL
from OpenGL import GLU        # OpenGL Utility Library, extends OpenGL functionality

import sys                    # we'll need this later to run our Qt application
from OpenGL.arrays import vbo
import numpy as np

def stl2mesh3d(stl_mesh):
    # stl_mesh is read by nympy-stl from a stl file; it is  an array of faces/triangles (i.e. three 3d points)
    # this function extracts the unique vertices and the lists I, J, K to define a Plotly mesh3d
    p, q, r = stl_mesh.vectors.shape #(p, 3, 3)
    # the array stl_mesh.vectors.reshape(p*q, r) can contain multiple copies of the same vertex;
    # extract unique vertices from all mesh triangles
    vertices, ixr = np.unique(stl_mesh.vectors.reshape(p*q, r), return_inverse=True, axis=0)
    I = np.take(ixr, [3*k for k in range(p)])
    J = np.take(ixr, [3*k+1 for k in range(p)])
    K = np.take(ixr, [3*k+2 for k in range(p)])
    return vertices, I, J, K

class Window(QWidget):

    def __init__(self):
        super().__init__()
        self.setWindowTitle("gl box")
        self.setGeometry(0, 0, 300, 300)
        self.glWidget = GLWidget


        glWidget = GLWidget(self)
        self.lcd = QLCDNumber()

        s1 = QSlider(Qt.Horizontal)
        s1.valueChanged.connect(lambda val : self.glWidget.rotX(val))
        s1.setMaximum(90)
        s1.setMinimum(0)
        s2 = QSlider(Qt.Horizontal)
        s2.valueChanged.connect(self.handleY)
        s2.setMaximum(90)
        s2.setMinimum(0)
        s3 = QSlider(Qt.Horizontal)
        s3.valueChanged.connect(self.handleZ)
        s3.setMaximum(90)
        s3.setMinimum(0)

        layout = QVBoxLayout()
        layout.addWidget(self.lcd)
        layout.addWidget(glWidget)
        layout.addWidget(s1)
        layout.addWidget(s2)
        layout.addWidget(s3)
        self.setLayout(layout)
        self.glWidget = GLWidget(self)
        # self.initGUI()

#        timer = QtCore.QTimer(self)
#        timer.setInterval(20)  # period, in milliseconds
#        timer.timeout.connect(self.glWidget.updateGL)
#        timer.start()
#        self.show()

    def handleZ(self, event):
        print (event)
        self.lcd.display(event)

    def handleX(self, event1):
        self.glWidget.setRotX(event1)

    def handleY(self, event2):
        self.glWidget.rotY(event2)

class GLWidget(QtOpenGL.QGLWidget):
    def __init__(self, parent=None):
        self.parent = parent
        QtOpenGL.QGLWidget.__init__(self, parent)

    def initializeGL(self):
        self.qglClearColor(QtGui.QColor(0, 0, 255))  # initialize the screen to blue
        gl.glEnable(gl.GL_DEPTH_TEST)  # enable depth testing

        self.initGeometry()

        self.rotX = 0.0
        self.rotY = 0.0
        self.rotZ = 0.0

    def resizeGL(self, width, height):
        gl.glViewport(0, 0, width, height)
        gl.glMatrixMode(gl.GL_PROJECTION)
        gl.glLoadIdentity()
        aspect = width / float(height)

        GLU.gluPerspective(45.0, aspect, 1.0, 100.0)
        gl.glMatrixMode(gl.GL_MODELVIEW)

    def paintGL(self):
        gl.glClear(gl.GL_COLOR_BUFFER_BIT | gl.GL_DEPTH_BUFFER_BIT)

        gl.glPushMatrix()  # push the current matrix to the current stack

        gl.glTranslate(0.0, 0.0, -50.0)  # third, translate cube to specified depth
        gl.glScale(20.0, 20.0, 20.0)  # second, scale cube
        #gl.glRotated(30, 0.5, 0.0, 0.0)
        gl.glRotated(30, 1.0, 0.0, 0.0)
        self.show()
        gl.glRotated(self.rotY, 0.0, 1.0, 0.0)
        gl.glRotated(30, 0.0, 0.0, 1.0)
        gl.glTranslate(-0.5, -0.5, -0.5)  # first, translate cube center to origin


        gl.glEnableClientState(gl.GL_VERTEX_ARRAY)
        gl.glEnableClientState(gl.GL_COLOR_ARRAY)

        gl.glVertexPointer(3, gl.GL_FLOAT, 0, self.vertVBO)
        gl.glColorPointer(3, gl.GL_FLOAT, 0, self.colorVBO)

        gl.glDrawElements(gl.GL_QUADS, len(self.cubeIdxArray), gl.GL_UNSIGNED_INT, self.cubeIdxArray)

        gl.glDisableClientState(gl.GL_VERTEX_ARRAY)
        gl.glDisableClientState(gl.GL_COLOR_ARRAY)

        gl.glPopMatrix()  # restore the previous modelview matrix

    def initGeometry(self):
        self.cubeVtxArray = np.array(
            [[0.0, 0.0, 0.0],
             [1.0, 0.0, 0.0],
             [1.0, 1.0, 0.0],
             [0.0, 1.0, 0.0],
             [0.0, 0.0, 1.0],
             [1.0, 0.0, 1.0],
             [1.0, 1.0, 1.0],
             [0.0, 1.0, 1.0]])
        self.vertVBO = vbo.VBO(np.reshape(self.cubeVtxArray,
                                          (1, -1)).astype(np.float32))
        self.vertVBO.bind()

        self.cubeClrArray = np.array(
            [[0.0, 0.0, 0.0],
             [1.0, 0.0, 0.0],
             [1.0, 1.0, 0.0],
             [0.0, 1.0, 0.0],
             [0.0, 0.0, 1.0],
             [1.0, 0.0, 1.0],
             [1.0, 1.0, 1.0],
             [0.0, 1.0, 1.0]])
        self.colorVBO = vbo.VBO(np.reshape(self.cubeClrArray,
                                           (1, -1)).astype(np.float32))
        self.colorVBO.bind()

        self.cubeIdxArray = np.array(
            [0, 1, 2, 3,
             3, 2, 6, 7,
             1, 0, 4, 5,
             2, 1, 5, 6,
             0, 3, 7, 4,
             7, 6, 5, 4])
    def getMesh(self):
        my_mesh = mesh.Mesh.from_file('C:\\Users\metet\Desktop\Yeni klasör\\menger.stl')
        vertices, I, J, K = stl2mesh3d(self.my_mesh)
        x, y, z = vertices.T
        #self.cubeVtxArray =
        self.vertVBO = vbo.VBO(np.reshape(self.cubeVtxArray,
                                          (1, -1)).astype(np.float32))
        #self.cubeClrArray =
        self.colorVBO = vbo.VBO(np.reshape(self.cubeClrArray,
                                           (1, -1)).astype(np.float32))
        self.colorVBO.bind()
        #self.cubeIdxArray =
        print(I)

    def setRotX(self, val):
        self.rotX = np.pi * val
        print(val)
        self.update()

    def setRotY(self, val):
        self.rotY = np.pi * val

    def setRotZ(self, val):

        self.rotZ = np.pi * val


app = QtWidgets.QApplication(sys.argv)
w = Window()
w.show()
app.exec_()
sys.exit()