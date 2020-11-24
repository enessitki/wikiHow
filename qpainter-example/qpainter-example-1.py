from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *
import sys
import math
from classes.RobotArmView import RobotArmView


class Window(QWidget):
    def __init__(self, parent=None):
        super(Window, self).__init__(parent=parent)
        self.setWindowTitle("QPainter Example 1")

        self.robotArmView = RobotArmView()
        layout = QHBoxLayout()
        layout.addWidget(self.robotArmView)
        self.setLayout(layout)
        self.show()

        self.timer = QTimer()
        self.timer.setInterval(50)
        self.timer.timeout.connect(self.update_robot_arm_view)
        self.timer.start()

    def update_robot_arm_view(self):
        self.robotArmView.angleVector[0] -= math.pi/180
        self.robotArmView.angleVector[1] += math.pi/90
        self.robotArmView.angleVector[2] -= math.pi/15
        self.robotArmView.update()




app = QApplication(sys.argv)
w = Window()
app.exec_()
sys.exit()