from __future__ import annotations

import json
import os
from pathlib import Path
from uuid import uuid4

from app.constants import CUSTOM_QUOTES_PATH, QUOTES_PATH, SCRIPTURE_QUOTES_PATH


class QuoteStore:
    def __init__(
        self,
        base_path: Path = QUOTES_PATH,
        custom_path: Path = CUSTOM_QUOTES_PATH,
        scripture_path: Path | None = SCRIPTURE_QUOTES_PATH,
    ):
        self.base_path = base_path
        self.custom_path = custom_path
        self.scripture_path = scripture_path

    def load_quotes(self) -> list[dict]:
        scripture = self._read_list(self.scripture_path) if self.scripture_path else []
        return self._read_list(self.base_path) + scripture + self.load_custom_quotes()

    def load_custom_quotes(self) -> list[dict]:
        return self._read_list(self.custom_path)

    def add_quote(self, text: str, category: str) -> dict:
        quote = {
            "id": f"custom_{uuid4().hex}",
            "text": text.strip(),
            "category": category,
            "weight": 1,
            "enabled": True,
        }
        quotes = self.load_custom_quotes()
        quotes.append(quote)
        self._save_custom_quotes(quotes)
        return quote

    def delete_quote(self, quote_id: str) -> bool:
        quotes = self.load_custom_quotes()
        remaining = [quote for quote in quotes if quote.get("id") != quote_id]
        if len(remaining) == len(quotes):
            return False
        self._save_custom_quotes(remaining)
        return True

    @staticmethod
    def _read_list(path: Path) -> list[dict]:
        if not path.exists():
            return []
        try:
            quotes = json.loads(path.read_text(encoding="utf-8"))
            return quotes if isinstance(quotes, list) else []
        except (json.JSONDecodeError, OSError):
            return []

    def _save_custom_quotes(self, quotes: list[dict]):
        self.custom_path.parent.mkdir(parents=True, exist_ok=True)
        temporary = self.custom_path.with_suffix(".tmp")
        temporary.write_text(json.dumps(quotes, ensure_ascii=False, indent=2), encoding="utf-8")
        os.replace(temporary, self.custom_path)
