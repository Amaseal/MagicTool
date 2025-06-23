import os
import datetime
from PyQt5.QtWidgets import QFileDialog
from PyQt5.QtWidgets import QTableWidgetItem


def add_files(self):
    files, _ = QFileDialog.getOpenFileNames(self, "Select files to add to BM archive")
    if not files:
        return
    self.files_to_add = getattr(self, "files_to_add", [])
    for file_path in files:
        stat = os.stat(file_path)
        mtime = int(
            (
                datetime.datetime.fromtimestamp(stat.st_mtime, datetime.timezone.utc)
                - datetime.datetime(1601, 1, 1, tzinfo=datetime.timezone.utc)
            ).total_seconds()
            * 10**7
        )
        file_info = {
            "path": file_path,
            "name": os.path.basename(file_path),
            "size": stat.st_size,
            "mtime": mtime,
        }
        self.files_to_add.append(file_info)
    self.table.setRowCount(0)
    for file_info in self.files_to_add:
        row = self.table.rowCount()
        self.table.insertRow(row)
        self.table.setItem(row, 0, QTableWidgetItem(file_info["name"]))
        self.table.setItem(row, 1, QTableWidgetItem(str(file_info["size"])))
        self.table.setItem(row, 2, QTableWidgetItem(str(file_info["size"])))
        self.table.setItem(row, 3, QTableWidgetItem("0"))
        self.table.setItem(row, 4, QTableWidgetItem("(new)"))
        self.table.setItem(row, 5, QTableWidgetItem("To be saved"))
    self.status_label.setText(f"{len(self.files_to_add)} files ready to save.")
    self.update_file_count_label()
