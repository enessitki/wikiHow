from PyQt5 import QtWidgets
from PyQt5 import QtCore
from PyQt5 import QtGui
import sys
import time


class QLoadingAnimation(QtWidgets.QLabel):
    def __init__(self, parent=None):
        super().__init__(parent=parent)

        self.movie = QtGui.QMovie("files/loading.gif")
        self.setMovie(self.movie)
        self.movie.start()


class Window(QtWidgets.QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Qt Demo 4 loading animation")
        self.setGeometry(0, 0, 500, 500)

        self.loadingAnimation = QLoadingAnimation()

        layout = QtWidgets.QVBoxLayout()
        layout.addWidget(self.loadingAnimation)
        self.setLayout(layout)

        self.show()

    @staticmethod
    def pic_button_clicked():
        print(time.time())


app = QtWidgets.QApplication(sys.argv)
w = Window()
app.exec_()
sys.exit()
