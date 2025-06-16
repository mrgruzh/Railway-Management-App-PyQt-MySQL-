# trains_form.py

from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QFormLayout, QTableWidget, QTableWidgetItem,
    QLabel, QPushButton, QMessageBox, QDialog, QComboBox, QLineEdit, QDateTimeEdit
)
from PyQt5.QtCore import QDateTime
from db import execute_query


class AddVanDialog(QDialog):
    def __init__(self, van_type='', capacity='', status='Ready'):
        super().__init__()
        self.setWindowTitle("Вагон")
        self.setFixedSize(300, 200)

        self.layout = QFormLayout()

        self.type_box = QComboBox()
        self.type_box.addItems(["Seated", "Compartment", "Luxury", "Open"])
        if van_type:
            self.type_box.setCurrentText(van_type)

        self.capacity_input = QLineEdit()
        self.capacity_input.setPlaceholderText("например, 60")
        self.capacity_input.setText(capacity)

        self.status_box = QComboBox()
        self.status_box.addItems(["Ready", "Maintenance", "Out of service"])
        if status:
            self.status_box.setCurrentText(status)

        self.layout.addRow("Тип вагона:", self.type_box)
        self.layout.addRow("Вместимость:", self.capacity_input)
        self.layout.addRow("Статус:", self.status_box)

        self.submit_btn = QPushButton("Сохранить")
        self.submit_btn.clicked.connect(self.accept)
        self.layout.addWidget(self.submit_btn)

        self.setLayout(self.layout)

    def get_data(self):
        return (
            self.type_box.currentText(),
            self.capacity_input.text(),
            self.status_box.currentText()
        )


class TrainsForm(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Поезда и вагоны")
        self.setGeometry(550, 250, 900, 600)
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()

        layout.addWidget(QLabel("Список поездов"))

        self.trains_table = QTableWidget()
        self.trains_table.setColumnCount(3)
        self.trains_table.setHorizontalHeaderLabels(["ID", "Тип", "Дата отправления"])
        self.trains_table.cellClicked.connect(self.load_vans_for_train)
        layout.addWidget(self.trains_table)

        btn_add_train = QPushButton("Добавить поезд")
        btn_add_train.clicked.connect(self.add_train)
        layout.addWidget(btn_add_train)

        btn_edit_train = QPushButton("Редактировать поезд")
        btn_edit_train.clicked.connect(self.edit_train)
        layout.addWidget(btn_edit_train)

        btn_delete_train = QPushButton("Удалить поезд")
        btn_delete_train.clicked.connect(self.delete_train)
        layout.addWidget(btn_delete_train)

        layout.addWidget(QLabel("Вагоны выбранного поезда"))

        self.vans_table = QTableWidget()
        self.vans_table.setColumnCount(3)
        self.vans_table.setHorizontalHeaderLabels(["ID", "Тип", "Вместимость"])
        layout.addWidget(self.vans_table)

        btn_add_van = QPushButton("Добавить вагон к выбранному поезду")
        btn_add_van.clicked.connect(self.add_van_to_selected_train)
        layout.addWidget(btn_add_van)

        btn_edit_van = QPushButton("Редактировать выбранный вагон")
        btn_edit_van.clicked.connect(self.edit_selected_van)
        layout.addWidget(btn_edit_van)

        btn_delete_van = QPushButton("Удалить выбранный вагон")
        btn_delete_van.clicked.connect(self.delete_selected_van)
        layout.addWidget(btn_delete_van)

        self.setLayout(layout)
        self.load_trains()
    def load_trains(self):
        self.trains_table.setRowCount(0)
        query = "SELECT id_train, train_type, train_date_and_time_of_departure FROM r_train"
        try:
            rows = execute_query(query)
            for row_num, row_data in enumerate(rows):
                self.trains_table.insertRow(row_num)
                for col_num, col_data in enumerate(row_data):
                    self.trains_table.setItem(row_num, col_num, QTableWidgetItem(str(col_data)))
        except Exception as e:
            QMessageBox.critical(self, "Ошибка", f"Не удалось загрузить поезда: {e}")

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
            except Exception as e:
                QMessageBox.critical(self, "Ошибка", f"Ошибка при добавлении вокзала: {e}")

    def load_vans_for_train(self, row, column):
        train_id = self.trains_table.item(row, 0).text()
        self.vans_table.setRowCount(0)

        query = """
            SELECT id_van, van_type, van_capacity
            FROM r_van
            WHERE r_train_id_train = %s
        """
        try:
            rows = execute_query(query, (train_id,))
            for row_num, row_data in enumerate(rows):
                self.vans_table.insertRow(row_num)
                for col_num, col_data in enumerate(row_data):
                    self.vans_table.setItem(row_num, col_num, QTableWidgetItem(str(col_data)))
        except Exception as e:
            QMessageBox.critical(self, "Ошибка", f"Не удалось загрузить вагоны: {e}")

    def add_train(self):
        dialog = QDialog(self)
        dialog.setWindowTitle("Добавление поезда")
        form = QFormLayout(dialog)

        type_box = QComboBox()
        type_box.addItems(["Express", "Fast", "Local"])

        departure_input = QDateTimeEdit()
        departure_input.setDateTime(QDateTime.currentDateTime())
        departure_input.setCalendarPopup(True)

        arrival_input = QDateTimeEdit()
        arrival_input.setDateTime(QDateTime.currentDateTime().addSecs(3600))
        arrival_input.setCalendarPopup(True)

        platform_box = QComboBox()
        station_box = QComboBox()

        try:
            platforms = execute_query("SELECT id_platform FROM r_platform")
            stations = execute_query("SELECT id_station FROM r_station")
            for p in platforms:
                platform_box.addItem(str(p[0]))
            for s in stations:
                station_box.addItem(str(s[0]))
        except Exception as e:
            QMessageBox.critical(self, "Ошибка", f"Ошибка при загрузке справочников: {e}")
            return

        form.addRow("Тип:", type_box)
        form.addRow("Дата и время отправления:", departure_input)
        form.addRow("Дата и время прибытия:", arrival_input)
        form.addRow("Платформа:", platform_box)
        form.addRow("Вокзал (станция):", station_box)

        btn = QPushButton("Добавить")
        btn.clicked.connect(dialog.accept)
        form.addWidget(btn)

        dialog.setLayout(form)

        if dialog.exec_():
            train_type = type_box.currentText()
            departure = departure_input.dateTime().toString("yyyy-MM-dd HH:mm:ss")
            arrival = arrival_input.dateTime().toString("yyyy-MM-dd HH:mm:ss")
            platform_id = platform_box.currentText()
            station_id = station_box.currentText()

            query_check = """
                SELECT COUNT(*) FROM r_platform
                WHERE id_platform = %s AND r_station_id_station = %s
            """
            try:
                result = execute_query(query_check, (platform_id, station_id))
                if result[0][0] == 0:
                    QMessageBox.warning(self, "Ошибка", "Платформа не принадлежит указанному вокзалу.")
                    return
            except Exception as e:
                QMessageBox.critical(self, "Ошибка", f"Ошибка при проверке платформы: {e}")
                return

            query = """
                INSERT INTO r_train (train_type, train_date_and_time_of_departure, train_date_and_time_of_arrival, r_platform_id_platform)
                VALUES (%s, %s, %s, %s)
            """
            try:
                execute_query(query, (train_type, departure, arrival, platform_id))
                QMessageBox.information(self, "Успех", "Поезд добавлен.")
                self.load_trains()
            except Exception as e:
                QMessageBox.critical(self, "Ошибка", str(e))



    def edit_train(self):
        row = self.trains_table.currentRow()
        if row < 0:
            QMessageBox.warning(self, "Ошибка", "Выберите поезд.")
            return

        train_id = self.trains_table.item(row, 0).text()
        old_type = self.trains_table.item(row, 1).text()
        old_departure = self.trains_table.item(row, 2).text()

        result = execute_query(
            "SELECT train_date_and_time_of_arrival, r_platform_id_platform FROM r_train WHERE id_train = %s",
            (train_id,)
        )
        if not result:
            QMessageBox.warning(self, "Ошибка", "Поезд не найден.")
            return
        old_arrival, platform_id = result[0]

        dialog = QDialog(self)
        dialog.setWindowTitle("Редактирование поезда")
        form = QFormLayout(dialog)

        type_box = QComboBox()
        type_box.addItems(["Express", "Fast", "Local"])
        type_box.setCurrentText(old_type)

        dep_edit = QDateTimeEdit()
        dep_edit.setDateTime(QDateTime.fromString(old_departure, "yyyy-MM-dd HH:mm:ss"))
        dep_edit.setCalendarPopup(True)

        arr_edit = QDateTimeEdit()
        arr_edit.setDateTime(QDateTime.fromString(str(old_arrival), "yyyy-MM-dd HH:mm:ss"))
        arr_edit.setCalendarPopup(True)

        platform_box = QComboBox()
        try:
            platforms = execute_query("SELECT id_platform FROM r_platform")
            for p in platforms:
                platform_box.addItem(str(p[0]))
            platform_box.setCurrentText(str(platform_id))
        except Exception as e:
            QMessageBox.critical(self, "Ошибка", f"Ошибка при загрузке платформ: {e}")
            return

        form.addRow("Тип:", type_box)
        form.addRow("Дата и время отправления:", dep_edit)
        form.addRow("Дата и время прибытия:", arr_edit)
        form.addRow("Платформа:", platform_box)

        btn = QPushButton("Сохранить")
        btn.clicked.connect(dialog.accept)
        form.addWidget(btn)
        dialog.setLayout(form)

        if dialog.exec_():
            new_type = type_box.currentText()
            new_departure = dep_edit.dateTime().toString("yyyy-MM-dd HH:mm:ss")
            new_arrival = arr_edit.dateTime().toString("yyyy-MM-dd HH:mm:ss")
            new_platform = platform_box.currentText()

            query = """
                UPDATE r_train
                SET train_type=%s, train_date_and_time_of_departure=%s,
                    train_date_and_time_of_arrival=%s, r_platform_id_platform=%s
                WHERE id_train=%s
            """
            try:
                execute_query(query, (new_type, new_departure, new_arrival, new_platform, train_id))
                QMessageBox.information(self, "Успех", "Поезд обновлён.")
                self.load_trains()
            except Exception as e:
                QMessageBox.critical(self, "Ошибка", str(e))

    def delete_train(self):
        row = self.trains_table.currentRow()
        if row < 0:
            QMessageBox.warning(self, "Ошибка", "Выберите поезд.")
            return

        train_id = self.trains_table.item(row, 0).text()

        confirm = QMessageBox.question(
            self, "Удаление", f"Удалить поезд ID {train_id} и все его вагоны?",
            QMessageBox.Yes | QMessageBox.No
        )

        if confirm == QMessageBox.Yes:
            try:
                platform_id = execute_query(
                    "SELECT r_platform_id_platform FROM r_train WHERE id_train = %s", (train_id,)
                )[0][0]

                execute_query(
                    "DELETE FROM r_van WHERE r_train_id_train = %s AND r_train_r_platform_id_platform = %s",
                    (train_id, platform_id)
                )
                execute_query("DELETE FROM r_train WHERE id_train = %s", (train_id,))
                QMessageBox.information(self, "Успех", "Поезд и вагоны удалены.")
                self.load_trains()
            except Exception as e:
                QMessageBox.critical(self, "Ошибка", str(e))

    def add_van_to_selected_train(self):
        row = self.trains_table.currentRow()
        if row < 0:
            QMessageBox.warning(self, "Ошибка", "Выберите поезд.")
            return

        train_id = self.trains_table.item(row, 0).text()
        platform_id = execute_query(
            "SELECT r_platform_id_platform FROM r_train WHERE id_train = %s", (train_id,)
        )[0][0]

        dialog = AddVanDialog()
        if dialog.exec_():
            van_type, capacity, status = dialog.get_data()
            if not capacity.isdigit():
                QMessageBox.warning(self, "Ошибка", "Вместимость должна быть числом.")
                return

            query = """
                INSERT INTO r_van (van_type, van_capacity, van_status, r_train_id_train, r_train_r_platform_id_platform)
                VALUES (%s, %s, %s, %s, %s)
            """
            try:
                execute_query(query, (van_type, int(capacity), status, train_id, platform_id))
                QMessageBox.information(self, "Успех", "Вагон добавлен.")
                self.load_vans_for_train(row, 0)
            except Exception as e:
                QMessageBox.critical(self, "Ошибка", str(e))

    def edit_selected_van(self):
        train_row = self.trains_table.currentRow()
        van_row = self.vans_table.currentRow()
        if train_row < 0 or van_row < 0:
            QMessageBox.warning(self, "Ошибка", "Выберите вагон.")
            return

        train_id = self.trains_table.item(train_row, 0).text()
        van_id = self.vans_table.item(van_row, 0).text()
        current_type = self.vans_table.item(van_row, 1).text()
        current_capacity = self.vans_table.item(van_row, 2).text()

        platform_id = execute_query(
            "SELECT r_platform_id_platform FROM r_train WHERE id_train = %s", (train_id,)
        )[0][0]

        dialog = AddVanDialog(current_type, current_capacity)
        if dialog.exec_():
            van_type, capacity, status = dialog.get_data()
            if not capacity.isdigit():
                QMessageBox.warning(self, "Ошибка", "Вместимость должна быть числом.")
                return

            query = """
                UPDATE r_van SET van_type=%s, van_capacity=%s, van_status=%s
                WHERE id_van=%s AND r_train_id_train=%s AND r_train_r_platform_id_platform=%s
            """
            try:
                execute_query(query, (van_type, int(capacity), status, van_id, train_id, platform_id))
                QMessageBox.information(self, "Успех", "Вагон обновлён.")
                self.load_vans_for_train(train_row, 0)
            except Exception as e:
                QMessageBox.critical(self, "Ошибка", str(e))

    def delete_selected_van(self):
        train_row = self.trains_table.currentRow()
        van_row = self.vans_table.currentRow()
        if train_row < 0 or van_row < 0:
            QMessageBox.warning(self, "Ошибка", "Выберите вагон.")
            return

        van_id = self.vans_table.item(van_row, 0).text()
        train_id = self.trains_table.item(train_row, 0).text()
        platform_id = execute_query(
            "SELECT r_platform_id_platform FROM r_train WHERE id_train = %s", (train_id,)
        )[0][0]

        confirm = QMessageBox.question(
            self, "Удаление", f"Удалить вагон ID {van_id}?",
            QMessageBox.Yes | QMessageBox.No
        )

        if confirm == QMessageBox.Yes:
            query = """
                DELETE FROM r_van
                WHERE id_van = %s AND r_train_id_train = %s AND r_train_r_platform_id_platform = %s
            """
            try:
                execute_query(query, (van_id, train_id, platform_id))
                QMessageBox.information(self, "Успех", "Вагон удалён.")
                self.load_vans_for_train(train_row, 0)
            except Exception as e:
                QMessageBox.critical(self, "Ошибка", str(e))


