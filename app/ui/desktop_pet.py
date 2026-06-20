from __future__ import annotations

from PySide6.QtCore import QPoint, QPointF, QRect, QRectF, Qt, QTimer, QUrl
from PySide6.QtGui import QColor, QIcon, QPainter, QPen, QPixmap, QRadialGradient
from PySide6.QtMultimedia import QSoundEffect
from PySide6.QtWidgets import QApplication, QDialog, QSystemTrayIcon, QWidget

from app.constants import BELL_SOUND_PATH, DEFAULT_ROLE_SIZE, MENU_WIDTH, MESSAGE_DURATION_MS
from app.core.animation_service import AnimationService
from app.core.autostart_service import AutostartService
from app.core.frame_animation import FrameAnimationService
from app.core.presence_service import PresenceService
from app.core.quote_service import QuoteService
from app.core.reminder_service import ReminderService
from app.core.state_machine import PetState
from app.data.note_store import NoteStore
from app.data.quote_store import QuoteStore
from app.data.settings_store import SettingsStore
from app.ui.breath_panel import BreathPanel
from app.ui.message_bubble import MessageBubble
from app.ui.note_windows import NOTE_RESPONSES, NoteCaptureDialog, NoteHistoryWindow
from app.ui.quick_menu import QuickMenu
from app.ui.quote_editor import QuoteEditorWindow
from app.ui.settings_window import SettingsWindow
from app.ui.tray_panel import TrayPanel


class DesktopPetWindow(QWidget):
    def __init__(self):
        super().__init__()
        self._base_window_flags = (
            Qt.FramelessWindowHint
            | Qt.WindowStaysOnTopHint
            | Qt.WindowDoesNotAcceptFocus
            | Qt.Window
        )
        self.setWindowFlags(self._base_window_flags)
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.setAttribute(Qt.WA_ShowWithoutActivating)

        self.drag_offset = QPoint()
        self.press_position = QPoint()
        self.state = PetState.IDLE
        self.pose = "idle"
        self.current_frame_index = 0
        self.restore_timer_id: int | None = None
        self._quitting = False
        self._user_hidden = False
        self._settings_pet_was_visible = True

        self.settings_store = SettingsStore()
        self.quote_store = QuoteStore()
        self.quote_service = QuoteService(self.quote_store)
        self.note_store = NoteStore()
        self.animation_service = AnimationService()
        self.autostart_service = AutostartService()
        self.frame_animation = FrameAnimationService()
        self.presence_service = PresenceService()
        self.settings = self.settings_store.load()
        self.settings["launch_at_login"] = self.autostart_service.is_enabled()
        self.base_size = DEFAULT_ROLE_SIZE

        self._apply_character_scale(initial=True)
        self._restore_window_position()
        self._apply_click_through(initial=True)

        self.message_bubble = MessageBubble()
        self.quick_menu = QuickMenu()
        self.quick_menu.setFixedWidth(MENU_WIDTH)
        self.quick_menu.hide()

        self.breath_panel = BreathPanel()
        self.breath_panel.finished.connect(self._restore_idle)

        self.tray_panel = TrayPanel()
        self.tray_panel.visibility_requested.connect(self._toggle_visibility)
        self.tray_panel.click_through_requested.connect(self._toggle_click_through)
        self.tray_panel.quote_requested.connect(self.show_quote)
        self.tray_panel.bell_requested.connect(self.manual_bell)
        self.tray_panel.note_requested.connect(self.open_note_prompt)
        self.tray_panel.note_history_requested.connect(self.open_note_history)
        self.tray_panel.settings_requested.connect(self.open_settings)
        self.tray_panel.quit_requested.connect(self._quit_from_tray)

        self.bell_sound = QSoundEffect(self)
        if BELL_SOUND_PATH.exists():
            self.bell_sound.setSource(QUrl.fromLocalFile(str(BELL_SOUND_PATH)))
            self.bell_sound.setVolume(0.28)

        self.reminder_service = ReminderService(self.settings_store, self.presence_service)
        self.reminder_service.reminder_due.connect(self._show_reminder)
        self.reminder_service.start()

        self.animation_timer = QTimer(self)
        self.animation_timer.timeout.connect(self._advance_frame)
        self._apply_animation_interval()
        self.tray_icon = self._create_tray_icon()

        self.quick_menu.quote_requested.connect(self.show_quote)
        self.quick_menu.breathe_requested.connect(self.start_breath_session)
        self.quick_menu.bell_requested.connect(self.manual_bell)
        self.quick_menu.note_requested.connect(self.open_note_prompt)
        self.quick_menu.note_history_requested.connect(self.open_note_history)
        self.quick_menu.settings_requested.connect(self.open_settings)
        QTimer.singleShot(1800, self._show_startup_quote)

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.press_position = event.globalPosition().toPoint()
            self.drag_offset = event.globalPosition().toPoint() - self.frameGeometry().topLeft()
        super().mousePressEvent(event)

    def mouseMoveEvent(self, event):
        if event.buttons() & Qt.LeftButton:
            self.move(event.globalPosition().toPoint() - self.drag_offset)
            self._reposition_bubble()
            self._reposition_menu()
        super().mouseMoveEvent(event)

    def mouseReleaseEvent(self, event):
        if event.button() == Qt.RightButton:
            self.toggle_menu()
        elif event.button() == Qt.LeftButton:
            delta = event.globalPosition().toPoint() - self.press_position
            if delta.manhattanLength() < 6:
                self.toggle_menu()
            else:
                self._persist_window_position()
        self.drag_offset = QPoint()
        self.press_position = QPoint()
        super().mouseReleaseEvent(event)

    def mouseDoubleClickEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.manual_bell()
        super().mouseDoubleClickEvent(event)

    def toggle_menu(self):
        if self.quick_menu.isVisible():
            self.quick_menu.hide()
            self._set_state(PetState.IDLE)
        else:
            self._reposition_menu()
            self.quick_menu.show()
            self.quick_menu.raise_()
            self._set_state(PetState.MENU_OPEN)

    def open_settings(self):
        self.quick_menu.hide()
        self.tray_panel.hide()
        self._settings_pet_was_visible = self.isVisible() and not self._user_hidden
        dialog = SettingsWindow(self.settings_store.load())
        dialog.saved.connect(self.save_settings)
        dialog.dismissed.connect(self._restore_after_settings)
        dialog.quotes_requested.connect(self.open_quote_editor)
        dialog.show()
        self.settings_window = dialog

    def open_quote_editor(self):
        if hasattr(self, "quote_editor") and self.quote_editor.isVisible():
            self.quote_editor.raise_()
            self.quote_editor.activateWindow()
            return
        self.quote_editor = QuoteEditorWindow(self.quote_store)
        self.quote_editor.show()
        self.quote_editor.raise_()

    def _restore_after_settings(self):
        if self._quitting or not self._settings_pet_was_visible:
            return
        self._user_hidden = False
        self.show()
        self.raise_()
        self.tray_panel.set_pet_visible(True)

    def save_settings(self, new_settings: dict):
        current = self.settings_store.load()
        current.update(new_settings)
        current["window_position"] = {"x": self.x(), "y": self.y()}
        self.autostart_service.set_enabled(bool(current.get("launch_at_login", False)))
        current["launch_at_login"] = self.autostart_service.is_enabled()
        self.settings_store.save(current)
        self.settings = current
        self.reminder_service.reload()
        self._apply_character_scale()
        self._apply_click_through()
        self._apply_animation_interval()

    def start_breath_session(self):
        self.quick_menu.hide()
        self.tray_panel.hide()
        self._set_state(PetState.BREATHING)
        self.breath_panel.start_session()

    def manual_bell(self):
        self.quick_menu.hide()
        self.tray_panel.hide()
        if self.bell_sound.source().isValid():
            self.bell_sound.play()
        self.reminder_service.trigger_manual("bell")

    def show_quote(self):
        self.quick_menu.hide()
        self.tray_panel.hide()
        self._show_reminder("quote")

    def _show_startup_quote(self):
        if self.isVisible() and not self._user_hidden:
            self._show_reminder("startup")

    def open_note_prompt(self):
        self.quick_menu.hide()
        self.tray_panel.hide()
        dialog = NoteCaptureDialog(self)
        if dialog.exec() == QDialog.Accepted:
            tag, text = dialog.values()
            self.note_store.add_note(tag, text)
            self._show_text(NOTE_RESPONSES.get(tag, "这一念，已经被看见了。"))

    def open_note_history(self):
        self.quick_menu.hide()
        self.tray_panel.hide()
        if hasattr(self, "note_history") and self.note_history.isVisible():
            self.note_history.reload()
            self.note_history.raise_()
            self.note_history.activateWindow()
            return
        self.note_history = NoteHistoryWindow(self.note_store)
        self.note_history.show()
        self.note_history.raise_()

    def _show_reminder(self, kind: str):
        state = PetState.MANUAL_BELL if kind == "bell" else PetState.REMINDING
        self._set_state(state)
        quote = self.quote_service.next_quote(self.settings.get("enabled_categories"))
        text = quote.get("text", "回到当下。")
        if quote.get("source"):
            text = f"{text}\n{quote['source']}"
        self._show_text(text)

    def _show_text(self, text: str):
        self.message_bubble.show_message(text, MESSAGE_DURATION_MS)
        self._reposition_bubble()
        self.repaint()
        if self.restore_timer_id is not None:
            self.killTimer(self.restore_timer_id)
        self.restore_timer_id = self.startTimer(MESSAGE_DURATION_MS)

    def timerEvent(self, event):
        if self.restore_timer_id == event.timerId():
            self.killTimer(self.restore_timer_id)
            self.restore_timer_id = None
        self._restore_idle()

    def _restore_idle(self):
        self._set_state(PetState.IDLE)

    def _set_state(self, state: PetState):
        self.state = state
        self.pose = self.animation_service.pose_for_state(state)
        self.current_frame_index = 0
        self._apply_animation_interval()
        self.update()

    def _advance_frame(self):
        frames = self.frame_animation.frames_for_pose(self.pose)
        if frames:
            self.current_frame_index = (self.current_frame_index + 1) % len(frames)
            self.update()
            return
        if self.current_frame_index != 0:
            self.current_frame_index = 0
            self.update()

    def _apply_animation_interval(self):
        interval = self._interval_for_pose(self.pose)
        if self.animation_timer.interval() != interval:
            self.animation_timer.setInterval(interval)
        if not self.animation_timer.isActive():
            self.animation_timer.start()

    def _apply_character_scale(self, initial: bool = False):
        scale = self.settings.get("character_scale", 1.0)
        try:
            scale = float(scale)
        except (TypeError, ValueError):
            scale = 1.0
        scale = max(0.5, min(scale, 2.5))
        new_size = max(int(self.base_size * scale), 64)
        old_geometry = self.geometry()
        self.resize(new_size, new_size)
        if not initial:
            self.move(old_geometry.x(), old_geometry.y())
            self._reposition_bubble()
            self._reposition_menu()
        self.update()

    def _apply_click_through(self, initial: bool = False):
        click_through = bool(self.settings.get("click_through", False))
        if hasattr(self, "tray_panel"):
            self.tray_panel.set_click_through(click_through)
        self.setAttribute(Qt.WA_TransparentForMouseEvents, click_through)
        if not initial and self.isVisible():
            self.update()
            self._reposition_bubble()
            self._reposition_menu()

    def _interval_for_pose(self, pose: str) -> int:
        defaults = {
            "idle": 300,
            "prayer": 220,
            "breathing": 380,
            "bell": 190,
        }
        configured = self.settings.get("animation_intervals_ms", {})
        interval = configured.get(pose, defaults.get(pose, 280))
        try:
            interval = int(interval)
        except (TypeError, ValueError):
            interval = defaults.get(pose, 280)
        return max(interval, 80)

    def _reposition_bubble(self):
        available = self._available_geometry()
        left_anchor = self.x() + int(self.width() * 0.28)
        left_x = left_anchor - self.message_bubble.width() + 2
        right_anchor = self.x() + int(self.width() * 0.72)
        right_x = right_anchor - 2
        if left_x >= available.left():
            bubble_x = left_x
            self.message_bubble.set_pointer_side("right")
        else:
            bubble_x = right_x
            self.message_bubble.set_pointer_side("left")
        bubble_x = max(available.left(), min(bubble_x, available.right() - self.message_bubble.width()))
        bubble_y = max(
            available.top(),
            min(self.y() + 8, available.bottom() - self.message_bubble.height()),
        )
        self.message_bubble.move(bubble_x, bubble_y)

    def _reposition_menu(self):
        available = self._available_geometry()
        right_x = self.x() + self.width() + 8
        left_x = self.x() - self.quick_menu.width() - 8
        menu_x = right_x if right_x + self.quick_menu.width() <= available.right() else left_x
        menu_x = max(available.left(), min(menu_x, available.right() - self.quick_menu.width()))
        menu_y = max(available.top(), min(self.y() + 12, available.bottom() - self.quick_menu.height()))
        self.quick_menu.move(menu_x, menu_y)

    def _persist_window_position(self):
        current = self.settings_store.load()
        current["window_position"] = {"x": self.x(), "y": self.y()}
        self.settings_store.save(current)
        self.settings = current

    def _restore_window_position(self):
        position = self.settings.get("window_position", {})
        try:
            x = int(position.get("x", 60))
            y = int(position.get("y", 520))
        except (TypeError, ValueError):
            x, y = 60, 520
        available = self._available_geometry(QPoint(x, y))
        x = max(available.left(), min(x, available.right() - self.width()))
        y = max(available.top(), min(y, available.bottom() - self.height()))
        self.move(x, y)

    def _available_geometry(self, point: QPoint | None = None) -> QRect:
        screen = QApplication.screenAt(point or self.frameGeometry().center())
        if screen is None:
            screen = QApplication.primaryScreen()
        return screen.availableGeometry()

    def _create_tray_icon(self) -> QSystemTrayIcon:
        tray = QSystemTrayIcon(self)
        tray.setIcon(self._build_tray_icon())
        tray.setToolTip("Mindful Monk")
        tray.activated.connect(self._handle_tray_activated)
        tray.show()
        return tray

    def _build_tray_icon(self) -> QIcon:
        pixmap = QPixmap(64, 64)
        pixmap.fill(Qt.transparent)
        painter = QPainter(pixmap)
        painter.setRenderHint(QPainter.Antialiasing)
        painter.setPen(Qt.NoPen)
        painter.setBrush(QColor("#efe3cd"))
        painter.drawEllipse(10, 10, 44, 44)
        painter.setBrush(QColor("#d3ad83"))
        painter.drawRoundedRect(18, 30, 28, 18, 10, 10)
        painter.setBrush(QColor("#f3d8b3"))
        painter.drawEllipse(20, 14, 24, 24)
        painter.setPen(QPen(QColor("#6e5845"), 2))
        painter.drawPoint(28, 26)
        painter.drawPoint(36, 26)
        painter.drawArc(QRect(27, 29, 10, 6), 200 * 16, 140 * 16)
        painter.end()
        return QIcon(pixmap)

    def _handle_tray_activated(self, reason: QSystemTrayIcon.ActivationReason):
        if reason in (QSystemTrayIcon.Trigger, QSystemTrayIcon.Context):
            if self.tray_panel.isVisible():
                self.tray_panel.hide()
            else:
                self._position_tray_panel()
                self.tray_panel.show()
                self.tray_panel.raise_()

    def _position_tray_panel(self):
        geometry = self.tray_icon.geometry()
        screen = QApplication.screenAt(geometry.center()) or QApplication.primaryScreen()
        available = screen.availableGeometry()
        self.tray_panel.adjustSize()
        if geometry.isValid():
            x = geometry.center().x() - self.tray_panel.width() // 2
            y = geometry.bottom() + 6
        else:
            x = available.right() - self.tray_panel.width() - 12
            y = available.top() + 12
        x = max(available.left(), min(x, available.right() - self.tray_panel.width()))
        y = max(available.top(), min(y, available.bottom() - self.tray_panel.height()))
        self.tray_panel.move(x, y)

    def _toggle_visibility(self):
        self.tray_panel.hide()
        if self.isVisible():
            self.quick_menu.hide()
            self.message_bubble.dismiss_message()
            self.hide()
            self._user_hidden = True
            self.tray_panel.set_pet_visible(False)
        else:
            self._user_hidden = False
            self.show()
            self.raise_()
            self.tray_panel.set_pet_visible(True)

    def _quit_from_tray(self):
        self._quitting = True
        self._persist_window_position()
        self.tray_icon.hide()
        self.tray_panel.close()
        self.close()
        QApplication.quit()

    def _toggle_click_through(self, checked: bool):
        current = self.settings_store.load()
        current["click_through"] = bool(checked)
        current["window_position"] = {"x": self.x(), "y": self.y()}
        self.settings_store.save(current)
        self.settings = current
        self._apply_click_through()

    def closeEvent(self, event):
        self._persist_window_position()
        if not self._quitting:
            event.ignore()
            self.quick_menu.hide()
            self.message_bubble.dismiss_message()
            self.hide()
            self._user_hidden = True
            if hasattr(self, "tray_panel"):
                self.tray_panel.set_pet_visible(False)
            return
        if hasattr(self, "tray_icon"):
            self.tray_icon.hide()
        self.message_bubble.close()
        self.quick_menu.close()
        self.breath_panel.close()
        self.tray_panel.close()
        if hasattr(self, "quote_editor"):
            self.quote_editor.close()
        if hasattr(self, "note_history"):
            self.note_history.close()
        super().closeEvent(event)

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        if self._draw_frame_asset(painter):
            return
        self._draw_shadow(painter)
        self._draw_lotus(painter)
        self._draw_monk(painter, self.pose)

    def _draw_frame_asset(self, painter: QPainter) -> bool:
        frames = self.frame_animation.frames_for_pose(self.pose)
        if not frames:
            return False
        frame = frames[self.current_frame_index % len(frames)]
        scaled = frame.scaled(
            self.size(),
            Qt.KeepAspectRatio,
            Qt.SmoothTransformation,
        )
        x = (self.width() - scaled.width()) // 2
        y = (self.height() - scaled.height()) // 2
        if self.settings.get("golden_aura_enabled", True):
            self._draw_golden_aura(painter, x, y, scaled.size())
        painter.drawPixmap(x, y, scaled)
        return True

    def _draw_golden_aura(self, painter: QPainter, x: int, y: int, size):
        center = QPointF(x + size.width() * 0.5, y + size.height() * 0.45)
        radius = size.width() * 0.38
        gradient = QRadialGradient(center, radius)
        gradient.setColorAt(0.0, QColor(235, 195, 105, 38))
        gradient.setColorAt(0.62, QColor(226, 181, 78, 16))
        gradient.setColorAt(1.0, QColor(224, 174, 67, 0))
        painter.save()
        painter.setPen(Qt.NoPen)
        painter.setBrush(gradient)
        painter.drawEllipse(QRectF(center.x() - radius, center.y() - radius, radius * 2, radius * 2))
        painter.restore()

    def _draw_shadow(self, painter: QPainter):
        painter.setPen(Qt.NoPen)
        painter.setBrush(QColor(0, 0, 0, 28))
        painter.drawEllipse(QRect(28, 128, 104, 18))

    def _draw_lotus(self, painter: QPainter):
        painter.setPen(Qt.NoPen)
        painter.setBrush(QColor("#b5c6af"))
        painter.drawEllipse(QRect(38, 108, 86, 26))

    def _draw_monk(self, painter: QPainter, pose: str):
        robe = QColor("#d7b48a")
        skin = QColor("#f0d7b7")
        outline = QPen(QColor("#6e5845"), 2)
        painter.setPen(outline)

        painter.setBrush(robe)
        painter.drawRoundedRect(QRect(42, 56, 78, 62), 28, 28)

        painter.setBrush(skin)
        painter.drawEllipse(QRect(54, 18, 54, 54))

        if pose == "prayer":
            self._draw_prayer_hands(painter)
        elif pose == "breathing":
            self._draw_breathing_hands(painter)
        elif pose == "bell":
            self._draw_bell_pose(painter)
        else:
            self._draw_idle_hands(painter)

        self._draw_face(painter, pose)
        self._draw_beads(painter)

    def _draw_face(self, painter: QPainter, pose: str):
        painter.setPen(QPen(QColor("#5f4938"), 2))
        if pose == "breathing":
            painter.drawLine(70, 44, 78, 44)
            painter.drawLine(84, 44, 92, 44)
        else:
            painter.drawPoint(74, 44)
            painter.drawPoint(88, 44)
        painter.drawArc(QRect(72, 50, 18, 10), 200 * 16, 140 * 16)

    def _draw_idle_hands(self, painter: QPainter):
        painter.setBrush(QColor("#f0d7b7"))
        painter.drawEllipse(QRect(44, 80, 20, 18))
        painter.drawEllipse(QRect(98, 80, 20, 18))

    def _draw_prayer_hands(self, painter: QPainter):
        painter.setBrush(QColor("#f0d7b7"))
        painter.drawRoundedRect(QRect(71, 74, 18, 28), 8, 8)

    def _draw_breathing_hands(self, painter: QPainter):
        painter.setBrush(QColor("#f0d7b7"))
        painter.drawRoundedRect(QRect(62, 86, 38, 12), 6, 6)

    def _draw_bell_pose(self, painter: QPainter):
        painter.setBrush(QColor("#f0d7b7"))
        painter.drawEllipse(QRect(48, 82, 20, 18))
        painter.drawEllipse(QRect(92, 72, 18, 18))
        painter.setBrush(QColor("#8a5d3b"))
        painter.drawEllipse(QRect(96, 94, 22, 16))
        painter.drawLine(102, 80, 104, 95)

    def _draw_beads(self, painter: QPainter):
        painter.setBrush(QColor("#7d6048"))
        for index in range(5):
            painter.drawEllipse(QRect(42 + index * 8, 106, 7, 7))
