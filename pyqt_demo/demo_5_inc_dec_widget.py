from PyQt5 import QtWidgets
from PyQt5 import QtCore
from PyQt5 import QtGui
import sys
import time


class QStatelessPicButton(QtWidgets.QLabel):
    def __init__(self, pixmap, parent=None):
        super().__init__(parent=parent)
        self.inputPixmap = pixmap
        self.setPixmap(pixmap)
        self.clicked = None

    def mousePressEvent(self, ev: QtGui.QMouseEvent) -> None:
        if self.clicked is not None:
            self.clicked()


class QIncDecLabel(QtWidgets.QWidget):
    def __init__(self, layout=QtWidgets.QHBoxLayout(), font=200, min_val=0, current_val=0, max_val=10, parent=None):
        super().__init__(parent=parent)
        self.setContentsMargins(0, 0, 0, 0)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(10)
        layout.setAlignment(QtCore.Qt.AlignCenter)
        self.currentValue = current_val
        self.minValue = min_val
        self.maxValue = max_val

        self.plus = QStatelessPicButton(QtGui.QPixmap("files/plus-128.png"))
        self.minus = QStatelessPicButton(QtGui.QPixmap("files/minus-128.png"))

        self.plus.clicked = self.increase
        self.minus.clicked = self.decrease

        self.valueLabel = QtWidgets.QLabel(str(current_val))
        self.valueLabel.setStyleSheet("QLabel{font : bold " + str(font) + "px ; color: white;}")
        self.valueLabel.setAlignment(QtCore.Qt.AlignCenter)

        layout.addWidget(self.minus)
        layout.addWidget(self.valueLabel)
        layout.addWidget(self.plus)

        self.setLayout(layout)

    def increase(self):
        if self.currentValue < self.maxValue:
            self.currentValue += 1

        self.valueLabel.setText(str(self.currentValue))

    def decrease(self):
        if self.currentValue > self.minValue:
            self.currentValue -= 1

        self.valueLabel.setText(str(self.currentValue))


class Window(QtWidgets.QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Qt Demo 4 loading animation")
        self.setGeometry(0, 0, 500, 500)

        self.loadingAnimation = QIncDecLabel()

        layout = QtWidgets.QVBoxLayout()
        layout.addWidget(self.loadingAnimation)
        self.setLayout(layout)

        self.show()

    def paintEvent(self, a0: QtGui.QPaintEvent) -> None:
        self.setAutoFillBackground(True)
        pal = self.palette()
        pal.setColor(self.backgroundRole(), QtGui.QColor(0, 0, 0))
        self.setPalette(pal)

    @staticmethod
    def pic_button_clicked():
        print(time.time())


app = QtWidgets.QApplication(sys.argv)
w = Window()
app.exec_()
sys.exit()
