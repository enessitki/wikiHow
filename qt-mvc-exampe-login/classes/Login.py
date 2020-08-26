from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *
import os
import hashlib
import xml.etree.ElementTree as ET
DIR_RESOURCES = "resources/"
DIR_DATABASE = "db/db.xml"

# tree = ET.parse(DIR_DATABASE)
# root=tree.getroot()


class UserModel:
    def __init__(self, role=None, password=None):
        self.role = role
        self.password = hashlib.sha256(bytes(password, 'utf-8')).hexdigest()
        self.isLoggedIn = False


class LoginModel(object):
    def __init__(self):
        self.currentUser = None
        self.admin = None
        self.user = None

    def set_admin(self, role, password):
        self.admin = UserModel(role, password)

    def set_user(self, role, password):
        self.user = UserModel(role, password)

    def check_user(self, role, password):
        if self.currentUser is not None:
            self.currentUser.isLoggedIn = False
        if self.admin is None or self.user is None:
            return False
        else:
            current_user = UserModel(role, password)
            if self.compare_users(self.admin, current_user) or self.compare_users(self.user, current_user):
                self.currentUser = current_user
                self.currentUser.isLoggedIn = True
                return True

    def is_admin(self):
        if self.admin is not None and self.user is not None and self.currentUser is not None:
            return self.currentUser.role == self.admin.role
        else:
            return False

    def is_logged_in(self):
        if self.currentUser is not None:
            return self.currentUser.isLoggedIn
        return False

    @staticmethod
    def compare_users(user1, user2):
        if user1.role == user2.role and user1.password == user2.password:
            return True
        return False


class LoginView(QWidget):
    def __init__(self, parent=None):
        super(LoginView, self).__init__(parent=parent)

        layout = QVBoxLayout()

        icon_pixmap = QPixmap(DIR_RESOURCES + "esetron_icon_128.png")
        self.iconLabel = QLabel()
        self.iconLabel.setPixmap(icon_pixmap.scaledToHeight(100))

        self.userRoleCombobox = QComboBox()
        self.userRoleCombobox.addItem("Yönetici")
        self.userRoleCombobox.addItem("Kullanıcı")

        self.loginPasswordLine = QLineEdit()
        self.loginPasswordLine.setEchoMode(QLineEdit.Password)
        self.loginPasswordLine.setPlaceholderText("Şifre")

        self.loginButton = QPushButton("Login")

        self.infoLabel = QLabel("")

        layout.addWidget(self.iconLabel)
        layout.addWidget(self.userRoleCombobox)
        layout.addWidget(self.loginPasswordLine)
        layout.addWidget(self.loginButton)
        layout.addWidget(self.infoLabel)

        self.setLayout(layout)


class LoginController:
    def __init__(self, login_mode: LoginModel, login_view: LoginView):
        self.model = login_mode
        self.view = login_view
        self.view.loginButton.clicked.connect(self.login)

    def set_user_roles(self, admin_role, admin_password, user_role, user_password):
        self.model.set_admin(admin_role, admin_password)
        self.model.set_user(user_role, user_password)

    def login(self):
        role = self.view.userRoleCombobox.currentText()
        password = self.view.loginPasswordLine.text()
        ret = self.model.check_user(role, password)
        self.update_view()
        return ret

    def update_view(self):
        if self.model.is_logged_in():
            if self.model.is_admin():
                self.view.infoLabel.setText("Admin")
            else:
                self.view.infoLabel.setText("User")
        else:
            self.view.infoLabel.setText("Login failed...")

