from PySide6.QtCore import QRectF, QTimer, Qt
from PySide6.QtGui import QColor, QFont, QPainter, QPainterPath, QPen
from PySide6.QtWidgets import QLabel, QWidget


class MessageBubble(QWidget):
    def __init__(self, parent=None):
        super().__init__(
            parent,
            Qt.ToolTip
            | Qt.FramelessWindowHint
            | Qt.WindowStaysOnTopHint
            | Qt.WindowDoesNotAcceptFocus,
        )
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.setAttribute(Qt.WA_TransparentForMouseEvents)
        self.pointer_side = "right"
        self.label = QLabel("", self)
        self.label.setWordWrap(True)
        self.label.setAlignment(Qt.AlignCenter)
        font = QFont()
        font.setPointSize(10)
        self.label.setFont(font)
        self.label.setStyleSheet("color: #3b3128; padding: 8px;")
        self.hide_timer = QTimer(self)
        self.hide_timer.setSingleShot(True)
        self.hide_timer.timeout.connect(self.hide)
        self.resize(210, 72)
        self.hide()

    def resizeEvent(self, event):
        self._layout_label()
        super().resizeEvent(event)

    def _layout_label(self):
        if self.pointer_side == "right":
            self.label.setGeometry(self.rect().adjusted(6, 5, -14, -5))
        else:
            self.label.setGeometry(self.rect().adjusted(14, 5, -6, -5))

    def set_pointer_side(self, side: str):
        self.pointer_side = "left" if side == "left" else "right"
        self._layout_label()
        self.update()

    def show_message(self, text: str, duration_ms: int):
        self.label.setText(text)
        content_width = self.width() - 28
        content_height = self.label.heightForWidth(content_width)
        self.resize(self.width(), max(72, min(content_height + 22, 126)))
        self.show()
        self.raise_()
        self.hide_timer.start(duration_ms)

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        painter.setPen(QPen(QColor(112, 91, 67, 105), 1))
        path = QPainterPath()
        middle = self.height() * 0.52
        if self.pointer_side == "right":
            body = QRectF(2, 2, self.width() - 12, self.height() - 4)
            path.addRoundedRect(body, 14, 14)
            path.moveTo(self.width() - 10, middle - 7)
            path.lineTo(self.width() - 2, middle + 1)
            path.lineTo(self.width() - 10, middle + 7)
        else:
            body = QRectF(10, 2, self.width() - 12, self.height() - 4)
            path.addRoundedRect(body, 14, 14)
            path.moveTo(10, middle - 7)
            path.lineTo(2, middle + 1)
            path.lineTo(10, middle + 7)
        path.closeSubpath()
        painter.setBrush(QColor("#f5eee1"))
        painter.drawPath(path)
