from PySide6.QtCore import QLockFile, QStandardPaths
from PySide6.QtWidgets import QApplication

from app.ui.desktop_pet import DesktopPetWindow


def run() -> int:
    app = QApplication([])
    app.setApplicationName("Mindful Monk")
    app.setApplicationDisplayName("一念小沙弥")
    app.setOrganizationName("Mindful Monk")
    app.setQuitOnLastWindowClosed(False)

    lock_path = QStandardPaths.writableLocation(QStandardPaths.TempLocation) + "/mindful-monk.lock"
    instance_lock = QLockFile(lock_path)
    instance_lock.setStaleLockTime(0)
    if not instance_lock.tryLock(100):
        return 0

    window = DesktopPetWindow()
    window.show()
    return app.exec()
