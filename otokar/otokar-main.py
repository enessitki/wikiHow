from PyQt5 import QtWidgets
from PyQt5 import QtCore
from PyQt5 import QtGui
import sys
from classes.Resources import Resources


class MyClass2:
    def __init__(self, a):
        self.a = a

    def __abs__(self):
        return 10

    def __len__(self):
        return 15

    def __getitem__(self, item):
        return 10


class Window(QtWidgets.QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Qt Demo")

        self.resources = Resources()
        style = self.resources.styleSheet()
        print(style)

        self.myClass = MyClass2(45)
        print(self.myClass.a)
        print(self.myClass[0])

        self.show()




app = QtWidgets.QApplication(sys.argv)
w = Window()
app.exec_()
sys.exit()