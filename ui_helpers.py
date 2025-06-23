def update_file_count_label(self):
    total = self.table.rowCount()
    visible = sum(not self.table.isRowHidden(row) for row in range(total))
    if visible == total:
        self.file_count_label.setText(f"Files: {total}")
    else:
        self.file_count_label.setText(f"Files: {visible} / {total}")


def search_table(self):
    text = self.search_box.text()
    for row in range(self.table.rowCount()):
        match = False
        for col in range(self.table.columnCount()):
            item = self.table.item(row, col)
            if item and text.lower() in item.text().lower():
                match = True
                break
        self.table.setRowHidden(row, not match)
    self.update_file_count_label()
