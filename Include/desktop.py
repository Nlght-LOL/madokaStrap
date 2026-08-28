import os
import shutil
import subprocess

from colorama import Fore

from .config import (
    DESKTOP_APPS,
    ENTRY_FILE,
    UNINSTALL_ENTRY_FILE,
)

from .utils import get_system_info

def create_desktop_entry(script_path):
    if not get_system_info()["is_linux"]:
        return False

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
Terminal=false
MimeType=x-scheme-handler/cc;x-scheme-handler/madoka-player;
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

    except Exception as error:
        print(
            Fore.RED
            + (
                "[!] Failed to create desktop entry: "
                f"{error}"
            )
        )

        return False

    uninstall_content = f"""[Desktop Entry]
Name=Uninstall Cartii Launcher
Comment=Uninstall Cartii Launcher Linux integration
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

    except Exception as error:
        print(
            Fore.RED
            + (
                "[!] Failed to create uninstall entry: "
                f"{error}"
            )
        )

        return False

    return True


def _update_desktop_database():
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

        return True

    except FileNotFoundError:
        print(
            Fore.YELLOW
            + "[!] update-desktop-database not found."
        )

        return False

    except Exception as error:
        print(
            Fore.YELLOW
            + (
                "[!] Could not update desktop database: "
                f"{error}"
            )
        )

        return False


def _register_mime_handler(
    mime_type,
    desktop_name,
):
    try:
        result = subprocess.run(
            [
                "xdg-mime",
                "default",
                desktop_name,
                mime_type,
            ],
            check=False,
            capture_output=True,
            text=True,
        )

        if result.returncode == 0:
            print(
                Fore.GREEN
                + (
                    f"[*] {mime_type} handler "
                    "registered successfully"
                )
            )

            return True

        print(
            Fore.RED
            + (
                f"[!] Failed to register "
                f"{mime_type}"
            )
        )

        if result.stderr.strip():
            print(
                Fore.YELLOW
                + result.stderr.strip()
            )

        return False

    except FileNotFoundError:
        print(
            Fore.RED
            + "[!] xdg-mime was not found."
        )

        return False

    except Exception as error:
        print(
            Fore.RED
            + (
                f"[!] Could not register {mime_type}: "
                f"{error}"
            )
        )

        return False


def _verify_mime_handler(
    mime_type,
    desktop_name,
):
    try:
        result = subprocess.run(
            [
                "xdg-mime",
                "query",
                "default",
                mime_type,
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
                f"[*] Current {mime_type} handler: "
                f"{current_handler}"
            )
        )

        if current_handler == desktop_name:
            print(
                Fore.GREEN
                + (
                    f"[*] {mime_type} handler "
                    "verified successfully!"
                )
            )

            return True

        print(
            Fore.YELLOW
            + (
                f"[!] {mime_type} handler "
                "verification failed."
            )
        )

        return False

    except Exception as error:
        print(
            Fore.YELLOW
            + (
                f"[!] Could not verify {mime_type}: "
                f"{error}"
            )
        )

        return False

def _check_existing_cc_handler(new_desktop_name):
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

        current_handler = result.stdout.strip()

        if not current_handler:
            print(
                Fore.GREEN
                + "[*] No existing CC:// handler found."
            )
            return True

        if current_handler == new_desktop_name:
            print(
                Fore.GREEN
                + "[*] Cartii Launcher is already the CC:// handler."
            )
            return True

        print(
            Fore.YELLOW
            + (
                "[!] An existing CC:// handler was found: "
                f"{current_handler}"
            )
        )

        response = input(
            Fore.CYAN
            + (
                "[?] Do you want to remove this handler "
                "and replace it with Cartii Launcher? [y/N]: "
            )
        ).strip().lower()

        if response not in ("y", "yes", "s", "sim"):
            print(
                Fore.RED
                + "[!] Installation cancelled by user."
            )
            return False

        desktop_file = DESKTOP_APPS / current_handler

        if desktop_file.exists():
            try:
                desktop_file.unlink()

                print(
                    Fore.GREEN
                    + f"[*] Removed existing CC:// handler: {desktop_file}"
                )
            except Exception as error:
                print(
                    Fore.RED
                    + (
                        "[!] Failed to remove existing CC:// handler: "
                        f"{error}"
                    )
                )
                return False
        else:
            print(
                Fore.YELLOW
                + (
                    "[!] The registered handler file was not found in "
                    f"{DESKTOP_APPS}: {current_handler}"
                )
            )

        return True

    except FileNotFoundError:
        print(
            Fore.RED
            + "[!] xdg-mime was not found."
        )
        return False

    except Exception as error:
        print(
            Fore.RED
            + (
                "[!] Could not check existing CC:// handler: "
                f"{error}"
            )
        )
        return False

def register_uri_handler():
    if not get_system_info()["is_linux"]:
        return False

    print(
        Fore.CYAN
        + "[*] Registering URI handlers..."
    )

    desktop_name = (
        "cartii-launcher.desktop"
    )

    _update_desktop_database()

    cc_registered = _register_mime_handler(
        "x-scheme-handler/cc",
        desktop_name,
    )

    madoka_registered = _register_mime_handler(
        "x-scheme-handler/madoka-player",
        desktop_name,
    )

    _verify_mime_handler(
        "x-scheme-handler/cc",
        desktop_name,
    )

    _verify_mime_handler(
        "x-scheme-handler/madoka-player",
        desktop_name,
    )

    return (
        cc_registered
        or madoka_registered
    )


def setup_linux_integration(script_path):
    if not get_system_info()["is_linux"]:
        return False

    print(
        Fore.CYAN
        + "[*] Setting up Linux integration..."
    )

    if not _check_existing_cc_handler(desktop_name):
        return False

    if not create_desktop_entry(
        script_path
    ):
        return False

    if not register_uri_handler():
        print(
            Fore.YELLOW
            + (
                "[!] URI handler registration "
                "was not completely successful."
            )
        )

    print(
        Fore.GREEN
        + "[*] Linux integration setup complete!"
    )

    return True


def uninstall_linux_integration():
    if not get_system_info()["is_linux"]:
        return False

    print(
        Fore.CYAN
        + "[*] Uninstalling Linux integration..."
    )

    for entry in (
        ENTRY_FILE,
        UNINSTALL_ENTRY_FILE,
    ):
        if entry.exists():
            try:
                entry.unlink()

                print(
                    Fore.GREEN
                    + f"[*] Removed: {entry}"
                )

            except Exception as error:
                print(
                    Fore.RED
                    + (
                        "[!] Failed to remove "
                        f"{entry}: {error}"
                    )
                )

    _update_desktop_database()

    print(
        Fore.GREEN
        + "[*] Linux integration uninstalled!"
    )

    return True
