from PyQt6.QtWidgets import QMessageBox


def show_notification(text):
    msg = QMessageBox()
    msg.setIcon(QMessageBox.Icon.Information)
    msg.setText(text)
    msg.setWindowTitle("Уведомление")
    msg.setStandardButtons(QMessageBox.StandardButton.Ok)
    msg.exec()
