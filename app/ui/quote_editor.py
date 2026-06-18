from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QComboBox,
    QHBoxLayout,
    QLabel,
    QListWidget,
    QListWidgetItem,
    QPlainTextEdit,
    QPushButton,
    QVBoxLayout,
    QWidget,
)


CATEGORY_LABELS = {
    "mind": "观心念",
    "breath": "观呼吸",
    "compassion": "慈悲安住",
    "morning_night": "晨昏偈语",
}


class QuoteEditorWindow(QWidget):
    def __init__(self, quote_store, parent=None):
        super().__init__(parent)
        self.quote_store = quote_store
        self.setWindowTitle("管理偈语")
        self.resize(440, 460)
        self.setStyleSheet(
            """
            QWidget { background: #f4eddf; color: #4c3e31; }
            QListWidget, QPlainTextEdit, QComboBox {
                background: #fffaf3; border: 1px solid #d7c6af; border-radius: 8px;
                padding: 6px;
            }
            QPushButton {
                background: #fffaf3; border: 1px solid #d7c6af; border-radius: 8px;
                min-height: 30px; padding: 0 10px;
            }
            QPushButton:hover { background: #ede0ca; }
            QPushButton:disabled { color: #aa9d8d; background: #eee6d9; }
            """
        )

        self.list = QListWidget()
        self.list.currentItemChanged.connect(self._update_delete_state)

        self.text = QPlainTextEdit()
        self.text.setPlaceholderText("写下一句温柔、简短的提醒……")
        self.text.setMaximumHeight(76)

        self.category = QComboBox()
        for key, label in CATEGORY_LABELS.items():
            self.category.addItem(label, key)

        add_button = QPushButton("添加偈语")
        add_button.clicked.connect(self._add_quote)
        self.delete_button = QPushButton("删除所选自定义偈语")
        self.delete_button.clicked.connect(self._delete_selected)
        self.delete_button.setEnabled(False)

        self.hint = QLabel("内置偈语会保留；你添加的偈语可以随时删除。")
        self.hint.setStyleSheet("color: #786856;")
        self.hint.setWordWrap(True)

        form = QHBoxLayout()
        form.addWidget(self.category)
        form.addWidget(add_button)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(18, 18, 18, 18)
        layout.setSpacing(10)
        layout.addWidget(QLabel("偈语库"))
        layout.addWidget(self.list, 1)
        layout.addWidget(self.text)
        layout.addLayout(form)
        layout.addWidget(self.delete_button)
        layout.addWidget(self.hint)
        self._reload()

    def _reload(self):
        self.list.clear()
        custom_ids = {quote.get("id") for quote in self.quote_store.load_custom_quotes()}
        for quote in self.quote_store.load_quotes():
            category = CATEGORY_LABELS.get(quote.get("category"), "其他")
            custom = quote.get("id") in custom_ids
            prefix = "自定义" if custom else quote.get("source", "内置")
            item = QListWidgetItem(f"[{prefix} · {category}]  {quote.get('text', '')}")
            reference = quote.get("reference")
            if reference:
                item.setToolTip(reference)
            item.setData(Qt.UserRole, quote.get("id"))
            item.setData(Qt.UserRole + 1, custom)
            self.list.addItem(item)

    def _add_quote(self):
        text = self.text.toPlainText().strip()
        if not text:
            self.hint.setText("先写下一句偈语，再点击添加。")
            return
        self.quote_store.add_quote(text, self.category.currentData())
        self.text.clear()
        self.hint.setText("已加入偈语库。")
        self._reload()
        self.list.scrollToBottom()

    def _delete_selected(self):
        item = self.list.currentItem()
        if item is None or not item.data(Qt.UserRole + 1):
            return
        self.quote_store.delete_quote(item.data(Qt.UserRole))
        self.hint.setText("已删除这句自定义偈语。")
        self._reload()

    def _update_delete_state(self, current, _previous):
        self.delete_button.setEnabled(bool(current and current.data(Qt.UserRole + 1)))
