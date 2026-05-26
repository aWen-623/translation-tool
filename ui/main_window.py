"""主翻译面板 — 深色高级简约设计。

特性:
- 下拉框语种选择（全中文）
- 翻译源选择（自动/百度/腾讯）
- 300ms 输入防抖
- 请求取消机制
- 状态指示（翻译中/完成/失败/已复制）
- 历史记录面板
- 设置窗口
- 系统托盘最小化
- 圆角窗口
"""

import threading
from PyQt5.QtCore import Qt, QTimer, QThread, pyqtSignal, QRectF
from PyQt5.QtGui import QCursor, QColor, QPainter, QPainterPath, QBrush, QPen
from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QTextEdit, QPushButton,
    QLabel, QApplication, QListWidget, QListWidgetItem, QComboBox,
    QGraphicsDropShadowEffect, QSizePolicy, QDialog,
)

import config
from core.language import (
    SOURCE_LANGS, TARGET_LANGS, detect_language, get_lang_name, get_default_target,
)
from core.translator import translate, TranslationResult
from core import history


# ── 常量 ──────────────────────────────────────────────────────────

MARGIN = 24        # 左右边距
GAP = 20           # 区域间垂直间距
LABEL_COMBO_GAP = 8  # 标签与下拉框间距
CORNER = 14        # 圆角半径
SHADOW = 10        # 阴影偏移

# ── 工作线程 ──────────────────────────────────────────────────────


class TranslateWorker(QThread):
    finished = pyqtSignal(object)

    def __init__(self, text: str, source: str, target: str,
                 source_pref: str, cancel_event: threading.Event):
        super().__init__()
        self.text = text
        self.source = source
        self.target = target
        self.source_pref = source_pref
        self.cancel_event = cancel_event

    def run(self):
        result = translate(
            self.text, self.source, self.target,
            source_pref=self.source_pref,
            cancel=self.cancel_event,
        )
        self.finished.emit(result)


# ── 主窗口 ────────────────────────────────────────────────────────


class MainWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.source_lang = "zh"
        self.target_lang = "en"
        self.worker = None
        self.cancel_event = threading.Event()
        self.history_visible = False
        self._drag_pos = None
        self._status_timer = QTimer()
        self._status_timer.setSingleShot(True)
        self._status_timer.setInterval(2500)
        self._status_timer.timeout.connect(lambda: self._set_status(""))

        self._init_ui()
        self._apply_style()
        self._setup_auto_hide()

    def _init_ui(self):
        self.setObjectName("MainWindow")
        self.setWindowFlags(
            Qt.WindowStaysOnTopHint | Qt.FramelessWindowHint | Qt.Tool
        )
        self.setAttribute(Qt.WA_TranslucentBackground, True)
        self.setFixedSize(config.WINDOW_WIDTH, config.WINDOW_HEIGHT)

        # 主容器
        self._container = QWidget(self)
        self._container.setObjectName("MainWindow")
        self._container.setGeometry(
            SHADOW, SHADOW,
            config.WINDOW_WIDTH - SHADOW * 2,
            config.WINDOW_HEIGHT - SHADOW * 2,
        )

        shadow = QGraphicsDropShadowEffect(self)
        shadow.setBlurRadius(20)
        shadow.setXOffset(0)
        shadow.setYOffset(4)
        shadow.setColor(QColor(0, 0, 0, 120))
        self._container.setGraphicsEffect(shadow)

        root = QVBoxLayout(self._container)
        root.setContentsMargins(MARGIN, 24, MARGIN, 24)
        root.setSpacing(GAP)

        # ── 标题栏 ──
        root.addLayout(self._build_title_bar())

        # ── 语种选择区 ──
        root.addLayout(self._build_lang_selector())

        # ── 输入区：标签 + 文本框（可伸缩，比例 3）──
        root.addWidget(self._make_label("输入文本"))
        root.addSpacing(LABEL_COMBO_GAP)
        self.input_box = QTextEdit()
        self.input_box.setPlaceholderText("输入或粘贴要翻译的文本...")
        self.input_box.setAcceptRichText(False)
        self.input_box.textChanged.connect(self._on_text_changed)
        root.addWidget(self.input_box, 3)

        # ── 输出区：标签头 + 结果框（可伸缩，比例 5）──
        root.addLayout(self._build_output_header())
        root.addSpacing(LABEL_COMBO_GAP)
        self.output_box = self._make_output_box()
        root.addWidget(self.output_box, 5)

        # ── 底部栏 ──
        root.addSpacing(GAP)
        root.addLayout(self._build_bottom_bar())

        # ── 历史面板（默认隐藏）──
        self.history_panel = QWidget()
        self.history_panel.setFixedHeight(180)
        hp_layout = QHBoxLayout(self.history_panel)
        hp_layout.setContentsMargins(0, 0, 0, 0)
        hp_layout.setSpacing(8)

        self.history_list = QListWidget()
        self.history_list.setObjectName("HistoryList")
        self.history_list.itemClicked.connect(self._load_from_history)
        hp_layout.addWidget(self.history_list, 1)

        self.clear_history_btn = QPushButton("清空")
        self.clear_history_btn.setObjectName("ClearHistoryBtn")
        self.clear_history_btn.setCursor(QCursor(Qt.PointingHandCursor))
        self.clear_history_btn.setFixedWidth(60)
        self.clear_history_btn.clicked.connect(self._clear_history)
        hp_layout.addWidget(self.clear_history_btn, 0, Qt.AlignBottom)

        self.history_panel.hide()
        root.addWidget(self.history_panel)

        # 防抖定时器
        self._translate_timer = QTimer()
        self._translate_timer.setSingleShot(True)
        self._translate_timer.setInterval(300)
        self._translate_timer.timeout.connect(self._do_translate)

    # ── UI 构件工厂 ───────────────────────────────────────────────

    def _build_title_bar(self) -> QHBoxLayout:
        bar = QHBoxLayout()
        bar.setSpacing(8)

        title = QLabel("翻译")
        title.setObjectName("TitleLabel")
        bar.addWidget(title)
        bar.addStretch()

        for text, slot in [("设置", self._open_settings),
                           ("历史", self._toggle_history),
                           ("最小化", self.hide)]:
            btn = QPushButton(text)
            btn.setObjectName("UtilBtn")
            btn.setCursor(QCursor(Qt.PointingHandCursor))
            btn.clicked.connect(slot)
            bar.addWidget(btn)

        return bar

    def _build_lang_selector(self) -> QHBoxLayout:
        row = QHBoxLayout()
        row.setSpacing(16)

        # 源语言列：标签 + 下拉框，左对齐
        src_col = QVBoxLayout()
        src_col.setSpacing(LABEL_COMBO_GAP)
        src_col.addWidget(self._make_label("源语言"))
        self.source_combo = QComboBox()
        self.source_combo.setFixedHeight(42)
        for code in SOURCE_LANGS:
            self.source_combo.addItem(get_lang_name(code), code)
        self.source_combo.currentIndexChanged.connect(self._on_source_changed)
        src_col.addWidget(self.source_combo)
        row.addLayout(src_col, 1)

        # 互换按钮：垂直居中
        swap_col = QVBoxLayout()
        swap_col.addStretch()
        swap_btn = QPushButton("⇄")
        swap_btn.setObjectName("SwapBtn")
        swap_btn.setCursor(QCursor(Qt.PointingHandCursor))
        swap_btn.clicked.connect(self._swap_langs)
        swap_col.addWidget(swap_btn)
        swap_col.addStretch()
        row.addLayout(swap_col)

        # 目标语言列：标签 + 下拉框，右对齐
        tgt_col = QVBoxLayout()
        tgt_col.setSpacing(LABEL_COMBO_GAP)
        tgt_col.addWidget(self._make_label("目标语言"))
        self.target_combo = QComboBox()
        self.target_combo.setFixedHeight(42)
        for code in TARGET_LANGS:
            self.target_combo.addItem(get_lang_name(code), code)
        self.target_combo.currentIndexChanged.connect(self._on_target_changed)
        tgt_col.addWidget(self.target_combo)
        row.addLayout(tgt_col, 1)

        return row

    def _build_output_header(self) -> QHBoxLayout:
        header = QHBoxLayout()
        header.setSpacing(10)
        header.addWidget(self._make_label("翻译结果"))

        self.phonetic_label = QLabel("")
        self.phonetic_label.setObjectName("PhoneticLabel")
        self.phonetic_label.hide()
        header.addWidget(self.phonetic_label)
        header.addStretch()

        self.status_label = QLabel("")
        self.status_label.setObjectName("StatusLabel")
        header.addWidget(self.status_label)
        return header

    def _build_bottom_bar(self) -> QHBoxLayout:
        bar = QHBoxLayout()
        bar.setSpacing(12)

        bar.addWidget(self._make_label("翻译源:"))

        self.source_selector = QComboBox()
        self.source_selector.setFixedHeight(36)
        self.source_selector.addItem("自动切换", "auto")
        self.source_selector.addItem("百度翻译", "baidu")
        self.source_selector.addItem("腾讯翻译", "tencent")
        self.source_selector.setCurrentIndex(0)
        self.source_selector.currentIndexChanged.connect(self._on_source_pref_changed)
        bar.addWidget(self.source_selector)

        self.api_label = QLabel("")
        self.api_label.setObjectName("StatusLabel")
        bar.addWidget(self.api_label)

        bar.addStretch()

        copy_btn = QPushButton("复制译文")
        copy_btn.setObjectName("CopyBtn")
        copy_btn.setCursor(QCursor(Qt.PointingHandCursor))
        copy_btn.clicked.connect(self._copy_translation)
        bar.addWidget(copy_btn)

        return bar

    @staticmethod
    def _make_label(text: str) -> QLabel:
        lbl = QLabel(text)
        lbl.setObjectName("SectionLabel")
        return lbl

    @staticmethod
    def _make_output_box() -> QTextEdit:
        box = QTextEdit()
        box.setObjectName("OutputBox")
        box.setReadOnly(True)
        return box

    def _apply_style(self):
        from ui.styles import MAIN
        self.setStyleSheet(MAIN)

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        path = QPainterPath()
        path.addRoundedRect(
            QRectF(SHADOW, SHADOW,
                   self.width() - SHADOW * 2, self.height() - SHADOW * 2),
            CORNER, CORNER,
        )
        painter.fillPath(path, QBrush(QColor("#0f0f14")))
        pen = QPen(QColor("#2a2a38"))
        pen.setWidth(1)
        painter.setPen(pen)
        painter.drawPath(path)
        painter.end()

    def _setup_auto_hide(self):
        self._focus_timer = QTimer()
        self._focus_timer.setInterval(100)
        self._focus_timer.timeout.connect(self._check_focus)
        self._focus_timer.start()

    def _check_focus(self):
        if not self.isVisible():
            return
        # 鼠标在窗口内 → 不隐藏
        if self.rect().contains(self.mapFromGlobal(QCursor.pos())):
            return
        # 有子控件持有焦点 → 不隐藏
        focused = QApplication.focusWidget()
        if focused and self.isAncestorOf(focused):
            return
        # 有打开的对话框 → 不隐藏
        for child in self.findChildren(QDialog):
            if child.isVisible():
                return
        self.hide()

    # ── 语种管理 ──────────────────────────────────────────────────

    def _on_source_changed(self, index):
        self.source_lang = self.source_combo.itemData(index)

    def _on_target_changed(self, index):
        self.target_lang = self.target_combo.itemData(index)

    def _swap_langs(self):
        src_idx = self.source_combo.currentIndex()
        tgt_idx = self.target_combo.currentIndex()
        self.source_combo.setCurrentIndex(
            self._find_idx(self.source_combo, self.target_combo.itemData(tgt_idx)))
        self.target_combo.setCurrentIndex(
            self._find_idx(self.target_combo, self.source_combo.itemData(src_idx)))
        output = self.output_box.toPlainText()
        if output and not output.startswith("⚠"):
            self.input_box.setPlainText(output)

    def _find_idx(self, combo, data):
        for i in range(combo.count()):
            if combo.itemData(i) == data:
                return i
        return 0

    # ── 翻译源 ────────────────────────────────────────────────────

    def _on_source_pref_changed(self, index):
        config.set("source", self.source_selector.itemData(index))

    # ── 翻译 ──────────────────────────────────────────────────────

    def _on_text_changed(self):
        self._translate_timer.start()

    def _do_translate(self):
        text = self.input_box.toPlainText().strip()
        if not text:
            self.output_box.clear()
            self.phonetic_label.hide()
            self._set_status("")
            self.api_label.setText("")
            return

        self.cancel_event.set()
        if self.worker is not None:
            try:
                if self.worker.isRunning():
                    self.worker.wait(200)
            except RuntimeError:
                pass
            self.worker = None
        self.cancel_event = threading.Event()

        detected = detect_language(text)
        if detected != self.source_lang:
            self.source_lang = detected
            self.target_lang = get_default_target(detected)
            self.source_combo.blockSignals(True)
            self.target_combo.blockSignals(True)
            self.source_combo.setCurrentIndex(
                self._find_idx(self.source_combo, detected))
            self.target_combo.setCurrentIndex(
                self._find_idx(self.target_combo, self.target_lang))
            self.source_combo.blockSignals(False)
            self.target_combo.blockSignals(False)

        self._set_status("翻译中...", "normal")
        self.output_box.clear()
        self.phonetic_label.hide()
        self.api_label.setText("")

        self.worker = TranslateWorker(
            text, self.source_lang, self.target_lang,
            config.get("source"), self.cancel_event,
        )
        self.worker.finished.connect(self._on_done)
        self.worker.start()

    def _on_done(self, result: TranslationResult):
        if result.error == "cancelled":
            return

        if result.ok:
            self.output_box.setPlainText(result.text)
            self._set_status("翻译完成", "ok")
            self.api_label.setText(f"via {result.api_used}")
            self._status_timer.start()

            if config.get("auto_copy"):
                QApplication.clipboard().setText(result.text)

            history.add(
                self.input_box.toPlainText().strip(),
                result.text, result.source, result.target,
            )
        else:
            self.output_box.clear()
            self._set_status(result.error, "error")
            self._status_timer.start()

    # ── 状态管理 ──────────────────────────────────────────────────

    def _set_status(self, text: str, kind: str = ""):
        self._status_timer.stop()
        self.status_label.setText(text)
        obj_name = {"ok": "StatusOk", "error": "StatusError"}.get(kind, "StatusLabel")
        self.status_label.setObjectName(obj_name)
        self.status_label.style().unpolish(self.status_label)
        self.status_label.style().polish(self.status_label)

    # ── 复制 ──────────────────────────────────────────────────────

    def _copy_translation(self):
        text = self.output_box.toPlainText()
        if text and not text.startswith("⚠"):
            QApplication.clipboard().setText(text)
            self._set_status("已复制到剪贴板", "ok")
            self._status_timer.start()

    # ── 历史 ──────────────────────────────────────────────────────

    def _toggle_history(self):
        self.history_visible = not self.history_visible
        base_h = config.WINDOW_HEIGHT
        if self.history_visible:
            self._refresh_history()
            self.history_panel.show()
            self.setFixedHeight(base_h + 190)
            self._container.setFixedHeight(base_h + 190 - SHADOW * 2)
        else:
            self.history_panel.hide()
            self.setFixedHeight(base_h)
            self._container.setFixedHeight(base_h - SHADOW * 2)

    def _refresh_history(self):
        self.history_list.clear()
        for entry in history.get_all():
            src = get_lang_name(entry.get("from", ""))
            tgt = get_lang_name(entry.get("to", ""))
            text = f"{entry['source']}  →  {entry['translated']}  [{src}→{tgt}]"
            item = QListWidgetItem(text)
            item.setData(Qt.UserRole, entry)
            self.history_list.addItem(item)

    def _load_from_history(self, item: QListWidgetItem):
        entry = item.data(Qt.UserRole)
        if entry:
            self.input_box.setPlainText(entry.get("source", ""))

    def _clear_history(self):
        history.clear()
        self.history_list.clear()

    # ── 设置 ──────────────────────────────────────────────────────

    def _open_settings(self):
        from ui.settings_dialog import SettingsDialog
        dlg = SettingsDialog(self, on_hotkey_changed=self._on_hotkey_changed)
        dlg.exec_()

    def _on_hotkey_changed(self, old_key, new_key):
        import keyboard
        try:
            keyboard.remove_hotkey(old_key)
        except (KeyError, AttributeError):
            pass
        try:
            keyboard.add_hotkey(
                new_key, lambda: QTimer.singleShot(0, self.toggle_visibility))
        except Exception as e:
            self._set_status(f"快捷键设置失败: {e}", "error")

    # ── 窗口拖动 ─────────────────────────────────────────────────

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self._drag_pos = event.globalPos() - self.frameGeometry().topLeft()
            event.accept()

    def mouseMoveEvent(self, event):
        if self._drag_pos and event.buttons() & Qt.LeftButton:
            self.move(event.globalPos() - self._drag_pos)
            event.accept()

    def mouseReleaseEvent(self, event):
        self._drag_pos = None

    # ── 显示/隐藏 ────────────────────────────────────────────────

    def toggle_visibility(self):
        if self.isVisible():
            self.hide()
        else:
            screen = QApplication.primaryScreen().geometry()
            x = (screen.width() - config.WINDOW_WIDTH) // 2
            y = (screen.height() - config.WINDOW_HEIGHT) // 2
            self.move(x, y)
            self.show()
            self.activateWindow()
            self.input_box.setFocus()
