from PyQt5 import QtWidgets
from PyQt5 import QtCore
from PyQt5 import QtGui
import sys


class Window(QtWidgets.QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Qt Demo")
        # sizing
        # self.setGeometry(0, 0, 500, 500)
        # self.setFixedHeight(100)
        # self.setFixedWidth(100)
        # self.setMaximumHeight(100)
        self.infoLabel2 = QtWidgets.QLabel("my info 2")

        self.infoLabel2.setStyleSheet("QLabel{border: 10px solid black; background-color: red; color: blue;}")

        self.setStyleSheet("QLabel{color: red;}")

        self.closeButton = QtWidgets.QPushButton("Close App")
        self.closeButton.clicked.connect(self.close_app)
        self.setContentsMargins(100, 0, 0, 0)

        self.infoLabel = QtWidgets.QLabel("my info")


        # layout
        layout = QtWidgets.QVBoxLayout()
        layout.addWidget(self.infoLabel)
        layout.addWidget(self.infoLabel2)
        layout.addWidget(self.closeButton)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(100)
        layout.setAlignment(QtCore.Qt.AlignCenter)
        self.setLayout(layout)

        # show ...
        # self.show()
        self.showFullScreen()
        # self.showMaximized()
        # self.showNormal()

    def close_app(self):
        self.close()

    def closeEvent(self, a0: QtGui.QCloseEvent) -> None:
        print("here")


app = QtWidgets.QApplication(sys.argv)
w = Window()
app.exec_()
sys.exit()
