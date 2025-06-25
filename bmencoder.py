from decode_arrays import (
    BMDECODE_ARRAY,
    BMSNM_DECODE_ARRAY,
    DOM_DECODE_ARRAY,
    BRUTEFORCED_DECODE_ARRAY,
)


class BMGameType:
    BloodMagic = 0
    BloodMagicSmokeAndMirrors = 1
    DawnOfMagic = 2
    DawnOfMagicGold = 3


class BMEncoder:
    @staticmethod
    def get_decode_array(game_type):
        if game_type == BMGameType.BloodMagic:
            return BMDECODE_ARRAY
        elif game_type == BMGameType.BloodMagicSmokeAndMirrors:
            return BMSNM_DECODE_ARRAY
        elif game_type == BMGameType.DawnOfMagic:
            return DOM_DECODE_ARRAY
        elif game_type == BMGameType.DawnOfMagicGold:
            # Use the same as Blood Magic Smoke and Mirrors
            return BMSNM_DECODE_ARRAY
        else:
            return None

    @staticmethod
    def decode(buffer, game_type):
        if game_type == BMGameType.DawnOfMagicGold:
            BMEncoder.decode_dom_gold(buffer)
        else:
            arr = BMEncoder.get_decode_array(game_type)
            for i in range(len(buffer)):
                buffer[i] = (buffer[i] - arr[i & 1023]) % 256

    @staticmethod
    def decode_dom_gold(buffer):
        # Try BMSNM
        arr_bmsnm = BMSNM_DECODE_ARRAY
        arr_brute = BRUTEFORCED_DECODE_ARRAY
        buf_bmsnm = bytearray(buffer)
        for i in range(len(buf_bmsnm)):
            buf_bmsnm[i] = (buf_bmsnm[i] - arr_bmsnm[i & 1023]) % 256
        if len(buf_bmsnm) > 2 and buf_bmsnm[0] == 0x78:
            buffer[:] = buf_bmsnm
            return
        # Try BRUTEFORCED
        buf_brute = bytearray(buffer)
        for i in range(len(buf_brute)):
            buf_brute[i] = (buf_brute[i] - arr_brute[i & 1023]) % 256
        if len(buf_brute) > 2 and buf_brute[0] == 0x78:
            buffer[:] = buf_brute
            return
        # If neither, prefer BMSNM result
        buffer[:] = buf_bmsnm

    @staticmethod
    def encode(buffer, game_type):
        arr = BMEncoder.get_decode_array(game_type)
        for i in range(len(buffer)):
            buffer[i] = (buffer[i] + arr[i & 1023]) % 256
