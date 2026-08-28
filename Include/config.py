from pathlib import Path

VERSION = "2.2.0"

PROJECT_DIR = Path(__file__).resolve().parent.parent
INCLUDE_DIR = PROJECT_DIR / "Include"

HOME_DIR = Path.home()

CONFIG_DIR = (
    HOME_DIR
    / ".config"
    / "madoka-player"
)

DATA_DIR = (
    HOME_DIR
    / ".local"
    / "share"
    / "madoka-player"
)

WINEPREFIX_DIR = (
    DATA_DIR
    / "wineprefix"
)

GE_PROTON_DIR = (
    DATA_DIR
    / "ge-proton"
)

RUNTIME_FILE = (
    PROJECT_DIR
    / "runtime.json"
)

FASTFLAGS_FILE = (
    PROJECT_DIR
    / "fastFlags.json"
)

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

STUDIO_ARCHIVE = (
    DATA_DIR
    / "MadokaStudio2021.zip"
)

STUDIO_DIR = (
    DATA_DIR
    / "MadokaStudio2021"
)

STUDIO_EXECUTABLE = (
    STUDIO_DIR
    / "RobloxStudio.exe"
)

DXVK_DIR = (
    DATA_DIR
    / "dxvk"
)

DXVK_VERSION_FILE = (
    WINEPREFIX_DIR
    / ".dxvk-version"
)

DESKTOP_APPS = (
    HOME_DIR
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
    / "madoka-player-uninstall.desktop"
)

DESKTOP_FILE = ENTRY_FILE

MIME_DIR = (
    HOME_DIR
    / ".local"
    / "share"
    / "mime"
)

GE_PROTON_API = (
    "https://api.github.com/repos/"
    "GloriousEggroll/proton-ge-custom/releases/latest"
)

DXVK_API_URL = (
    "https://api.github.com/repos/"
    "doitsujin/dxvk/releases/latest"
)

URI_KEY_ARG_MAP = {
    "placeId": "--placeId",
    "gameId": "--gameId",
    "jobId": "--jobId",
    "userId": "--userId",
    "year": "--year",
    "place": "--placeId",
    "game": "--gameId",
}

SUPPORTED_RUNTIMES = [
    "wine",
    "ge-proton",
]

for directory in [
    CONFIG_DIR,
    DATA_DIR,
    WINEPREFIX_DIR,
    GE_PROTON_DIR,
    DXVK_DIR,
    STUDIO_DIR,
    DESKTOP_APPS,
]:
    directory.mkdir(
        parents=True,
        exist_ok=True,
    )