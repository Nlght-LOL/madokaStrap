import os
import shutil
import subprocess

from colorama import Fore

from .config import WINEPREFIX_DIR


def get_wine_cmd():
    for command in (
        "wine",
        "wine64",
    ):
        path = shutil.which(command)
        if path:
            return path

    return None


def get_wine_command():
    return get_wine_cmd()


def get_wine_environment():
    environment = dict(os.environ)

    environment["WINEPREFIX"] = str(WINEPREFIX_DIR)

    return environment


def build_wine_command(executable, args=None):
    wine_cmd = get_wine_cmd()

    if not wine_cmd:
        return None

    command = [
        wine_cmd,
        str(executable),
    ]

    if args:
        command.extend(args)

    return command


def launch_wine(executable, args=None, cwd=None):
    wine_cmd = get_wine_cmd()

    if not wine_cmd:
        raise RuntimeError(
            "Wine is not installed or was not found in PATH."
        )

    WINEPREFIX_DIR.mkdir(
        parents=True,
        exist_ok=True,
    )

    environment = get_wine_environment()

    command = [
        wine_cmd,
        str(executable),
    ]

    if args:
        command.extend(args)

    return subprocess.Popen(
        command,
        env=environment,
        cwd=str(cwd) if cwd else None,
    )


def build_runtime_command(executable, args=None):
    from .runtime import get_selected_runtime

    runtime = get_selected_runtime()

    if runtime == "wine":
        return build_wine_command(
            executable,
            args,
        )

    return None
