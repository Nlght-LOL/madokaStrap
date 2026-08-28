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
    get_selected_runtime,
    launch_runtime,
)
from .utils import (
    get_system_info,
    press_any_key,
)

def get_bootstrapper_path():
    system_info = get_system_info()

    if system_info["is_linux"]:
        # Aponta para uma estrutura isolada fora do prefixo
        target_dir = (
            Path.home()
            / ".local"
            / "share"
            / "madoka-player"
            / "game_files"
            / "cartiirev"
        )

        target_dir.mkdir(parents=True, exist_ok=True)
        return target_dir, target_dir / BOOTSTRAPPER_FILE
    return none, none

def download_bootstrapper():
    target_dir, target_exe = get_bootstrapper_path()

    if target_dir is None:
        print(
            Fore.RED
            + "[!] Sistema operacional não suportado."
        )
        press_any_key()
        return None

    if target_exe.exists():
        return target_exe

    print(
        Fore.CYAN
        + "[*] cartiiLauncher.exe não encontrado."
    )

    print(
        Fore.CYAN
        + "[*] Baixando bootstrapper..."
    )

    try:
        success = download_file(
            LAUNCHER_URL,
            target_exe,
            BOOTSTRAPPER_FILE,
        )
    except Exception as error:
        print(
            Fore.RED
            + f"[!] Falha no download: {error}"
        )
        return None

    if not success:
        print(
            Fore.RED
            + "[!] Falha ao baixar o bootstrapper."
        )
        return None

    print(
        Fore.GREEN
        + "[*] Bootstrapper baixado com sucesso."
    )

    return target_exe


def launch_bootstrapper():
    system_info = get_system_info()

    target_exe = download_bootstrapper()

    if target_exe is None:
        return

    target_dir = target_exe.parent

    if system_info["is_windows"]:
        print(
            Fore.CYAN
            + f"[*] Executando {BOOTSTRAPPER_FILE}..."
        )

        try:
            subprocess.Popen(
                [
                    str(target_exe),
                ],
                cwd=str(target_dir),
            )

            print(
                Fore.GREEN
                + "[*] Bootstrapper lançado com sucesso!"
            )

        except Exception as error:
            print(
                Fore.RED
                + (
                    "[!] Falha ao iniciar "
                    f"o bootstrapper: {error}"
                )
            )

        press_any_key()
        return

    if not system_info["is_linux"]:
        print(
            Fore.RED
            + "[!] Sistema operacional não suportado."
        )

        press_any_key()
        return

    runtime = get_selected_runtime()

    print()
    print(
        Fore.CYAN
        + f"[*] Runtime selecionado: {runtime}"
    )

    print(
        Fore.CYAN
        + f"[*] WINEPREFIX: {WINEPREFIX_DIR}"
    )

    print(
        Fore.CYAN
        + f"[*] Executável: {target_exe}"
    )

    try:
        process = launch_runtime(
            target_exe,
            cwd=target_dir,
        )

        if process is not None:
            print(
                Fore.GREEN
                + "[*] Bootstrapper lançado com sucesso!"
            )

    except Exception as error:
        print(
            Fore.RED
            + (
                "[!] Falha ao iniciar "
                f"o bootstrapper: {error}"
            )
        )

    press_any_key()