from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import QPushButton, QVBoxLayout, QWidget


class TrayPanel(QWidget):
    visibility_requested = Signal()
    click_through_requested = Signal(bool)
    quote_requested = Signal()
    bell_requested = Signal()
    note_requested = Signal()
    note_history_requested = Signal()
    settings_requested = Signal()
    quit_requested = Signal()

    def __init__(self):
        super().__init__(None, Qt.Tool | Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint)
        self.setFixedWidth(190)
        self.setStyleSheet(
            """
            QWidget { background: #f2eadc; border: 1px solid #d7c6af; border-radius: 14px; }
            QPushButton {
                background: #fffaf3; border: none; border-radius: 10px;
                color: #4c3e31; min-height: 32px; padding: 0 10px; text-align: left;
            }
            QPushButton:hover { background: #ede0ca; }
            QPushButton:checked { background: #dfd2bc; }
            """
        )

        self.visibility_button = QPushButton("隐藏小沙弥")
        self.click_through_button = QPushButton("点击穿透")
        self.click_through_button.setCheckable(True)
        quote_button = QPushButton("听一句偈语")
        bell_button = QPushButton("唤钟一下")
        note_button = QPushButton("记一念")
        note_history_button = QPushButton("看念迹")
        settings_button = QPushButton("设置")
        quit_button = QPushButton("退出")

        self.visibility_button.clicked.connect(self.visibility_requested.emit)
        self.click_through_button.toggled.connect(self.click_through_requested.emit)
        quote_button.clicked.connect(self.quote_requested.emit)
        bell_button.clicked.connect(self.bell_requested.emit)
        note_button.clicked.connect(self.note_requested.emit)
        note_history_button.clicked.connect(self.note_history_requested.emit)
        settings_button.clicked.connect(self.settings_requested.emit)
        quit_button.clicked.connect(self.quit_requested.emit)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(6)
        for button in (
            self.visibility_button,
            self.click_through_button,
            quote_button,
            bell_button,
            note_button,
            note_history_button,
            settings_button,
            quit_button,
        ):
            layout.addWidget(button)

    def set_pet_visible(self, visible: bool):
        self.visibility_button.setText("隐藏小沙弥" if visible else "显示小沙弥")

    def set_click_through(self, enabled: bool):
        self.click_through_button.blockSignals(True)
        self.click_through_button.setChecked(enabled)
        self.click_through_button.blockSignals(False)
