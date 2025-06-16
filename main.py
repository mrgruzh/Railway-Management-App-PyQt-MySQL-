# main.py
import sys
from PyQt5.QtWidgets import QApplication
from auth import LoginWindow
from dashboard import Dashboard
from db import init_db_connection

def main():
    if not init_db_connection():
        sys.exit("Ошибка подключения к базе данных.")

    app = QApplication(sys.argv)

    login_window = LoginWindow()
    def on_login(role):
        dashboard = Dashboard(role)
        dashboard.show()
    login_window.login_successful.connect(on_login)

    login_window.show()
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()
