import matplotlib.pyplot as plt
import numpy as np

import math
# import urllib2
import urllib.request as urllib2
import requests
# import io as StringIO
from io import BytesIO
from PIL import Image


from PyQt5 import QtWidgets
from PyQt5 import QtGui
from PyQt5 import QtCore
import qimage2ndarray
from PyQt5.QtCore import Qt, pyqtSignal, QSize, QPoint, pyqtSlot, pyqtProperty, QTimer, QRect
from PyQt5.QtGui import QPainter, QColor, QFont, QFontMetricsF, QPalette, QPolygon, QPen, QBrush, QPixmap

import sys


class MapView(QtWidgets.QLabel):
    def __init__(self, parent=None):
        super().__init__(parent=parent)
        self.headers = {
                        'User-Agent': 'My User Agent 1.0',
                        'From': 'youremail@domain.com'  # This is another valid field
                       }
        self.dynamicTiles = [None]*9

        self.getImageCluster(39.973734, 32.761588, 0.002, 0.005, 16)

        # qImage = qimage2ndarray.array2qimage(np.asarray(a))
        # pixmap = QtGui.QPixmap(qImage)
        # self.mapView.setPixmap(pixmap)
        # self.setScaledContents(True)
        # self.update()

    def paintEvent(self, a0: QtGui.QPaintEvent) -> None:
        print("here")
        xmin, ymax = self.deg2num(lat_deg, lon_deg, zoom)
        xmax, ymin = self.deg2num(lat_deg + delta_lat, lon_deg + delta_long, zoom)

        qp = QPainter()
        qp.begin(self)
        qp.drawPixmap(QRect(0, 0, 200, 200), QPixmap("tiles/15_19366_12408.png"))

    @staticmethod
    def deg2num(lat_deg, lon_deg, zoom):
        lat_rad = math.radians(lat_deg)
        n = 2.0 ** zoom
        xtile = int((lon_deg + 180.0) / 360.0 * n)
        ytile = int((1.0 - math.log(math.tan(lat_rad) + (1 / math.cos(lat_rad))) / math.pi) / 2.0 * n)
        return (xtile, ytile)

    @staticmethod
    def num2deg(xtile, ytile, zoom):
        n = 2.0 ** zoom
        lon_deg = xtile / n * 360.0 - 180.0
        lat_rad = math.atan(math.sinh(math.pi * (1 - 2 * ytile / n)))
        lat_deg = math.degrees(lat_rad)
        return (lat_deg, lon_deg)

    def getImageCluster(self, lat_deg, lon_deg, delta_lat, delta_long, zoom):
        smurl = r"http://b.tile.osm.org/{0}/{1}/{2}.png"
        xmin, ymax = self.deg2num(lat_deg, lon_deg, zoom)
        xmax, ymin = self.deg2num(lat_deg + delta_lat, lon_deg + delta_long, zoom)

        # Cluster = Image.new('RGB', ((xmax - xmin + 1) * 256 - 1, (ymax - ymin + 1) * 256 - 1))
        for xtile in range(xmin, xmax + 1):
            for ytile in range(ymin, ymax + 1):
                # try:
                    imgurl = smurl.format(zoom, xtile, ytile)
                    print("Opening: " + imgurl)
                    imgstr = requests.get(imgurl, headers=self.headers).content
                    print(imgstr)
                    tile = Image.open(BytesIO(imgstr))
                    save_path = "tiles/{0}_{1}_{2}.png".format(zoom, xtile, ytile)
                    tile.save(save_path)
                    # Cluster.paste(tile, box=((xtile - xmin) * 256, (ytile - ymin) * 255))
                # except:
                #     print("Couldn't download image")
                #     tile = None

        # return Cluster


class Window(QtWidgets.QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("local maps")
        self.setGeometry(0, 0, 500, 500)

        self.mapView = MapView()
        layout = QtWidgets.QHBoxLayout()
        layout.addWidget(self.mapView)
        self.setLayout(layout)
        self.show()
        # self.mapView.repaint()

app = QtWidgets.QApplication(sys.argv)
w = Window()
app.exec_()
sys.exit()




# https://stackoverflow.com/questions/28476117/easy-openstreetmap-tile-displaying-for-python
# https://stackoverflow.com/questions/7391945/how-do-i-read-image-data-from-a-url-in-python



# if __name__ == '__main__':
#     # 39.973734, 32.761588
#     a = getImageCluster(39.973734, 32.761588, 0.002, 0.005, 15)
#     fig = plt.figure()
#     fig.patch.set_facecolor('white')
#     plt.imshow(np.asarray(a))
#     plt.show()

