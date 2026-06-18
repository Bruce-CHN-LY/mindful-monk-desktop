from __future__ import annotations

from collections import Counter
from datetime import datetime, timedelta

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QComboBox,
    QDialog,
    QDialogButtonBox,
    QHBoxLayout,
    QLabel,
    QListWidget,
    QListWidgetItem,
    QPlainTextEdit,
    QPushButton,
    QVBoxLayout,
    QWidget,
)


NOTE_TAGS = [
    ("急", "着急"),
    ("烦", "烦躁"),
    ("散", "散乱"),
    ("执", "放不下"),
    ("怕", "害怕"),
    ("倦", "疲倦"),
    ("乱", "混乱"),
    ("紧", "紧绷"),
    ("稳", "安稳"),
    ("喜", "欢喜"),
    ("念", "惦念"),
    ("感", "感激"),
]

NOTE_RESPONSES = {
    "急": "急也被看见了。先缓一口气，再走下一步。",
    "烦": "不必立刻赶走烦躁，先让它有一点空处。",
    "散": "心散了并不要紧，觉察就是归来的开始。",
    "执": "能看见放不下，手心便已经松了一点。",
    "怕": "怕也可以同行。此刻，只照顾眼前这一小步。",
    "倦": "倦不是过错。先歇一歇，也是在照顾此心。",
    "乱": "乱时不求想通一切，只先安住这一口呼吸。",
    "紧": "肩颈松一点，牙关松一点，让身体先知道安全。",
    "稳": "记得这一刻的安稳，它也是你走过的路。",
    "喜": "欢喜已被记下。不攥紧它，静静领受就好。",
    "念": "惦念说明心有所系，看见它，不必被它牵走。",
    "感": "这一份感激已落在心里，愿它慢慢生长。",
}

WINDOW_STYLE = """
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


class NoteCaptureDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("记一念")
        self.resize(380, 230)
        self.setStyleSheet(WINDOW_STYLE)

        prompt = QLabel("此刻心里是什么样子？")
        prompt.setStyleSheet("font-size: 15px; font-weight: 600;")

        self.tag = QComboBox()
        for key, label in NOTE_TAGS:
            self.tag.addItem(f"{key} · {label}", key)

        self.text = QPlainTextEdit()
        self.text.setPlaceholderText("也可以写下一句话（选填，最多 200 字）")
        self.text.setMaximumHeight(88)

        hint = QLabel("只为看见，不作评判。记录只保存在这台电脑上。")
        hint.setStyleSheet("color: #786856;")
        hint.setWordWrap(True)

        buttons = QDialogButtonBox(QDialogButtonBox.Cancel | QDialogButtonBox.Save)
        buttons.button(QDialogButtonBox.Save).setText("记下")
        buttons.button(QDialogButtonBox.Cancel).setText("暂不记")
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(18, 18, 18, 18)
        layout.setSpacing(10)
        layout.addWidget(prompt)
        layout.addWidget(self.tag)
        layout.addWidget(self.text)
        layout.addWidget(hint)
        layout.addWidget(buttons)

    def values(self) -> tuple[str, str]:
        return self.tag.currentData(), self.text.toPlainText().strip()[:200]


class NoteHistoryWindow(QWidget):
    def __init__(self, note_store, parent=None):
        super().__init__(parent)
        self.note_store = note_store
        self.setWindowTitle("念迹")
        self.resize(460, 500)
        self.setStyleSheet(WINDOW_STYLE)

        title = QLabel("念迹")
        title.setStyleSheet("font-size: 18px; font-weight: 600;")
        subtitle = QLabel("念起，知念；念去，不追。这里留下的只是走过的痕迹。")
        subtitle.setStyleSheet("color: #786856;")
        subtitle.setWordWrap(True)

        self.summary = QLabel()
        self.summary.setWordWrap(True)
        self.list = QListWidget()
        self.list.currentItemChanged.connect(self._update_delete_state)
        self.empty = QLabel("还没有念迹。下一次看见心动时，再来记一笔。")
        self.empty.setAlignment(Qt.AlignCenter)
        self.empty.setStyleSheet("color: #8b7b68; padding: 28px;")

        self.delete_button = QPushButton("删除所选记录")
        self.delete_button.setEnabled(False)
        self.delete_button.clicked.connect(self._delete_selected)
        close_button = QPushButton("合上")
        close_button.clicked.connect(self.close)

        footer = QHBoxLayout()
        footer.addWidget(self.delete_button)
        footer.addStretch(1)
        footer.addWidget(close_button)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(18, 18, 18, 18)
        layout.setSpacing(10)
        layout.addWidget(title)
        layout.addWidget(subtitle)
        layout.addWidget(self.summary)
        layout.addWidget(self.list, 1)
        layout.addWidget(self.empty, 1)
        layout.addLayout(footer)
        self.reload()

    def reload(self):
        notes = self.note_store.load_notes()
        self.list.clear()
        for index in range(len(notes) - 1, -1, -1):
            note = notes[index]
            timestamp = self._format_timestamp(note.get("timestamp"))
            tag = str(note.get("tag", "念"))
            text = str(note.get("text", "")).strip()
            label = f"{timestamp}   [{tag}]"
            if text:
                label += f"\n{text}"
            item = QListWidgetItem(label)
            item.setData(Qt.UserRole, index)
            self.list.addItem(item)

        self._set_summary(notes)
        has_notes = bool(notes)
        self.list.setVisible(has_notes)
        self.empty.setVisible(not has_notes)
        self.delete_button.setEnabled(False)

    def _set_summary(self, notes: list[dict]):
        if not notes:
            self.summary.setText("共 0 念")
            return
        now = datetime.now()
        week_ago = now - timedelta(days=7)
        recent = sum(
            1
            for note in notes
            if (parsed := self._parse_timestamp(note.get("timestamp"))) and parsed >= week_ago
        )
        counts = Counter(str(note.get("tag", "念")) for note in notes)
        common = "  ".join(f"{tag} {count}" for tag, count in counts.most_common(4))
        self.summary.setText(f"共 {len(notes)} 念 · 近 7 日 {recent} 念\n{common}")

    def _delete_selected(self):
        item = self.list.currentItem()
        if item is None:
            return
        if self.note_store.delete_note_at(item.data(Qt.UserRole)):
            self.reload()

    def _update_delete_state(self, current, _previous):
        self.delete_button.setEnabled(current is not None)

    @staticmethod
    def _parse_timestamp(value) -> datetime | None:
        try:
            return datetime.fromisoformat(str(value))
        except (TypeError, ValueError):
            return None

    @classmethod
    def _format_timestamp(cls, value) -> str:
        parsed = cls._parse_timestamp(value)
        return parsed.strftime("%m月%d日 %H:%M") if parsed else "时间不详"
