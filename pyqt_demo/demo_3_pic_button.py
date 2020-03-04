from PyQt5 import QtWidgets
from PyQt5 import QtCore
from PyQt5 import QtGui
import sys
import time


class PicButton(QtWidgets.QLabel):
    def __init__(self, pixmaps, state, parent=None):
        super().__init__(parent=parent)
        self.pixmaps = pixmaps
        self.setPixmap(self.pixmaps[state])
        self.state = state
        self.maxState = len(pixmaps)
        self.clicked = None

    def mousePressEvent(self, ev: QtGui.QMouseEvent) -> None:
        self.on_click()

    def on_click(self, state=None):
        if self.clicked is not None:
            self.clicked()

        if state is None:
            self.state += 1
            if self.state > self.maxState - 1:
                self.state = 0
        else:
            self.state = state

        self.setPixmap(self.pixmaps[self.state])


class Window(QtWidgets.QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Qt Demo")
        self.setGeometry(0, 0, 500, 500)
        pixmaps = [QtGui.QPixmap("files/square-128.png").scaledToHeight(50),
                   QtGui.QPixmap("files/circle-128.png").scaledToHeight(50),
                   QtGui.QPixmap("files/x-mark-128.png").scaledToHeight(50)]
        self.picButton = PicButton(pixmaps, state=0)
        self.picButton.clicked = self.pic_button_clicked

        layout = QtWidgets.QVBoxLayout()
        layout.addWidget(self.picButton)
        self.setLayout(layout)

        self.show()

    @staticmethod
    def pic_button_clicked():
        print(time.time())


app = QtWidgets.QApplication(sys.argv)
w = Window()
app.exec_()
sys.exit()
