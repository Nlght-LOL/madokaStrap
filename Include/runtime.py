import json
import os
import shutil
import subprocess
import tarfile
import tempfile
import urllib.request
from pathlib import Path

from colorama import Fore

from .config import (
    GE_PROTON_API,
    GE_PROTON_DIR,
    RUNTIME_FILE,
    SUPPORTED_RUNTIMES,
    WINEPREFIX_DIR,
)
from .utils import press_any_key


def load_runtime_config():
    if not RUNTIME_FILE.exists():
        return {"runtime": "wine"}

    try:
        with open(RUNTIME_FILE, "r", encoding="utf-8") as file:
            data = json.load(file)

        if not isinstance(data, dict):
            return {"runtime": "wine"}

        runtime = data.get("runtime", "wine")

        if runtime not in SUPPORTED_RUNTIMES:
            runtime = "wine"

        return {"runtime": runtime}

    except Exception:
        return {"runtime": "wine"}


def save_runtime_config(runtime):
    if runtime not in SUPPORTED_RUNTIMES:
        return False

    try:
        RUNTIME_FILE.parent.mkdir(
            parents=True,
            exist_ok=True,
        )

        with open(
            RUNTIME_FILE,
            "w",
            encoding="utf-8",
        ) as file:
            json.dump(
                {"runtime": runtime},
                file,
                indent=2,
            )

        return True

    except Exception as error:
        print(
            Fore.RED
            + f"[!] Failed to save runtime configuration: {error}"
        )
        return False


def get_selected_runtime():
    return load_runtime_config().get(
        "runtime",
        "wine",
    )


def get_umu_command():
    commands = (
        "umu-run",
        "umu",
    )

    for command in commands:
        path = shutil.which(command)

        if path:
            return path

    possible_paths = [
        Path.home() / ".local" / "bin" / "umu-run",
        Path.home() / ".local" / "bin" / "umu",
        Path("/usr/bin/umu-run"),
        Path("/usr/bin/umu"),
        Path("/usr/local/bin/umu-run"),
        Path("/usr/local/bin/umu"),
    ]

    for path in possible_paths:
        if path.is_file() and os.access(path, os.X_OK):
            return str(path)

    return None


def get_wine_command():
    for command in (
        "wine",
        "wine64",
    ):
        path = shutil.which(command)

        if path:
            return path

    return None


def get_wine_cmd():
    return get_wine_command()


def normalize_arguments(args):
    if args is None:
        return []

    if isinstance(args, (str, Path)):
        return [str(args)]

    if not isinstance(args, (list, tuple)):
        raise TypeError(
            "Runtime arguments must be a list, tuple, string or Path."
        )

    return [str(argument) for argument in args]


def is_valid_ge_proton(path):
    path = Path(path)

    if not path.is_dir():
        return False

    proton = path / "proton"

    if not proton.is_file():
        return False

    files_dir = path / "files"

    if not files_dir.is_dir():
        return False

    wine_files = list(path.glob("files/bin/wine*"))

    if not wine_files:
        return False

    return True


def get_installed_ge_proton():
    if not GE_PROTON_DIR.exists():
        return None

    versions = []

    try:
        entries = GE_PROTON_DIR.iterdir()
    except OSError:
        return None

    for path in entries:
        if not path.is_dir():
            continue

        if not is_valid_ge_proton(path):
            continue

        versions.append(path)

    if not versions:
        return None

    versions.sort(
        key=lambda path: path.stat().st_mtime,
        reverse=True,
    )

    return versions[0]


def is_ge_proton_installed():
    return get_installed_ge_proton() is not None


def get_latest_ge_proton():
    request = urllib.request.Request(
        GE_PROTON_API,
        headers={
            "User-Agent": "madokaStrap",
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
    ).strip()

    if not version:
        raise RuntimeError(
            "Could not determine latest GE-Proton version."
        )

    for asset in data.get("assets", []):
        name = asset.get(
            "name",
            "",
        )

        if (
            name.startswith("GE-Proton")
            and name.endswith(".tar.gz")
            and "arm64" not in name.lower()
            and "aarch64" not in name.lower()
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
        "A compatible x86_64 GE-Proton release archive was not found."
    )


def install_ge_proton():
    print(
        Fore.CYAN
        + "[*] Checking GE-Proton..."
    )

    try:
        release = get_latest_ge_proton()

    except Exception as error:
        print(
            Fore.RED
            + (
                "[!] Failed to get GE-Proton information: "
                f"{error}"
            )
        )

        press_any_key()
        return False

    version = release["version"]
    url = release["url"]

    GE_PROTON_DIR.mkdir(
        parents=True,
        exist_ok=True,
    )

    target_dir = GE_PROTON_DIR / version

    if (
        target_dir.exists()
        and is_valid_ge_proton(target_dir)
    ):
        print(
            Fore.GREEN
            + (
                f"[*] GE-Proton {version} "
                "is already installed."
            )
        )

        save_runtime_config("ge-proton")

        print(
            Fore.GREEN
            + "[*] GE-Proton selected as active runtime."
        )

        return True

    archive_path = (
        Path(tempfile.gettempdir())
        / release["name"]
    )

    temp_extract = None

    print(
        Fore.CYAN
        + f"[*] Installing GE-Proton {version}..."
    )

    try:
        print(
            Fore.YELLOW
            + "[*] Downloading GE-Proton..."
        )

        urllib.request.urlretrieve(
            url,
            archive_path,
        )

        print(
            Fore.GREEN
            + "[*] GE-Proton download completed."
        )

        temp_extract = Path(
            tempfile.mkdtemp(
                prefix="madokastrap-ge-proton-"
            )
        )

        print(
            Fore.CYAN
            + "[*] Extracting GE-Proton..."
        )

        with tarfile.open(
            archive_path,
            "r:gz",
        ) as archive:
            archive.extractall(
                temp_extract
            )

        extracted_dirs = [
            path
            for path in temp_extract.iterdir()
            if path.is_dir()
        ]

        if not extracted_dirs:
            raise RuntimeError(
                "GE-Proton archive did not contain a directory."
            )

        extracted_root = extracted_dirs[0]

        if target_dir.exists():
            shutil.rmtree(target_dir)

        shutil.move(
            str(extracted_root),
            str(target_dir),
        )

        if not is_valid_ge_proton(target_dir):
            raise RuntimeError(
                "Downloaded GE-Proton is invalid or incomplete."
            )

        print(
            Fore.GREEN
            + (
                f"[*] GE-Proton {version} "
                "installed successfully!"
            )
        )

        save_runtime_config("ge-proton")

        print(
            Fore.GREEN
            + "[*] GE-Proton selected as active runtime."
        )

        return True

    except Exception as error:
        print(
            Fore.RED
            + (
                "[!] Failed to install GE-Proton: "
                f"{error}"
            )
        )

        if (
            target_dir.exists()
            and not is_valid_ge_proton(target_dir)
        ):
            try:
                shutil.rmtree(target_dir)
            except Exception:
                pass

        return False

    finally:
        try:
            if archive_path.exists():
                archive_path.unlink()
        except Exception:
            pass

        if temp_extract is not None:
            shutil.rmtree(
                temp_extract,
                ignore_errors=True,
            )


def get_runtime_environment():
    runtime = get_selected_runtime()

    if runtime == "wine":
        try:
            from .wine import get_wine_environment

            return get_wine_environment()

        except ImportError:
            environment = dict(os.environ)

            environment["WINEPREFIX"] = str(
                Path(WINEPREFIX_DIR).resolve()
            )

            return environment

    environment = dict(os.environ)

    wineprefix = Path(
        WINEPREFIX_DIR
    ).resolve()

    wineprefix.mkdir(
        parents=True,
        exist_ok=True,
    )

    environment["WINEPREFIX"] = str(
        wineprefix
    )

    proton = get_installed_ge_proton()

    if proton is not None:
        environment["PROTONPATH"] = str(
            Path(proton).resolve()
        )
    else:
        environment.pop(
            "PROTONPATH",
            None,
        )

    environment["UMU_NO_RUNTIME_UPDATE"] = "0"
    environment["GAMEID"] = "madoka-player"
    environment["STORE"] = "none"

    return environment


def prepare_executable_for_proton(executable):
    executable = Path(executable).resolve()
    wineprefix = Path(WINEPREFIX_DIR).resolve()

    if not executable.exists():
        raise RuntimeError(
            f"Executable does not exist: {executable}"
        )

    try:
        executable.relative_to(wineprefix)
        return executable

    except ValueError:
        pass

    destination_root = (
        wineprefix
        / "drive_c"
        / "madoka_game"
    )

    destination_root.mkdir(
        parents=True,
        exist_ok=True,
    )

    source_dir = executable.parent

    destination_dir = (
        destination_root
        / source_dir.name
    )

    if source_dir.resolve() == destination_dir.resolve():
        destination_executable = (
            destination_dir
            / executable.name
        )

        if destination_executable.exists():
            return destination_executable

    if not destination_dir.exists():
        shutil.copytree(
            source_dir,
            destination_dir,
            dirs_exist_ok=True,
        )
    else:
        for source in source_dir.iterdir():
            destination = destination_dir / source.name

            try:
                if source.is_dir():
                    shutil.copytree(
                        source,
                        destination,
                        dirs_exist_ok=True,
                    )
                else:
                    shutil.copy2(
                        source,
                        destination,
                    )
            except Exception:
                pass

    destination_executable = (
        destination_dir
        / executable.name
    )

    if not destination_executable.exists():
        raise RuntimeError(
            "Failed to prepare executable inside Wine prefix."
        )

    return destination_executable


def unix_path_to_wine_path(path):
    path = Path(path).resolve()
    wineprefix = Path(WINEPREFIX_DIR).resolve()

    try:
        relative = path.relative_to(wineprefix)

    except ValueError:
        return str(path)

    parts = relative.parts

    if not parts:
        return "Z:\\"

    if parts[0].lower() == "drive_c":
        windows_parts = parts[1:]

        if not windows_parts:
            return "C:\\"

        return (
            "C:\\"
            + "\\".join(windows_parts)
        )

    return (
        "Z:\\"
        + "\\".join(parts)
    )


def build_proton_command(
    executable,
    args=None,
):
    umu_command = get_umu_command()

    if not umu_command:
        return None

    proton = get_installed_ge_proton()

    if proton is None:
        return None

    executable = Path(
        executable
    ).resolve()

    normalized_args = normalize_arguments(args)

    executable_for_proton = prepare_executable_for_proton(
        executable
    )

    return [
        str(umu_command),
        str(executable_for_proton),
        *normalized_args,
    ]

def launch_with_ge_proton(
    executable,
    args=None,
    cwd=None,
):
    umu_command = get_umu_command()

    if not umu_command:
        raise RuntimeError("umu-launcher was not found.")

    proton = get_installed_ge_proton()

    if proton is None:
        raise RuntimeError("GE-Proton is not installed.")

    executable_path = Path(executable).resolve()

    if not executable_path.is_file():
        raise RuntimeError(
            f"Client executable was not found:\n{executable_path}"
        )

    wineprefix_path = Path(WINEPREFIX_DIR).resolve()

    wineprefix_path.mkdir(
        parents=True,
        exist_ok=True,
    )

    normalized_args = normalize_arguments(args)

    if cwd is None:
        cwd_path = executable_path.parent
    else:
        cwd_path = Path(cwd)

        if not cwd_path.exists():
            cwd_path = executable_path.parent

        cwd_path = cwd_path.resolve()

    try:
        relative_path = executable_path.relative_to(
            wineprefix_path
        )

        parts = relative_path.parts

        if (
            len(parts) > 0
            and parts[0].lower() == "drive_c"
        ):
            windows_executable = (
                "C:\\"
                + "\\".join(parts[1:])
            )
        else:
            windows_executable = (
                "Z:\\"
                + "\\".join(parts)
            )

    except ValueError:
        windows_executable = str(executable_path)

    environment = dict(os.environ)

    environment["PROTON_USE_WINED3D"] = "1"
    environment["LIBGL_DRIVERS_PATH"] = "/usr/lib/x86_64-linux-gnu/dri"
    environment["WINEPREFIX"] = str(wineprefix_path)
    environment["PROTONPATH"] = str(Path(proton).resolve())
    environment["GAMEID"] = "madoka-player"
    environment["STORE"] = "none"
    environment["UMU_LOG"] = "1"

    command = [
        str(umu_command),
        windows_executable,
        *normalized_args,
    ]

    print()
    print(
        Fore.CYAN
        + "========================================"
    )
    print(
        Fore.CYAN
        + "        Launching Client"
    )
    print(
        Fore.CYAN
        + "========================================"
    )
    print()

    print(
        Fore.CYAN
        + f"[*] Executable: {executable_path}"
    )

    print(
        Fore.CYAN
        + f"[*] WINEPREFIX: {wineprefix_path}"
    )

    print(
        Fore.CYAN
        + f"[*] PROTONPATH: {proton}"
    )

    print(
        Fore.CYAN
        + f"[*] umu-run: {umu_command}"
    )

    print(
        Fore.CYAN
        + "[*] PROTON_USE_WINED3D=1"
    )

    print(
        Fore.CYAN
        + "[*] LIBGL_DRIVERS_PATH=/usr/lib/x86_64-linux-gnu/dri"
    )

    print()

    print(
        Fore.CYAN
        + "[*] Arguments:"
    )

    print(
        Fore.WHITE
        + " ".join(
            subprocess.list2cmdline([arg])
            for arg in normalized_args
        )
    )

    print()

    print(
        Fore.YELLOW
        + "[*] Starting Client..."
    )

    print()

    process = subprocess.Popen(
        command,
        env=environment,
        cwd=str(cwd_path),
        stdin=subprocess.DEVNULL,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
        start_new_session=True,
    )

    print(
        Fore.GREEN
        + f"[+] Process started with PID {process.pid}"
    )

    print()

    try:
        return_code = process.wait()

        print()

        if return_code == 0:
            print(
                Fore.GREEN
                + "[+] Client exited normally."
            )
        else:
            print(
                Fore.RED
                + (
                    "[!] Client exited "
                    f"with code {return_code}."
                )
            )

    except KeyboardInterrupt:
        print()

        print(
            Fore.YELLOW
            + "[*] Stopped waiting."
        )

    return process

def launch_runtime(
    executable,
    args=None,
    cwd=None,
):
    runtime = get_selected_runtime()

    WINEPREFIX_DIR.mkdir(
        parents=True,
        exist_ok=True,
    )

    executable = Path(
        executable
    ).resolve()

    normalized_args = normalize_arguments(
        args
    )

    if runtime == "wine":
        from .wine import launch_wine

        print(
            Fore.CYAN
            + "[*] Starting with Wine..."
        )

        return launch_wine(
            executable,
            args=normalized_args,
            cwd=cwd,
        )

    if runtime == "ge-proton":
        print(
            Fore.CYAN
            + "[*] Starting with GE-Proton through umu-launcher..."
        )

        return launch_with_ge_proton(
            executable,
            args=normalized_args,
            cwd=cwd,
        )

    raise RuntimeError(
        f"Unsupported runtime: {runtime}"
    )


def get_runtime_command(
    executable,
    args=None,
):
    runtime = get_selected_runtime()

    executable = Path(
        executable
    ).resolve()

    normalized_args = normalize_arguments(
        args
    )

    if runtime == "wine":
        from .wine import build_wine_command

        return build_wine_command(
            executable,
            normalized_args,
        )

    if runtime == "ge-proton":
        return build_proton_command(
            executable,
            normalized_args,
        )

    return None


def validate_runtime():
    runtime = get_selected_runtime()

    if runtime == "wine":
        wine = get_wine_command()

        if not wine:
            return (
                False,
                "Wine is not installed or was not found in PATH.",
            )

        return True, ""

    if runtime == "ge-proton":
        umu = get_umu_command()

        if not umu:
            return (
                False,
                "umu-launcher was not found. "
                "Make sure umu-run is available in PATH.",
            )

        proton = get_installed_ge_proton()

        if proton is None:
            return (
                False,
                "GE-Proton is not installed. "
                "Install GE-Proton from the Runtime menu first.",
            )

        return True, ""

    return (
        False,
        f"Unsupported runtime: {runtime}",
    )


def deactivate_runtime():
    current = get_selected_runtime()

    print(
        Fore.YELLOW
        + f"[*] Current runtime: {current}"
    )

    save_runtime_config(
        "wine"
    )

    print(
        Fore.GREEN
        + "[*] Runtime switched back to Wine."
    )


def remove_ge_proton():
    if not GE_PROTON_DIR.exists():
        print(
            Fore.YELLOW
            + "[*] GE-Proton is not installed."
        )

        press_any_key()
        return

    confirm = input(
        Fore.RED
        + (
            "\nRemove all installed GE-Proton "
            "versions? (y/N): "
        )
    ).strip().lower()

    if confirm != "y":
        print(
            Fore.YELLOW
            + "[*] Cancelled."
        )

        press_any_key()
        return

    try:
        shutil.rmtree(
            GE_PROTON_DIR
        )

        save_runtime_config(
            "wine"
        )

        print(
            Fore.GREEN
            + "[*] GE-Proton removed."
        )

    except Exception as error:
        print(
            Fore.RED
            + f"[!] Failed to remove GE-Proton: {error}"
        )

    press_any_key()


def choose_runtime():
    current = get_selected_runtime()

    while True:
        print()

        print(
            Fore.YELLOW
            + "Runtime Selection"
        )

        print(
            Fore.CYAN
            + f"Current runtime: {current}"
        )

        print()

        print("1. Wine")
        print("2. GE-Proton")
        print("3. Disable / switch back to Wine")
        print("4. Remove GE-Proton")
        print("0. Back")

        choice = input(
            Fore.WHITE
            + "\nEnter your choice: "
        ).strip()

        if choice == "1":
            if save_runtime_config("wine"):
                print(
                    Fore.GREEN
                    + "[*] Wine selected."
                )

            press_any_key()
            return

        if choice == "2":
            if install_ge_proton():
                press_any_key()

            return

        if choice == "3":
            deactivate_runtime()
            press_any_key()
            return

        if choice == "4":
            remove_ge_proton()
            return

        if choice == "0":
            return

        print(
            Fore.RED
            + "[!] Invalid choice."
        )

        current = get_selected_runtime()
