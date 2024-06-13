def apply_table_style(table):
    table.setStyleSheet("""
        QTableView {
            background-color: #b5babd;
            alternate-background-color: #e5d5df;
            selection-background-color: #545756;
            selection-color: #c7a1b8;
            gridline-color: #1e1e1f;
        }

        QHeaderView::section {
            background-color: #9da3a1;
            color: white;
            padding-left: 4px;
            border: 1px solid #878c8b;
        }

        QHeaderView::section:hover {
            background-color: #545756;
        }
    """)

def apply_windows_style(window):
    window.setStyleSheet("""
    QPushButton {
        background-color: #545756;
        color: white;
        border-radius: 3px;
        padding: 5px;
    }
    QPushButton:hover {
        background-color: #787a7a;
    }
    QPushButton:pressed {
        background-color: #4b4d4c;
    }
    QLabel {
            font-size: 12px; 
            font-family: Arial; 
            color: black; 
        }
""")