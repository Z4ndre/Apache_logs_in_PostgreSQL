import sys
import os
import re
import configparser
from PyQt6.QtWidgets import (QApplication, QWidget, QTableView, QVBoxLayout,
                             QHBoxLayout, QDateTimeEdit, QLabel, QLineEdit, QPushButton, QCheckBox)
from PyQt6.QtCore import QTimer, QAbstractTableModel, Qt, QDateTime
from db import DataBase
from messages_for_user import show_notification
import pandas as pd
import requests
import appearance


class PandasModel(QAbstractTableModel):
    def __init__(self, data):
        super().__init__()
        self._data = data

    def rowCount(self, parent=None):
        return self._data.shape[0]

    def columnCount(self, parent=None):
        return self._data.shape[1]

    def data(self, index, role=Qt.ItemDataRole.DisplayRole):
        if role == Qt.ItemDataRole.DisplayRole:
            return str(self._data.iloc[index.row(), index.column()])
        return None

    def headerData(self, section, orientation, role=Qt.ItemDataRole.DisplayRole):
        if role == Qt.ItemDataRole.DisplayRole:
            if orientation == Qt.Orientation.Horizontal:
                return str(self._data.columns[section])
            elif orientation == Qt.Orientation.Vertical:
                return str(self._data.index[section])
        return None


class Window(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Apache Logs")
        self.setGeometry(700, 600, 800, 450)
        appearance.apply_windows_style(self)
        self.setStyleSheet("background-color: #97a6a5;")

        self.setFixedSize(1050, 450)
        self.pattern = re.compile(
            r'(?P<ip>\S+) '
            r'(?P<remote_logname>-|\S+) '
            r'-\s'
            r'\[(?P<datetime>[^]]+)\] '
            r'"(?P<request>[^"]*)" '
            r'(?P<status>\d+)'
            r'(?: (?P<size>\S+))?'
        )
        self.get_config()
        self.database = DataBase(self.config)
        self.database.connect_to_Db(self.dbname, self.user, self.password, self.host, self.port)
        self.last_modified_time = os.path.getmtime(self.path_to_log_file)
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.check_file_modification)
        self.timer.start(1000)
        self.horiz_layout = QHBoxLayout(self)
        self.table = QTableView(self)
        self.init_inter()
        self.update_table()
        self.init_table()
        self.settings_table()

    def init_check_group(self):
        self.group_ip_box = QHBoxLayout(self)
        self.check_group_by_ip = QCheckBox(self)
        self.check_group_by_ip.setFixedSize(30, 30)
        self.label_5 = QLabel(self)
        self.label_5.setFixedSize(130, 50)
        self.label_5.setText("Группировка по IP")

        self.group_ip_box.addWidget(self.label_5)
        self.group_ip_box.addSpacing(14)
        self.group_ip_box.addWidget(self.check_group_by_ip)

    def init_start_calendar(self):
        self.in_start_box = QHBoxLayout(self)
        self.check_enable_start_date = QCheckBox(self)
        self.check_enable_start_date.setFixedSize(30, 30)
        self.start_date = QDateTimeEdit(self)
        self.start_date.setFixedSize(130, 30)
        self.start_date.setEnabled(False)

        self.in_start_box.addWidget(self.start_date)
        self.in_start_box.addSpacing(10)
        self.in_start_box.addWidget(self.check_enable_start_date)

    def init_end_date_calendar(self):
        self.in_end_box = QHBoxLayout(self)
        self.check_enable_end_date = QCheckBox(self)
        self.check_enable_end_date.setFixedSize(30, 30)
        self.end_date = QDateTimeEdit(self)
        self.end_date.setFixedSize(130, 30)
        self.end_date.setEnabled(False)
        self.end_date.setDateTime(QDateTime.currentDateTime())

        self.in_end_box.addWidget(self.end_date)
        self.in_end_box.addSpacing(10)
        self.in_end_box.addWidget(self.check_enable_end_date)

    def init_status_code(self):
        self.status_box = QHBoxLayout(self)
        self.check_enable_status_code = QCheckBox(self)
        self.check_enable_status_code.setFixedSize(30, 30)
        self.status_code_line = QLineEdit(self)
        self.status_code_line.setFixedSize(130, 30)
        self.status_code_line.setEnabled(False)

        self.status_box.addWidget(self.status_code_line)
        self.status_box.addSpacing(10)
        self.status_box.addWidget(self.check_enable_status_code)

    def init_ip_line(self):
        self.ip_hor_box = QHBoxLayout(self)
        self.check_enable_ip_line = QCheckBox(self)
        self.check_enable_ip_line.setFixedSize(30, 30)
        self.ip_line = QLineEdit(self)
        self.ip_line.setFixedSize(130, 30)
        self.ip_line.setEnabled(False)

        self.ip_hor_box.addWidget(self.ip_line)
        self.ip_hor_box.addSpacing(10)
        self.ip_hor_box.addWidget(self.check_enable_ip_line)

    def init_inter(self):
        self.vert_layout = QVBoxLayout(self)

        self.label_1 = QLabel(self)
        self.label_1.setFixedSize(100, 40)
        self.label_1.setText("IP адресс")

        self.label_2 = QLabel(self)
        self.label_2.setFixedSize(100, 40)
        self.label_2.setText("Статус код")

        self.label_3 = QLabel(self)
        self.label_3.setFixedSize(100, 40)
        self.label_3.setText("Начальная дата")

        self.label_4 = QLabel(self)
        self.label_4.setFixedSize(100, 40)
        self.label_4.setText("Конечная дата")

        self.get_button = QPushButton(self)
        self.get_button.setText("Получить данные")
        self.get_button.setFixedSize(130, 35)

        self.init_check_group()
        self.vert_layout.addLayout(self.group_ip_box)
        self.ip_ver_box = QVBoxLayout(self)
        self.ip_ver_box.addWidget(self.label_1)
        self.init_ip_line()
        self.ip_ver_box.addLayout(self.ip_hor_box)
        self.vert_layout.addLayout(self.ip_ver_box)

        self.status_ver_box = QVBoxLayout(self)
        self.status_ver_box.addWidget(self.label_2)
        self.init_status_code()
        self.status_ver_box.addLayout(self.status_box)
        self.vert_layout.addLayout(self.status_ver_box)

        self.start_ver_box = QVBoxLayout(self)
        self.start_ver_box.addWidget(self.label_3)
        self.init_start_calendar()
        self.start_ver_box.addLayout(self.in_start_box)
        self.vert_layout.addLayout(self.start_ver_box)

        self.end_ver_box = QVBoxLayout(self)
        self.end_ver_box.addWidget(self.label_4)
        self.init_end_date_calendar()
        self.end_ver_box.addLayout(self.in_end_box)
        self.vert_layout.addLayout(self.end_ver_box)

        self.vert_layout.addSpacing(10)
        self.vert_layout.addWidget(self.get_button)

        self.get_button.clicked.connect(self.update_table)
        self.check_group_by_ip.stateChanged.connect(self.update_table)
        self.check_enable_ip_line.stateChanged.connect(self.toggle_ip_line)
        self.check_enable_status_code.stateChanged.connect(self.toggle_status_code)
        self.check_enable_start_date.stateChanged.connect(self.toggle_start_date)
        self.check_enable_end_date.stateChanged.connect(self.toggle_end_date)

        self.vert_layout.addStretch(0)
        self.horiz_layout.addItem(self.vert_layout)

    def toggle_start_date(self, state):
        if state == Qt.CheckState.Checked.value:
            self.start_date.setEnabled(True)
        else:
            self.start_date.setEnabled(False)

    def toggle_end_date(self, state):
        if state == Qt.CheckState.Checked.value:
            self.end_date.setEnabled(True)
        else:
            self.end_date.setEnabled(False)

    def toggle_status_code(self, state):
        if state == Qt.CheckState.Checked.value:
            self.status_code_line.setEnabled(True)
        else:
            self.status_code_line.setEnabled(False)

    def toggle_ip_line(self, state):
        if state == Qt.CheckState.Checked.value:
            self.ip_line.setEnabled(True)
        else:
            self.ip_line.setEnabled(False)

    def init_table(self):
        url = 'http://127.0.0.1:5000/get_all_info'
        response = requests.get(url)
        data = response.json()
        df = pd.DataFrame(data)
        model = PandasModel(df)
        self.table.setModel(model)
        self.table.setColumnWidth(0, 50)
        self.table.setColumnWidth(1, 100)
        self.table.setColumnWidth(2, 100)
        self.table.setColumnWidth(3, 100)
        self.table.setColumnWidth(4, 80)
        self.table.setColumnWidth(5, 80)
        self.table.setColumnWidth(6, 190)

    def settings_table(self):
        self.table.setFixedSize(720, 400)
        appearance.apply_table_style(self.table)
        self.table.setShowGrid(True)
        self.table.setGridStyle(Qt.PenStyle.DotLine)
        self.table.setAlternatingRowColors(True)
        self.table.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOn)
        self.table.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOn)
        self.table.setSelectionBehavior(QTableView.SelectionBehavior.SelectRows)
        self.table.setSelectionMode(QTableView.SelectionMode.SingleSelection)
        self.table.setEditTriggers(QTableView.EditTrigger.DoubleClicked)
        self.table.setCornerButtonEnabled(False)
        self.table.verticalHeader().setVisible(False)
        self.horiz_layout.addWidget(self.table)
        self.setLayout(self.horiz_layout)

    def update_table(self):
        try:
            ip_address = self.ip_line.text() if self.ip_line.isEnabled() else None
            status_code = self.status_code_line.text() if self.status_code_line.isEnabled() else None
            start_date = self.start_date.dateTime().toString('dd/MMM/yyyy') if self.start_date.isEnabled() else None
            end_date = self.end_date.dateTime().toString('dd/MMM/yyyy') if self.end_date.isEnabled() else None
            group_by_ip = self.check_group_by_ip.isChecked()
            params = {
                'ip_address': ip_address,
                'status_code': status_code,
                'start_date': start_date,
                'end_date': end_date,
                'group_by_ip': group_by_ip
            }
            response = requests.get('http://127.0.0.1:5000/get_all_info', params=params)
            data = response.json()
            df = pd.DataFrame(data)
            model = PandasModel(df)
            self.table.setModel(model)
        except Exception as e:
            show_notification(f"Ошибка при обновлении таблицы: {e}")

    def get_config(self):
        try:
            self.config = configparser.ConfigParser()
            self.config.read('config.ini', encoding='utf-8')
            self.dbname = self.config['DataBase']['dbname']
            self.user = self.config['DataBase']['user']
            self.password = self.config['DataBase']['password']
            self.host = self.config['DataBase']['host']
            self.port = self.config['DataBase']['port']
            self.procedure_name = self.config['DataBase']['procedure_name']
            self.path_to_log_file = self.config['Files']['path_to_log_file']
        except Exception as e:
            show_notification(f"Ошибка при чтении конфиг файла config.ini: {e}")

    def check_file_modification(self):
        try:
            current_modified_time = os.path.getmtime(self.path_to_log_file)
            if current_modified_time != self.last_modified_time:
                self.last_modified_time = current_modified_time
                self.insert_last_line()
        except Exception as e:
            show_notification(f"Ошибка при проверке изменения файла: {e}")

    def insert_last_line(self):
        try:
            self.database.insert_to_log_table(self.path_to_log_file, self.procedure_name, self.pattern)
        except Exception as e:
            show_notification(f"Ошибка при добавлении последней строки: {e}")

    def closeEvent(self, event):
        self.timer.stop()
        event.accept()


if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = Window()
    window.show()
    sys.exit(app.exec())
