import subprocess


def is_java_installed(parent=None):
    try:
        subprocess.run(
            ["java", "-version"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            check=True,
        )
        return True
    except Exception as ex:
        if parent:
            from ui_helpers import show_dark_message

            show_dark_message(
                parent,
                "Java Not Found",
                "Java is not installed or not in PATH. Lua decompilation will be skipped.",
            )
        return False
