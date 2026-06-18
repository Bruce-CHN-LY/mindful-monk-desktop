from pathlib import Path

from PySide6.QtCore import QPoint
from PySide6.QtGui import QColor, QImage

from app.core.frame_animation import FrameAnimationService


def test_frame_animation_returns_empty_for_missing_pose(tmp_path: Path):
    service = FrameAnimationService(tmp_path)
    assert service.frames_for_pose("idle") == []


def test_anchor_uses_lower_figure_bounds():
    image = QImage(100, 100, QImage.Format_RGBA8888)
    image.fill(QColor(0, 0, 0, 0))
    for y in range(80, 95):
        for x in range(30, 70):
            image.setPixelColor(x, y, QColor(255, 255, 255, 255))

    assert FrameAnimationService._anchor_for_image(image) == QPoint(50, 95)
