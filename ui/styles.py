"""深色高级简约主题。

设计系统 (ui-ux-pro-max + frontend-design):
  底色:     #0f0f14
  面板:     #1a1a24
  边框:     #2a2a38
  文字:     #e8e8ec
  辅助文字: #8a8a96
  点缀:     #c8a55a (暖金)
  成功:     #5cb85c
  错误:     #e05555
  圆角:     14px
"""

MAIN = """
/* ── 窗口 ── */

QWidget#MainWindow {
    background-color: #0f0f14;
    border-radius: 14px;
}

/* ── 通用字体 ── */

QLabel {
    color: #8a8a96;
    font-size: 14px;
    font-family: "Microsoft YaHei UI", "Segoe UI", sans-serif;
}

QLabel#TitleLabel {
    font-size: 20px;
    font-weight: 600;
    color: #e8e8ec;
    letter-spacing: 1px;
}

QLabel#SectionLabel {
    font-size: 14px;
    font-weight: 600;
    color: #8a8a96;
    letter-spacing: 0.8px;
}

QLabel#StatusLabel {
    font-size: 13px;
    color: #6a6a78;
}

QLabel#StatusOk {
    font-size: 13px;
    color: #5cb85c;
    font-weight: 500;
}

QLabel#StatusError {
    font-size: 13px;
    color: #e05555;
}

QLabel#PhoneticLabel {
    font-size: 14px;
    color: #c8a55a;
    font-style: italic;
}

/* ── 下拉框 ── */

QComboBox {
    background-color: #1a1a24;
    border: 1px solid #2a2a38;
    border-radius: 10px;
    padding: 8px 14px;
    font-size: 15px;
    font-weight: 500;
    color: #e8e8ec;
    font-family: "Microsoft YaHei UI", "Segoe UI", sans-serif;
    min-height: 24px;
}

QComboBox:hover {
    border-color: #3a3a4a;
    background-color: #1e1e2a;
}

QComboBox:focus {
    border-color: #c8a55a;
}

QComboBox::drop-down {
    subcontrol-origin: padding;
    subcontrol-position: center right;
    width: 28px;
    border: none;
}

QComboBox::down-arrow {
    image: none;
    width: 0;
    height: 0;
    border-left: 5px solid transparent;
    border-right: 5px solid transparent;
    border-top: 6px solid #8a8a96;
    margin-right: 10px;
}

QComboBox QAbstractItemView {
    background-color: #1a1a24;
    border: 1px solid #2a2a38;
    border-radius: 10px;
    padding: 6px;
    outline: none;
    font-size: 15px;
    color: #e8e8ec;
    selection-background-color: rgba(200, 165, 90, 0.15);
    selection-color: #c8a55a;
}

QComboBox QAbstractItemView::item {
    padding: 10px 14px;
    border-radius: 8px;
    min-height: 22px;
}

QComboBox QAbstractItemView::item:hover {
    background-color: #22222e;
}

/* ── 文本框 ── */

QTextEdit {
    background-color: #1a1a24;
    border: 1px solid #2a2a38;
    border-radius: 12px;
    padding: 14px 16px;
    font-size: 17px;
    font-weight: 400;
    color: #e8e8ec;
    font-family: "Microsoft YaHei UI", "Segoe UI", sans-serif;
    selection-background-color: rgba(200, 165, 90, 0.25);
    selection-color: #e8e8ec;
    line-height: 1.7;
}

QTextEdit:focus {
    border-color: #3a3a4a;
    background-color: #1e1e2a;
}

QTextEdit#OutputBox {
    background-color: #14141c;
    color: #d0d0d8;
}

QTextEdit#OutputBox:focus {
    border-color: #2a2a38;
    background-color: #14141c;
}

QTextEdit QScrollBar:vertical {
    background: transparent;
    width: 6px;
    margin: 8px 3px;
}

QTextEdit QScrollBar::handle:vertical {
    background: #2a2a38;
    border-radius: 3px;
    min-height: 28px;
}

QTextEdit QScrollBar::handle:vertical:hover {
    background: #3a3a4a;
}

QTextEdit QScrollBar::add-line:vertical,
QTextEdit QScrollBar::sub-line:vertical,
QTextEdit QScrollBar::add-page:vertical,
QTextEdit QScrollBar::sub-page:vertical {
    height: 0;
    background: transparent;
}

/* ── 按钮 ── */

QPushButton#SwapBtn {
    background-color: #1a1a24;
    border: 1px solid #2a2a38;
    border-radius: 10px;
    color: #8a8a96;
    font-size: 18px;
    min-width: 40px;
    max-width: 40px;
    min-height: 40px;
    max-height: 40px;
}

QPushButton#SwapBtn:hover {
    background-color: #22222e;
    border-color: #3a3a4a;
    color: #c8a55a;
}

QPushButton#CopyBtn {
    background-color: #c8a55a;
    border: none;
    border-radius: 10px;
    padding: 10px 28px;
    font-size: 15px;
    font-weight: 600;
    color: #0f0f14;
    font-family: "Microsoft YaHei UI", "Segoe UI", sans-serif;
}

QPushButton#CopyBtn:hover {
    background-color: #d4b46a;
}

QPushButton#CopyBtn:pressed {
    background-color: #b8954a;
}

QPushButton#UtilBtn {
    background-color: transparent;
    border: none;
    border-radius: 8px;
    padding: 6px 12px;
    font-size: 14px;
    font-weight: 500;
    color: #6a6a78;
}

QPushButton#UtilBtn:hover {
    background-color: #1a1a24;
    color: #8a8a96;
}

/* ── 设置对话框 ── */

QDialog#SettingsDialog {
    background-color: #0f0f14;
    border-radius: 14px;
}

QLabel#SettingsTitle {
    font-size: 20px;
    font-weight: 600;
    color: #e8e8ec;
}

QLabel#SettingsLabel {
    font-size: 15px;
    color: #8a8a96;
    font-weight: 500;
}

QLineEdit#SettingsInput {
    background-color: #1a1a24;
    border: 1px solid #2a2a38;
    border-radius: 10px;
    padding: 10px 14px;
    font-size: 16px;
    color: #e8e8ec;
    font-family: "Microsoft YaHei UI", "Segoe UI", sans-serif;
}

QLineEdit#SettingsInput:focus {
    border-color: #c8a55a;
}

QCheckBox#SettingsCheck {
    font-size: 15px;
    color: #8a8a96;
    spacing: 10px;
}

QCheckBox#SettingsCheck::indicator {
    width: 20px;
    height: 20px;
    border: 2px solid #3a3a4a;
    border-radius: 5px;
    background-color: #1a1a24;
}

QCheckBox#SettingsCheck::indicator:checked {
    background-color: #c8a55a;
    border-color: #c8a55a;
}

QPushButton#SettingsSaveBtn {
    background-color: #c8a55a;
    border: none;
    border-radius: 10px;
    padding: 10px 28px;
    font-size: 15px;
    font-weight: 600;
    color: #0f0f14;
}

QPushButton#SettingsSaveBtn:hover {
    background-color: #d4b46a;
}

QPushButton#SettingsCancelBtn {
    background-color: #1a1a24;
    border: 1px solid #2a2a38;
    border-radius: 10px;
    padding: 10px 28px;
    font-size: 15px;
    font-weight: 500;
    color: #8a8a96;
}

QPushButton#SettingsCancelBtn:hover {
    background-color: #22222e;
    border-color: #3a3a4a;
}

/* ── 历史列表 ── */

QListWidget#HistoryList {
    background-color: #14141c;
    border: 1px solid #2a2a38;
    border-radius: 12px;
    font-size: 14px;
    color: #b8b8c4;
    outline: none;
    padding: 6px;
}

QListWidget#HistoryList::item {
    padding: 12px 14px;
    border-bottom: 1px solid #1e1e2a;
    border-radius: 8px;
    margin: 2px 3px;
}

QListWidget#HistoryList::item:hover {
    background-color: #1a1a24;
}

QListWidget#HistoryList::item:selected {
    background-color: rgba(200, 165, 90, 0.12);
    color: #e8e8ec;
}

QListWidget#HistoryList QScrollBar:vertical {
    background: transparent;
    width: 6px;
    margin: 6px 3px;
}

QListWidget#HistoryList QScrollBar::handle:vertical {
    background: #2a2a38;
    border-radius: 3px;
    min-height: 28px;
}

QListWidget#HistoryList QScrollBar::handle:vertical:hover {
    background: #3a3a4a;
}

QListWidget#HistoryList QScrollBar::add-line:vertical,
QListWidget#HistoryList QScrollBar::sub-line:vertical {
    height: 0;
}

QPushButton#ClearHistoryBtn {
    background-color: #1a1a24;
    border: 1px solid #2a2a38;
    border-radius: 10px;
    padding: 8px 16px;
    font-size: 14px;
    font-weight: 500;
    color: #8a8a96;
    font-family: "Microsoft YaHei UI", "Segoe UI", sans-serif;
}

QPushButton#ClearHistoryBtn:hover {
    background-color: #22222e;
    border-color: #e05555;
    color: #e05555;
}
"""
