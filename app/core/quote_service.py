from __future__ import annotations

import random
from collections import deque


class QuoteService:
    def __init__(self, quote_store):
        self.quote_store = quote_store
        self.recent_ids = deque(maxlen=5)

    def next_quote(self, enabled_categories: list[str] | None = None) -> dict:
        quotes = self.quote_store.load_quotes()
        eligible = [
            quote
            for quote in quotes
            if quote.get("enabled", True)
            and (not enabled_categories or quote.get("category") in enabled_categories)
        ]
        filtered = [quote for quote in eligible if quote.get("id") not in self.recent_ids]
        if not filtered:
            filtered = eligible
        if not filtered:
            return {"text": "轻轻看一眼这一念。", "category": "mind"}

        weights = [self._weight(quote.get("weight", 1)) for quote in filtered]
        choice = random.choices(filtered, weights=weights, k=1)[0]
        quote_id = choice.get("id")
        if quote_id:
            self.recent_ids.append(quote_id)
        return choice

    @staticmethod
    def _weight(value) -> int:
        try:
            return max(int(value), 1)
        except (TypeError, ValueError):
            return 1
