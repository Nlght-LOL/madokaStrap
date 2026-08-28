import os
import shutil
import subprocess
import urllib.request

from colorama import Fore

from .config import (
    WINEPREFIX_DIR,
    DATA_DIR,
)
from .runtime import (
    get_selected_runtime,
    get_installed_ge_proton,
    get_umu_command,
)
from .wine import (
    get_wine_cmd,
    get_wine_environment,
)
from .utils import (
    get_system_info,
    press_any_key,
)


WINRAR_URL = (
    "https://www.win-rar.com/"
    "fileadmin/winrar-versions/"
    "winrar/winrar-x64-723.exe"
)


def get_download_directory():
    directory = DATA_DIR / "downloads"

    directory.mkdir(
        parents=True,
        exist_ok=True,
    )

    return directory


def download_winrar():
    download_dir = get_download_directory()

    winrar_exe = (
        download_dir
        / "winrar-x64-723.exe"
    )

    print(
        Fore.CYAN
        + f"[*] Baixando WinRAR de: {WINRAR_URL}"
    )

    print(
        Fore.YELLOW
        + "[*] Por favor, aguarde..."
    )

    try:
        urllib.request.urlretrieve(
            WINRAR_URL,
            winrar_exe,
        )

        if not winrar_exe.exists():
            raise RuntimeError(
                "O arquivo não existe após o download."
            )

        if winrar_exe.stat().st_size == 0:
            raise RuntimeError(
                "O arquivo baixado está vazio."
            )

        print(
            Fore.GREEN
            + "[*] Download concluído com sucesso!"
        )

        print(
            Fore.CYAN
            + f"[*] Instalador: {winrar_exe}"
        )

        return winrar_exe

    except Exception as error:
        print(
            Fore.RED
            + (
                "[!] Falha ao baixar "
                f"o WinRAR: {error}"
            )
        )

        return None


def launch_winrar_with_wine(winrar_exe):
    wine_cmd = get_wine_cmd()

    if not wine_cmd:
        raise RuntimeError(
            "Wine não foi encontrado no PATH."
        )

    environment = get_wine_environment()

    print(
        Fore.CYAN
        + "[*] Iniciando WinRAR com Wine..."
    )

    print(
        Fore.CYAN
        + f"[*] Wine: {wine_cmd}"
    )

    print(
        Fore.CYAN
        + f"[*] WINEPREFIX: {WINEPREFIX_DIR}"
    )

    command = [
        wine_cmd,
        str(winrar_exe),
    ]

    print(
        Fore.WHITE
        + "[*] Executando instalador..."
    )

    return subprocess.run(
        command,
        env=environment,
        cwd=str(winrar_exe.parent),
    )


def launch_winrar_with_ge_proton(winrar_exe):
    umu_command = get_umu_command()

    if not umu_command:
        raise RuntimeError(
            "umu-run não foi encontrado."
        )

    proton = get_installed_ge_proton()

    if proton is None:
        raise RuntimeError(
            "GE-Proton não está instalado."
        )

    environment = dict(os.environ)

    environment["WINEPREFIX"] = str(
        WINEPREFIX_DIR
    )

    environment["PROTONPATH"] = str(
        proton
    )

    environment["UMU_NO_RUNTIME_UPDATE"] = "0"

    architecture = "x86_64"

    print(
        Fore.CYAN
        + "[*] Iniciando WinRAR com GE-Proton/umu..."
    )

    print(
        Fore.CYAN
        + f"[*] Runtime: {proton.name}"
    )

    print(
        Fore.CYAN
        + f"[*] Architecture: {architecture}"
    )

    print(
        Fore.CYAN
        + f"[*] umu-run: {umu_command}"
    )

    print(
        Fore.CYAN
        + f"[*] PROTONPATH: {proton}"
    )

    print(
        Fore.CYAN
        + f"[*] WINEPREFIX: {WINEPREFIX_DIR}"
    )

    print(
        Fore.CYAN
        + f"[*] Executável: {winrar_exe}"
    )

    if not winrar_exe.exists():
        raise RuntimeError(
            "O instalador desapareceu antes de ser executado."
        )

    command = [
        umu_command,
        str(winrar_exe),
    ]

    print(
        Fore.WHITE
        + "[*] Executando umu-run..."
    )

    return subprocess.run(
        command,
        env=environment,
        cwd=str(winrar_exe.parent),
    )


def install_winrar():
    sys_info = get_system_info()

    if not sys_info["is_linux"]:
        print(
            Fore.RED
            + (
                "[!] A instalação do WinRAR via runtime "
                "é suportada apenas no Linux."
            )
        )

        press_any_key()
        return

    runtime = get_selected_runtime()

    print(
        Fore.CYAN
        + f"[*] Runtime: {runtime}"
    )

    if runtime == "ge-proton":
        print(
            Fore.CYAN
            + (
                "[*] O instalador será executado "
                "usando GE-Proton/umu."
            )
        )
    else:
        print(
            Fore.CYAN
            + "[*] O instalador será executado usando Wine."
        )

    print(
        Fore.CYAN
        + (
            "[*] Verificando e criando diretório "
            "do WINEPREFIX..."
        )
    )

    WINEPREFIX_DIR.mkdir(
        parents=True,
        exist_ok=True,
    )

    winrar_exe = download_winrar()

    if winrar_exe is None:
        press_any_key()
        return

    print(
        Fore.CYAN
        + "[*] Iniciando o instalador do WinRAR..."
    )

    print(
        Fore.YELLOW
        + (
            "[!] Faça a instalação normalmente "
            "pela janela do runtime."
        )
    )

    try:
        if runtime == "ge-proton":
            result = launch_winrar_with_ge_proton(
                winrar_exe
            )
        elif runtime == "wine":
            result = launch_winrar_with_wine(
                winrar_exe
            )
        else:
            raise RuntimeError(
                f"Runtime desconhecido: {runtime}"
            )

        print()

        if result.returncode == 0:
            print(
                Fore.GREEN
                + (
                    "[*] Instalador do WinRAR "
                    "finalizado com sucesso!"
                )
            )
        else:
            print(
                Fore.YELLOW
                + (
                    "[!] O instalador do WinRAR "
                    f"terminou com código {result.returncode}."
                )
            )

    except Exception as error:
        print(
            Fore.RED
            + (
                "[!] Falha ao executar "
                f"o instalador: {error}"
            )
        )

    if winrar_exe.exists():
        try:
            winrar_exe.unlink()

            print(
                Fore.CYAN
                + (
                    "[*] Instalador removido "
                    "para liberar espaço."
                )
            )

        except Exception as error:
            print(
                Fore.YELLOW
                + (
                    "[!] Não foi possível remover "
                    f"o instalador: {error}"
                )
            )

    press_any_key()
