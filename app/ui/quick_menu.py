from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import QPushButton, QVBoxLayout, QWidget


class QuickMenu(QWidget):
    quote_requested = Signal()
    breathe_requested = Signal()
    bell_requested = Signal()
    note_requested = Signal()
    note_history_requested = Signal()
    settings_requested = Signal()

    def __init__(self, parent=None):
        super().__init__(parent, Qt.Tool | Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint)
        self.setWindowTitle("Mindful Monk")
        self.setStyleSheet(
            """
            QWidget { background: #f2eadc; border: 1px solid #d7c6af; border-radius: 16px; }
            QPushButton {
                background: #fffaf3;
                border: none;
                border-radius: 12px;
                color: #4c3e31;
                min-height: 36px;
                padding: 0 12px;
                text-align: left;
            }
            QPushButton:hover { background: #ede0ca; }
            """
        )

        layout = QVBoxLayout(self)
        layout.setContentsMargins(12, 12, 12, 12)
        layout.setSpacing(8)

        quote = QPushButton("听一句偈语")
        breathe = QPushButton("观息 1 分钟")
        bell = QPushButton("唤钟一下")
        note = QPushButton("记一念")
        note_history = QPushButton("看念迹")
        settings = QPushButton("设置")

        quote.clicked.connect(self.quote_requested.emit)
        breathe.clicked.connect(self.breathe_requested.emit)
        bell.clicked.connect(self.bell_requested.emit)
        note.clicked.connect(self.note_requested.emit)
        note_history.clicked.connect(self.note_history_requested.emit)
        settings.clicked.connect(self.settings_requested.emit)

        for button in (quote, breathe, bell, note, note_history, settings):
            layout.addWidget(button)
