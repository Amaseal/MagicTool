from PyQt5.QtWidgets import QFileDialog, QMessageBox


def brute_force_decode_array(self, array_len=1024):
    # Get selected row
    selected_rows = self.table.selectionModel().selectedRows()
    if not selected_rows:
        QMessageBox.information(
            self,
            "No selection",
            "Please select a file in the table to use as ENCODED data.",
        )
        return None
    row = selected_rows[0].row()
    file_name_item = self.table.item(row, 0)
    packed_size_item = self.table.item(row, 2)
    offset_item = self.table.item(row, 3)
    if None in (file_name_item, packed_size_item, offset_item):
        QMessageBox.critical(self, "Error", "Table data missing for selected row.")
        return None
    file_name = file_name_item.text()
    packed_size = int(packed_size_item.text())
    offset = int(offset_item.text())
    file_path = self.label.text().replace("Loaded: ", "").strip()
    # Read encoded data from BM archive
    try:
        with open(file_path, "rb") as f:
            f.seek(offset)
            encoded = f.read(packed_size)
    except Exception as ex:
        QMessageBox.critical(self, "Error", f"Failed to read encoded data: {ex}")
        return None
    # Prompt for expected (decrypted) file
    expected_path, _ = QFileDialog.getOpenFileName(
        self, f"Select known decrypted file for {file_name}"
    )
    if not expected_path:
        return None
    try:
        with open(expected_path, "rb") as f:
            expected = f.read()
    except Exception as ex:
        QMessageBox.critical(self, "Error", f"Failed to read expected file: {ex}")
        return None
    # Brute force
    brute_array = bytearray(array_len)
    for i in range(array_len):
        if i < len(encoded) and i < len(expected):
            brute_array[i] = (encoded[i] - expected[i]) % 256
        else:
            brute_array[i] = 0
    save_path, _ = QFileDialog.getSaveFileName(
        self,
        "Save Brute-forced Decode Array",
        "decode_array.py",
        "Python Files (*.py);;Text Files (*.txt);;All Files (*)",
    )
    if save_path:
        with open(save_path, "w") as f:
            f.write("# Brute-forced decode array\n")
            f.write("BRUTEFORCED_DECODE_ARRAY = [\n    ")
            for i, b in enumerate(brute_array):
                f.write(f"{b}, ")
                if (i + 1) % 16 == 0:
                    f.write("\n    ")
            f.write("\n]\n")
    return brute_array
