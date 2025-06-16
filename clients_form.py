# clients_form.py

from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QPushButton, QTableWidget, QTableWidgetItem,
    QHBoxLayout, QMessageBox, QLineEdit, QLabel
)
from db import execute_query, execute_non_query
from add_client_form import AddClientForm
from edit_client_form import EditClientForm

class ClientsForm(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Клиенты")
        self.setGeometry(500, 250, 700, 500)
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()

        # Поле поиска
        search_layout = QHBoxLayout()
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Поиск по ФИО...")
        self.search_input.textChanged.connect(self.apply_filter)
        search_layout.addWidget(QLabel("Поиск:"))
        search_layout.addWidget(self.search_input)
        layout.addLayout(search_layout)

        # Таблица
        self.table = QTableWidget()
        self.table.setColumnCount(4)
        self.table.setHorizontalHeaderLabels(["ID", "ФИО", "Телефон", "Email"])
        layout.addWidget(self.table)

        # Кнопки
        btn_refresh = QPushButton("Обновить")
        btn_refresh.clicked.connect(self.load_data)

        btn_add = QPushButton("Добавить клиента")
        btn_add.clicked.connect(self.open_add_client_form)

        btn_edit = QPushButton("Редактировать")
        btn_edit.clicked.connect(self.edit_client)

        btn_delete = QPushButton("Удалить")
        btn_delete.clicked.connect(self.delete_client)

        btns = QHBoxLayout()
        btns.addWidget(btn_refresh)
        btns.addWidget(btn_add)
        btns.addWidget(btn_edit)
        btns.addWidget(btn_delete)
        layout.addLayout(btns)

        self.setLayout(layout)
        self.load_data()

    def load_data(self):
        self.all_clients = execute_query(
            "SELECT id_client, client_full_name, client_phone_number, client_email FROM r_client"
        )
        self.display_data(self.all_clients)

    def display_data(self, data):
        self.table.setRowCount(0)
        for row_num, row_data in enumerate(data):
            self.table.insertRow(row_num)
            for col_num, col_data in enumerate(row_data):
                self.table.setItem(row_num, col_num, QTableWidgetItem(str(col_data)))

    def apply_filter(self):
        keyword = self.search_input.text().lower()
        filtered = [row for row in self.all_clients if keyword in row[1].lower()]
        self.display_data(filtered)

    def open_add_client_form(self):
        self.add_window = AddClientForm()
        self.add_window.show()
        self.add_window.destroyed.connect(self.load_data)

    def delete_client(self):
        row = self.table.currentRow()
        if row == -1:
            QMessageBox.warning(self, "Выберите запись", "Выберите клиента для удаления.")
            return
        client_id = self.table.item(row, 0).text()
        reply = QMessageBox.question(self, "Подтвердите", "Удалить выбранного клиента?",
                                     QMessageBox.Yes | QMessageBox.No)
        if reply == QMessageBox.Yes:
            try:
                execute_non_query("DELETE FROM r_client WHERE id_client = %s", (client_id,))
                self.load_data()
                QMessageBox.information(self, "Успех", "Клиент удалён.")
            except Exception as e:
                QMessageBox.critical(self, "Ошибка", f"Ошибка удаления: {e}")

    def edit_client(self):
        row = self.table.currentRow()
        if row == -1:
            QMessageBox.warning(self, "Выберите запись", "Выберите клиента для редактирования.")
            return
        client_data = {
            'id': self.table.item(row, 0).text(),
            'name': self.table.item(row, 1).text(),
            'phone': self.table.item(row, 2).text(),
            'email': self.table.item(row, 3).text()
        }
        self.edit_window = EditClientForm(client_data)
        self.edit_window.show()
        self.edit_window.destroyed.connect(self.load_data)
