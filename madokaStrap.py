import sys


from Include.menu import main_menu
from Include.uri import handle_uri_launch
from Include.desktop import uninstall_linux_integration


def main():
    if len(sys.argv) > 1:
        arg = sys.argv[1]

        if arg in ("--uri", "-u"):
            if len(sys.argv) > 2:
                handle_uri_launch(sys.argv[2])
            return

        if arg.startswith("cc://") or arg.startswith("madoka-player://"):
            handle_uri_launch(arg)
            return

        if arg == "--uninstall":
            uninstall_linux_integration()
            return

    main_menu()


if __name__ == "__main__":
    main()
