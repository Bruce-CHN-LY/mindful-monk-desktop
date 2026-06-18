from pathlib import Path

from app.constants import data_dir_for_platform


def test_data_dir_uses_macos_application_support():
    assert data_dir_for_platform("darwin", Path("/Users/test"), {}) == Path(
        "/Users/test/Library/Application Support/Mindful Monk"
    )


def test_data_dir_uses_windows_appdata():
    assert data_dir_for_platform(
        "win32",
        Path("C:/Users/test"),
        {"APPDATA": "C:/Users/test/AppData/Roaming"},
    ) == Path("C:/Users/test/AppData/Roaming/Mindful Monk")


def test_data_dir_uses_linux_xdg_data_home():
    assert data_dir_for_platform(
        "linux", Path("/home/test"), {"XDG_DATA_HOME": "/tmp/data"}
    ) == Path("/tmp/data/mindful-monk")
