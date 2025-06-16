from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QFormLayout, QLineEdit,
    QPushButton, QMessageBox, QDateEdit, QTimeEdit
)
from PyQt5.QtCore import QDate, QTime, QDateTime
from db import execute_insert

class AddTicketForm(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Добавление билета")
        self.setGeometry(600, 300, 400, 320)
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()
        form = QFormLayout()

        self.client_id_input = QLineEdit()
        self.train_id_input = QLineEdit()
        self.order_id_input = QLineEdit()

        # Отдельно дата
        self.date_input = QDateEdit()
        self.date_input.setDate(QDate.currentDate())
        self.date_input.setCalendarPopup(True)

        # Отдельно время
        self.time_input = QTimeEdit()
        self.time_input.setTime(QTime.currentTime())

        self.status_input = QLineEdit()

        form.addRow("ID клиента:", self.client_id_input)
        form.addRow("ID поезда:", self.train_id_input)
        form.addRow("ID заказа:", self.order_id_input)
        form.addRow("Дата отправления:", self.date_input)
        form.addRow("Время отправления:", self.time_input)
        form.addRow("Статус (Sold / Reserved / Cancelled):", self.status_input)

        save_btn = QPushButton("Добавить билет")
        save_btn.clicked.connect(self.add_ticket)

        layout.addLayout(form)
        layout.addWidget(save_btn)
        self.setLayout(layout)

    def add_ticket(self):
        client_id = self.client_id_input.text().strip()
        train_id = self.train_id_input.text().strip()
        order_id = self.order_id_input.text().strip()
        date = self.date_input.date()
        time = self.time_input.time()
        status = self.status_input.text().strip()

        if not all([client_id, train_id, order_id, status]):
            QMessageBox.warning(self, "Ошибка", "Все поля обязательны.")
            return

        full_datetime = QDateTime(date, time).toString("yyyy-MM-dd HH:mm:ss")

        try:
            query = """
                INSERT INTO r_ticket (
                    r_client_id_client, r_train_id_train, r_order_id_order,
                    ticket_date_and_time_of_departure, ticket_status
                ) VALUES (%s, %s, %s, %s, %s)
            """
            execute_insert(query, (client_id, train_id, order_id, full_datetime, status))
            QMessageBox.information(self, "Успех", "Билет добавлен.")
            self.close()
        except Exception as e:
            QMessageBox.critical(self, "Ошибка", f"Ошибка при добавлении билета: {e}")
