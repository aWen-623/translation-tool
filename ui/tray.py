"""系统托盘图标。"""

from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QSystemTrayIcon, QMenu, QApplication
from PyQt5.QtGui import QIcon, QPixmap, QPainter, QColor, QFont


def _create_icon() -> QIcon:
    px = QPixmap(32, 32)
    px.fill(QColor(0, 0, 0, 0))
    painter = QPainter(px)
    painter.setRenderHint(QPainter.Antialiasing)
    painter.setPen(Qt.NoPen)
    painter.setBrush(QColor("#c8a55a"))
    painter.drawEllipse(2, 2, 28, 28)
    font = QFont("Segoe UI", 16, QFont.Bold)
    painter.setFont(font)
    painter.setPen(QColor("#0f0f14"))
    painter.drawText(px.rect(), Qt.AlignCenter, "T")
    painter.end()
    return QIcon(px)


class TrayIcon(QSystemTrayIcon):
    def __init__(self, main_window, parent=None):
        super().__init__(parent)
        self.main_window = main_window
        self.setIcon(_create_icon())
        self.setToolTip("翻译工具")

        menu = QMenu()
        show_action = menu.addAction("显示主窗口")
        show_action.triggered.connect(self._show_window)
        menu.addSeparator()
        quit_action = menu.addAction("退出程序")
        quit_action.triggered.connect(self._quit)
        self.setContextMenu(menu)

        self.activated.connect(self._on_activated)

    def _on_activated(self, reason):
        if reason == QSystemTrayIcon.Trigger:
            self._show_window()

    def _show_window(self):
        self.main_window.toggle_visibility()

    def _quit(self):
        self.hide()
        QApplication.quit()
