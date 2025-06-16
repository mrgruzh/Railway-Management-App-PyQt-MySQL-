from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QTableWidget, QTableWidgetItem,
    QPushButton, QLabel, QMessageBox, QDialog, QFormLayout,
    QComboBox, QLineEdit
)
from db import execute_query


class AddPlatformDialog(QDialog):
    def __init__(self, number='', status='Active'):
        super().__init__()
        self.setWindowTitle("Платформа")
        self.setFixedSize(300, 150)

        layout = QFormLayout()

        self.number_input = QLineEdit()
        self.number_input.setText(number)

        self.status_box = QComboBox()
        self.status_box.addItems(["Active", "Maintenance", "Closed"])
        if status in ["Active", "Maintenance", "Closed"]:
            self.status_box.setCurrentText(status)

        layout.addRow("Номер платформы:", self.number_input)
        layout.addRow("Статус:", self.status_box)

        self.submit_btn = QPushButton("Сохранить")
        self.submit_btn.clicked.connect(self.accept)
        layout.addWidget(self.submit_btn)

        self.setLayout(layout)

    def get_data(self):
        return self.number_input.text(), self.status_box.currentText()


class PlatformsForm(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Вокзалы и платформы")
        self.setGeometry(550, 250, 900, 600)
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()

        layout.addWidget(QLabel("Список вокзалов"))
        self.stations_table = QTableWidget()
        self.stations_table.setColumnCount(4)
        self.stations_table.setHorizontalHeaderLabels(["ID", "Название", "Адрес", "Кол-во платформ"])
        self.stations_table.cellClicked.connect(self.load_platforms_for_station)
        layout.addWidget(self.stations_table)

        btn_refresh = QPushButton("Обновить вокзалы")
        btn_refresh.clicked.connect(self.load_stations)
        layout.addWidget(btn_refresh)
        btn_add_station = QPushButton("Добавить вокзал")
        btn_add_station.clicked.connect(self.add_station)
        layout.addWidget(btn_add_station)

        layout.addWidget(QLabel("Платформы на выбранном вокзале"))
        self.platforms_table = QTableWidget()
        self.platforms_table.setColumnCount(3)
        self.platforms_table.setHorizontalHeaderLabels(["ID", "Номер", "Статус"])
        layout.addWidget(self.platforms_table)

        btn_add_platform = QPushButton("Добавить платформу к выбранному вокзалу")
        btn_add_platform.clicked.connect(self.add_platform_to_station)
        layout.addWidget(btn_add_platform)

        btn_edit_platform = QPushButton("Редактировать выбранную платформу")
        btn_edit_platform.clicked.connect(self.edit_selected_platform)
        layout.addWidget(btn_edit_platform)

        btn_delete_platform = QPushButton("Удалить выбранную платформу")
        btn_delete_platform.clicked.connect(self.delete_selected_platform)
        layout.addWidget(btn_delete_platform)

        self.setLayout(layout)
        self.load_stations()

    def load_stations(self):
        self.stations_table.setRowCount(0)
        query = "SELECT id_station, station_name, station_address, station_quantity_platforms FROM r_station"
        try:
            rows = execute_query(query)
            for row_num, row_data in enumerate(rows):
                self.stations_table.insertRow(row_num)
                for col_num, col_data in enumerate(row_data):
                    self.stations_table.setItem(row_num, col_num, QTableWidgetItem(str(col_data)))
        except Exception as e:
            QMessageBox.critical(self, "Ошибка", f"Не удалось загрузить вокзалы: {e}")

    def load_platforms_for_station(self, row, column):
        station_id_item = self.stations_table.item(row, 0)
        if not station_id_item:
            return

        station_id = station_id_item.text()

        # Автообновление количества платформ
        update_query = """
            UPDATE r_station
            SET station_quantity_platforms = (
                SELECT COUNT(*) FROM r_platform WHERE r_station_id_station = %s
            )
            WHERE id_station = %s
        """
        try:
            execute_query(update_query, (station_id, station_id))
            self.load_stations()  # Обновим верхнюю таблицу
        except Exception as e:
            QMessageBox.critical(self, "Ошибка", f"Не удалось обновить количество платформ: {e}")

        self.platforms_table.setRowCount(0)

        query = """
            SELECT id_platform, platform_number, platform_status
            FROM r_platform
            WHERE r_station_id_station = %s
        """
        try:
            rows = execute_query(query, (station_id,))
            for row_num, row_data in enumerate(rows):
                self.platforms_table.insertRow(row_num)
                for col_num, col_data in enumerate(row_data):
                    self.platforms_table.setItem(row_num, col_num, QTableWidgetItem(str(col_data)))
        except Exception as e:
            QMessageBox.critical(self, "Ошибка", f"Не удалось загрузить платформы: {e}")

    def add_platform_to_station(self):
        current_row = self.stations_table.currentRow()
        if current_row < 0:
            QMessageBox.warning(self, "Выбор вокзала", "Выберите вокзал, к которому нужно добавить платформу.")
            return

        station_id_item = self.stations_table.item(current_row, 0)
        if not station_id_item:
            QMessageBox.warning(self, "Ошибка", "Не удалось получить ID вокзала.")
            return

        station_id = station_id_item.text()

        dialog = AddPlatformDialog()
        if dialog.exec_() == QDialog.Accepted:
            number, status = dialog.get_data()

            if not number:
                QMessageBox.warning(self, "Ошибка", "Введите номер платформы.")
                return

            query = """
                INSERT INTO r_platform (platform_number, platform_status, r_station_id_station)
                VALUES (%s, %s, %s)
            """
            try:
                execute_query(query, (number, status, station_id))
                QMessageBox.information(self, "Успех", "Платформа успешно добавлена.")
                self.load_platforms_for_station(current_row, 0)
            except Exception as e:
                QMessageBox.critical(self, "Ошибка", f"Ошибка при добавлении платформы: {e}")

    def edit_selected_platform(self):
        row = self.platforms_table.currentRow()
        station_row = self.stations_table.currentRow()

        if row < 0 or station_row < 0:
            QMessageBox.warning(self, "Ошибка", "Выберите платформу для редактирования.")
            return

        platform_id = self.platforms_table.item(row, 0).text()
        number = self.platforms_table.item(row, 1).text()
        status = self.platforms_table.item(row, 2).text()

        dialog = AddPlatformDialog(number, status)
        if dialog.exec_() == QDialog.Accepted:
            new_number, new_status = dialog.get_data()
            if not new_number:
                QMessageBox.warning(self, "Ошибка", "Введите номер платформы.")
                return

            query = """
                UPDATE r_platform
                SET platform_number = %s, platform_status = %s
                WHERE id_platform = %s
            """
            try:
                execute_query(query, (new_number, new_status, platform_id))
                QMessageBox.information(self, "Успех", "Платформа обновлена.")
                self.load_platforms_for_station(station_row, 0)
            except Exception as e:
                QMessageBox.critical(self, "Ошибка", f"Ошибка при обновлении: {e}")

    def delete_selected_platform(self):
        row = self.platforms_table.currentRow()
        station_row = self.stations_table.currentRow()

        if row < 0:
            QMessageBox.warning(self, "Ошибка", "Выберите платформу для удаления.")
            return

        platform_id = self.platforms_table.item(row, 0).text()

        confirm = QMessageBox.question(
            self,
            "Удаление",
            "Вы уверены, что хотите удалить выбранную платформу?",
            QMessageBox.Yes | QMessageBox.No
        )

        if confirm == QMessageBox.Yes:
            query = "DELETE FROM r_platform WHERE id_platform = %s"
            try:
                execute_query(query, (platform_id,))
                QMessageBox.information(self, "Успех", "Платформа удалена.")
                self.load_platforms_for_station(station_row, 0)
            except Exception as e:
                QMessageBox.critical(self, "Ошибка", f"Ошибка при удалении: {e}")

    def add_station(self):
        dialog = QDialog(self)
        dialog.setWindowTitle("Добавление вокзала")
        form = QFormLayout(dialog)

        name_input = QLineEdit()
        address_input = QLineEdit()

        form.addRow("Название станции:", name_input)
        form.addRow("Адрес станции:", address_input)

        btn = QPushButton("Добавить")
        btn.clicked.connect(dialog.accept)
        form.addWidget(btn)

        dialog.setLayout(form)

        if dialog.exec_():
            name = name_input.text().strip()
            address = address_input.text().strip()

            if not name or not address:
                QMessageBox.warning(self, "Ошибка", "Все поля обязательны.")
                return

            query = """
                INSERT INTO r_station (station_name, station_address, station_quantity_platforms)
                VALUES (%s, %s, 0)
            """
            try:
                execute_query(query, (name, address))
                QMessageBox.information(self, "Успех", "Вокзал добавлен.")
                self.load_stations()
            except Exception as e:
                QMessageBox.critical(self, "Ошибка", f"Ошибка при добавлении вокзала: {e}")
