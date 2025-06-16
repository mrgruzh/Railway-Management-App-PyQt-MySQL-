from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QTableWidget, QTableWidgetItem,
    QPushButton, QLabel, QMessageBox, QDialog, QFormLayout,
    QComboBox, QLineEdit
)
from db import execute_query


class OperatorDialog(QDialog):
    def __init__(self, name='', number='', station_id=None, stations=None):
        super().__init__()
        self.setWindowTitle("Операционист")
        self.setFixedSize(350, 200)

        layout = QFormLayout()

        self.name_input = QLineEdit()
        self.name_input.setText(name)

        self.number_input = QLineEdit()
        self.number_input.setText(number)

        self.station_box = QComboBox()
        self.station_map = {}
        if stations:
            for sid, sname in stations:
                self.station_box.addItem(sname)
                self.station_map[sname] = sid
            if station_id:
                for name, sid in self.station_map.items():
                    if sid == station_id:
                        self.station_box.setCurrentText(name)

        layout.addRow("Имя:", self.name_input)
        layout.addRow("Номер:", self.number_input)
        layout.addRow("Станция:", self.station_box)

        self.submit_btn = QPushButton("Сохранить")
        self.submit_btn.clicked.connect(self.accept)
        layout.addWidget(self.submit_btn)

        self.setLayout(layout)

    def get_data(self):
        name = self.name_input.text()
        number = self.number_input.text()
        station_id = self.station_map.get(self.station_box.currentText())
        return name, number, station_id


class OperatorsForm(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Операционисты")
        self.setGeometry(550, 250, 900, 500)
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()

        layout.addWidget(QLabel("Список операционистов"))
        self.table = QTableWidget()
        self.table.setColumnCount(4)
        self.table.setHorizontalHeaderLabels(["ID", "Имя", "Номер", "ID Станции"])
        layout.addWidget(self.table)

        btn_refresh = QPushButton("Обновить")
        btn_refresh.clicked.connect(self.load_data)
        layout.addWidget(btn_refresh)

        btn_add = QPushButton("Добавить операциониста")
        btn_add.clicked.connect(self.add_operator)
        layout.addWidget(btn_add)

        btn_edit = QPushButton("Редактировать выбранного")
        btn_edit.clicked.connect(self.edit_operator)
        layout.addWidget(btn_edit)

        btn_delete = QPushButton("Удалить выбранного")
        btn_delete.clicked.connect(self.delete_operator)
        layout.addWidget(btn_delete)

        self.setLayout(layout)
        self.load_data()

    def load_data(self):
        self.table.setRowCount(0)
        query = "SELECT id_operator, operator_name, operator_number, r_station_id_station FROM r_operator"
        try:
            rows = execute_query(query)
            for row_num, row_data in enumerate(rows):
                self.table.insertRow(row_num)
                for col_num, col_data in enumerate(row_data):
                    self.table.setItem(row_num, col_num, QTableWidgetItem(str(col_data)))
        except Exception as e:
            QMessageBox.critical(self, "Ошибка", f"Не удалось загрузить операционистов: {e}")

    def fetch_stations(self):
        try:
            return execute_query("SELECT id_station, station_name FROM r_station")
        except:
            return []

    def add_operator(self):
        stations = self.fetch_stations()
        dialog = OperatorDialog(stations=stations)
        if dialog.exec_() == QDialog.Accepted:
            name, number, station_id = dialog.get_data()
            if not name or not number or not station_id:
                QMessageBox.warning(self, "Ошибка", "Все поля обязательны.")
                return
            try:
                execute_query(
                    "INSERT INTO r_operator (operator_name, operator_number, r_station_id_station) VALUES (%s, %s, %s)",
                    (name, number, station_id)
                )
                self.load_data()
            except Exception as e:
                QMessageBox.critical(self, "Ошибка", f"Ошибка при добавлении: {e}")

    def edit_operator(self):
        row = self.table.currentRow()
        if row < 0:
            QMessageBox.warning(self, "Ошибка", "Выберите строку.")
            return
        op_id = self.table.item(row, 0).text()
        name = self.table.item(row, 1).text()
        number = self.table.item(row, 2).text()
        station_id = int(self.table.item(row, 3).text())
        stations = self.fetch_stations()

        dialog = OperatorDialog(name, number, station_id, stations)
        if dialog.exec_() == QDialog.Accepted:
            name, number, station_id = dialog.get_data()
            try:
                execute_query(
                    "UPDATE r_operator SET operator_name=%s, operator_number=%s, r_station_id_station=%s WHERE id_operator=%s",
                    (name, number, station_id, op_id)
                )
                self.load_data()
            except Exception as e:
                QMessageBox.critical(self, "Ошибка", f"Ошибка при редактировании: {e}")

    def delete_operator(self):
        row = self.table.currentRow()
        if row < 0:
            QMessageBox.warning(self, "Ошибка", "Выберите строку.")
            return
        op_id = self.table.item(row, 0).text()
        confirm = QMessageBox.question(
            self,
            "Удаление",
            "Удалить выбранного операциониста?",
            QMessageBox.Yes | QMessageBox.No
        )
        if confirm == QMessageBox.Yes:
            try:
                execute_query("DELETE FROM r_operator WHERE id_operator = %s", (op_id,))
                self.load_data()
            except Exception as e:
                QMessageBox.critical(self, "Ошибка", f"Ошибка при удалении: {e}")
