import os
from PyQt5.QtWidgets import QFileDialog, QMessageBox
from bmencoder import BMEncoder, BMGameType


def export_decrypted_file(self):
    selected_rows = set(idx.row() for idx in self.table.selectionModel().selectedRows())
    if not selected_rows:
        QMessageBox.information(
            self, "No selection", "Please select one or more files to export."
        )
        return
    out_dir = QFileDialog.getExistingDirectory(
        self, "Select output folder for decrypted files"
    )
    if not out_dir:
        return
    file_path = self.label.text().replace("Loaded: ", "").strip()
    errors = []
    exported = 0
    try:
        with open(file_path, "rb") as f:
            for row in selected_rows:
                file_name_item = self.table.item(row, 0)
                packed_size_item = self.table.item(row, 2)
                offset_item = self.table.item(row, 3)
                file_state_item = self.table.item(row, 5)
                if None in (
                    file_name_item,
                    packed_size_item,
                    offset_item,
                    file_state_item,
                ):
                    errors.append(f"Row {row + 1}: Table data missing.")
                    continue
                file_name = file_name_item.text()
                packed_size = int(packed_size_item.text())
                offset = int(offset_item.text())
                file_state = file_state_item.text()
                f.seek(offset)
                data = bytearray(f.read(packed_size))
                if self.rb_bm.isChecked():
                    game_type = BMGameType.BloodMagic
                elif self.rb_bm_sm.isChecked():
                    game_type = BMGameType.BloodMagicSmokeAndMirrors
                elif self.rb_dom_gold.isChecked():
                    game_type = BMGameType.DawnOfMagicGold
                else:
                    game_type = BMGameType.DawnOfMagic
                if file_state in ("Encrypted", "Encrypted/Compressed"):
                    BMEncoder.decode(data, game_type)
                out_path = os.path.join(out_dir, file_name)
                with open(out_path, "wb") as out_f:
                    out_f.write(data)
                exported += 1
        msg = f"Exported {exported} decrypted file(s)."
        if errors:
            from ui_helpers import log_error_to_file

            msg += "\n\nSome files could not be exported:\n" + "\n".join(errors)
            log_error_to_file(self, f"Export Decrypted Error: {msg}")
    except Exception as ex:
        from ui_helpers import log_error_to_file

        log_error_to_file(self, f"Export Decrypted Error: {ex}")
