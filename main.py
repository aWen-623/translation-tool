"""Translation Tool — Quick translation panel with global hotkey.

Usage:
    python main.py
    python main.py --hotkey "ctrl+shift+t"

Press the hotkey to show/hide the translation panel.
Close window to minimize to system tray.
"""

import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import keyboard
from PyQt5.QtWidgets import QApplication
from PyQt5.QtCore import QTimer

import config
from ui.main_window import MainWindow
from ui.tray import TrayIcon


def main():
    config.init()

    app = QApplication(sys.argv)
    app.setQuitOnLastWindowClosed(False)

    # Parse custom hotkey
    hotkey = config.get("hotkey")
    if "--hotkey" in sys.argv:
        idx = sys.argv.index("--hotkey")
        if idx + 1 < len(sys.argv):
            hotkey = sys.argv[idx + 1]

    # Create window
    window = MainWindow()

    # System tray
    tray = TrayIcon(window)
    tray.show()

    # Register global hotkey
    keyboard.add_hotkey(hotkey, lambda: QTimer.singleShot(0, window.toggle_visibility))

    print(f"Translate ready. Press {hotkey} to toggle.")
    print("Close window to minimize to tray. Right-click tray icon to quit.")

    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
