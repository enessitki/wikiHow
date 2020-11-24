from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *
import sys
import math
# http://zetcode.com/gui/pyqt5/painting/
# https://www.learnpyqt.com/tutorials/bitmap-graphics/


class RobotArmView(QWidget):
    def __init__(self, parent=None):
        super(RobotArmView, self).__init__(parent=parent)
        self.setFixedSize(600, 600)
        self.margin = 0
        self.angleVector = [0, 0, 0]  # th0, th1, th2 (radian)
        self.linkLengths = [1, 1, 1]  # meter

        self.linkPen = QPen(QColor(0, 255, 0), 6, Qt.SolidLine)
        self.linkBrush = QBrush(QColor(0, 255, 0, 255), Qt.SolidPattern)
        self.nodePen = QPen(QColor(255, 0, 0), 6, Qt.SolidLine)
        self.nodeBrush = QBrush(QColor(255, 0, 0, 255), Qt.SolidPattern)

        self.backgroundPixmap = QPixmap("resources/reactorx-200-robot-arm.jpg")

    def get_node_positions(self):
        # x0, y0 = self.width()/2, self.height()/2
        x0, y0 = 0, 0
        x1, y1 = self.calculate_final_point(x0, y0, self.angleVector[0], self.linkLengths[0])
        x2, y2 = self.calculate_final_point(x1, y1, self.angleVector[1], self.linkLengths[1])
        x3, y3 = self.calculate_final_point(x2, y2, self.angleVector[2], self.linkLengths[2])
        return [(x0, y0), (x1, y1), (x2, y2), (x3, y3)]

    @staticmethod
    def calculate_final_point(xi, yi, th, length):
        length = length * 100
        xf = xi + length * math.cos(th)
        yf = yi + length * math.sin(th)

        return xf, yf

    def paintEvent(self, event):
        qp = QPainter()
        qp.begin(self)

        qp.setPen(self.linkPen)
        qp.setBrush(self.linkBrush)

        # qp.drawRect(0, 0, 100, 100)
        qp.translate(self.width() / 2, self.height() / 2)
        # qp.rotate(45)

        nodes = self.get_node_positions()
        # y_max = self.width()/2

        for n in range(len(nodes) - 1):
            p0 = nodes[n]
            p1 = nodes[n + 1]
            qp.drawLine(p0[0], -p0[1], p1[0], -p1[1])

        qp.setPen(self.nodePen)
        qp.setBrush(self.nodeBrush)
        for node in nodes:
            qp.drawEllipse(node[0] - 3, -node[1] - 3, 6, 6)

        x3, y3 = nodes[3]
        a = 50
        qp.translate(x3, -y3)
        qp.rotate(-self.angleVector[-1]/math.pi*180)
        qp.drawPixmap(QRect(- a/2, - a/2, a, a), self.backgroundPixmap)

        # qp.drawRect(self.margin, self.margin, 100, 100)
        #
        # # qp.setPen(self.nodePen)
        # qp.setBrush(self.nodeBrush)
        # qp.drawRect(self.margin + 80, self.margin + 80, 250, 250)

        # qp.drawLine(self.margin + 2, self.margin + 2, 50, 50)
        qp.end()
