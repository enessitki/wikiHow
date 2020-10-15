from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *
import sys
from classes.Login import LoginModel, LoginView, LoginController


class Window(QWidget):
    def __init__(self, parent=None):
        super(Window, self).__init__(parent=parent)
        self.setWindowTitle("Qt MCV LOGIN")

        self.loginModel = LoginModel()
        self.loginView = LoginView()
        self.loginController = LoginController(self.loginModel, self.loginView)
        admin_role, admin_password, user_role, user_password = self.get_user_credentials()
        self.loginController.set_user_roles(admin_role, admin_password, user_role, user_password)

        layout = QVBoxLayout()
        layout.addWidget(self.loginView)
        self.setLayout(layout)

        self.show()

    @staticmethod
    def get_user_credentials():
        return "Yönetici", "123456", "Kullanıcı", "123456"


app = QApplication(sys.argv)
w = Window()
app.exec_()
sys.exit()
