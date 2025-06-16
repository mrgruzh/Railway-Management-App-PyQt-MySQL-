from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QTableWidget,
    QTableWidgetItem, QPushButton, QMessageBox, QLineEdit, QFileDialog
)
from db import execute_query
import openpyxl


class OrdersForm(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Заказы и их билеты")
        self.setGeometry(550, 250, 1000, 600)
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()

        # Поисковая строка
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Поиск по заказам...")
        self.search_input.textChanged.connect(self.apply_order_filter)
        layout.addWidget(self.search_input)

        # Заголовок и таблица заказов
        layout.addWidget(QLabel("Список заказов"))
        self.orders_table = QTableWidget()
        self.orders_table.setColumnCount(6)
        self.orders_table.setHorizontalHeaderLabels([
            "ID", "Тип", "Откуда", "Куда", "Дата регистрации", "Статус"
        ])
        self.orders_table.cellClicked.connect(self.load_tickets_for_order)
        layout.addWidget(self.orders_table)

        btn_layout = QHBoxLayout()
        btn_refresh = QPushButton("Обновить заказы")
        btn_refresh.clicked.connect(self.load_orders)
        btn_export = QPushButton("Экспорт заказов в Excel")
        btn_export.clicked.connect(self.export_orders_to_excel)
        btn_layout.addWidget(btn_refresh)
        btn_layout.addWidget(btn_export)
        layout.addLayout(btn_layout)

        # Таблица билетов
        layout.addWidget(QLabel("Билеты, входящие в заказ"))
        self.tickets_table = QTableWidget()
        self.tickets_table.setColumnCount(6)
        self.tickets_table.setHorizontalHeaderLabels([
            "ID билета", "ФИО клиента", "ID поезда", "Дата отправления", "Место", "Стоимость"
        ])
        layout.addWidget(self.tickets_table)

        self.setLayout(layout)
        self.load_orders()

    def load_orders(self):
        self.orders_table.setRowCount(0)
        self.all_orders = []
        query = """
            SELECT id_order, order_type, order_initial_station,
                   order_terminal_station, order_registration_date, order_status
            FROM r_order
        """
        try:
            rows = execute_query(query)
            self.all_orders = rows
            self.apply_order_filter()
        except Exception as e:
            QMessageBox.critical(self, "Ошибка", f"Ошибка при загрузке заказов: {e}")

    def apply_order_filter(self):
        keyword = self.search_input.text().lower()
        self.orders_table.setRowCount(0)

        for row_data in self.all_orders:
            if any(keyword in str(cell).lower() for cell in row_data):
                row_num = self.orders_table.rowCount()
                self.orders_table.insertRow(row_num)
                for col_num, col_data in enumerate(row_data):
                    self.orders_table.setItem(row_num, col_num, QTableWidgetItem(str(col_data)))

    def load_tickets_for_order(self, row, column):
        self.tickets_table.setRowCount(0)
        order_id_item = self.orders_table.item(row, 0)
        if not order_id_item:
            return
        order_id = order_id_item.text()

        query = """
            SELECT t.id_ticket, c.client_full_name, t.r_train_id_train,
                   t.ticket_date_and_time_of_departure, t.ticket_place_number, t.ticket_cost
            FROM r_ticket t
            JOIN r_client c ON t.r_client_id_client = c.id_client
            WHERE t.r_order_id_order = %s
        """
        try:
            rows = execute_query(query, (order_id,))
            for row_num, row_data in enumerate(rows):
                self.tickets_table.insertRow(row_num)
                for col_num, col_data in enumerate(row_data):
                    self.tickets_table.setItem(row_num, col_num, QTableWidgetItem(str(col_data)))
        except Exception as e:
            QMessageBox.critical(self, "Ошибка", f"Ошибка при загрузке билетов: {e}")

    def export_orders_to_excel(self):
        if self.orders_table.rowCount() == 0:
            QMessageBox.information(self, "Нет данных", "Нет заказов для экспорта.")
            return

        path, _ = QFileDialog.getSaveFileName(
            self, "Сохранить заказы в Excel", "заказы.xlsx", "Excel Files (*.xlsx)"
        )
        if not path:
            return

        try:
            wb = openpyxl.Workbook()
            ws = wb.active
            ws.title = "Заказы"

            # Заголовки
            headers = [self.orders_table.horizontalHeaderItem(i).text() for i in range(self.orders_table.columnCount())]
            ws.append(headers)

            # Данные
            for row in range(self.orders_table.rowCount()):
                values = [
                    self.orders_table.item(row, col).text() if self.orders_table.item(row, col) else ""
                    for col in range(self.orders_table.columnCount())
                ]
                ws.append(values)

            wb.save(path)
            QMessageBox.information(self, "Успех", "Файл Excel успешно сохранён.")
        except Exception as e:
            QMessageBox.critical(self, "Ошибка", f"Ошибка при сохранении: {e}")
