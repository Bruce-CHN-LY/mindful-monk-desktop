import plistlib

from app.core.autostart_service import AutostartService


def test_autostart_writes_and_removes_launch_agent(tmp_path, monkeypatch):
    monkeypatch.setattr("app.core.autostart_service.sys.platform", "darwin")
    service = AutostartService(tmp_path)

    assert service.set_enabled(True)
    assert service.is_enabled()
    with service.plist_path.open("rb") as stream:
        payload = plistlib.load(stream)
    assert payload["Label"] == service.label
    assert payload["RunAtLoad"] is True

    assert service.set_enabled(False)
    assert not service.is_enabled()
