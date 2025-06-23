import struct
import zlib
from PyQt5.QtWidgets import QFileDialog, QMessageBox
from bmencoder import BMEncoder, BMGameType


def save_bm(self):
    mode = self.combo_mode.currentText()
    if not hasattr(self, "files_to_add") or not self.files_to_add:
        QMessageBox.warning(
            self, "No files", "No files to save. Please add files first."
        )
        return
    out_path, _ = QFileDialog.getSaveFileName(
        self, "Save BM File", "", "BM Files (*.bm)"
    )
    if not out_path:
        return
    if self.rb_bm.isChecked():
        game_type = BMGameType.BloodMagic
    elif self.rb_bm_sm.isChecked():
        game_type = BMGameType.BloodMagicSmokeAndMirrors
    elif self.rb_dom_gold.isChecked():
        game_type = BMGameType.DawnOfMagicGold
    else:
        game_type = BMGameType.DawnOfMagic
    entries = []
    data_blobs = []
    offset = 8 + len(self.files_to_add) * 92
    for file_info in self.files_to_add:
        with open(file_info["path"], "rb") as f:
            raw = f.read()
        packed = raw
        file_state = 0
        if mode == "Encryption":
            packed = bytearray(raw)
            BMEncoder.encode(packed, game_type)
            file_state = 4
        elif mode == "Encryption/Compression":
            packed = bytearray(raw)
            BMEncoder.encode(packed, game_type)
            packed = zlib.compress(packed)
            file_state = 5
        entry = {
            "name": file_info["name"],
            "unpacked_size": len(raw),
            "packed_size": len(packed),
            "offset": offset,
            "file_time": file_info["mtime"],
            "file_state": file_state,
        }
        entries.append(entry)
        data_blobs.append(packed)
        offset += len(packed)
    with open(out_path, "wb") as out_f:
        out_f.write(struct.pack("<Q", len(entries)))
        for entry in entries:
            name_bytes = entry["name"].encode("ascii", errors="replace")[:63]
            name_bytes += b"\x00" * (64 - len(name_bytes))
            out_f.write(name_bytes)
            out_f.write(struct.pack("<I", entry["unpacked_size"]))
            out_f.write(struct.pack("<I", entry["packed_size"]))
            out_f.write(struct.pack("<Q", entry["offset"]))
            out_f.write(struct.pack("<Q", entry["file_time"]))
            out_f.write(struct.pack("<I", entry["file_state"]))
        for blob in data_blobs:
            out_f.write(blob)
    QMessageBox.information(self, "BM Saved", f"BM file saved: {out_path}")
    self.status_label.setText("")
    self.files_to_add = []
