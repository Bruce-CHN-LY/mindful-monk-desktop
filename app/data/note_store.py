from __future__ import annotations

import json
import os
from datetime import datetime
from pathlib import Path
from uuid import uuid4

from app.constants import DATA_DIR, NOTES_PATH


class NoteStore:
    def __init__(self, notes_path: Path = NOTES_PATH):
        self.notes_path = notes_path
        self.notes_path.parent.mkdir(parents=True, exist_ok=True)

    def add_note(self, tag: str, text: str = "") -> dict:
        notes = self.load_notes()
        note = {
            "id": uuid4().hex,
            "timestamp": datetime.now().isoformat(timespec="seconds"),
            "tag": str(tag).strip(),
            "text": str(text).strip()[:200],
        }
        notes.append(note)
        self._save_notes(notes)
        return note

    def delete_note_at(self, index: int) -> bool:
        notes = self.load_notes()
        if not 0 <= index < len(notes):
            return False
        del notes[index]
        self._save_notes(notes)
        return True

    def _save_notes(self, notes: list[dict]):
        temporary = self.notes_path.with_suffix(".tmp")
        temporary.write_text(json.dumps(notes, ensure_ascii=False, indent=2), encoding="utf-8")
        os.replace(temporary, self.notes_path)

    def load_notes(self) -> list[dict]:
        if not self.notes_path.exists():
            return []
        try:
            notes = json.loads(self.notes_path.read_text(encoding="utf-8"))
            return notes if isinstance(notes, list) else []
        except (json.JSONDecodeError, OSError):
            return []
