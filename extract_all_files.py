import os
import zlib
from PyQt5.QtWidgets import QFileDialog, QApplication
from bmencoder import (
    BMEncoder,
    BMGameType,
)
from lua_helpers import is_lua_50_bytecode, decompile_lua_bytecode
from java_check import is_java_installed


def extract_all_files(self):
    out_dir = QFileDialog.getExistingDirectory(
        self, "Select output folder for all files"
    )
    if not out_dir:
        return
    file_path = self.label.text().replace("Loaded: ", "").strip()
    errors = []
    extracted = 0
    java_warning_shown = False
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
                        game_type = BMGameType.DawnOfMagicGold
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
                        out_f.write(data[:unpacked_size])
                    # Only decompile Lua if checkbox is checked
                    if (
                        self.decompile_lua_checkbox.isChecked()
                        and file_name.lower().endswith(".lua")
                        and is_lua_50_bytecode(data[:unpacked_size])
                    ):
                        self.status_label.setText(f"Decompiling Lua: {file_name}")
                        QApplication.processEvents()
                        if is_java_installed(parent=None):
                            decompiled_path = out_path + ".decompiled.lua"
                            success = decompile_lua_bytecode(
                                out_path, decompiled_path, parent=self
                            )
                            if not success:
                                errors.append(
                                    f"{file_name}: Failed to decompile Lua bytecode."
                                )
                        elif not java_warning_shown:
                            from ui_helpers import show_dark_message

                            show_dark_message(
                                self,
                                "Java Not Found",
                                "Java is not installed or not in PATH. Lua decompilation will be skipped.",
                            )
                            java_warning_shown = True
                    extracted += 1
                except Exception as ex:
                    errors.append(
                        f"{file_name if 'file_name' in locals() else 'Row ' + str(row + 1)}: {str(ex)}"
                    )
        self.status_label.setText("")
        msg = f"Extracted {extracted} files."
        if errors:
            msg += "\n\nSome files could not be extracted:"
            from ui_helpers import show_dark_message

            show_dark_message(self, "Extract All", msg + "\n" + "\n".join(errors))
        else:
            from ui_helpers import show_dark_message

            show_dark_message(self, "Extract All", msg)
    except Exception as ex:
        from ui_helpers import log_error_to_file

        log_error_to_file(self, f"Extract All Error: {ex}")
