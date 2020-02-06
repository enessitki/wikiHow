from PyQt5 import QtWidgets
from PyQt5 import QtGui
from PyQt5 import QtCore
import sys

class Window(QtWidgets.QWidget):

    def __init__(self):
        super().__init__()
        self.setWindowTitle("local maps")
        self.setGeometry(0, 0, 500, 500)
        self.show()

app = QtWidgets.QApplication(sys.argv)
w = Window()
app.exec_()
sys.exit()
