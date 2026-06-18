from PySide6.QtCore import QTimer, Qt, Signal
from PySide6.QtWidgets import QLabel, QProgressBar, QPushButton, QVBoxLayout, QWidget


class BreathPanel(QWidget):
    finished = Signal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("观息")
        self.setWindowFlags(Qt.Tool | Qt.WindowStaysOnTopHint)
        self.setFixedSize(280, 220)
        self.setStyleSheet(
            """
            QWidget { background: #f4eddf; color: #4c3e31; }
            QLabel#title { font-size: 18px; font-weight: 600; }
            QLabel#phase { font-size: 28px; color: #806a52; }
            QProgressBar { border: 0; background: #e4d7c2; border-radius: 4px; height: 8px; }
            QProgressBar::chunk { background: #9eaf91; border-radius: 4px; }
            QPushButton { border: 0; color: #786856; padding: 8px; }
            """
        )
        self.remaining_seconds = 60
        self.total_seconds = 60

        self.title = QLabel("只观这一口气")
        self.title.setObjectName("title")
        self.title.setAlignment(Qt.AlignCenter)
        self.phase = QLabel("自然呼吸")
        self.phase.setObjectName("phase")
        self.phase.setAlignment(Qt.AlignCenter)
        self.clock = QLabel("01:00")
        self.clock.setAlignment(Qt.AlignCenter)
        self.progress = QProgressBar()
        self.progress.setTextVisible(False)
        self.progress.setRange(0, 60)
        self.cancel = QPushButton("先到这里")
        self.cancel.clicked.connect(self.finish_session)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(28, 24, 28, 18)
        layout.setSpacing(12)
        layout.addWidget(self.title)
        layout.addWidget(self.phase)
        layout.addWidget(self.clock)
        layout.addWidget(self.progress)
        layout.addWidget(self.cancel)

        self.timer = QTimer(self)
        self.timer.timeout.connect(self._tick)

    def start_session(self, seconds: int = 60):
        self.total_seconds = max(int(seconds), 1)
        self.remaining_seconds = self.total_seconds
        self.progress.setRange(0, self.total_seconds)
        self.progress.setValue(0)
        self._update_display()
        self.show()
        self.raise_()
        self.activateWindow()
        self.timer.start(1000)

    def _tick(self):
        self.remaining_seconds -= 1
        self._update_display()
        if self.remaining_seconds <= 0:
            self.finish_session()

    def _update_display(self):
        elapsed = self.total_seconds - self.remaining_seconds
        phases = ("吸气", "吸气", "安住", "呼气", "呼气", "呼气")
        self.phase.setText(phases[elapsed % len(phases)])
        minutes, seconds = divmod(max(self.remaining_seconds, 0), 60)
        self.clock.setText(f"{minutes:02d}:{seconds:02d}")
        self.progress.setValue(elapsed)

    def finish_session(self):
        if not self.timer.isActive() and not self.isVisible():
            return
        self.timer.stop()
        self.hide()
        self.finished.emit()

    def closeEvent(self, event):
        was_active = self.timer.isActive()
        self.timer.stop()
        if was_active:
            self.finished.emit()
        super().closeEvent(event)
