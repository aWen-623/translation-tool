# Architecture

## 概览

TranslationTool 是一个 PyQt5 桌面翻译工具，采用双翻译源 + 自动切换架构。

```
┌─────────────────────────────────────────────────┐
│  main.py                                        │
│  ├─ config.init()                               │
│  ├─ MainWindow                                  │
│  ├─ TrayIcon                                    │
│  └─ keyboard.add_hotkey()                       │
└─────────────────────────────────────────────────┘

┌─ ui/ ───────────────────────────────────────────┐
│  MainWindow                                     │
│  ├─ 输入框 (QTextEdit)                          │
│  ├─ 语种选择 (QComboBox × 2 + ⇄ 按钮)          │
│  ├─ 输出框 (QTextEdit, readonly)                │
│  ├─ 状态栏 (QLabel)                             │
│  ├─ 翻译源选择 (QComboBox)                      │
│  └─ TranslateWorker (QThread)                   │
│                                                 │
│  SettingsDialog                                 │
│  ├─ 快捷键配置 (QKeySequenceEdit)               │
│  └─ 自动复制开关 (QCheckBox)                    │
│                                                 │
│  TrayIcon (QSystemTrayIcon)                     │
└─────────────────────────────────────────────────┘

┌─ core/ ─────────────────────────────────────────┐
│  translator.py                                  │
│  ├─ translate() → TranslationResult             │
│  ├─ _baidu_translate()  (主)                    │
│  └─ _tencent_translate() (备用)                 │
│                                                 │
│  language.py                                    │
│  ├─ detect_language()  Unicode 字符范围分析      │
│  ├─ get_api_code()     语言代码映射             │
│  └─ get_lang_name()    中文显示名               │
│                                                 │
│  history.py                                     │
│  ├─ add()       追加记录（去重）                 │
│  ├─ get_all()   读取全部                        │
│  └─ clear()     清空                            │
└─────────────────────────────────────────────────┘

┌─ config.py ─────────────────────────────────────┐
│  .env → API 密钥                                │
│  settings.json → 用户设置（快捷键、自动复制）    │
│  WINDOW_WIDTH / WINDOW_HEIGHT / MAX_HISTORY     │
└─────────────────────────────────────────────────┘
```

## 翻译流程

1. 用户输入文本 → `QTextEdit.textChanged` 信号
2. 300ms 防抖定时器启动 → `_do_translate()`
3. `detect_language()` 识别源语言 → 自动切换语种下拉框
4. 创建 `TranslateWorker(QThread)` → 后台调用 `translate()`
5. `translate()` 根据 `source_pref` 选择翻译源：
   - `auto`：先百度，失败再腾讯
   - `baidu`：仅百度
   - `tencent`：仅腾讯
6. 结果通过 `pyqtSignal` 回传 → `_on_done()` 更新 UI

## 请求取消机制

- 每次新输入创建新的 `threading.Event`
- 旧 worker 通过 `cancel_event.set()` 通知取消
- `translate()` 在关键步骤检查 `cancel.is_set()`
- worker 结束时检查 `result.error == "cancelled"` 则丢弃

## 窗口行为

- **Frameless + Translucent**：`Qt.FramelessWindowHint | Qt.WA_TranslucentBackground`
- **圆角绘制**：`paintEvent` 中用 `QPainterPath.addRoundedRect` 绘制背景
- **阴影效果**：`QGraphicsDropShadowEffect` 应用于容器 widget
- **自动隐藏**：100ms 定时器检查鼠标位置、焦点、对话框状态
- **拖动**：`mousePressEvent/mouseMoveEvent/mouseReleaseEvent` 实现

## 语言检测算法

基于 Unicode 字符范围统计：

| 字符范围 | 判定 |
|----------|------|
| 平假名 0x3040-0x309F / 片假名 0x30A0-0x30FF | 日语 |
| 韩文 0xAC00-0xD7AF | 韩语 |
| 西里尔字母 0x0400-0x04FF (>30%) | 俄语 |
| CJK 0x4E00-0x9FFF + 繁体特征字 (>30%) | 繁体中文 |
| CJK 其他 | 简体中文 |
| ASCII 字母 | 英语 |

## API 签名

### 百度翻译

```
sign = MD5(appid + text + salt + secret_key)
GET https://fanyi-api.baidu.com/api/trans/vip/translate
```

### 腾讯翻译

```
TC3-HMAC-SHA256 签名:
1. 构造规范请求 (canonical request)
2. 构造待签名字符串 (string to sign)
3. 计算签名 (HMAC-SHA256 链式)
POST https://tmt.tencentcloudapi.com
```
