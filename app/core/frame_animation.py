from __future__ import annotations

from pathlib import Path
from statistics import median

from PySide6.QtCore import QPoint, Qt
from PySide6.QtGui import QImage, QPainter, QPixmap

from app.constants import MONK_ASSETS_DIR


class FrameAnimationService:
    def __init__(self, base_dir: Path | None = None):
        self.base_dir = base_dir or MONK_ASSETS_DIR
        self._cache: dict[str, list[QPixmap]] = {}

    def frames_for_pose(self, pose: str) -> list[QPixmap]:
        if pose not in self._cache:
            self._cache[pose] = self._load_pose_frames(pose)
        return self._cache[pose]

    def reload(self):
        self._cache.clear()

    def _load_pose_frames(self, pose: str) -> list[QPixmap]:
        pose_dir = self.base_dir / pose
        if not pose_dir.exists():
            return []

        frames: list[QPixmap] = []
        anchors: list[QPoint] = []
        for path in sorted(pose_dir.glob("*.png")):
            pixmap = QPixmap(str(path))
            if not pixmap.isNull():
                frames.append(pixmap)
                anchors.append(self._anchor_for_image(pixmap.toImage()))
        if not frames:
            return []

        target = QPoint(
            round(median(anchor.x() for anchor in anchors)),
            round(median(anchor.y() for anchor in anchors)),
        )
        return [self._shift_frame(frame, target - anchor) for frame, anchor in zip(frames, anchors)]

    @staticmethod
    def _anchor_for_image(image: QImage) -> QPoint:
        rgba = image.convertToFormat(QImage.Format_RGBA8888)
        width, height = rgba.width(), rgba.height()
        data = bytes(rgba.constBits())
        start_y = int(height * 0.72)
        min_x, max_x, bottom = width, -1, -1

        for y in range(start_y, height):
            row = y * width * 4
            for x in range(width):
                if data[row + x * 4 + 3] > 12:
                    min_x = min(min_x, x)
                    max_x = max(max_x, x)
                    bottom = y + 1

        if max_x < min_x:
            return QPoint(width // 2, height)
        return QPoint(round((min_x + max_x + 1) / 2), bottom)

    @staticmethod
    def _shift_frame(frame: QPixmap, offset: QPoint) -> QPixmap:
        if offset.isNull():
            return frame
        shifted = QPixmap(frame.size())
        shifted.fill(Qt.transparent)
        painter = QPainter(shifted)
        painter.drawPixmap(offset, frame)
        painter.end()
        return shifted
