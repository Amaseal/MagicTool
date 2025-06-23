import os
import zlib
from PyQt5.QtWidgets import QFileDialog, QMessageBox
from bmencoder import (
    BMEncoder,
    BMGameType,
)


def extract_selected_file(self):
    selected_rows = set(idx.row() for idx in self.table.selectionModel().selectedRows())
    if not selected_rows:
        QMessageBox.information(
            self, "No selection", "Please select one or more files to extract."
        )
        return
    out_dir = QFileDialog.getExistingDirectory(self, "Select output folder")
    if not out_dir:
        return
    file_path = self.label.text().replace("Loaded: ", "").strip()
    errors = []
    extracted = 0
    try:
        with open(file_path, "rb") as f:
            for row in selected_rows:
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
                f.seek(offset)
                data = bytearray(f.read(packed_size))
                if self.rb_bm.isChecked():
                    game_type = BMGameType.BloodMagic
                elif self.rb_bm_sm.isChecked():
                    game_type = BMGameType.BloodMagicSmokeAndMirrors
                elif self.rb_dom_gold.isChecked():
                    from bmencoder import BMSNM_DECODE_ARRAY, BRUTEFORCED_DECODE_ARRAY

                    temp_data = bytearray(data)
                    for i in range(len(temp_data)):
                        temp_data[i] = (
                            temp_data[i] - BMSNM_DECODE_ARRAY[i & 1023]
                        ) % 256
                    try:
                        decompressed = zlib.decompress(temp_data)
                        out_path = os.path.join(out_dir, file_name)
                        with open(out_path, "wb") as out_f:
                            out_f.write(
                                decompressed[: min(len(decompressed), unpacked_size)]
                            )
                        extracted += 1
                        continue
                    except Exception as ex1:
                        temp_data2 = bytearray(data)
                        for i in range(len(temp_data2)):
                            temp_data2[i] = (
                                temp_data2[i] - BRUTEFORCED_DECODE_ARRAY[i & 1023]
                            ) % 256
                        try:
                            decompressed = zlib.decompress(temp_data2)
                            out_path = os.path.join(out_dir, file_name)
                            with open(out_path, "wb") as out_f:
                                out_f.write(
                                    decompressed[
                                        : min(len(decompressed), unpacked_size)
                                    ]
                                )
                            extracted += 1
                            continue
                        except Exception as ex2:
                            errors.append(
                                f"{file_name}: Failed with both decode arrays. BMSNM: {ex1} | BRUTEFORCED: {ex2}"
                            )
                            continue
                else:
                    game_type = BMGameType.DawnOfMagic
                if file_state in ("Encrypted", "Encrypted/Compressed"):
                    BMEncoder.decode(data, game_type)
                if file_state in ("Encrypted/Compressed", "Compressed"):
                    try:
                        decompressed = zlib.decompress(data)
                        out_path = os.path.join(out_dir, file_name)
                        with open(out_path, "wb") as out_f:
                            out_f.write(
                                decompressed[: min(len(decompressed), unpacked_size)]
                            )
                        extracted += 1
                        continue
                    except Exception as exz:
                        errors.append(f"{file_name}: zlib decompress failed: {exz}")
                        continue
                out_path = os.path.join(out_dir, file_name)
                with open(out_path, "wb") as out_f:
                    out_f.write(data[: min(len(data), unpacked_size)])
                extracted += 1
        msg = f"Extracted {extracted} file(s)."
        if errors:
            msg += "\n\nSome files could not be extracted:\n" + "\n".join(errors)
        QMessageBox.information(self, "Extract Selected", msg)
    except Exception as ex:
        QMessageBox.critical(self, "Extract Selected Error", str(ex))
