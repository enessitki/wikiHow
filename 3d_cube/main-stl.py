import plotly
import plotly.offline as ply
import numpy as np
import plotly.graph_objs as go
from stl import mesh
import os
from OpenGL.arrays import vbo
from PyQt5 import QtWidgets
from PyQt5.QtCore import *
from PyQt5.QtWidgets import *
from PyQt5.QtWebKitWidgets import QWebView
from matplotlib import pyplot
import sys, math
import time
from operator import itemgetter

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

class window(QtWidgets.QWidget):
    def __init__(self):
        super().__init__(parent=None)
        #theta = 0
        browser = QWebView()
        self.draw_3d()
        print("here", self.local_url)
        browser.load(self.local_url)
        self.s1 = QSlider(Qt.Horizontal)
        self.s1.setMinimum(-3)
        self.s1.setMaximum(3)
        self.s1.setValue(0)
        self.s2 = QSlider(Qt.Horizontal)
        self.s2.setMinimum(0)
        self.s2.setMaximum(90)
        self.s2.setValue(0)
        #browser.update_layout(scene_camera= dict(eye =dict(x=0, y=2.5, z= 2.5)))
        #self.fig.update_layout(scene_camera=dict(eye = dict(x=0, y=2.5, z= 2.5)))
        self.s3 = QSlider(Qt.Horizontal)
        self.s3.setMinimum(0)
        self.s3.setMaximum(90)
        self.s3.setValue(0)
        layout = QtWidgets.QVBoxLayout(self)
        layout.addWidget(browser)
        layout.addWidget(self.s1)
        layout.addWidget(self.s2)
        layout.addWidget(self.s3)

        self.s1.valueChanged.connect(self.draw_3d)
        self.s2.valueChanged.connect(self.setY)
        self.s3.valueChanged.connect(self.setZ)

        self.show()
        #app.exec_()

    def setX(self):
        print("set x", self.s1.value())
        theta = self.s1.value()
        #self.my_mesh.rotate([0.5, 0.0, 0.0], math.radians(self.s1.value()))
        #radX= self.s1.value()
        #return theta

    def setY(self):
        radY= self.s1.value()
        return radY

    def setZ(self):
        radZ= self.s1.value()
        return radZ

    def openSTL(self):
        theMesh = mesh.Mesh.from_file('C:\\Users\metet\Desktop\Yeni klasör\\menger.stl')
        #print (theMesh.x)
        #radX = self.setX()
        #radY = self.setY()
        #radZ = self.setZ()
        radX = 0
        radY = 0
        radZ = 0
        theMesh.rotate([0.5, 0.0, 0.0], math.radians(radX))
        theMesh.rotate([0.0, 0.5, 0.0], math.radians(radY))
        theMesh.rotate([0.0, 0.5, 0.5], math.radians(radZ))
        #newMesh= theMesh
        #print (newMesh.x)
        return theMesh

    def draw_3d(self):
#        my_mesh = mesh.Mesh.from_file('C:\\Users\metet\Desktop\Yeni klasör\\menger.STL')
        self.my_mesh = self.openSTL()
        my_mesh.vectors.shape
        print(self.my_mesh.vectors.shape)
        vertices, I, J, K = stl2mesh3d(self.my_mesh)
        x, y, z = vertices.T
        #print("set x", self.s1.value())
        vertices.shape
 #       print(vertices.shape)
        colorscale = [[0, '#e5dee5'], [1, '#e5dee5']]
  #      my_mesh
        mesh3D = go.Mesh3d(
            x=x,
            y=y,
            z=z,
            i=I,
            j=J,
            k=K,
            flatshading=True,
            colorscale=colorscale,
            intensity=z,
            name='meri',
            showscale=False)
        layout = go.Layout(paper_bgcolor='rgb(1,1,1)',
                           title_text='',
                           title_x=0.5,
                           font_color='white',
                           width=800,
                           height=800,
                           dragmode=False,
                           scene_xaxis_visible=False,
                           scene_yaxis_visible=False,
                           scene_zaxis_visible=False,
                           #margin = dict(t=30, r=0, l=50, b=10)
                           scene_camera=dict(eye=dict(x=0, y=1.25, z=0))
                           )
        #colorscale
        self.fig = go.Figure(data=[mesh3D], layout=layout)
        self.fig.data[0].update(lighting=dict(ambient=0.18,
                                         diffuse=1,
                                         fresnel=.1,
                                         specular=1,
                                         roughness=.1,
                                         facenormalsepsilon=0))
        self.fig.data[0].update()
        self.fig.data[0].update(lightposition=dict(x=3000,
                                              y=3000,
                                              z=10000))
        #self.fig.update_layout(scene_camera = dict(eye = dict(x=0, y=0, z=1.25)))
        #fig.write_html('C:\\Users\metet\PycharmProjects\\numpy-stl-Test\\venv\\.html')
        ply.plot(self.fig, filename='meri', auto_open=False)
        file_path = os.path.abspath(os.path.join(os.path.dirname(__file__), 'C:\\Users\metet\PycharmProjects\\numpy-stl-Test\\menger.html'))
        self.local_url = QUrl.fromLocalFile(file_path)


app = QApplication(sys.argv)
w = window()
#browser = QWebView()
#file_path = os.path.abspath(os.path.join(os.path.dirname(__file__), 'C:\\Users\metet\PycharmProjects\\numpy-stl-Test\\menger.html'))
#local_url = QUrl.fromLocalFile(file_path)
#print(local_url)
#browser.load(local_url)
#browser.show()
app.exec_()


#        theMesh = mesh.Mesh.from_file('C:\\Users\metet\Desktop\Yeni klasör\\menger.stl')
#        p, q, r = theMesh.vectors.shape

#        vertices, ixr = np.unique(theMesh.vectors.reshape(p * q, r), return_inverse=True, axis=0)
#        I = np.take(ixr, [3 * k for k in range(p)])
#        J = np.take(ixr, [3 * k + 1 for k in range(p)])
#        K = np.take(ixr, [3 * k + 2 for k in range(p)])
#        x, y, z = self.vertices.T