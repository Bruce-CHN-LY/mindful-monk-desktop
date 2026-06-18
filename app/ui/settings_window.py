import sys

from PySide6.QtCore import QTime, Signal
from PySide6.QtWidgets import (
    QCheckBox,
    QDoubleSpinBox,
    QFormLayout,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QSpinBox,
    QTimeEdit,
    QVBoxLayout,
    QWidget,
)


class SettingsWindow(QWidget):
    saved = Signal(dict)
    dismissed = Signal()
    quotes_requested = Signal()

    def __init__(self, settings: dict, parent=None):
        super().__init__(parent)
        self.setWindowTitle("设置")
        self.interval = QSpinBox()
        self.interval.setRange(1, 240)
        self.interval.setValue(settings.get("reminder_interval_minutes", 45))

        self.random_enabled = QCheckBox("启用随机提醒")
        self.random_enabled.setChecked(settings.get("random_reminder_enabled", True))

        self.random_min = QSpinBox()
        self.random_min.setRange(1, 240)
        self.random_min.setValue(settings.get("random_reminder_min_minutes", 60))

        self.random_max = QSpinBox()
        self.random_max.setRange(1, 240)
        self.random_max.setValue(settings.get("random_reminder_max_minutes", 120))

        self.quiet_enabled = QCheckBox("启用静默时段")
        self.quiet_enabled.setChecked(settings.get("quiet_hours_enabled", True))

        self.quiet_start = self._time_box(settings.get("quiet_start", "22:30"), "22:30")
        self.quiet_end = self._time_box(settings.get("quiet_end", "07:00"), "07:00")

        self.character_scale = QDoubleSpinBox()
        self.character_scale.setRange(0.5, 2.5)
        self.character_scale.setSingleStep(0.1)
        self.character_scale.setDecimals(1)
        self.character_scale.setValue(settings.get("character_scale", 1.0))

        self.click_through = QCheckBox("启用点击穿透")
        self.click_through.setChecked(settings.get("click_through", False))

        self.golden_aura = QCheckBox("启用背后暖金光")
        self.golden_aura.setChecked(settings.get("golden_aura_enabled", True))

        self.launch_at_login = QCheckBox("登录后自动启动")
        self.launch_at_login.setChecked(settings.get("launch_at_login", False))
        if sys.platform != "darwin":
            self.launch_at_login.setChecked(False)
            self.launch_at_login.setEnabled(False)
            self.launch_at_login.setText("登录后自动启动（当前仅支持 macOS）")

        enabled_categories = set(settings.get("enabled_categories", []))
        self.category_mind = QCheckBox("观心念")
        self.category_breath = QCheckBox("观呼吸")
        self.category_compassion = QCheckBox("慈悲安住")
        self.category_morning_night = QCheckBox("晨昏偈语")
        categories = {
            "mind": self.category_mind,
            "breath": self.category_breath,
            "compassion": self.category_compassion,
            "morning_night": self.category_morning_night,
        }
        for key, checkbox in categories.items():
            checkbox.setChecked(key in enabled_categories)
        self.categories = categories

        animation = settings.get("animation_intervals_ms", {})
        self.idle_speed = self._speed_box(animation.get("idle", 300))
        self.prayer_speed = self._speed_box(animation.get("prayer", 220))
        self.breathing_speed = self._speed_box(animation.get("breathing", 380))
        self.bell_speed = self._speed_box(animation.get("bell", 190))

        form = QFormLayout()
        form.addRow("固定提醒间隔(分钟)", self.interval)
        form.addRow("", self.random_enabled)
        form.addRow("随机提醒最短(分钟)", self.random_min)
        form.addRow("随机提醒最长(分钟)", self.random_max)
        form.addRow("", self.quiet_enabled)
        form.addRow("静默开始", self.quiet_start)
        form.addRow("静默结束", self.quiet_end)
        form.addRow("角色大小倍数", self.character_scale)
        form.addRow("", self.golden_aura)
        form.addRow("", self.click_through)
        form.addRow("", self.launch_at_login)
        form.addRow("偈语", self.category_mind)
        form.addRow("", self.category_breath)
        form.addRow("", self.category_compassion)
        form.addRow("", self.category_morning_night)
        form.addRow("待机速度(ms)", self.idle_speed)
        form.addRow("合十速度(ms)", self.prayer_speed)
        form.addRow("观息速度(ms)", self.breathing_speed)
        form.addRow("木鱼速度(ms)", self.bell_speed)

        hint = QLabel("提醒不必太多。留一点空白，小沙弥才像陪伴，而不是催促。")
        hint.setWordWrap(True)

        save = QPushButton("保存")
        save.clicked.connect(self._emit_save)
        quotes = QPushButton("管理偈语…")
        quotes.clicked.connect(self.quotes_requested.emit)

        footer = QHBoxLayout()
        footer.addWidget(quotes)
        footer.addStretch(1)
        footer.addWidget(save)

        layout = QVBoxLayout(self)
        layout.addLayout(form)
        layout.addWidget(hint)
        layout.addLayout(footer)

    def _emit_save(self):
        enabled_categories = [
            key for key, checkbox in self.categories.items() if checkbox.isChecked()
        ] or ["mind"]
        settings = {
            "reminder_interval_minutes": self.interval.value(),
            "random_reminder_enabled": self.random_enabled.isChecked(),
            "random_reminder_min_minutes": self.random_min.value(),
            "random_reminder_max_minutes": self.random_max.value(),
            "quiet_hours_enabled": self.quiet_enabled.isChecked(),
            "quiet_start": self.quiet_start.time().toString("HH:mm"),
            "quiet_end": self.quiet_end.time().toString("HH:mm"),
            "character_scale": self.character_scale.value(),
            "golden_aura_enabled": self.golden_aura.isChecked(),
            "click_through": self.click_through.isChecked(),
            "launch_at_login": self.launch_at_login.isChecked(),
            "enabled_categories": enabled_categories,
            "animation_intervals_ms": {
                "idle": self.idle_speed.value(),
                "prayer": self.prayer_speed.value(),
                "breathing": self.breathing_speed.value(),
                "bell": self.bell_speed.value(),
            },
        }
        self.saved.emit(settings)
        self.close()

    def closeEvent(self, event):
        self.dismissed.emit()
        super().closeEvent(event)

    @staticmethod
    def _speed_box(value: int) -> QSpinBox:
        box = QSpinBox()
        box.setRange(80, 2000)
        box.setSingleStep(10)
        box.setValue(int(value))
        return box

    @staticmethod
    def _time_box(value: str, fallback: str) -> QTimeEdit:
        box = QTimeEdit()
        box.setDisplayFormat("HH:mm")
        parsed = QTime.fromString(str(value), "HH:mm")
        box.setTime(parsed if parsed.isValid() else QTime.fromString(fallback, "HH:mm"))
        return box
