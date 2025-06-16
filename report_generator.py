from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QPushButton,
    QTableWidget, QTableWidgetItem, QDateEdit, QHBoxLayout,
    QMessageBox, QFileDialog, QLineEdit
)
from PyQt5.QtCore import QDate, Qt
from db import execute_query
import openpyxl


class ReportGenerator(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Отчёт по билетам за период")
        self.setGeometry(550, 250, 1000, 600)
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()

        # Период
        period_layout = QHBoxLayout()
        self.start_date = QDateEdit()
        self.start_date.setDate(QDate.currentDate().addMonths(-1))
        self.start_date.setCalendarPopup(True)

        self.end_date = QDateEdit()
        self.end_date.setDate(QDate.currentDate())
        self.end_date.setCalendarPopup(True)

        btn_generate = QPushButton("Сформировать отчёт")
        btn_generate.clicked.connect(self.load_data)

        period_layout.addWidget(QLabel("С:"))
        period_layout.addWidget(self.start_date)
        period_layout.addWidget(QLabel("По:"))
        period_layout.addWidget(self.end_date)
        period_layout.addWidget(btn_generate)

        layout.addLayout(period_layout)

        # Фильтры
        filter_layout = QHBoxLayout()
        self.station_filter = QLineEdit()
        self.station_filter.setPlaceholderText("Фильтр по станции отправления")
        self.station_filter.textChanged.connect(self.apply_filters)

        self.status_filter = QLineEdit()
        self.status_filter.setPlaceholderText("Фильтр по статусу билета")
        self.status_filter.textChanged.connect(self.apply_filters)

        filter_layout.addWidget(self.station_filter)
        filter_layout.addWidget(self.status_filter)
        layout.addLayout(filter_layout)

        # Таблица
        self.table = QTableWidget()
        self.table.setColumnCount(6)
        self.table.setHorizontalHeaderLabels([
            "ID", "ФИО клиента", "Станция отправления", "Поезд", "Дата отправления", "Статус"
        ])
        self.table.setSortingEnabled(True)
        layout.addWidget(self.table)

        # Кнопки экспорта
        export_layout = QHBoxLayout()
        btn_export_txt = QPushButton("Экспорт в TXT")
        btn_export_txt.clicked.connect(self.export_txt)
        btn_export_xlsx = QPushButton("Экспорт в XLSX")
        btn_export_xlsx.clicked.connect(self.export_xlsx)
        export_layout.addWidget(btn_export_txt)
        export_layout.addWidget(btn_export_xlsx)
        layout.addLayout(export_layout)

        self.setLayout(layout)

    def load_data(self):
        self.table.setRowCount(0)
        query = """
            SELECT t.id_ticket, c.client_full_name, t.ticket_initial_station, t.r_train_id_train,
                   t.ticket_date_and_time_of_departure, t.ticket_status
            FROM r_ticket t
            JOIN r_client c ON t.r_client_id_client = c.id_client
            WHERE t.ticket_date_and_time_of_departure BETWEEN %s AND %s
        """
        start = self.start_date.date().toString("yyyy-MM-dd")
        end = self.end_date.date().toString("yyyy-MM-dd")

        try:
            self.all_data = execute_query(query, (start, end))
            self.apply_filters()
        except Exception as e:
            QMessageBox.critical(self, "Ошибка", f"Ошибка загрузки данных: {e}")

    def apply_filters(self):
        station_kw = self.station_filter.text().lower()
        status_kw = self.status_filter.text().lower()

        self.table.setRowCount(0)
        for row_data in self.all_data:
            if station_kw not in row_data[2].lower():
                continue
            if status_kw not in row_data[5].lower():
                continue

            row_num = self.table.rowCount()
            self.table.insertRow(row_num)
            for col, val in enumerate(row_data):
                self.table.setItem(row_num, col, QTableWidgetItem(str(val)))

    def export_txt(self):
        path, _ = QFileDialog.getSaveFileName(self, "Сохранить отчёт в TXT", "", "Text Files (*.txt)")
        if not path:
            return
        try:
            with open(path, "w", encoding="utf-8") as file:
                for row in range(self.table.rowCount()):
                    values = [
                        self.table.item(row, col).text() if self.table.item(row, col) else ""
                        for col in range(self.table.columnCount())
                    ]
                    file.write("\t".join(values) + "\n")
            QMessageBox.information(self, "Успех", "Отчёт экспортирован в TXT.")
        except Exception as e:
            QMessageBox.critical(self, "Ошибка", f"Ошибка при сохранении: {e}")

    def export_xlsx(self):
        path, _ = QFileDialog.getSaveFileName(self, "Сохранить отчёт в Excel", "", "Excel Files (*.xlsx)")
        if not path:
            return
        try:
            wb = openpyxl.Workbook()
            ws = wb.active
            ws.title = "Отчёт"

            # Заголовки
            headers = [self.table.horizontalHeaderItem(i).text() for i in range(self.table.columnCount())]
            ws.append(headers)

            # Данные
            for row in range(self.table.rowCount()):
                values = [
                    self.table.item(row, col).text() if self.table.item(row, col) else ""
                    for col in range(self.table.columnCount())
                ]
                ws.append(values)

            wb.save(path)
            QMessageBox.information(self, "Успех", "Отчёт экспортирован в Excel.")
        except Exception as e:
            QMessageBox.critical(self, "Ошибка", f"Ошибка при сохранении XLSX: {e}")
