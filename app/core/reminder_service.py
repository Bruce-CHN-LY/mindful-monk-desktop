from __future__ import annotations

import random
from PySide6.QtCore import QObject, QTimer, Signal


class ReminderService(QObject):
    reminder_due = Signal(str)

    def __init__(self, settings_store, presence_service):
        super().__init__()
        self.settings_store = settings_store
        self.presence_service = presence_service
        self.fixed_timer = QTimer(self)
        self.fixed_timer.timeout.connect(lambda: self._emit_if_allowed("scheduled"))
        self.random_timer = QTimer(self)
        self.random_timer.timeout.connect(lambda: self._emit_if_allowed("random"))

    def start(self):
        settings = self.settings_store.load()
        interval_ms = self._minutes(settings.get("reminder_interval_minutes"), 45) * 60 * 1000
        self.fixed_timer.start(max(interval_ms, 60_000))
        self._schedule_random(settings)

    def trigger_manual(self, kind: str = "manual"):
        self.reminder_due.emit(kind)

    def reload(self):
        self.fixed_timer.stop()
        self.random_timer.stop()
        self.start()

    def _emit_if_allowed(self, kind: str):
        settings = self.settings_store.load()
        if not self.presence_service.should_suppress(settings):
            self.reminder_due.emit(kind)
        if kind == "random":
            self._schedule_random(settings)

    def _schedule_random(self, settings: dict):
        if not settings.get("random_reminder_enabled", True):
            return
        min_minutes = self._minutes(settings.get("random_reminder_min_minutes"), 60)
        max_minutes = self._minutes(settings.get("random_reminder_max_minutes"), 120)
        delay_minutes = random.randint(min_minutes, max(max_minutes, min_minutes))
        self.random_timer.start(delay_minutes * 60 * 1000)

    @staticmethod
    def _minutes(value, fallback: int) -> int:
        try:
            return max(int(value), 1)
        except (TypeError, ValueError):
            return fallback
