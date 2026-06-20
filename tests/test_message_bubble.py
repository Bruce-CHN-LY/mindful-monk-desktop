from unittest.mock import patch

from PySide6.QtCore import Qt
from PySide6.QtWidgets import QApplication

from app.ui.message_bubble import MessageBubble


def test_message_bubble_is_configured_not_to_activate_app():
    app = QApplication.instance() or QApplication([])
    bubble = MessageBubble()

    assert bubble.testAttribute(Qt.WA_ShowWithoutActivating)
    assert bubble.windowFlags() & Qt.WindowDoesNotAcceptFocus

    bubble.close()
    app.processEvents()


def test_showing_a_message_does_not_show_window_again():
    app = QApplication.instance() or QApplication([])
    bubble = MessageBubble()

    with patch.object(bubble, "show") as show:
        bubble.show_message("继续手头的事。", 1000)

    show.assert_not_called()
    bubble.dismiss_message()
    bubble.close()
    app.processEvents()
