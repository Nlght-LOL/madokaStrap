import sys

from colorama import Fore

from .config import VERSION
from .utils import (
    clear,
    get_system_info,
)
from .studio import launch_studio
from .fastflags import ask_fastflags
from .bootstrapper import launch_bootstrapper
from .integration import setup_linux_integration
from .winrar import install_winrar
from .runtime import choose_runtime

def main_menu():
    while True:
        clear()

        sys_info = get_system_info()

        gradient = [
            (7, 200, 249),
            (5, 157, 230),
            (4, 123, 220),
            (3, 98, 210),
            (2, 74, 200),
        ]

        ascii_logo = [
            r" *.*__   __*.*  __          _______   __    __   *.*__________*.* ",
            r" |  \ |  | |  |        / _____| |  |  |  |  |           | ",
            r" |   \|  | |  |       |  | __   |  |__|  |  `---|  |----` ",
            r" |  *.* `  | |  |       |  | |_ |  |   __   |      |  |      ",
            r" |__| \__| |_____|   \_____| |__|  |__|      |__|      ",
        ]

        for (r, g, b), line in zip(
            gradient,
            ascii_logo,
        ):
            print(
                f"\033[38;2;{r};{g};{b}m"
                f"{line}"
                f"\033[0m"
            )

        print(
            Fore.BLUE
            + "Made for Linux Madoka"
        )

        platform_name = (
            "Windows"
            if sys_info["is_windows"]
            else (
                "Linux"
                if sys_info["is_linux"]
                else (
                    "macOS"
                    if sys_info["is_macos"]
                    else "Unknown"
                )
            )
        )

        print(
            Fore.CYAN
            + (
                f"Running on: {platform_name} "
                f"| Version: {VERSION}"
            )
        )

        if sys_info["is_linux"]:
            print(
                Fore.YELLOW
                + "Linux Support"
            )

            print(
                Fore.YELLOW
                + (
                    "Note: Wine is required "
                    "for Windows executables"
                )
            )

        print()

        print(
            Fore.YELLOW
            + "Select your option:"
        )

        print(
            Fore.GREEN
            + "1 - Launch Studio (MadokaStudio2021)"
        )

        print(
            Fore.GREEN
            + "2 - Set FastFlags"
        )

        print(
            Fore.BLUE
            + "3 - Launch cartiiLauncher.exe"
        )

        if sys_info["is_linux"]:
            print(
                Fore.CYAN
                + "4 - Setup Linux Integration"
            )

            print(
                Fore.CYAN
                + "5 - Install WinRAR in WINEPREFIX"
            )

        print(
            Fore.MAGENTA
            + "6 - Select Runtime (Wine / GE-Proton)"
        )
        
        print(
            Fore.RED
            + "0 - Exit"
        )

        choice = input(
            Fore.WHITE
            + "\nEnter your choice: "
        ).strip()

        if choice == "1":
            launch_studio()

        elif choice == "2":
            ask_fastflags()

        elif choice == "3":
            launch_bootstrapper()

        elif (
            choice == "4"
            and sys_info["is_linux"]
        ):
            setup_linux_integration()

            from .utils import press_any_key

            press_any_key()

        elif (
            choice == "5"
            and sys_info["is_linux"]
        ):
            install_winrar()
        elif choice == "6":
            choose_runtime()
        elif choice == "0":
            sys.exit(0)