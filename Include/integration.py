import os
import urllib.request

from colorama import Fore

from .desktop import (
    create_desktop_entry,
    register_uri_handler,
)
from .dxvk import setup_dxvk
from .runtime import (
    get_selected_runtime,
    validate_runtime,
)
from .utils import (
    get_system_info,
    press_any_key,
)


def setup_linux_integration():
    if not get_system_info()["is_linux"]:
        return

    print(
        Fore.CYAN
        + "[*] Setting up Linux integration..."
    )

    runtime = get_selected_runtime()

    print(
        Fore.CYAN
        + f"[*] Runtime: {runtime}"
    )

    valid, error = validate_runtime()

    if not valid:
        print(
            Fore.RED
            + f"[!] {error}"
        )
        press_any_key()
        return

    print(
        Fore.CYAN
        + "\n[*] Checking graphics runtime..."
    )

    if runtime == "wine":
        print(
            Fore.CYAN
            + "[*] Wine runtime selected."
        )

        print(
            Fore.CYAN
            + "[*] Checking DXVK..."
        )

        if not setup_dxvk():
            press_any_key()
            return

    elif runtime == "ge-proton":
        print(
            Fore.CYAN
            + "[*] GE-Proton runtime selected."
        )

        print(
            Fore.GREEN
            + (
                "[*] GE-Proton manages its own "
                "DXVK/Proton graphics stack."
            )
        )

        print(
            Fore.GREEN
            + "[*] Manual DXVK installation skipped."
        )

    print(
        Fore.CYAN
        + "\n[*] Creating desktop integration..."
    )

    script_path = os.path.abspath(
        os.path.join(
            os.path.dirname(__file__),
            "..",
            "main.py",
        )
    )

    create_desktop_entry(
        script_path
    )

    register_uri_handler(
        script_path
    )

    print(
        Fore.GREEN
        + "[*] Linux integration setup complete!"
    )