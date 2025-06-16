from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QFormLayout, QLineEdit,
    QPushButton, QMessageBox
)
from db import execute_insert

class AddClientForm(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Добавление клиента")
        self.setGeometry(600, 300, 400, 200)
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()
        form = QFormLayout()

        self.name_input = QLineEdit()
        self.phone_input = QLineEdit()
        self.email_input = QLineEdit()

        form.addRow("ФИО:", self.name_input)
        form.addRow("Телефон:", self.phone_input)
        form.addRow("Email:", self.email_input)

        save_btn = QPushButton("Добавить")
        save_btn.clicked.connect(self.add_client)

        layout.addLayout(form)
        layout.addWidget(save_btn)
        self.setLayout(layout)

    def add_client(self):
        name = self.name_input.text().strip()
        phone = self.phone_input.text().strip()
        email = self.email_input.text().strip()

        if not name or not phone or not email:
            QMessageBox.warning(self, "Ошибка", "Все поля обязательны.")
            return

        try:
            query = """
                INSERT INTO r_client (client_full_name, client_phone_number, client_email)
                VALUES (%s, %s, %s)
            """
            execute_insert(query, (name, phone, email))
            QMessageBox.information(self, "Успех", "Клиент добавлен.")
            self.close()
        except Exception as e:
            QMessageBox.critical(self, "Ошибка", f"Ошибка при добавлении клиента: {e}")
