import os
import subprocess
from pathlib import Path

from colorama import Fore

from .config import (
    BOOTSTRAPPER_FILE,
    LAUNCHER_URL,
    WINEPREFIX_DIR,
)
from .downloader import download_file
from .runtime import (
    get_runtime_command,
    get_runtime_environment,
    get_selected_runtime,
    validate_runtime,
)
from .utils import (
    get_system_info,
    press_any_key,
)


def get_linux_bootstrapper_path():
    # Salva FORA do WINEPREFIX para evitar erros do Proton/UMU com rotas do Wine
    target_dir = (
        Path.home()
        / ".local"
        / "share"
        / "madoka-player"
        / "game_files"
        / "cartiirev"
    )

    target_dir.mkdir(
        parents=True,
        exist_ok=True,
    )

    return target_dir / BOOTSTRAPPER_FILE


def get_windows_bootstrapper_path():
    local_app_data = os.getenv(
        "LOCALAPPDATA",
        "",
    )

    if not local_app_data:
        local_app_data = os.path.expanduser(
            "~/AppData/Local"
        )

    target_dir = os.path.abspath(local_app_data)
    target_dir = os.path.join(
        target_dir,
        "cartiirev",
    )

    os.makedirs(
        target_dir,
        exist_ok=True,
    )

    return os.path.join(
        target_dir,
        BOOTSTRAPPER_FILE,
    )


def ensure_bootstrapper(target_exe):
    if os.path.exists(target_exe):
        return True

    print(
        Fore.CYAN
        + (
            "[*] cartiiLauncher.exe "
            "not found."
        )
    )

    return download_file(
        LAUNCHER_URL,
        str(target_exe),
        BOOTSTRAPPER_FILE,
    )


def launch_linux(target_exe):
    runtime = get_selected_runtime()

    valid, error = validate_runtime()

    if not valid:
        print(
            Fore.RED
            + f"[!] {error}"
        )
        press_any_key()
        return False

    print(
        Fore.CYAN
        + f"[*] Runtime: {runtime}"
    )

    env = get_runtime_environment()

    command = get_runtime_command(
        target_exe
    )

    if not command:
        print(
            Fore.RED
            + "[!] Failed to build runtime command."
        )
        return False

    target_dir = os.path.dirname(
        target_exe
    )

    print(
        Fore.CYAN
        + f"[*] WINEPREFIX: {WINEPREFIX_DIR}"
    )

    print(
        Fore.CYAN
        + "[*] Command:"
    )

    print(
        Fore.WHITE
        + "    "
        + " ".join(command)
    )

    try:
        subprocess.Popen(
            command,
            env=env,
            cwd=target_dir,
        )

        print(
            Fore.GREEN
            + "[*] Bootstrapper launched successfully!"
        )

        return True

    except Exception as e:
        print(
            Fore.RED
            + (
                "[!] Failed to launch "
                f"bootstrapper: {e}"
            )
        )

        return False


def launch_windows(target_exe):
    target_dir = os.path.dirname(
        target_exe
    )

    print(
        Fore.CYAN
        + (
            f"[*] Executing "
            f"{BOOTSTRAPPER_FILE}..."
        )
    )

    try:
        subprocess.Popen(
            [
                target_exe
            ],
            cwd=target_dir,
        )

        print(
            Fore.GREEN
            + "[*] Bootstrapper launched successfully!"
        )

        return True

    except Exception as e:
        print(
            Fore.RED
            + (
                "[!] Failed to launch "
                f"bootstrapper: {e}"
            )
        )

        return False


def launch_bootstrapper():
    sys_info = get_system_info()

    if sys_info["is_linux"]:
        target_exe = (
            get_linux_bootstrapper_path()
        )

        if not ensure_bootstrapper(
            target_exe
        ):
            press_any_key()
            return

        launch_linux(
            str(target_exe)
        )

    elif sys_info["is_windows"]:
        target_exe = (
            get_windows_bootstrapper_path()
        )

        if not ensure_bootstrapper(
            target_exe
        ):
            press_any_key()
            return

        launch_windows(
            str(target_exe)
        )

    else:
        print(
            Fore.RED
            + "[!] Unsupported operating system."
        )

    press_any_key()