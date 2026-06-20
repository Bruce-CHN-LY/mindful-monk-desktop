import json

from app.data.settings_store import SettingsStore


def test_settings_store_loads_defaults(tmp_path):
    defaults_path = tmp_path / "defaults.json"
    settings_path = tmp_path / "data" / "settings.json"
    defaults_path.write_text(
        json.dumps({"reminder_interval_minutes": 45, "nested": {"a": 1, "b": 2}}),
        encoding="utf-8",
    )
    store = SettingsStore(defaults_path, settings_path)
    settings = store.load()
    assert "reminder_interval_minutes" in settings


def test_settings_store_deep_merges_nested_values(tmp_path):
    defaults_path = tmp_path / "defaults.json"
    settings_path = tmp_path / "settings.json"
    defaults_path.write_text(json.dumps({"nested": {"a": 1, "b": 2}}), encoding="utf-8")
    settings_path.write_text(json.dumps({"nested": {"a": 9}}), encoding="utf-8")

    settings = SettingsStore(defaults_path, settings_path).load()

    assert settings["nested"] == {"a": 9, "b": 2}


def test_settings_store_recovers_from_invalid_json(tmp_path):
    defaults_path = tmp_path / "defaults.json"
    settings_path = tmp_path / "settings.json"
    defaults_path.write_text(json.dumps({"value": 1}), encoding="utf-8")
    settings_path.write_text("not-json", encoding="utf-8")

    settings = SettingsStore(defaults_path, settings_path).load()

    assert settings == {"value": 1}
    assert settings_path.with_suffix(".broken.json").exists()


def test_settings_store_recovers_from_valid_non_object_json(tmp_path):
    defaults_path = tmp_path / "defaults.json"
    settings_path = tmp_path / "settings.json"
    defaults_path.write_text(json.dumps({"value": 1}), encoding="utf-8")
    settings_path.write_text("[]", encoding="utf-8")

    settings = SettingsStore(defaults_path, settings_path).load()

    assert settings == {"value": 1}
    assert settings_path.with_suffix(".broken.json").read_text(encoding="utf-8") == "[]"


def test_settings_store_keeps_multiple_broken_backups(tmp_path):
    defaults_path = tmp_path / "defaults.json"
    settings_path = tmp_path / "settings.json"
    defaults_path.write_text(json.dumps({"value": 1}), encoding="utf-8")
    settings_path.write_text("first", encoding="utf-8")
    store = SettingsStore(defaults_path, settings_path)
    store.load()
    settings_path.write_text("second", encoding="utf-8")

    store.load()

    assert settings_path.with_suffix(".broken.json").read_text(encoding="utf-8") == "first"
    assert settings_path.with_suffix(".broken-2.json").read_text(encoding="utf-8") == "second"
