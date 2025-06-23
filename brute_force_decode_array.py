from PyQt5.QtWidgets import QFileDialog


def brute_force_decode_array(self, encoded: bytes, expected: bytes, array_len=1024):
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
