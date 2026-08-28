import os
import subprocess
import zipfile
from pathlib import Path

from colorama import Fore

from .config import (
    STUDIO_ARCHIVE,
    STUDIO_URL,
    WINEPREFIX_DIR,
)
from .utils import (
    get_system_info,
    press_any_key,
)
from .wine import (
    get_wine_cmd,
    get_wine_environment,
)
from .downloader import download_file


def launch_studio():
    sys_info = get_system_info()

    script_dir = Path(
        os.path.abspath(
            os.path.join(
                os.path.dirname(__file__),
                "..",
            )
        )
    )

    zip_path = (
        script_dir
        / STUDIO_ARCHIVE
    )

    if sys_info["is_linux"]:
        user = os.getenv(
            "USER",
            "user",
        )

        target_dir = (
            WINEPREFIX_DIR
            / "drive_c"
            / "users"
            / user
            / "AppData"
            / "Local"
            / "MadokaStudio"
        )

        exe_path = (
            target_dir
            / "MadokaStudioBeta.exe"
        )

        if not exe_path.exists():
            if not zip_path.exists():
                print(
                    Fore.CYAN
                    + (
                        "[*] Madoka Studio "
                        "não foi encontrado."
                    )
                )

                if not download_file(
                    STUDIO_URL,
                    zip_path,
                    STUDIO_ARCHIVE,
                ):
                    press_any_key()
                    return

            print(
                Fore.CYAN
                + (
                    f"[*] Extraindo "
                    f"{STUDIO_ARCHIVE}..."
                )
            )

            target_dir.mkdir(
                parents=True,
                exist_ok=True,
            )

            try:
                with zipfile.ZipFile(
                    zip_path,
                    "r",
                ) as zip_ref:
                    zip_ref.extractall(
                        target_dir
                    )

                print(
                    Fore.GREEN
                    + "[*] Extração concluída com sucesso!"
                )

            except Exception as e:
                print(
                    Fore.RED
                    + (
                        "[!] Erro ao extrair "
                        f"o Studio: {e}"
                    )
                )

                press_any_key()
                return

        runtime = get_selected_runtime()

        print(
            Fore.CYAN
            + f"[*] Runtime: {runtime}"
        )
        if not wine_cmd:
            print(
                Fore.RED
                + "[!] Wine não está instalado."
            )

            press_any_key()
            return

        env = get_wine_environment()

        print(
            Fore.CYAN
            + (
                "[*] Executando "
                "MadokaStudioBeta.exe via Wine..."
            )
        )

        try:
            subprocess.Popen(
                [
                    wine_cmd,
                    str(exe_path),
                ],
                env=env,
                cwd=str(target_dir),
            )

            print(
                Fore.GREEN
                + "[*] Madoka Studio lançado!"
            )

        except Exception as e:
            print(
                Fore.RED
                + (
                    "[!] Falha ao iniciar "
                    f"o Studio: {e}"
                )
            )

    elif sys_info["is_windows"]:
        local_app_data = os.getenv(
            "LOCALAPPDATA",
            "",
        )

        target_dir = (
            Path(local_app_data)
            / "MadokaStudio"
        )

        exe_path = (
            target_dir
            / "MadokaStudioBeta.exe"
        )

        if not exe_path.exists():
            if not zip_path.exists():
                print(
                    Fore.CYAN
                    + (
                        "[*] Madoka Studio "
                        "não foi encontrado."
                    )
                )

                if not download_file(
                    STUDIO_URL,
                    zip_path,
                    STUDIO_ARCHIVE,
                ):
                    press_any_key()
                    return

            target_dir.mkdir(
                parents=True,
                exist_ok=True,
            )

            try:
                with zipfile.ZipFile(
                    zip_path,
                    "r",
                ) as zip_ref:
                    zip_ref.extractall(
                        target_dir
                    )

                print(
                    Fore.GREEN
                    + "[*] Extração concluída com sucesso!"
                )

            except Exception as e:
                print(
                    Fore.RED
                    + (
                        "[!] Erro ao extrair "
                        f"o Studio: {e}"
                    )
                )

                press_any_key()
                return

        print(
            Fore.CYAN
            + "[*] Executando MadokaStudioBeta.exe..."
        )

        try:
            subprocess.Popen(
                [
                    str(exe_path)
                ],
                cwd=str(target_dir),
            )

            print(
                Fore.GREEN
                + "[*] Madoka Studio lançado!"
            )

        except Exception as e:
            print(
                Fore.RED
                + (
                    "[!] Falha ao iniciar "
                    f"o Studio: {e}"
                )
            )

    else:
        print(
            Fore.RED
            + "[!] Sistema operacional não suportado."
        )

    press_any_key()