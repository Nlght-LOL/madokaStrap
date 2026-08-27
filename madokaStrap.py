import os
import subprocess
import sys
import json
import platform
import urllib.request
import urllib.error
import urllib.parse
import shutil
import tarfile
import zipfile
import tempfile
from pathlib import Path

from colorama import Fore, Style, init


init(autoreset=True)


VERSION = "2.2.0"

FASTFLAGS_FILE = "fastFlags.json"
BOOTSTRAPPER_FILE = "cartiiLauncher.exe"

LAUNCHER_URL = (
    "https://cdn.madxka.com/clients/cartiiLauncher.exe"
)

STUDIO_URL = (
    "https://cdn.discordapp.com/attachments/"
    "1522635545631523069/"
    "1525514631454523422/"
    "MadokaStudio2021.zip"
    "?ex=6a91a036"
    "&is=6a904eb6"
    "&hm=b93669316f6a83b3e842a7a3a27b04071e45e119a256eda339ddaeabd8bfc610"
)

STUDIO_ARCHIVE = "MadokaStudio2021.zip"


HOME_DIR = (
    Path.home()
    / ".local"
    / "share"
    / "madoka-player"
)

WINEPREFIX_DIR = (
    Path.home()
    / ".local"
    / "share"
    / "wineprefixes"
    / "madoka"
)

ICONS_FOLDER = (
    Path.home()
    / ".local"
    / "share"
    / "icons"
    / "hicolor"
)

DESKTOP_APPS = (
    Path.home()
    / ".local"
    / "share"
    / "applications"
)

ENTRY_FILE = (
    DESKTOP_APPS
    / "cartii-launcher.desktop"
)

UNINSTALL_ENTRY_FILE = (
    DESKTOP_APPS
    / "uninstall-cartii-launcher.desktop"
)


URI_KEY_ARG_MAP = {
    "launchmode": "--",
    "gameinfo": "-t",
    "ticket": "-t",
    "placelauncherurl": "-j",
    "launchtime": "--launchtime=",
    "task": "-task",
    "place": "-placeId",
    "placeId": "-placeId",
    "universeId": "-universeId",
    "userId": "-userId",
}


def press_any_key(prompt="Press any key to continue..."):
    if os.name == "nt":
        import msvcrt

        print(
            Fore.MAGENTA + prompt,
            end="",
            flush=True,
        )

        msvcrt.getch()
        print()

    else:
        input(
            Fore.MAGENTA + prompt
        )


def clear():
    os.system(
        "cls"
        if os.name == "nt"
        else "clear"
    )


def get_system_info():
    system = platform.system().lower()

    return {
        "is_windows": system == "windows",
        "is_linux": system == "linux",
        "is_macos": system == "darwin",
        "system_name": system,
    }


def quote_arg_for_display(value):
    value = str(value)

    if any(
        c in value
        for c in [" ", "&", "?", "="]
    ):
        return (
            '"'
            + value.replace('"', '\\"')
            + '"'
        )

    return value


def first_query_value(
    query_params,
    key,
    default="",
):
    values = query_params.get(key)

    if not values:
        return default

    return values[0]


def detect_year(query_params):
    value = first_query_value(
        query_params,
        "year",
        "2020",
    )

    value = str(value)

    if "2018" in value:
        return "2018"

    if "2021" in value:
        return "2021"

    if "2017" in value:
        return "2017"

    return "2020"


def build_place_launcher_url(
    place_id,
    ticket,
    year,
):
    if not place_id or not ticket:
        return ""

    query = urllib.parse.urlencode(
        {
            "placeid": place_id,
            "ticket": ticket,
            year: "true",
        }
    )

    return (
        "http://madxka.com/game/PlaceLauncher.ashx?"
        + query
    )


def parse_uri(uri):
    if not isinstance(uri, str):
        raise ValueError(
            "URI inválida: valor não é string"
        )

    uri = uri.strip()

    if uri.startswith(
        "madoka-player://"
    ):
        uri = (
            "cc://"
            + uri[len("madoka-player://"):]
        )

    elif (
        uri.startswith("cc:")
        and not uri.startswith("cc://")
    ):
        uri = "cc://" + uri[3:]

    elif not (
        uri.startswith("cc://")
        or uri.startswith("http://")
        or uri.startswith("https://")
    ):
        uri = "cc://" + uri

    try:
        parsed = urllib.parse.urlparse(uri)

        query_params = urllib.parse.parse_qs(
            parsed.query,
            keep_blank_values=True,
        )

    except Exception as e:
        raise ValueError(
            f"Falha ao interpretar URI: {e}"
        )

    year = detect_year(
        query_params
    )

    place_id = first_query_value(
        query_params,
        "place",
        "",
    )

    if not place_id:
        place_id = first_query_value(
            query_params,
            "placeId",
            "",
        )

    ticket = first_query_value(
        query_params,
        "ticket",
        "",
    )

    place_launcher_url = first_query_value(
        query_params,
        "placelauncherurl",
        "",
    )

    if place_launcher_url:
        try:
            place_launcher_url = urllib.parse.unquote(
                place_launcher_url
            )
        except Exception:
            pass

    params = [
        "-a",
        "http://madxka.com/Login/Negotiate.ashx",
    ]

    if place_launcher_url:
        params.extend(
            [
                "-j",
                place_launcher_url,
            ]
        )

    elif place_id and ticket:
        fallback_url = build_place_launcher_url(
            place_id,
            ticket,
            year,
        )

        if fallback_url:
            params.extend(
                [
                    "-j",
                    fallback_url,
                ]
            )

    if ticket:
        params.extend(
            [
                "-t",
                ticket,
            ]
        )

    if place_id:
        params.extend(
            [
                "-placeId",
                place_id,
            ]
        )

    ignored_keys = {
        "place",
        "placeId",
        "ticket",
        "placelauncherurl",
        "year",
    }

    for key, values in query_params.items():

        if key in ignored_keys:
            continue

        if not values:
            continue

        flag = URI_KEY_ARG_MAP.get(key)

        if not flag:
            continue

        value = values[0]

        if key == "launchmode":
            params.extend(
                [
                    flag,
                    value,
                ]
            )

        elif key == "launchtime":
            params.append(
                f"{flag}{value}"
            )

        else:
            params.extend(
                [
                    flag,
                    value,
                ]
            )

    return {
        "uri": params,
        "uri_string": " ".join(
            quote_arg_for_display(x)
            for x in params
        ),
        "year": year,
        "place_id": place_id,
        "ticket": ticket,
        "place_launcher_url": place_launcher_url,
    }


def format_command_for_display(
    command,
):
    result = []

    hide_next = False

    for arg in command:

        if hide_next:
            result.append("<TICKET>")
            hide_next = False
            continue

        if arg == "-t":
            result.append("-t")
            hide_next = True
            continue

        result.append(
            quote_arg_for_display(arg)
        )

    return " ".join(result)


def create_desktop_entry(script_path):
    if not get_system_info()["is_linux"]:
        return

    print(
        Fore.CYAN
        + "[*] Creating Desktop Entry for Cartii Launcher..."
    )

    DESKTOP_APPS.mkdir(
        parents=True,
        exist_ok=True,
    )

    python_path = (
        shutil.which("python3")
        or "/usr/bin/python3"
    )

    script_path = os.path.abspath(
        script_path
    )

    desktop_content = f"""[Desktop Entry]
Name=Cartii Launcher
Comment=Cartii Launcher CC URI Handler
Exec="{python_path}" "{script_path}" --uri %u
Type=Application
Terminal=true
MimeType=x-scheme-handler/cc;
Categories=Game;
Icon=madoka-player
NoDisplay=true
"""

    try:
        with open(
            ENTRY_FILE,
            "w",
            encoding="utf-8",
        ) as file:
            file.write(
                desktop_content
            )

        try:
            ENTRY_FILE.chmod(0o755)
        except Exception:
            pass

        print(
            Fore.GREEN
            + f"[*] Desktop entry created: {ENTRY_FILE}"
        )

    except Exception as e:
        print(
            Fore.RED
            + f"[!] Failed to create desktop entry: {e}"
        )

        return

    uninstall_content = f"""[Desktop Entry]
Name=Uninstall Cartii Launcher
Exec="{python_path}" "{script_path}" --uninstall
Type=Application
Terminal=true
Categories=Game;
Icon=madoka-player
"""

    try:
        with open(
            UNINSTALL_ENTRY_FILE,
            "w",
            encoding="utf-8",
        ) as file:
            file.write(
                uninstall_content
            )

        try:
            UNINSTALL_ENTRY_FILE.chmod(0o755)
        except Exception:
            pass

        print(
            Fore.GREEN
            + (
                "[*] Uninstall entry created: "
                f"{UNINSTALL_ENTRY_FILE}"
            )
        )

    except Exception as e:
        print(
            Fore.RED
            + f"[!] Failed to create uninstall entry: {e}"
        )


def register_uri_handler():
    if not get_system_info()["is_linux"]:
        return

    print(
        Fore.CYAN
        + "[*] Registering MIME type handler (cc://)..."
    )

    desktop_name = (
        "cartii-launcher.desktop"
    )

    try:
        subprocess.run(
            [
                "update-desktop-database",
                str(DESKTOP_APPS),
            ],
            check=False,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )

        print(
            Fore.GREEN
            + "[*] Desktop database updated"
        )

    except FileNotFoundError:
        print(
            Fore.YELLOW
            + "[!] update-desktop-database not found."
        )

    except Exception as e:
        print(
            Fore.YELLOW
            + f"[!] Could not update desktop database: {e}"
        )

    try:
        result = subprocess.run(
            [
                "xdg-mime",
                "default",
                desktop_name,
                "x-scheme-handler/cc",
            ],
            check=False,
            capture_output=True,
            text=True,
        )

        if result.returncode == 0:
            print(
                Fore.GREEN
                + "[*] MIME type cc:// registered"
            )

        else:
            print(
                Fore.RED
                + "[!] Failed to register cc://"
            )

            if result.stderr.strip():
                print(
                    Fore.YELLOW
                    + result.stderr.strip()
                )

    except FileNotFoundError:
        print(
            Fore.RED
            + "[!] xdg-mime was not found."
        )

        return

    except Exception as e:
        print(
            Fore.RED
            + f"[!] Could not register MIME type: {e}"
        )

        return

    try:
        result = subprocess.run(
            [
                "xdg-mime",
                "query",
                "default",
                "x-scheme-handler/cc",
            ],
            check=False,
            capture_output=True,
            text=True,
        )

        current_handler = (
            result.stdout.strip()
        )

        print(
            Fore.CYAN
            + (
                "[*] Current cc:// handler: "
                f"{current_handler}"
            )
        )

        if current_handler == desktop_name:
            print(
                Fore.GREEN
                + "[*] cc:// handler verified successfully!"
            )

        else:
            print(
                Fore.RED
                + "[!] cc:// handler verification failed."
            )

    except Exception as e:
        print(
            Fore.YELLOW
            + f"[!] Could not verify cc:// handler: {e}"
        )


def get_wine_cmd():
    if shutil.which("wine64"):
        return "wine64"

    if shutil.which("wine"):
        return "wine"

    return None


def get_wine_environment():
    env = os.environ.copy()

    env["WINEPREFIX"] = str(
        WINEPREFIX_DIR
    )

    env["__NV_PRIME_RENDER_OFFLOAD"] = "1"
    env["__GLX_VENDOR_LIBRARY_NAME"] = "nvidia"

    return env


def get_executable_path(year):
    sys_info = get_system_info()

    clean_year = (
        str(year)
        .replace("L", "")
        .replace("M", "")
        .strip()
    )

    if sys_info["is_linux"]:

        user = os.getenv(
            "USER",
            "user",
        )

        base = (
            WINEPREFIX_DIR
            / "drive_c"
            / "users"
            / user
            / "AppData"
            / "Local"
            / "cartiirev"
            / f"Client{clean_year}"
        )

        preferred = (
            base
            / "CartiPlayerBeta.exe"
        )

        if preferred.is_file():
            return str(preferred)

        alternatives = [
            "CartiiPlayerBeta.exe",
            "ProjectXPlayerBeta.exe",
            "CartiPlayer.exe",
        ]

        for name in alternatives:

            path = base / name

            if path.is_file():
                return str(path)

    elif sys_info["is_windows"]:

        local_app_data = os.getenv(
            "LOCALAPPDATA",
            "",
        )

        base = (
            Path(local_app_data)
            / "cartiirev"
            / f"Client{clean_year}"
        )

        preferred = (
            base
            / "CartiPlayerBeta.exe"
        )

        if preferred.is_file():
            return str(preferred)

    return None


def handle_uri_launch(uri):
    sys_info = get_system_info()

    if not sys_info["is_linux"]:
        print(
            Fore.RED
            + "[!] URI handling is only supported on Linux"
        )

        sys.exit(1)

    print(
        Fore.CYAN
        + f"[*] Handling URI: {uri}"
    )

    try:
        parsed = parse_uri(uri)

    except Exception as e:
        print(
            Fore.RED
            + f"[!] Failed to parse URI: {e}"
        )

        sys.exit(1)

    year = parsed["year"]
    args = parsed["uri"]

    print(
        Fore.CYAN
        + f"[*] Target year: {year}"
    )

    print(
        Fore.CYAN
        + "[*] Launch arguments:"
    )

    hide_next = False

    for i, arg in enumerate(args):

        if hide_next:
            print(
                Fore.WHITE
                + f"    [{i}] <TICKET>"
            )

            hide_next = False
            continue

        if arg == "-t":
            print(
                Fore.WHITE
                + f"    [{i}] -t"
            )

            hide_next = True
            continue

        print(
            Fore.WHITE
            + f"    [{i}] {arg}"
        )

    print(
        Fore.CYAN
        + "\n[*] Join diagnostics:"
    )

    print(
        Fore.WHITE
        + (
            "    PlaceId: "
            + str(
                parsed.get(
                    "place_id",
                    "",
                )
            )
        )
    )

    print(
        Fore.WHITE
        + "    Ticket: "
        + (
            "present"
            if parsed.get("ticket")
            else "MISSING"
        )
    )

    if parsed.get(
        "place_launcher_url"
    ):
        print(
            Fore.GREEN
            + "    PlaceLauncher: received from CC"
        )

    else:
        print(
            Fore.YELLOW
            + "    PlaceLauncher: generated fallback"
        )

    fastflags = load_fastflags()

    if fastflags:

        print(
            Fore.CYAN
            + (
                f"[*] Applying "
                f"{len(fastflags)} FastFlag(s)..."
            )
        )

        apply_fastflags(
            fastflags
        )

    exe_path = get_executable_path(
        year
    )

    if not exe_path:

        user = os.getenv(
            "USER",
            "user",
        )

        expected_path = (
            WINEPREFIX_DIR
            / "drive_c"
            / "users"
            / user
            / "AppData"
            / "Local"
            / "cartiirev"
            / f"Client{year}"
            / "CartiPlayerBeta.exe"
        )

        print(
            Fore.RED
            + (
                "[!] Executável não encontrado "
                f"para Client{year}!"
            )
        )

        print(
            Fore.YELLOW
            + f"Caminho esperado: {expected_path}"
        )

        sys.exit(1)

    print(
        Fore.GREEN
        + f"[*] Found executable: {exe_path}"
    )

    wine_cmd = get_wine_cmd()

    if not wine_cmd:

        print(
            Fore.RED
            + "[!] Wine is not installed!"
        )

        sys.exit(1)

    env = get_wine_environment()

    cmd = [
        wine_cmd,
        exe_path,
    ] + args

    print(
        Fore.CYAN
        + "\n[*] Final command:"
    )

    print(
        Fore.WHITE
        + format_command_for_display(cmd)
    )

    WINEPREFIX_DIR.mkdir(
        parents=True,
        exist_ok=True,
    )

    log_file = (
        WINEPREFIX_DIR
        / "wine_launch.log"
    )

    try:

        with open(
            log_file,
            "a",
            encoding="utf-8",
        ) as log:

            log.write(
                "\n\n"
                + "=" * 70
                + "\n"
            )

            log.write(
                f"Cartii Launcher {VERSION}\n"
            )

            log.write(
                f"URI: {uri}\n"
            )

            log.write(
                f"Year: {year}\n"
            )

            log.write(
                "Arguments:\n"
            )

            hide_next = False

            for arg in args:

                if hide_next:

                    log.write(
                        "  [ticket hidden]\n"
                    )

                    hide_next = False
                    continue

                if arg == "-t":

                    log.write(
                        "  -t\n"
                    )

                    hide_next = True
                    continue

                log.write(
                    f"  {arg}\n"
                )

            log.write(
                "=" * 70
                + "\n"
            )

            log.flush()

            subprocess.Popen(
                cmd,
                env=env,
                stdin=subprocess.DEVNULL,
                stdout=log,
                stderr=log,
                start_new_session=True,
            )

        print(
            Fore.GREEN
            + "[*] Client launched successfully!"
        )

        sys.exit(0)

    except Exception as e:

        print(
            Fore.RED
            + f"[!] Failed to launch client: {e}"
        )

        sys.exit(1)


def load_fastflags():
    path = Path(
        FASTFLAGS_FILE
    )

    if not path.exists():

        try:
            with open(
                path,
                "w",
                encoding="utf-8",
            ) as file:

                json.dump(
                    {},
                    file,
                    indent=2,
                )

        except Exception:
            pass

        return {}

    try:

        with open(
            path,
            "r",
            encoding="utf-8",
        ) as file:

            data = json.load(file)

        if not isinstance(data, dict):
            return {}

        return data

    except json.JSONDecodeError:

        print(
            Fore.RED
            + (
                "[!] Error reading "
                "fastFlags.json - invalid JSON format"
            )
        )

        return {}

    except Exception as e:

        print(
            Fore.RED
            + f"[!] Failed to read FastFlags: {e}"
        )

        return {}


def save_fastflags(fastflags):
    try:

        with open(
            FASTFLAGS_FILE,
            "w",
            encoding="utf-8",
        ) as file:

            json.dump(
                fastflags,
                file,
                indent=2,
            )

        print(
            Fore.GREEN
            + "[*] FastFlags saved successfully!"
        )

    except Exception as e:

        print(
            Fore.RED
            + f"[!] Failed to save FastFlags: {e}"
        )


def apply_fastflags(fastflags):
    user = os.getenv(
        "USER",
        "user",
    )

    base_cartii = (
        WINEPREFIX_DIR
        / "drive_c"
        / "users"
        / user
        / "AppData"
        / "Local"
        / "cartiirev"
    )

    success = False

    if not base_cartii.exists():
        return False

    for client_folder in base_cartii.glob(
        "Client*"
    ):

        if not client_folder.is_dir():
            continue

        client_settings = (
            client_folder
            / "ClientSettings"
        )

        settings_file = (
            client_settings
            / "ClientAppSettings.json"
        )

        try:

            client_settings.mkdir(
                parents=True,
                exist_ok=True,
            )

            with open(
                settings_file,
                "w",
                encoding="utf-8",
            ) as file:

                json.dump(
                    fastflags,
                    file,
                    indent=2,
                )

            print(
                Fore.GREEN
                + (
                    "[*] FastFlags aplicados em "
                    f"{client_folder.name}/ClientSettings"
                )
            )

            success = True

        except Exception as e:

            print(
                Fore.RED
                + (
                    "[!] Erro ao aplicar FastFlags "
                    f"em {client_folder.name}: {e}"
                )
            )

    return success


def auto_detect_value_type(value_str):
    value_str = value_str.strip()

    if value_str.lower() == "true":
        return True

    if value_str.lower() == "false":
        return False

    try:

        if (
            "."
            not in value_str
            and "e"
            not in value_str.lower()
        ):
            return int(value_str)

    except ValueError:
        pass

    try:
        return float(value_str)

    except ValueError:
        pass

    return value_str


def ask_fastflags():
    while True:

        clear()

        print(
            Fore.YELLOW
            + "FastFlags Configuration"
        )

        fastflags = load_fastflags()

        if fastflags:

            print(
                Fore.CYAN
                + "Current FFlags:"
            )

            for i, (key, value) in enumerate(
                fastflags.items(),
                1,
            ):

                value_type = (
                    type(value).__name__
                )

                print(
                    Fore.YELLOW
                    + (
                        f" {i}. {key} = "
                        f"{value} ({value_type})"
                    )
                )

        else:

            print(
                Fore.MAGENTA
                + "No fflags set yet"
            )

        print(
            Fore.GREEN
            + "\nOptions:"
        )

        print("1. Add FastFlag")
        print("2. Remove FastFlag")
        print("3. Clear all FastFlags")
        print("4. Apply FastFlags")
        print("5. Import FastFlags from JSON")
        print("0. Back to main menu")

        choice = input(
            Fore.WHITE
            + "\nEnter choice: "
        ).strip()

        if choice == "1":

            add_fastflag(
                fastflags
            )

        elif choice == "2":

            remove_fastflag(
                fastflags
            )

        elif choice == "3":

            clear_fastflags()

        elif choice == "4":

            if fastflags:

                if apply_fastflags(
                    fastflags
                ):

                    print(
                        Fore.GREEN
                        + (
                            "[*] FastFlags "
                            "applied successfully."
                        )
                    )

                else:

                    print(
                        Fore.RED
                        + "[!] Failed to apply FastFlags"
                    )

            else:

                print(
                    Fore.YELLOW
                    + "[*] No FastFlags to apply"
                )

            press_any_key()

        elif choice == "5":

            import_fastflags()

        elif choice == "0":
            break

        else:

            print(
                Fore.RED
                + "Invalid choice!"
            )

            press_any_key()


def add_fastflag(fastflags):
    print(
        Fore.GREEN
        + "\nAdd New FastFlag:"
    )

    key = input(
        Fore.WHITE
        + "\nKey: "
    ).strip()

    if not key:

        print(
            Fore.RED
            + "[*] Cancelled - no key provided"
        )

        press_any_key()
        return

    value_input = input(
        Fore.WHITE
        + "Value: "
    ).strip()

    if value_input == "":

        print(
            Fore.RED
            + "[*] Cancelled - no value provided"
        )

        press_any_key()
        return

    value = auto_detect_value_type(
        value_input
    )

    fastflags[key] = value

    save_fastflags(
        fastflags
    )

    value_type = (
        type(value).__name__
    )

    print(
        Fore.GREEN
        + (
            f"[*] Added FastFlag: "
            f"{key} = {value} ({value_type})"
        )
    )

    press_any_key()


def remove_fas