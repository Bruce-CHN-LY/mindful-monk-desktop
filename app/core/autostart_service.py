from __future__ import annotations

import plistlib
import sys
from pathlib import Path


class AutostartService:
    label = "com.mindfulmonk.desktop"

    def __init__(self, launch_agents_dir: Path | None = None):
        self.launch_agents_dir = launch_agents_dir or Path.home() / "Library" / "LaunchAgents"
        self.plist_path = self.launch_agents_dir / f"{self.label}.plist"

    def is_enabled(self) -> bool:
        return sys.platform == "darwin" and self.plist_path.exists()

    def set_enabled(self, enabled: bool) -> bool:
        if sys.platform != "darwin":
            return False
        if not enabled:
            self.plist_path.unlink(missing_ok=True)
            return True

        self.launch_agents_dir.mkdir(parents=True, exist_ok=True)
        payload = {
            "Label": self.label,
            "ProgramArguments": self._program_arguments(),
            "RunAtLoad": True,
            "ProcessType": "Interactive",
        }
        if not getattr(sys, "frozen", False):
            payload["WorkingDirectory"] = str(Path(__file__).resolve().parents[2])
        with self.plist_path.open("wb") as stream:
            plistlib.dump(payload, stream)
        return True

    @staticmethod
    def _program_arguments() -> list[str]:
        if getattr(sys, "frozen", False):
            return [sys.executable]
        return [sys.executable, "-m", "app.main"]
