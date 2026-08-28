import json
import os
from pathlib import Path

from colorama import Fore

from .config import (
    FASTFLAGS_FILE,
    WINEPREFIX_DIR,
)
from .utils import (
    clear,
    press_any_key,
)


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


def remove_fastflag(fastflags):
    if not fastflags:
        print(
            Fore.YELLOW
            + "[*] No FastFlags to remove"
        )

        press_any_key()
        return

    key = input(
        Fore.WHITE
        + "\nEnter key to remove: "
    ).strip()

    if key in fastflags:
        del fastflags[key]

        save_fastflags(
            fastflags
        )

        print(
            Fore.GREEN
            + f"[*] Removed FastFlag: {key}"
        )

    else:
        print(
            Fore.RED
            + f"[!] FastFlag '{key}' not found"
        )

    press_any_key()


def clear_fastflags():
    confirm = input(
        Fore.RED
        + (
            "Are you sure you want to "
            "clear ALL FastFlags? (y/N): "
        )
    ).strip().lower()

    if confirm == "y":
        save_fastflags({})

        print(
            Fore.GREEN
            + "[*] All FastFlags cleared"
        )

    else:
        print(
            Fore.YELLOW
            + "[*] Cancelled"
        )

    press_any_key()


def import_fastflags():
    print(
        Fore.CYAN
        + "\nImport FastFlags from JSON:"
    )

    print(
        Fore.YELLOW
        + (
            "Paste JSON content and press "
            "Enter twice when done:"
        )
    )

    lines = []
    empty_count = 0

    while True:
        line = input()

        if line == "":
            empty_count += 1

            if (
                empty_count >= 2
                or (
                    len(lines) > 0
                    and lines[-1] == ""
                )
            ):
                break

        else:
            empty_count = 0

        lines.append(line)

    while (
        lines
        and lines[-1] == ""
    ):
        lines.pop()

    json_text = "\n".join(
        lines
    )

    if not json_text.strip():
        print(
            Fore.YELLOW
            + "[*] No content provided"
        )

        press_any_key()
        return

    try:
        imported_flags = json.loads(
            json_text
        )

        if not isinstance(
            imported_flags,
            dict,
        ):
            print(
                Fore.RED
                + "[!] JSON must be an object/dictionary"
            )

            press_any_key()
            return

        current_flags = load_fastflags()

        current_flags.update(
            imported_flags
        )

        save_fastflags(
            current_flags
        )

        print(
            Fore.GREEN
            + (
                f"[*] Imported "
                f"{len(imported_flags)} FastFlag(s)"
            )
        )

    except json.JSONDecodeError as e:
        print(
            Fore.RED
            + f"[!] Invalid JSON format: {e}"
        )

    press_any_key()