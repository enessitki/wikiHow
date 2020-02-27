from PyQt5 import QtWidgets
from PyQt5 import QtCore
from PyQt5 import QtGui
import sys


class Window(QtWidgets.QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Qt Demo")

        self.setContentsMargins(5, 5, 5, 5)

        self.closeButton = QtWidgets.QPushButton("Close")
        self.closeButton.clicked.connect(self.close_app)
        self.closeButton.setMaximumWidth(200)

        self.openButton = QtWidgets.QPushButton("Open")
        self.openButton.setMaximumWidth(200)

        # header_widget = QtWidgets.QWidget()
        # header_layout = QtWidgets.QHBoxLayout()
        # header_layout.setAlignment(QtCore.Qt.AlignRight)
        # header_widget.setLayout(header_layout)
        # header_layout.addWidget(self.openButton, QtCore.Qt.AlignRight)
        # header_layout.addWidget(QtWidgets.QPushButton())
        # header_layout.addWidget(self.closeButton)
        # header_widget.setFixedHeight(50)

        # layout
        layout = QtWidgets.QHBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setAlignment(QtCore.Qt.AlignTop)
        layout.setSpacing(10)
        layout.addWidget(self.openButton, QtCore.Qt.AlignLeft)
        layout.addWidget(QtWidgets.QLabel())
        layout.addWidget(self.closeButton, QtCore.Qt.AlignRight)
        self.setLayout(layout)

        self.showFullScreen()

    def close_app(self):
        self.close()


app = QtWidgets.QApplication(sys.argv)
w = Window()
app.exec_()
sys.exit()
