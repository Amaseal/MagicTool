import os
import zlib
from bmencoder import BMSNM_DECODE_ARRAY, BRUTEFORCED_DECODE_ARRAY


def extract_dom_gold_file(data, file_name, out_dir, unpacked_size, errors=None):
    """
    Attempt to extract a DOM Gold file using both decode arrays.
    Returns True if extraction succeeded, False otherwise.
    If errors is provided, appends error messages to it.
    """
    # Try BMSNM_DECODE_ARRAY
    temp_data = bytearray(data)
    for i in range(len(temp_data)):
        temp_data[i] = (temp_data[i] - BMSNM_DECODE_ARRAY[i & 1023]) % 256
    try:
        decompressed = zlib.decompress(temp_data)
        out_path = os.path.join(out_dir, file_name)
        with open(out_path, "wb") as out_f:
            out_f.write(decompressed[: min(len(decompressed), unpacked_size)])
        return True
    except Exception as ex1:
        # Try BRUTEFORCED_DECODE_ARRAY
        temp_data2 = bytearray(data)
        for i in range(len(temp_data2)):
            temp_data2[i] = (temp_data2[i] - BRUTEFORCED_DECODE_ARRAY[i & 1023]) % 256
        try:
            decompressed = zlib.decompress(temp_data2)
            out_path = os.path.join(out_dir, file_name)
            with open(out_path, "wb") as out_f:
                out_f.write(decompressed[: min(len(decompressed), unpacked_size)])
            return True
        except Exception as ex2:
            if errors is not None:
                errors.append(
                    f"{file_name}: Failed with both decode arrays. BMSNM: {ex1} | BRUTEFORCED: {ex2}"
                )
            return False
