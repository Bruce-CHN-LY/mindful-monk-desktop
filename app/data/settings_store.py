from __future__ import annotations

import json
import os
from copy import deepcopy
from pathlib import Path

from app.constants import DATA_DIR, DEFAULT_SETTINGS_PATH, SETTINGS_PATH


class SettingsStore:
    def __init__(self, defaults_path: Path = DEFAULT_SETTINGS_PATH, settings_path: Path = SETTINGS_PATH):
        self.defaults_path = defaults_path
        self.settings_path = settings_path
        self.settings_path.parent.mkdir(parents=True, exist_ok=True)

    def load(self) -> dict:
        defaults = self._read_json(self.defaults_path)
        if not self.settings_path.exists():
            self.save(defaults)
            return defaults

        try:
            current = self._read_json(self.settings_path)
        except (json.JSONDecodeError, OSError, TypeError):
            backup = self.settings_path.with_suffix(".broken.json")
            try:
                self.settings_path.replace(backup)
            except OSError:
                pass
            self.save(defaults)
            return defaults
        return self._deep_merge(defaults, current)

    def save(self, settings: dict):
        payload = json.dumps(settings, ensure_ascii=False, indent=2)
        temporary = self.settings_path.with_suffix(".tmp")
        temporary.write_text(payload, encoding="utf-8")
        os.replace(temporary, self.settings_path)

    @staticmethod
    def _read_json(path):
        return json.loads(path.read_text(encoding="utf-8"))

    @classmethod
    def _deep_merge(cls, defaults: dict, current: dict) -> dict:
        merged = deepcopy(defaults)
        for key, value in current.items():
            if isinstance(value, dict) and isinstance(merged.get(key), dict):
                merged[key] = cls._deep_merge(merged[key], value)
            else:
                merged[key] = value
        return merged
