from PyQt5 import QtWidgets
from PyQt5 import QtGui
from PyQt5 import QtCore
from PyQt5 import Qt
from PyQt5.QtTest import QTest
import sys
from pyqtlet import L, MapWidget
from PyQt5.QtWidgets import QApplication, QVBoxLayout, QWidget, QPushButton


class MapWindow(QWidget):
    def __init__(self):
        # Setting up the widgets and layout
        super().__init__()
        self.mapWidget = MapWidget()
        self.layoutHarita = QVBoxLayout()
        self.layoutHarita.addWidget(self.mapWidget)
        self.setLayout(self.layoutHarita)
        self.startButton = QtWidgets.QPushButton("Start")
        self.startButton.clicked.connect(self.player.start)



        # Working with the maps with pyqtlet
        self.map = L.map(self.mapWidget)
        self.map.setView([39.973734, 32.761588], 10)
        L.tileLayer('http://{s}.tile.osm.org/{z}/{x}/{y}.png').addTo(self.map)
        self.marker = L.marker([39.973734, 32.761588])
        self.marker.bindPopup('Maps are a treasure.')
        self.map.addLayer(self.marker)
        self.show()


if __name__ == '__main__':
    app = QApplication(sys.argv)
    widget = MapWindow()
    sys.exit(app.exec_())