from PyQt5 import QtWidgets
from PyQt5 import QtCore
from PyQt5 import QtGui
import sys
from classes.Models import FilesModel
from classes.Views import FilesView
from classes.Controllers import FilesController


class Window(QtWidgets.QWidget):
    def __init__(self, parent=None):
        super(Window, self).__init__(parent=parent)
        self.filesView = FilesView()
        self.filesController = FilesController(FilesModel(), self.filesView)
        self.filesController.set_files(self.get_data())
        # self.filesController.update_view()

        layout = QtWidgets.QHBoxLayout()
        layout.addWidget(self.filesView)
        self.setLayout(layout)
        self.show()

    def get_data(self):
        return [("test1", "/home/test1.log", "log"),
                ("test2", "/home/test2.mp4", "mp4")]


app = QtWidgets.QApplication(sys.argv)
w = Window()
app.exec_()
sys.exit()
