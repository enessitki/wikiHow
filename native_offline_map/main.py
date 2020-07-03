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
import os

# https://stackoverflow.com/questions/28476117/easy-openstreetmap-tile-displaying-for-python
# https://stackoverflow.com/questions/7391945/how-do-i-read-image-data-from-a-url-in-python


class MapView(QtWidgets.QLabel):
    def __init__(self, lat, lon, zoom, parent=None):
        super().__init__(parent=parent)
        self.x0 = None
        self.y0 = None
        self.XShift = 0
        self.YShift = 0
        self.isPressed = False
        self.headers = {
                        'User-Agent': 'My User Agent 1.0',
                        'From': 'youremail@domain.com'  # This is another valid field
                       }
        self.reference_point = None
        self.native_zoom = 1
        self.set_reference(lat, lon, zoom)
        self.markers = {}

        # qImage = qimage2ndarray.array2qimage(np.asarray(a))
        # pixmap = QtGui.QPixmap(qImage)
        # self.mapView.setPixmap(pixmap)
        # self.setScaledContents(True)
        # self.update()

    def paintEvent(self, a0: QtGui.QPaintEvent) -> None:
        if self.reference_point is not None:
            lat_double, lon_double, zoom = self.reference_point
            h = self.size().height()
            w = self.size().width()
            dx = int(w)
            dy = int(h)
            # dx = int(w) * self.native_zoom
            # dy = int(h) * self.native_zoom
            # native_zoom_offset_x = dx*(self.native_zoom-1)
            # native_zoom_offset_y = dy*(self.native_zoom-1)

            xmid, ymid = int(lat_double), int(lon_double)
            xmid_, ymid_ = lat_double, lon_double
            offset_x, offset_y = (xmid_ - xmid), (ymid_ - ymid)
            xmin, ymax = xmid - 1, ymid + 1
            xmax, ymin = xmid + 1, ymid - 1

            qp = QPainter()
            qp.begin(self)

            x, y = - dx + self.XShift, -dy + self.YShift
            x += (0.5 - offset_x) * dx
            y += (0.5 - offset_y) * dy
            # x -= native_zoom_offset_x
            # y -= native_zoom_offset_y
            x0 = x
            y0 = y

            self.reference_point = lat_double + self.XShift / dx, lon_double + self.YShift / dy, zoom
            self.XShift = 0
            self.YShift = 0

            # for n in [[0, 1], [1, 0], [0, -1], [-1, 0]]:
            for n in [[0, 0]]:
                if not os.path.isfile("tiles/{0}_{1}_{2}.png".format(zoom, xmid + n[0], ymid + n[1])):
                    self.getImageCluster(xmin, ymid, zoom)
                    break

            for xtile in range(xmin, xmax + 1):
                for ytile in range(ymin, ymax + 1):
                    save_path = None

                    try:
                        save_path = "tiles/{0}_{1}_{2}.png".format(zoom, xtile, ytile)
                        qp.drawPixmap(QRect(x, y, dx, dy), QPixmap(save_path))
                    except:
                        print("tile not found:", save_path)

                    y += dy

                y = y0
                x += dx

            # add markers
            for name in self.markers.keys():
                lat, lon, color, title, size, font = self.markers[name]
                xtile, ytile = self.deg2double(lat, lon, zoom)
                if xmin <= xtile <= xmax + 1 and ymin <= ytile <= ymax:
                    x, y = xtile - xmin, ytile - ymin
                    x, y = x0 + x*dx, y0 + y*dy
                    qp.setBrush(QBrush(color, Qt.SolidPattern))
                    qp.drawEllipse(x - size / 2, y - size / 2, size, size)

                    if not title == "":
                        qp.setFont(QFont('Decorative', font))
                        qp.drawText(x - size / 2, y - 2 - size / 2, title),

            # if self.native_zoom > 1:
            #     print(self.native_zoom)
                # qp.translate(int(dx/2), int(dy/2))
                # qp.scale(self.native_zoom, self.native_zoom)

            qp.end()

    def mousePressEvent(self, a0: QtGui.QMouseEvent) -> None:
        self.isPressed = True
        # h = self.size().height()
        # w = self.size().width()

        # lat_deg, lon_deg, zoom = self.reference_point
        # xmid, ymid = self.deg2num(lat_deg, lon_deg, zoom)
        # xmin, ymax = xmid - 1, ymid + 1
        # xmax, ymin = xmid + 1, ymid - 1
        # xtile = xmin + a0.x()/w*3
        # ytile = ymin + a0.y()/h*3
        # lat, lon = self.num2deg(xtile, ytile, zoom)
        # print(lat, lon)

    def mouseReleaseEvent(self, a0: QtGui.QMouseEvent) -> None:
        self.isPressed = False
        self.x0 = None
        self.y0 = None

    def mouseMoveEvent(self, a0: QtGui.QMouseEvent) -> None:
        if self.isPressed:
            if self.x0 is None:
                self.x0 = a0.globalX()
                self.y0 = a0.globalY()
            else:
                dx = - self.x0 + a0.globalX()
                dy = - self.y0 + a0.globalY()
                self.XShift -= dx
                self.YShift -= dy
                self.update()
                self.x0 = a0.globalX()
                self.y0 = a0.globalY()

    @staticmethod
    def deg2num(lat_deg, lon_deg, zoom):
        lat_rad = math.radians(lat_deg)
        n = 2.0 ** zoom
        xtile = int((lon_deg + 180.0) / 360.0 * n)
        ytile = int((1.0 - math.log(math.tan(lat_rad) + (1 / math.cos(lat_rad))) / math.pi) / 2.0 * n)
        return (xtile, ytile)

    @staticmethod
    def deg2double(lat_deg, lon_deg, zoom):
        lat_rad = math.radians(lat_deg)
        n = 2.0 ** zoom
        xtile = (lon_deg + 180.0) / 360.0 * n
        ytile = (1.0 - math.log(math.tan(lat_rad) + (1 / math.cos(lat_rad))) / math.pi) / 2.0 * n
        return (xtile, ytile)

    @staticmethod
    def num2deg(xtile, ytile, zoom):
        n = 2.0 ** zoom
        lon_deg = xtile / n * 360.0 - 180.0
        lat_rad = math.atan(math.sinh(math.pi * (1 - 2 * ytile / n)))
        lat_deg = math.degrees(lat_rad)
        return (lat_deg, lon_deg)

    def getImageCluster(self, xmid, ymid, zoom):
        smurl = r"http://b.tile.osm.org/{0}/{1}/{2}.png"
        # xmin, ymax = self.deg2num(lat_deg, lon_deg, zoom)
        # xmax, ymin = self.deg2num(lat_deg + delta_lat, lon_deg + delta_long, zoom)
        # xmid, ymid = self.deg2num(lat_deg, lon_deg, zoom)
        xmin, ymax = xmid - 1, ymid + 1
        xmax, ymin = xmid + 1, ymid - 1

        # Cluster = Image.new('RGB', ((xmax - xmin + 1) * 256 - 1, (ymax - ymin + 1) * 256 - 1))
        for xtile in range(xmin, xmax + 1):
            for ytile in range(ymin, ymax + 1):
                try:
                    imgurl = smurl.format(zoom, xtile, ytile)
                    print("Opening: " + imgurl)
                    imgstr = requests.get(imgurl, headers=self.headers).content
                    print(imgstr)
                    tile = Image.open(BytesIO(imgstr))
                    save_path = "tiles/{0}_{1}_{2}.png".format(zoom, xtile, ytile)
                    tile.save(save_path)
                    # Cluster.paste(tile, box=((xtile - xmin) * 256, (ytile - ymin) * 255))
                except:
                    print("Couldn't download image")
                    tile = None

        # return Cluster

    def set_reference(self, lat, lon, zoom):
        xtile, ytile = self.deg2double(lat, lon, zoom)
        self.reference_point = xtile, ytile, zoom

    def zoom_in(self):
        lat_double, lon_double, zoom = self.reference_point
        self.zoom_to(zoom + 1)

    def zoom_out(self):
        lat_double, lon_double, zoom = self.reference_point
        self.zoom_to(zoom - 1)

    def zoom_to(self, level):
        if 0 <= level <= 19:
            lat_double, lon_double, zoom = self.reference_point
            lat, lon = self.num2deg(lat_double, lon_double, zoom)
            zoom = level
            lat_double, lon_double = self.deg2double(lat, lon, zoom)
            self.reference_point = lat_double, lon_double, zoom
            self.update()

    def native_zoom_in(self):
        self.native_zoom_to(self.native_zoom + 1)

    def native_zoom_out(self):
        self.native_zoom_to(self.native_zoom - 1)

    def native_zoom_to(self, level):
        if 1 <= level <= 5:
            self.native_zoom = level
            self.update()

    def add_marker(self, name, lat, lon, color=Qt.red, title="", size=10, font=10):
        self.markers[name] = (lat, lon, color, title, size, font)


class Window(QtWidgets.QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("local maps")
        self.setGeometry(0, 0, 800, 800)

        self.mapView = MapView(39.973734, 32.761588, 19)
        self.mapView.add_marker("ukb", 39.973734, 32.761588, title="UKB")
        # self.mapView.setFixedSize(128, 128)

        self.zoomIn = QtWidgets.QPushButton("Yakınlaştır")
        self.zoomOut = QtWidgets.QPushButton("Uzaklaştır")

        self.zoomIn.clicked.connect(self.mapView.zoom_in)
        self.zoomOut.clicked.connect(self.mapView.zoom_out)

        self.nativeZoomIn = QtWidgets.QPushButton("Native Yakınlaştır")
        self.nativeZoomOut = QtWidgets.QPushButton("Native Uzaklaştır")

        self.nativeZoomIn.clicked.connect(self.mapView.native_zoom_in)
        self.nativeZoomOut.clicked.connect(self.mapView.native_zoom_out)

        self.moveMarker = QtWidgets.QPushButton("Move the marker")
        self.moveMarker.clicked.connect(self.move_marker)

        layout = QtWidgets.QVBoxLayout()
        layout.addWidget(self.mapView)
        layout.addWidget(self.zoomIn)
        layout.addWidget(self.zoomOut)
        layout.addWidget(self.nativeZoomIn)
        layout.addWidget(self.nativeZoomOut)
        layout.addWidget(self.moveMarker)

        self.setLayout(layout)
        self.show()

    def move_marker(self):
        lat, lon, color, title, size, font = self.mapView.markers["ukb"]
        lat = lat + 0.00001
        self.mapView.markers["ukb"] = lat, lon, color, title, size, font
        self.mapView.update()


app = QtWidgets.QApplication(sys.argv)
win = Window()
app.exec_()
sys.exit()








# if __name__ == '__main__':
#     # 39.973734, 32.761588
#     a = getImageCluster(39.973734, 32.761588, 0.002, 0.005, 15)
#     fig = plt.figure()
#     fig.patch.set_facecolor('white')
#     plt.imshow(np.asarray(a))
#     plt.show()

