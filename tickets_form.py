# tickets_form.py

from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QPushButton, QTableWidget, QTableWidgetItem,
    QHBoxLayout, QMessageBox, QLineEdit, QLabel
)
from db import execute_query
from add_ticket_form import AddTicketForm

class TicketsForm(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Билеты")
        self.setGeometry(550, 270, 900, 500)
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()

        # Фильтры
        filter_layout = QHBoxLayout()
        self.search_name = QLineEdit()
        self.search_name.setPlaceholderText("Поиск по ФИО клиента...")
        self.search_name.textChanged.connect(self.apply_filter)

        self.search_status = QLineEdit()
        self.search_status.setPlaceholderText("Поиск по статусу (Sold / Reserved / Cancelled)...")
        self.search_status.textChanged.connect(self.apply_filter)

        filter_layout.addWidget(QLabel("ФИО:"))
        filter_layout.addWidget(self.search_name)
        filter_layout.addWidget(QLabel("Статус:"))
        filter_layout.addWidget(self.search_status)

        layout.addLayout(filter_layout)

        # Таблица
        self.table = QTableWidget()
        self.table.setColumnCount(6)
        self.table.setHorizontalHeaderLabels([
            "ID билета", "ФИО клиента", "ID поезда", "ID заказа",
            "Дата отправления", "Статус"
        ])
        layout.addWidget(self.table)

        # Кнопки
        btn_refresh = QPushButton("Обновить")
        btn_refresh.clicked.connect(self.load_data)

        btn_add = QPushButton("Добавить билет")
        btn_add.clicked.connect(self.open_add_ticket_form)

        btns = QHBoxLayout()
        btns.addWidget(btn_refresh)
        btns.addWidget(btn_add)
        layout.addLayout(btns)

        self.setLayout(layout)
        self.load_data()

    def load_data(self):
        query = """
            SELECT t.id_ticket, c.client_full_name, t.r_train_id_train,
                   t.r_order_id_order, t.ticket_date_and_time_of_departure, t.ticket_status
            FROM r_ticket t
            JOIN r_client c ON t.r_client_ID_client = c.ID_client
        """
        try:
            self.all_tickets = execute_query(query)
            self.display_data(self.all_tickets)
        except Exception as e:
            QMessageBox.critical(self, "Ошибка", f"Не удалось загрузить билеты: {e}")

    def display_data(self, data):
        self.table.setRowCount(0)
        for row_num, row_data in enumerate(data):
            self.table.insertRow(row_num)
            for col_num, col_data in enumerate(row_data):
                self.table.setItem(row_num, col_num, QTableWidgetItem(str(col_data)))

    def apply_filter(self):
        name_kw = self.search_name.text().lower()
        status_kw = self.search_status.text().lower()

        filtered = [
            row for row in self.all_tickets
            if name_kw in row[1].lower() and status_kw in row[5].lower()
        ]
        self.display_data(filtered)

    def open_add_ticket_form(self):
        self.add_window = AddTicketForm()
        self.add_window.show()
        self.add_window.destroyed.connect(self.load_data)
