from PyQt5.QtWidgets import (
    QDialog,
    QVBoxLayout,
    QLabel,
    QPushButton,
    QWidget,
    QHBoxLayout,
    QTableWidgetItem,
    QScrollArea,
)
from PyQt5.QtCore import Qt


def update_file_count_label(self):
    total = self.table.rowCount()
    visible = sum(not self.table.isRowHidden(row) for row in range(total))
    if visible == total:
        self.file_count_label.setText(f"Files: {total}")
    else:
        self.file_count_label.setText(f"Files: {visible} / {total}")


def search_table(self):
    text = self.search_box.text().lower()
    # Store all rows on first search
    if not hasattr(self, "_all_table_data"):
        self._all_table_data = []
        for row in range(self.table.rowCount()):
            row_data = []
            for col in range(self.table.columnCount()):
                item = self.table.item(row, col)
                row_data.append(item.text() if item else "")
            self._all_table_data.append(row_data)
    # If search is empty, restore all rows
    if not text:
        self.table.setRowCount(0)
        for row_data in self._all_table_data:
            row = self.table.rowCount()
            self.table.insertRow(row)
            for col, value in enumerate(row_data):
                self.table.setItem(row, col, QTableWidgetItem(value))
        self.update_file_count_label()
        return
    # Otherwise, filter rows
    filtered = []
    for row_data in self._all_table_data:
        if any(text in value.lower() for value in row_data):
            filtered.append(row_data)
    self.table.setRowCount(0)
    for row_data in filtered:
        row = self.table.rowCount()
        self.table.insertRow(row)
        for col, value in enumerate(row_data):
            self.table.setItem(row, col, QTableWidgetItem(value))
    self.update_file_count_label()


def log_error_to_file(self, error_message, log_path=None):
    import os

    if log_path is None:
        log_path = os.path.join(os.getcwd(), "magictool_errors.txt")
    with open(log_path, "a", encoding="utf-8") as f:
        f.write(error_message + "\n")


class CustomTitleBar(QWidget):
    def __init__(self, parent, title):
        super().__init__(parent)
        self.parent = parent
        self.setFixedHeight(36)
        self.setStyleSheet("""
            background-color: #181818;
            color: #e0e0e0;
            border-top-left-radius: 8px;
            border-top-right-radius: 8px;
        """)
        layout = QHBoxLayout(self)
        layout.setContentsMargins(12, 0, 8, 0)
        self.title = QLabel(title, self)
        self.title.setStyleSheet("font-weight: bold; font-size: 12pt; color: #e0e0e0;")
        layout.addWidget(self.title)
        layout.addStretch()
        self.close_btn = QPushButton("×", self)
        self.close_btn.setFixedSize(28, 28)
        self.close_btn.setStyleSheet(
            "QPushButton { background: #8B0000; color: #fff; border: none; border-radius: 4px; font-size: 16pt; } QPushButton:hover { background: #a83232; }"
        )
        self.close_btn.clicked.connect(self.parent.reject)
        layout.addWidget(self.close_btn)
        self._mouse_pos = None

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self._mouse_pos = event.globalPos() - self.parent.frameGeometry().topLeft()
            event.accept()

    def mouseMoveEvent(self, event):
        if self._mouse_pos and event.buttons() == Qt.LeftButton:
            self.parent.move(event.globalPos() - self._mouse_pos)
            event.accept()

    def mouseReleaseEvent(self, event):
        self._mouse_pos = None


def show_dark_message(self, title, message, icon="info"):
    dlg = QDialog(self)
    dlg.setWindowFlags(Qt.FramelessWindowHint | Qt.Dialog)
    dlg.setStyleSheet("""
        QDialog { background: #181818; color: #e0e0e0; border-radius: 8px; }
        QLabel { color: #e0e0e0; font-size: 10pt; }
        QPushButton { background: #8B0000; color: #fff; border-radius: 4px; padding: 6px 16px; }
        QPushButton:hover { background: #a83232; }
        QScrollArea { background: transparent; border: none; }
    """)
    layout = QVBoxLayout()
    layout.setContentsMargins(0, 0, 0, 0)
    # Custom title bar
    title_bar = CustomTitleBar(dlg, title)
    layout.addWidget(title_bar)
    # Message with scroll area
    scroll = QScrollArea()
    scroll.setWidgetResizable(True)
    label = QLabel(message)
    label.setWordWrap(True)
    label.setStyleSheet("padding: 16px 16px 0 16px;")
    scroll.setWidget(label)
    scroll.setMinimumHeight(80)
    scroll.setMaximumHeight(240)
    layout.addWidget(scroll)
    # OK button
    btn = QPushButton("OK")
    btn.clicked.connect(dlg.accept)
    btn.setStyleSheet("margin: 12px 16px 16px 16px;")
    layout.addWidget(btn)
    dlg.setLayout(layout)
    dlg.setMinimumWidth(360)
    dlg.exec_()


def reset_table_filter(self):
    if hasattr(self, "_all_table_data"):
        self.search_box.setText("")
        self.table.setRowCount(0)
        for row_data in self._all_table_data:
            row = self.table.rowCount()
            self.table.insertRow(row)
            for col, value in enumerate(row_data):
                self.table.setItem(row, col, QTableWidgetItem(value))
        self.update_file_count_label()
