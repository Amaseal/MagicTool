import os
import zlib
from PyQt5.QtWidgets import QFileDialog, QMessageBox, QApplication
from bmencoder import (
    BMEncoder,
    BMGameType,
)
from dom_gold_extract_helper import extract_dom_gold_file


def extract_all_files(self):
    out_dir = QFileDialog.getExistingDirectory(
        self, "Select output folder for all files"
    )
    if not out_dir:
        return
    file_path = self.label.text().replace("Loaded: ", "").strip()
    errors = []
    extracted = 0
    try:
        with open(file_path, "rb") as f:
            for row in range(self.table.rowCount()):
                try:
                    file_name_item = self.table.item(row, 0)
                    unpacked_size_item = self.table.item(row, 1)
                    packed_size_item = self.table.item(row, 2)
                    offset_item = self.table.item(row, 3)
                    file_state_item = self.table.item(row, 5)
                    if None in (
                        file_name_item,
                        unpacked_size_item,
                        packed_size_item,
                        offset_item,
                        file_state_item,
                    ):
                        errors.append(f"Row {row + 1}: Table data missing.")
                        continue
                    file_name = file_name_item.text()
                    unpacked_size = int(unpacked_size_item.text())
                    packed_size = int(packed_size_item.text())
                    offset = int(offset_item.text())
                    file_state = file_state_item.text()
                    self.status_label.setText(
                        f"Extracting file: {file_name} ({row + 1}/{self.table.rowCount()})"
                    )
                    QApplication.processEvents()
                    f.seek(offset)
                    data = bytearray(f.read(packed_size))
                    if self.rb_bm.isChecked():
                        game_type = BMGameType.BloodMagic
                    elif self.rb_bm_sm.isChecked():
                        game_type = BMGameType.BloodMagicSmokeAndMirrors
                    elif self.rb_dom_gold.isChecked():
                        # Handle DOM Gold: write plain files directly, use helper for others
                        if file_state == "Plain":
                            out_path = os.path.join(out_dir, file_name)
                            with open(out_path, "wb") as out_f:
                                out_f.write(data)
                            extracted += 1
                        else:
                            success = extract_dom_gold_file(
                                data, file_name, out_dir, unpacked_size, errors
                            )
                            if success:
                                extracted += 1
                        continue
                    else:
                        game_type = BMGameType.DawnOfMagic
                    if file_state in ("Encrypted", "Encrypted/Compressed"):
                        BMEncoder.decode(data, game_type)
                    if file_state in ("Encrypted/Compressed", "Compressed"):
                        try:
                            data = zlib.decompress(data)
                            # Check for double-compressed (zlib header: 0x78)
                            if len(data) > 2 and data[0] == 0x78:
                                try:
                                    data = zlib.decompress(data)
                                except Exception:
                                    pass  # If second decompress fails, keep first result
                            if len(data) < unpacked_size:
                                pass
                        except Exception as ex:
                            errors.append(
                                f"{file_name}: {str(ex)} (Check game type selection)"
                            )
                            continue
                    out_path = os.path.join(out_dir, file_name)
                    with open(out_path, "wb") as out_f:
                        if file_state == "Plain":
                            out_f.write(data)
                        else:
                            out_f.write(data[: min(len(data), unpacked_size)])
                    extracted += 1
                except Exception as ex:
                    errors.append(
                        f"{file_name if 'file_name' in locals() else 'Row ' + str(row + 1)}: {str(ex)}"
                    )
        self.status_label.setText("")
        msg = f"Extracted {extracted} files."
        if errors:
            msg += "\n\nSome files could not be extracted:"
            from PyQt5.QtWidgets import (
                QDialog,
                QVBoxLayout,
                QTextEdit,
                QPushButton,
                QLabel,
            )

            dlg = QDialog(self)
            dlg.setWindowTitle("Extract All - Errors")
            layout = QVBoxLayout()
            text_edit = QTextEdit()
            text_edit.setReadOnly(True)
            text_edit.setPlainText("\n".join(errors))
            layout.addWidget(QLabel(msg))
            layout.addWidget(text_edit)
            btn = QPushButton("OK")
            btn.clicked.connect(dlg.accept)
            layout.addWidget(btn)
            dlg.setLayout(layout)
            dlg.resize(600, 400)
            dlg.exec_()
        else:
            QMessageBox.information(self, "Extract All", msg)
    except Exception as ex:
        QMessageBox.critical(self, "Extract All Error", str(ex))
