import os
import sys
import subprocess
import urllib.parse

from colorama import Fore
from pathlib import Path

from .config import (
    URI_KEY_ARG_MAP,
    VERSION,
    WINEPREFIX_DIR,
)

from .utils import (
    get_system_info,
    quote_arg_for_display,
)

from .fastflags import (
    load_fastflags,
    apply_fastflags,
)

from .runtime import (
    get_selected_runtime,
    launch_runtime,
)


def first_query_value(query_params, key, default=""):
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


def build_place_launcher_url(place_id, ticket, year):
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

    if uri.startswith("madoka-player://"):
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

    except Exception as error:
        raise ValueError(
            f"Falha ao interpretar URI: {error}"
        )

    year = detect_year(query_params)

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
            quote_arg_for_display(arg)
            for arg in params
        ),
        "year": year,
        "place_id": place_id,
        "ticket": ticket,
        "place_launcher_url": place_launcher_url,
    }


def format_command_for_display(command):
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


def get_client_executable(year):
    client_dir = (
        WINEPREFIX_DIR
        / "drive_c"
        / "users"
        / "steamuser"
        / "AppData"
        / "Local"
        / "cartiirev"
        / f"Client{year}"
    )

    executable = client_dir / "CartiPlayerBeta.exe"

    if executable.exists():
        return executable

    return None

def write_launch_log(
    log_file,
    uri,
    year,
    args,
    runtime,
):
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
            f"Runtime: {runtime}\n"
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


def handle_uri_launch(uri):
    system_info = get_system_info()

    if not system_info["is_linux"]:
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
    except Exception as error:
        print(
            Fore.RED
            + f"[!] Failed to parse URI: {error}"
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

    for index, arg in enumerate(args):
        if hide_next:
            print(
                Fore.WHITE
                + f"    [{index}] <TICKET>"
            )
            hide_next = False
            continue

        if arg == "-t":
            print(
                Fore.WHITE
                + f"    [{index}] -t"
            )
            hide_next = True
            continue

        print(
            Fore.WHITE
            + f"    [{index}] {arg}"
        )

    print(
        Fore.CYAN
        + "\n[*] Join diagnostics:"
    )

    print(
        Fore.WHITE
        + "    PlaceId: "
        + str(
            parsed.get(
                "place_id",
                "",
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

    if parsed.get("place_launcher_url"):
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

        try:
            apply_fastflags(fastflags)
        except Exception as error:
            print(
                Fore.YELLOW
                + (
                    "[!] Failed to apply FastFlags: "
                    f"{error}"
                )
            )

    exe_path = get_client_executable(year)

    if not exe_path:
        expected_path = (
            WINEPREFIX_DIR
            / "drive_c"
            / "users"
            / "steamuser"
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

    exe_path = Path(exe_path).resolve()

    print(
        Fore.GREEN
        + f"[*] Found executable: {exe_path}"
    )

    if not exe_path.exists():
        print(
            Fore.RED
            + "[!] Executable disappeared before launch."
        )
        sys.exit(1)

    runtime = get_selected_runtime()

    print(
        Fore.CYAN
        + f"[*] Runtime: {runtime}"
    )

    print(
        Fore.CYAN
        + f"[*] WINEPREFIX: {WINEPREFIX_DIR}"
    )

    try:
        WINEPREFIX_DIR.mkdir(
            parents=True,
            exist_ok=True,
        )
    except Exception as error:
        print(
            Fore.RED
            + (
                "[!] Failed to create WINEPREFIX: "
                f"{error}"
            )
        )
        sys.exit(1)

    log_file = (
        WINEPREFIX_DIR
        / "wine_launch.log"
    )

    try:
        write_launch_log(
            log_file,
            uri,
            year,
            args,
            runtime,
        )
    except Exception as error:
        print(
            Fore.YELLOW
            + (
                "[!] Failed to write launch log: "
                f"{error}"
            )
        )

    print()

    if runtime == "ge-proton":
        print(
            Fore.CYAN
            + "[*] Starting with GE-Proton through umu-launcher..."
        )
    else:
        print(
            Fore.CYAN
            + "[*] Starting with Wine..."
        )

    try:
        process = launch_runtime(
            exe_path,
            args,
            cwd=exe_path.parent,
        )

    except TypeError as error:
        print(
            Fore.RED
            + (
                "[!] launch_runtime() rejected "
                f"the launch arguments: {error}"
            )
        )

        print(
            Fore.YELLOW
            + (
                "[!] Check Include/runtime.py. "
                "launch_runtime must accept "
                "(exe_path, args, cwd=...)."
            )
        )

        sys.exit(1)

    except Exception as error:
        print(
            Fore.RED
            + (
                "[!] Failed to launch client: "
                f"{error}"
            )
        )

        sys.exit(1)

    if process is None:
        print()

        if runtime == "ge-proton":
            print(
                Fore.RED
                + "[!] GE-Proton could not be started."
            )

            print(
                Fore.YELLOW
                + (
                    "[!] Make sure GE-Proton is installed "
                    "and umu-run is available."
                )
            )
        else:
            print(
                Fore.RED
                + "[!] Wine could not be started."
            )

            print(
                Fore.YELLOW
                + (
                    "[!] Make sure Wine is installed "
                    "and available in PATH."
                )
            )

        sys.exit(1)

    if isinstance(process, subprocess.Popen):
        print(
            Fore.GREEN
            + "[*] Client launched successfully!"
        )

        print(
            Fore.CYAN
            + f"[*] PID: {process.pid}"
        )

        print(
            Fore.CYAN
            + f"[*] Launch log: {log_file}"
        )

        return

    print(
        Fore.RED
        + (
            "[!] Runtime returned an unexpected "
            f"object: {type(process).__name__}"
        )
    )

    print(
        Fore.YELLOW
        + (
            "[!] launch_runtime() must return "
            "subprocess.Popen."
        )
    )

    sys.exit(1)
