from PyQt5.QtCore import Qt, pyqtSignal, QSize, QPoint, pyqtSlot, pyqtProperty, QTimer
from PyQt5.QtGui import QPainter, QColor, QFont, QFontMetricsF, QPalette, QPolygon, QPen, QBrush
from PyQt5 import QtWidgets
import math
import sys


class ImuView2D(QtWidgets.QWidget):
    def __init__(self, parent=None):
        super().__init__(parent=parent)
        self.setGeometry(0, 0, 250, 250)
        self.setFixedWidth(250)
        self.setFixedHeight(250)

        # args
        self.max_width = 250
        self.max_height = 250
        self.margin = self.max_width/20
        self.mid_size = self.max_width/5
        self.min_size = self.max_width/10
        self.font_size = 16

        # vars
        self.roll = 0
        self.pitch = 0
        self.yaw = 0

    def rotate(self, roll, pitch, yaw):
        self.roll = roll % 360
        if self.roll > 180:
            self.roll = self.roll - 360

        self.pitch = pitch % 360
        if self.pitch > 180:
            self.pitch = self.pitch - 360

        self.yaw = yaw % 360
        if self.yaw > 180:
            self.yaw = self.yaw - 360

        self.update()

    def paintEvent(self, event):
        qp = QPainter()
        qp.begin(self)
        pen = QPen(QColor(190, 190, 190), 3, Qt.SolidLine)
        qp.setPen(pen)
        qp.setFont(QFont('Decorative', self.font_size/2))
        self.draw_roll_pitch_yaw(event, qp)
        qp.end()

    def draw_roll_pitch_yaw(self, event, qp):
        qp.drawRect(0, 0, self.max_width, self.max_height)

        # roll & pitch drawing
        qp.translate(self.max_width / 2, self.max_height / 2)
        qp.rotate(self.roll)

        qp.setBrush(QBrush(QColor(84, 38, 27, 255), Qt.SolidPattern))
        qp.drawRect(-self.max_width, self.pitch / 180 * self.max_height, 2 * self.max_width, 2 * self.max_height)

        qp.setBrush(QBrush(QColor(0, 95, 123, 255), Qt.SolidPattern))
        qp.drawRect(-self.max_width, self.pitch / 180 * self.max_height, 2 * self.max_width, -2 * self.max_height)

        # qp.drawText(-12, self.pitch / 180 * self.max_width - 2, str(self.pitch))

        # pitch drawing
        for shift in [-40, -20, -10, 10, 20, 40]:
            qp.drawLine(-self.min_size, (self.pitch + shift) / 180 * self.max_height,
                        +self.min_size, (self.pitch + shift) / 180 * self.max_height)
            qp.drawText(self.min_size + 2, (self.pitch + shift) / 180 * self.max_height + 4, str(-1*shift))

        pen = QPen(Qt.red, 3, Qt.SolidLine)
        qp.setPen(pen)
        # pitch red lines
        shift = - 31
        qp.drawLine(-self.min_size, (self.pitch + shift) / 180 * self.max_height,
                    +self.min_size, (self.pitch + shift) / 180 * self.max_height)
        qp.drawText(self.min_size + 2, (self.pitch + shift) / 180 * self.max_height + 4, str(-1 * shift))

        shift = 31
        qp.drawLine(-self.min_size, (self.pitch + shift) / 180 * self.max_height,
                    +self.min_size, (self.pitch + shift) / 180 * self.max_height)
        qp.drawText(self.min_size + 2, (self.pitch + shift) / 180 * self.max_height + 4, str(-1 * shift))

        qp.rotate(-self.roll)

        qp.drawLine(0, self.margin - self.max_height / 2,
                    0, self.margin + self.min_size - self.max_height / 2)

        pen = QPen(QColor(190, 190, 190), 3, Qt.SolidLine)
        qp.setPen(pen)

        # yaw red lines
        limiter = (self.yaw % 10) * self.min_size / 10 + self.min_size/2
        yaw = math.floor(self.yaw/10)*10 + 40

        qp.setFont(QFont('Decorative', self.font_size/2))
        while limiter <= self.max_width - 2 * self.margin:
            qp.drawText(-self.max_width / 2 + self.margin + limiter - 5,
                        self.margin + self.min_size - self.max_height / 2 - 5,
                        str(yaw))

            qp.drawLine(-self.max_width / 2 + self.margin + limiter, self.margin - self.max_height/2,
                        -self.max_width / 2 + self.margin + limiter, self.margin + self.margin/2 - self.max_height/2)

            yaw -= 10
            limiter += self.min_size

        # qp.setFont(QFont('Decorative', self.font_size))
        # qp.drawText(-12, self.font_size + self.margin / 2 - self.max_height / 2, str(self.yaw))

        # pen = QPen(Qt.red, 3, Qt.SolidLine)
        # qp.setPen(pen)
        # qp.drawLine(0, 2 * self.margin - self.max_height / 2,
        #             0, 2 * self.margin + self.min_size - self.max_height / 2)

        # static pointer
        pen = QPen(QColor(0, 0, 0, 255), 3, Qt.SolidLine)
        qp.setPen(pen)
        qp.setBrush(QBrush(QColor(0, 0, 0, 255), Qt.SolidPattern))
        qp.drawPolygon(QPolygon([QPoint(0, 0), QPoint(10, 10), QPoint(-10, 10)]))
        qp.drawLine(-10, 0, 10, 0)
        qp.drawLine(-self.mid_size - self.min_size, 0, -self.mid_size, 0)
        qp.drawLine(self.mid_size + self.min_size, 0, self.mid_size, 0)



class Window(QtWidgets.QWidget):
    def __init__(self):
        super().__init__()
        self.setGeometry(0, 0, 500, 500)
        layout = QtWidgets.QVBoxLayout(self)
        self.imuView = ImuView2D()
        layout.addWidget(self.imuView)
        self.show()

        self.angle = 0
        self.increment = 1
        timer = QTimer(self)
        timer.setInterval(200)  # period, in milliseconds
        timer.timeout.connect(self.test_fn)
        timer.start()

    def test_fn(self):
        self.imuView.rotate(self.angle, self.angle, self.angle)

        self.angle += self.increment

        if self.angle == 91:
            self.increment = -1
        if self.angle == -91:
            self.increment = +1


app = QtWidgets.QApplication(sys.argv)
w = Window()
app.exec_()
sys.exit()