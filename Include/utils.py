import os
import platform
import getpass
from pathlib import Path


def clear():
    os.system(
        "cls"
        if os.name == "nt"
        else "clear"
    )


def press_any_key():
    try:
        input("\nPress Enter to continue...")
    except EOFError:
        pass


def get_user_name():
    try:
        return getpass.getuser()
    except Exception:
        return os.getenv("USER", "steamuser")


def get_system_info():
    system = platform.system().lower()

    return {
        "system": system,
        "is_linux": system == "linux",
        "is_windows": system == "windows",
        "is_macos": system == "darwin",
        "architecture": platform.machine(),
    }


def quote_arg_for_display(value):
    value = str(value)

    if not value:
        return '""'

    special_chars = ['"', "'", "\\", "&", "(", ")", "[", "]", "{", "}", ";", "?", "=", ":"]

    if any(char.isspace() for char in value) or any(char in value for char in special_chars):
        return '"' + value.replace('"', '\\"') + '"'

    return value