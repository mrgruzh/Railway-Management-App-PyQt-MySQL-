from PyQt5.QtWidgets import QWidget, QVBoxLayout, QLabel, QLineEdit, QPushButton, QMessageBox
from PyQt5.QtCore import pyqtSignal
from PyQt5.QtGui import QPixmap, QPalette, QBrush
from db import execute_query
from PIL import Image, ImageFilter
import io

class LoginWindow(QWidget):
    login_successful = pyqtSignal(str)

    def __init__(self):
        super().__init__()
        self.setWindowTitle("Вход в систему")
        self.setGeometry(600, 300, 300, 200)

        self.set_blurred_background("back.jpg", blur_radius=5)

        layout = QVBoxLayout()

        self.label_login = QLabel("ЛОГИН:")
        self.label_login.setStyleSheet("color: white; font-weight: bold; font-size: 9pt;")
        self.input_login = QLineEdit()

        self.label_password = QLabel("ПАРОЛЬ:")
        self.label_password.setStyleSheet("color: white; font-weight: bold; font-size: 9pt;")
        self.input_password = QLineEdit()
        self.input_password.setEchoMode(QLineEdit.Password)

        self.login_button = QPushButton("Авторизироваться")
        self.login_button.setStyleSheet("""
            QPushButton {
                background-color: #1D6B30;  /* насыщенный зелёный */
                color: white;
                font-weight: bold;
                font-size: 12pt;
                border-radius: 16px;
                padding: 10px 20px;
            }
            QPushButton:hover {
                background-color: #218838;
            }
        """)

        self.login_button.clicked.connect(self.handle_login)

        layout.addWidget(self.label_login)
        layout.addWidget(self.input_login)
        layout.addWidget(self.label_password)
        layout.addWidget(self.input_password)
        layout.addSpacing(20)
        layout.addWidget(self.login_button)

        self.setLayout(layout)

    def set_blurred_background(self, image_path, blur_radius=5):
        img = Image.open(image_path)
        blurred = img.filter(ImageFilter.GaussianBlur(radius=blur_radius))

        buf = io.BytesIO()
        blurred.save(buf, format="PNG")
        buf.seek(0)

        qimg = QPixmap()
        qimg.loadFromData(buf.read())

        palette = QPalette()
        palette.setBrush(QPalette.Window, QBrush(qimg.scaled(self.size(), aspectRatioMode=1)))
        self.setAutoFillBackground(True)
        self.setPalette(palette)

    def resizeEvent(self, event):
        self.set_blurred_background("back.jpg", blur_radius=5)
        super().resizeEvent(event)

    def handle_login(self):
        login = self.input_login.text()
        password = self.input_password.text()
        query = "SELECT role FROM users WHERE login=%s AND password=%s"
        result = execute_query(query, (login, password))

        if result:
            role = result[0][0]
            self.login_successful.emit(role)
            self.close()
        else:
            QMessageBox.warning(self, "Ошибка", "Неверный логин или пароль")
