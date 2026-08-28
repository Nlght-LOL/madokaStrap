import json
import os
import shutil
import subprocess
import tarfile
import urllib.request
from pathlib import Path

from colorama import Fore

from .config import WINEPREFIX_DIR
from .runtime import get_selected_runtime
from .wine import get_wine_cmd
from .utils import (
    get_system_info,
    press_any_key,
)


DXVK_API_URL = (
    "https://api.github.com/repos/"
    "doitsujin/dxvk/releases/latest"
)


DXVK_DLLS = [
    "d3d8",
    "d3d9",
    "d3d10core",
    "d3d11",
    "dxgi",
]


def get_latest_dxvk():
    request = urllib.request.Request(
        DXVK_API_URL,
        headers={
            "User-Agent": "MadokaStrap"
        },
    )

    with urllib.request.urlopen(
        request,
        timeout=30,
    ) as response:
        data = json.loads(
            response.read().decode("utf-8")
        )

    version = data.get(
        "tag_name",
        "",
    ).strip().lstrip("v")

    if not version:
        raise RuntimeError(
            "Could not determine latest DXVK version."
        )

    for asset in data.get(
        "assets",
        [],
    ):
        name = asset.get(
            "name",
            "",
        )

        if (
            name.startswith("dxvk-")
            and name.endswith(".tar.gz")
        ):
            url = asset.get(
                "browser_download_url",
                "",
            )

            if not url:
                continue

            return {
                "version": version,
                "name": name,
                "url": url,
            }

    raise RuntimeError(
        "Could not find DXVK release archive."
    )


def get_installed_dxvk_version():
    version_file = (
        WINEPREFIX_DIR
        / ".dxvk-version"
    )

    if not version_file.exists():
        return None

    try:
        return version_file.read_text(
            encoding="utf-8"
        ).strip()
    except Exception:
        return None


def get_wine_environment():
    env = os.environ.copy()

    env["WINEPREFIX"] = str(
        WINEPREFIX_DIR
    )

    return env


def configure_dxvk_overrides(wine_cmd):
    env = get_wine_environment()

    print(
        Fore.CYAN
        + "[*] Configuring DXVK DLL overrides..."
    )

    for dll in DXVK_DLLS:
        try:
            result = subprocess.run(
                [
                    wine_cmd,
                    "reg",
                    "add",
                    r"HKCU\Software\Wine\DllOverrides",
                    "/v",
                    dll,
                    "/t",
                    "REG_SZ",
                    "/d",
                    "native,builtin",
                    "/f",
                ],
                env=env,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                check=False,
            )

            if result.returncode != 0:
                print(
                    Fore.YELLOW
                    + (
                        f"[!] Failed to configure "
                        f"override for {dll}."
                    )
                )

        except Exception as error:
            print(
                Fore.YELLOW
                + (
                    f"[!] Failed to configure "
                    f"{dll}: {error}"
                )
            )


def install_wine_dxvk():
    wine_cmd = get_wine_cmd()

    if not wine_cmd:
        print(
            Fore.RED
            + "[!] Wine is not installed."
        )

        press_any_key()
        return False

    WINEPREFIX_DIR.mkdir(
        parents=True,
        exist_ok=True,
    )

    try:
        release = get_latest_dxvk()

    except Exception as error:
        print(
            Fore.RED
            + (
                "[!] Failed to check latest "
                f"DXVK version: {error}"
            )
        )

        press_any_key()
        return False

    latest_version = release[
        "version"
    ]

    installed_version = (
        get_installed_dxvk_version()
    )

    print(
        Fore.CYAN
        + (
            f"[*] Latest DXVK version: "
            f"{latest_version}"
        )
    )

    if installed_version:
        print(
            Fore.CYAN
            + (
                f"[*] Installed DXVK version: "
                f"{installed_version}"
            )
        )

    if installed_version == latest_version:
        print(
            Fore.GREEN
            + "[*] DXVK is already up to date."
        )

        return True

    archive_path = (
        WINEPREFIX_DIR
        / release["name"]
    )

    extract_root = (
        WINEPREFIX_DIR
        / f"dxvk-{latest_version}"
    )

    try:
        print(
            Fore.CYAN
            + (
                f"[*] Installing DXVK "
                f"{latest_version}..."
            )
        )

        print(
            Fore.YELLOW
            + "[*] Downloading DXVK..."
        )

        urllib.request.urlretrieve(
            release["url"],
            archive_path,
        )

        print(
            Fore.GREEN
            + "[*] DXVK download completed."
        )

        print(
            Fore.CYAN
            + "[*] Extracting DXVK..."
        )

        with tarfile.open(
            archive_path,
            "r:gz",
        ) as archive:
            archive.extractall(
                WINEPREFIX_DIR
            )

        if not extract_root.exists():
            candidates = [
                path
                for path in WINEPREFIX_DIR.iterdir()
                if (
                    path.is_dir()
                    and path.name.startswith(
                        "dxvk-"
                    )
                )
            ]

            if not candidates:
                raise RuntimeError(
                    "DXVK extracted directory was not found."
                )

            candidates.sort(
                key=lambda path: path.stat().st_mtime,
                reverse=True,
            )

            extract_root = candidates[0]

        x64_dir = (
            extract_root
            / "x64"
        )

        x32_dir = (
            extract_root
            / "x32"
        )

        if not x64_dir.is_dir():
            raise RuntimeError(
                "DXVK x64 directory was not found."
            )

        if not x32_dir.is_dir():
            raise RuntimeError(
                "DXVK x32 directory was not found."
            )

        system32 = (
            WINEPREFIX_DIR
            / "drive_c"
            / "windows"
            / "system32"
        )

        syswow64 = (
            WINEPREFIX_DIR
            / "drive_c"
            / "windows"
            / "syswow64"
        )

        system32.mkdir(
            parents=True,
            exist_ok=True,
        )

        syswow64.mkdir(
            parents=True,
            exist_ok=True,
        )

        print(
            Fore.CYAN
            + "[*] Installing DXVK x64 DLLs..."
        )

        for dll in x64_dir.glob(
            "*.dll"
        ):
            shutil.copy2(
                dll,
                system32 / dll.name,
            )

        print(
            Fore.CYAN
            + "[*] Installing DXVK x32 DLLs..."
        )

        for dll in x32_dir.glob(
            "*.dll"
        ):
            shutil.copy2(
                dll,
                syswow64 / dll.name,
            )

        configure_dxvk_overrides(
            wine_cmd
        )

        version_file = (
            WINEPREFIX_DIR
            / ".dxvk-version"
        )

        version_file.write_text(
            latest_version,
            encoding="utf-8",
        )

        print(
            Fore.GREEN
            + (
                f"[*] DXVK {latest_version} "
                "installed successfully!"
            )
        )

        return True

    except Exception as error:
        print(
            Fore.RED
            + (
                "[!] Failed to install DXVK: "
                f"{error}"
            )
        )

        return False

    finally:
        try:
            if archive_path.exists():
                archive_path.unlink()

        except Exception:
            pass

        try:
            if extract_root.exists():
                shutil.rmtree(
                    extract_root
                )

        except Exception:
            pass


def setup_dxvk():
    runtime = get_selected_runtime()

    print(
        Fore.CYAN
        + f"[*] Runtime: {runtime}"
    )

    if runtime == "wine":
        return install_wine_dxvk()

    if runtime == "ge-proton":
        print(
            Fore.GREEN
            + "[*] GE-Proton selected."
        )

        print(
            Fore.CYAN
            + (
                "[*] GE-Proton provides its own "
                "DXVK/Proton graphics stack."
            )
        )

        print(
            Fore.GREEN
            + "[*] Manual DXVK installation skipped."
        )

        return True

    print(
        Fore.RED
        + f"[!] Unsupported runtime: {runtime}"
    )

    return False


def setup_linux_dxvk():
    if not get_system_info()["is_linux"]:
        return

    setup_dxvk()


def setup_linux_integration():
    if not get_system_info()["is_linux"]:
        return

    runtime = get_selected_runtime()

    if runtime == "ge-proton":
        print(
            Fore.CYAN
            + (
                "[*] GE-Proton selected. "
                "DXVK is provided by Proton."
            )
        )

        return

    if runtime == "wine":
        setup_dxvk()
        return

    print(
        Fore.RED
        + f"[!] Unsupported runtime: {runtime}"
    )

    press_any_key()
