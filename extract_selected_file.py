import os
import zlib
from PyQt5.QtWidgets import QFileDialog, QApplication
from bmencoder import (
    BMEncoder,
    BMGameType,
)
from ui_helpers import show_dark_message
from lua_helpers import is_lua_50_bytecode, decompile_lua_bytecode

from java_check import is_java_installed


def extract_selected_file(self):
    selected_rows = set(idx.row() for idx in self.table.selectionModel().selectedRows())
    if not selected_rows:
        show_dark_message(
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
            for idx, row in enumerate(selected_rows):
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
                # Show extraction progress
                self.status_label.setText(
                    f"Extracting file: {file_name} ({idx + 1}/{len(selected_rows)})"
                )
                QApplication.processEvents()
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
                if file_state in ("Encrypted/Compressed", "Compressed"):
                    try:
                        decompressed = zlib.decompress(data)
                        # Check for double-compressed (zlib header: 0x78)
                        if len(decompressed) > 2 and decompressed[0] == 0x78:
                            try:
                                decompressed2 = zlib.decompress(decompressed)
                                data = decompressed2
                            except Exception:
                                data = decompressed  # If second decompress fails, keep first result
                        else:
                            data = decompressed
                        if len(data) < unpacked_size:
                            pass
                    except Exception as ex:
                        errors.append(
                            f"{file_name}: {str(ex)} (Check game type selection)"
                        )
                        from ui_helpers import log_error_to_file

                        log_error_to_file(
                            self,
                            f"Extract Selected Error (decompress): {file_name}: {ex}",
                        )
                        continue
                # Always write only the first unpacked_size bytes after decoding/decompression
                out_path = os.path.join(out_dir, file_name)
                with open(out_path, "wb") as out_f:
                    out_f.write(data[:unpacked_size])
                # If file is .lua and is Lua 5.0 bytecode, try to decompile
                if file_name.lower().endswith(".lua") and is_lua_50_bytecode(
                    data[:unpacked_size]
                ):
                    self.status_label.setText(f"Decompiling Lua: {file_name}")
                    QApplication.processEvents()
                    if is_java_installed(parent=self):
                        decompiled_path = out_path + ".decompiled.lua"
                        success = decompile_lua_bytecode(
                            out_path, decompiled_path, parent=self
                        )
                        if not success:
                            errors.append(
                                f"{file_name}: Failed to decompile Lua bytecode."
                            )
                    # If Java is not installed, just skip decompilation and do not append error
                extracted += 1
        self.status_label.setText("")
        msg = f"Extracted {extracted} file(s)."
        if errors:
            msg += "\n\nSome files could not be extracted:\n" + "\n".join(errors)
        show_dark_message(self, "Extract Selected", msg)
    except Exception as ex:
        from ui_helpers import log_error_to_file

        log_error_to_file(self, f"Extract Selected Error: {ex}")
