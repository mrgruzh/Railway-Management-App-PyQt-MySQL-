# edit_client_form.py

from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QFormLayout, QLineEdit,
    QPushButton, QMessageBox
)
from db import execute_non_query

class EditClientForm(QWidget):
    def __init__(self, client):
        super().__init__()
        self.client = client
        self.setWindowTitle("Редактирование клиента")
        self.setGeometry(600, 300, 400, 200)
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()
        form = QFormLayout()

        self.name_input = QLineEdit(self.client['name'])
        self.phone_input = QLineEdit(self.client['phone'])
        self.email_input = QLineEdit(self.client['email'])

        form.addRow("ФИО:", self.name_input)
        form.addRow("Телефон:", self.phone_input)
        form.addRow("Email:", self.email_input)

        save_btn = QPushButton("Сохранить изменения")
        save_btn.clicked.connect(self.save_client)

        layout.addLayout(form)
        layout.addWidget(save_btn)
        self.setLayout(layout)

    def save_client(self):
        name = self.name_input.text().strip()
        phone = self.phone_input.text().strip()
        email = self.email_input.text().strip()

        if not name or not phone or not email:
            QMessageBox.warning(self, "Ошибка", "Все поля обязательны.")
            return

        try:
            query = """
                UPDATE r_client
                SET client_full_name = %s,
                    client_phone_number = %s,
                    client_email = %s
                WHERE id_client = %s
            """
            execute_non_query(query, (name, phone, email, self.client['id']))
            QMessageBox.information(self, "Успех", "Данные клиента обновлены.")
            self.close()
        except Exception as e:
            QMessageBox.critical(self, "Ошибка", f"Ошибка при обновлении: {e}")
