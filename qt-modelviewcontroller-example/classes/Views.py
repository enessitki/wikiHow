from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *
import sys


class FilesView(QWidget):
    def __init__(self, parent=None):
        super(FilesView, self).__init__(parent=parent)

        self.scanButton = QPushButton("Scan")
        self.filesLabel = QLabel("")
        self.deleteButton = QPushButton("Delete")

        layout = QHBoxLayout()

        layout.addWidget(self.scanButton)
        layout.addWidget(self.filesLabel)
        layout.addWidget(self.deleteButton)

        self.setLayout(layout)

    def update_view(self, files_array):
        self.filesLabel.setText(str(files_array).replace(" ", "").replace("]", "").replace("[", "").replace(")", "\n").replace("(", "").replace("'", ""))

    def clear(self):
        self.filesLabel.setText("")
