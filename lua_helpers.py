import subprocess
import sys
import os


def is_lua_50_bytecode(data):
    """Check if the given data is Lua 5.0 bytecode."""
    return data[:5] == b"\x1bLua\x50"


def get_unluac_jar_path():
    """Return the correct path to unluac.jar, whether running bundled or not."""
    if hasattr(sys, "_MEIPASS"):
        return os.path.join(sys._MEIPASS, "unluac.jar")
    else:
        return "unluac.jar"


def decompile_lua_bytecode(
    bytecode_path,
    output_path,
    unluac_jar_path=None,
    parent=None,
    log_error_to_file=None,
):
    """
    Decompile Lua 5.0 bytecode file using unluac.jar.
    Requires Java and unluac.jar in the specified path.
    """
    if unluac_jar_path is None:
        unluac_jar_path = get_unluac_jar_path()
    cmd = ["java", "-jar", unluac_jar_path, bytecode_path]
    try:
        with open(output_path, "w", encoding="utf-8") as out_f:
            subprocess.run(cmd, stdout=out_f, stderr=subprocess.PIPE, check=True)
        return True
    except subprocess.CalledProcessError as ex:
        error_msg = ex.stderr.decode(errors="replace")
        if log_error_to_file:
            log_error_to_file(parent, f"Lua decompilation failed: {error_msg}")
        from ui_helpers import show_dark_message

        show_dark_message(parent, "Lua Decompilation Error", error_msg)
        return False
    except Exception as ex:
        error_msg = str(ex)
        if log_error_to_file:
            log_error_to_file(parent, f"Lua decompilation error: {error_msg}")
        from ui_helpers import show_dark_message

        show_dark_message(parent, "Lua Decompilation Error", error_msg)
        return False
