import os
import sys
from pathlib import Path


APP_NAME = "mindful_monk"
BASE_DIR = Path(getattr(sys, "_MEIPASS", Path(__file__).resolve().parent))
ASSETS_DIR = BASE_DIR / "assets"
MONK_ASSETS_DIR = ASSETS_DIR / "monk"
SOUNDS_DIR = ASSETS_DIR / "sounds"


def data_dir_for_platform(
    platform_name: str,
    home: Path | None = None,
    environ: dict[str, str] | None = None,
) -> Path:
    home = home or Path.home()
    environ = environ if environ is not None else os.environ
    if platform_name == "darwin":
        return home / "Library" / "Application Support" / "Mindful Monk"
    if platform_name == "win32":
        appdata = environ.get("APPDATA")
        return Path(appdata) / "Mindful Monk" if appdata else home / "AppData" / "Roaming" / "Mindful Monk"
    data_home = environ.get("XDG_DATA_HOME")
    return Path(data_home) / "mindful-monk" if data_home else home / ".local" / "share" / "mindful-monk"


DATA_DIR = data_dir_for_platform(sys.platform)
QUOTES_PATH = ASSETS_DIR / "quotes.json"
SCRIPTURE_QUOTES_PATH = ASSETS_DIR / "scripture_quotes.json"
DEFAULT_SETTINGS_PATH = ASSETS_DIR / "default_settings.json"
SETTINGS_PATH = DATA_DIR / "settings.json"
NOTES_PATH = DATA_DIR / "notes.json"
CUSTOM_QUOTES_PATH = DATA_DIR / "custom_quotes.json"
BELL_SOUND_PATH = SOUNDS_DIR / "bell.wav"

DEFAULT_ROLE_SIZE = 164
MESSAGE_DURATION_MS = 8000
MENU_WIDTH = 220
