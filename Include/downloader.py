import shutil
import urllib.request
from pathlib import Path

from colorama import Fore


def download_file(
    url,
    destination,
    display_name=None,
):
    destination = Path(destination)

    destination.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    name = display_name or destination.name

    temporary = destination.with_suffix(
        destination.suffix + ".download"
    )

    try:
        print(
            Fore.YELLOW
            + f"[*] Downloading {name}..."
        )

        request = urllib.request.Request(
            url,
            headers={
                "User-Agent": "MadokaStrap"
            },
        )

        with urllib.request.urlopen(
            request,
            timeout=30,
        ) as response:
            with open(
                temporary,
                "wb",
            ) as file:
                shutil.copyfileobj(
                    response,
                    file,
                )

        temporary.replace(
            destination
        )

        print(
            Fore.GREEN
            + f"[*] {name} downloaded successfully."
        )

        return True

    except Exception as e:
        print(
            Fore.RED
            + f"[!] Failed to download {name}: {e}"
        )

        try:
            if temporary.exists():
                temporary.unlink()
        except Exception:
            pass

        return False