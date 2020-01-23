"""
install note
pip install PyQt5
pip install pyqtwebengine
pip install pyqtlet

Mobile Atlas Creator
https://stackoverflow.com/questions/43608919/html-offline-map-with-local-tiles-via-leaflet

pyqtlet
https://github.com/skylarkdrones/pyqtlet
https://leafletjs.com/reference-1.6.0.html#tooltip
"""
from PyQt5 import QtWidgets
from PyQt5 import QtGui
from PyQt5 import QtCore
import sys
from pyqtlet import L, MapWidget


class Window(QtWidgets.QWidget):

    def __init__(self):
        super().__init__()
        self.setWindowTitle("local maps")
        self.setGeometry(0, 0, 500, 500)

        layout = QtWidgets.QVBoxLayout(self)
        self.mapWidget = MapWidget()
        layout.addWidget(self.mapWidget)

        # Working with the maps with pyqtlet
        self.map = L.map(self.mapWidget,
                    {"maxZoom": 15,
                     "zoomDelta": 2,
                     "scrollWheelZoom": False,
                     "attributionControl": False})

        self.map.setView([39.97, 32.76], 3)
        L.tileLayer('file:///home/esetron/PycharmProjects/wikiHow/offline_maps/4uMaps/{z}/{x}/{y}.png').addTo(self.map)

        self.marker = L.marker([39.973734, 32.761588])
        self.marker.bindPopup('Marked position.')
        self.map.addLayer(self.marker)

        self.polyline = L.polyline([[40, 33], [39.97, 32.76], [39, 32]],
                                   {
                                       # "color": 'red',
                                       "color": "#a1ff42",
                                       "weight": 3,
                                       "opacity": 1,
                                       "smoothFactor": 1
                                   }
                                   )
        self.polyline.addTo(self.map)

        # pointList = [L.LatLng(39.973734, 32.761588)]

        print(dir(L))


        self.show()


app = QtWidgets.QApplication(sys.argv)
w = Window()
app.exec_()
sys.exit()
