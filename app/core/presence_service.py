from __future__ import annotations

from datetime import datetime


class PresenceService:
    def is_quiet_hours(self, settings: dict) -> bool:
        if not settings.get("quiet_hours_enabled", True):
            return False

        now = datetime.now().time()
        try:
            start = self._parse_time(settings.get("quiet_start", "22:30"))
            end = self._parse_time(settings.get("quiet_end", "07:00"))
        except (TypeError, ValueError):
            return False

        if start <= end:
            return start <= now <= end
        return now >= start or now <= end

    def should_suppress(self, settings: dict) -> bool:
        return self.is_quiet_hours(settings)

    @staticmethod
    def _parse_time(value: str):
        if not isinstance(value, str) or ":" not in value:
            raise ValueError("Time must use HH:MM format")
        hour, minute = [int(part) for part in value.split(":", 1)]
        if not 0 <= hour <= 23 or not 0 <= minute <= 59:
            raise ValueError("Time is outside the valid range")
        return datetime.now().replace(hour=hour, minute=minute, second=0, microsecond=0).time()
