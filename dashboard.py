from PyQt5.QtWidgets import QMainWindow, QPushButton, QLabel, QVBoxLayout, QWidget
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QPixmap

from clients_form import ClientsForm
from orders_form import OrdersForm
from tickets_form import TicketsForm
from trains_form import TrainsForm
from platforms_form import PlatformsForm
from operators_form import OperatorsForm
from report_generator import ReportGenerator


class Dashboard(QMainWindow):
    def __init__(self, role):
        super().__init__()
        self.setWindowTitle("Железнодорожная система — Главное меню")
        self.setGeometry(400, 200, 400, 650)
        self.role = role

        self.clients_window = None
        self.orders_window = None
        self.tickets_window = None
        self.trains_window = None
        self.platforms_window = None
        self.operators_window = None
        self.reports_window = None

        self.init_ui()

    def init_ui(self):
        container = QWidget()
        layout = QVBoxLayout(container)
        layout.setSpacing(15)

        # Белый фон окна
        self.setStyleSheet("""
            QMainWindow {
                background-color: white;
            }
        """)

        # Картинка поезда
        header = QLabel()
        pixmap = QPixmap("back2.jpg")
        header.setPixmap(pixmap.scaledToWidth(320, Qt.SmoothTransformation))
        header.setAlignment(Qt.AlignCenter)
        layout.addWidget(header)

        # Приветствие
        welcome_label = QLabel(f"Добро пожаловать! Ваша роль: {self.role}")
        welcome_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(welcome_label)

        # Кнопки
        self.buttons = {}
        entities = [
            ("Клиенты", "clients"),
            ("Заказы", "orders"),
            ("Билеты", "tickets"),
            ("Поезда и вагоны", "trains"),
            ("Платформы и станции", "platforms"),
            ("Операционисты", "operators"),
            ("Отчёты", "reports")
        ]

        for name, key in entities:
            btn = QPushButton(name)
            btn.setFixedHeight(40)
            btn.setStyleSheet("""
                QPushButton {
                    background-color: #1D6B30;
                    color: white;
                    font-weight: bold;
                    font-size: 10pt;
                    border-radius: 10px;
                    padding: 10px;
                }
                QPushButton:hover {
                    background-color: #218838;
                }
            """)
            btn.clicked.connect(lambda checked, k=key: self.open_section(k))
            layout.addWidget(btn)
            self.buttons[key] = btn

        if self.role != "admin":
            self.buttons["operators"].setDisabled(True)

        self.setCentralWidget(container)

    def open_section(self, section_key):
        if section_key == "clients":
            if self.clients_window is None:
                self.clients_window = ClientsForm()
            self.clients_window.show()
        elif section_key == "orders":
            if self.orders_window is None:
                self.orders_window = OrdersForm()
            self.orders_window.show()
        elif section_key == "tickets":
            if self.tickets_window is None:
                self.tickets_window = TicketsForm()
            self.tickets_window.show()
        elif section_key == "trains":
            if self.trains_window is None:
                self.trains_window = TrainsForm()
            self.trains_window.show()
        elif section_key == "platforms":
            if self.platforms_window is None:
                self.platforms_window = PlatformsForm()
            self.platforms_window.show()
        elif section_key == "operators":
            if self.operators_window is None:
                self.operators_window = OperatorsForm()
            self.operators_window.show()
        elif section_key == "reports":
            if self.reports_window is None:
                self.reports_window = ReportGenerator()
            self.reports_window.show()
