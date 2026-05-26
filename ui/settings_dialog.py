"""设置对话框 — 快捷键配置与自动复制开关。"""

from PyQt5.QtCore import Qt, QRectF
from PyQt5.QtGui import QCursor, QPainter, QPainterPath, QColor, QPen, QBrush
from PyQt5.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QWidget,
    QCheckBox, QPushButton, QKeySequenceEdit,
)

import config


class SettingsDialog(QDialog):
    def __init__(self, parent=None, on_hotkey_changed=None):
        super().__init__(parent)
        self.on_hotkey_changed = on_hotkey_changed
        self._init_ui()
        self._load_values()

    def _init_ui(self):
        self.setObjectName("SettingsDialog")
        self.setFixedSize(420, 340)
        self.setWindowFlags(
            Qt.Dialog | Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint
        )
        self.setAttribute(Qt.WA_TranslucentBackground, True)

        # 容器
        self._container = QWidget(self)
        self._container.setObjectName("SettingsDialog")
        self._container.setGeometry(8, 8, 404, 324)

        layout = QVBoxLayout(self._container)
        layout.setContentsMargins(28, 24, 28, 28)
        layout.setSpacing(0)

        # 标题栏
        title_bar = QHBoxLayout()
        title = QLabel("设置")
        title.setObjectName("SettingsTitle")
        title_bar.addWidget(title)
        title_bar.addStretch()

        close_btn = QPushButton("关闭")
        close_btn.setObjectName("UtilBtn")
        close_btn.setCursor(QCursor(Qt.PointingHandCursor))
        close_btn.clicked.connect(self.reject)
        title_bar.addWidget(close_btn)
        layout.addLayout(title_bar)

        layout.addSpacing(28)

        # 快捷键
        hk_label = QLabel("全局唤醒快捷键")
        hk_label.setObjectName("SettingsLabel")
        layout.addWidget(hk_label)
        layout.addSpacing(8)

        self.hotkey_input = QKeySequenceEdit()
        self.hotkey_input.setObjectName("SettingsInput")
        self.hotkey_input.setFixedHeight(42)
        self.hotkey_input.setKeySequence(config.get("hotkey"))
        layout.addWidget(self.hotkey_input)

        layout.addSpacing(8)

        hint = QLabel("请按下你想要的快捷键组合")
        hint.setObjectName("StatusLabel")
        layout.addWidget(hint)

        layout.addSpacing(24)

        # 自动复制
        self.auto_copy_check = QCheckBox("翻译完成后自动复制结果")
        self.auto_copy_check.setObjectName("SettingsCheck")
        self.auto_copy_check.setChecked(config.get("auto_copy"))
        layout.addWidget(self.auto_copy_check)

        layout.addStretch()

        # 按钮行
        btn_row = QHBoxLayout()
        btn_row.setSpacing(12)
        btn_row.addStretch()

        cancel_btn = QPushButton("取消")
        cancel_btn.setObjectName("SettingsCancelBtn")
        cancel_btn.setCursor(QCursor(Qt.PointingHandCursor))
        cancel_btn.clicked.connect(self.reject)
        btn_row.addWidget(cancel_btn)

        save_btn = QPushButton("保存")
        save_btn.setObjectName("SettingsSaveBtn")
        save_btn.setCursor(QCursor(Qt.PointingHandCursor))
        save_btn.clicked.connect(self._save_settings)
        btn_row.addWidget(save_btn)

        layout.addLayout(btn_row)

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        path = QPainterPath()
        path.addRoundedRect(QRectF(8, 8, self.width() - 16, self.height() - 16), 14, 14)
        painter.fillPath(path, QBrush(QColor("#0f0f14")))
        pen = QPen(QColor("#2a2a38"))
        pen.setWidth(1)
        painter.setPen(pen)
        painter.drawPath(path)
        painter.end()

    def _load_values(self):
        self.hotkey_input.setKeySequence(config.get("hotkey"))
        self.auto_copy_check.setChecked(config.get("auto_copy"))

    def _save_settings(self):
        seq = self.hotkey_input.keySequence()
        hotkey_str = seq.toString().lower().replace("+", "+") if not seq.isEmpty() else config.get("hotkey")

        old_hotkey = config.get("hotkey")
        config.set("hotkey", hotkey_str)
        config.set("auto_copy", self.auto_copy_check.isChecked())

        if hotkey_str != old_hotkey and self.on_hotkey_changed:
            self.on_hotkey_changed(old_hotkey, hotkey_str)

        self.accept()
