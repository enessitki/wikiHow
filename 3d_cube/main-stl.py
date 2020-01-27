import plotly
import plotly.offline as ply
import numpy as np
import plotly.graph_objs as go
from stl import mesh
import sys
import os
from PyQt5.QtGui import QGuiApplication
from PyQt5.QtCore import QUrl
from PyQt5.QtWidgets import *
from PyQt5.QtWebKitWidgets import QWebView
import chart_studio.plotly as py

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


my_mesh = mesh.Mesh.from_file('C:\\Users\metet\Desktop\Yeni klasör\\M113_APC1.STL')
my_mesh.vectors.shape
print(my_mesh.vectors.shape)

vertices, I, J, K = stl2mesh3d(my_mesh)
x, y, z = vertices.T

vertices.shape
print(vertices.shape)
colorscale= [[0, '#e5dee5'], [1, '#e5dee5']]

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
            name='M113',
            showscale=False)
#print(mesh3D)

#title = "Mesh3d from a STL file<br>menger.html"
layout = go.Layout(paper_bgcolor='rgb(1,1,1)',
            title_text='', title_x=0.5,
                   font_color='white',
            width=800,
            height=800,
            scene_camera=dict(eye=dict(x=1.25, y=-1.25, z=1)),
            scene_xaxis_visible=False,
            scene_yaxis_visible=False,
            scene_zaxis_visible=False)
#print(layout)

fig = go.Figure(data=[mesh3D], layout=layout)

fig.data[0].update(lighting=dict(ambient= 0.18,
                                 diffuse= 1,
                                 fresnel=  .1,
                                 specular= 1,
                                 roughness= .1,
                                 facenormalsepsilon=0))
fig.data[0].update(lightposition=dict(x=3000,
                                      y=3000,
                                      z=10000));

#print (fig)
#ply.plot(fig, filename='M113')

app = QApplication(sys.argv)

browser = QWebView()
file_path = os.path.abspath(os.path.join(os.path.dirname(__file__), 'C:\\Users\metet\PycharmProjects\\numpy-stl-Test\\M113.html'))
local_url = QUrl.fromLocalFile(file_path)
print(local_url)
browser.load(local_url)

#val = browser.shape
#print(val)
#browser.show()

#app.exec_()