# Translation Tool

Windows 桌面快捷翻译工具，支持全局热键唤出、多翻译源自动切换。

## 功能

- **全局热键**：`Ctrl+Alt+T` 唤出/隐藏翻译面板（可自定义）
- **自动语种检测**：输入文本自动识别中/英/日/韩/俄/繁体
- **多翻译源**：百度翻译（主）+ 腾讯翻译（备用），自动切换
- **深色高级主题**：暖金点缀 + 圆角窗口 + 阴影效果
- **系统托盘**：关闭窗口后最小化到托盘，右键退出
- **翻译历史**：最近 10 条记录，点击可回填
- **自动复制**：翻译完成自动复制结果（可选）

## 安装

```bash
pip install -r requirements.txt
```

依赖：PyQt5, keyboard, requests, python-dotenv

## 配置 API 密钥

复制 `.env.example` 为 `.env`，填入你的 API 密钥：

```bash
cp .env.example .env
```

### 百度翻译（主）

1. 注册 [百度翻译开放平台](https://fanyi-api.baidu.com/)
2. 开通「通用翻译 API」
3. 获取 APP ID 和密钥，填入 `.env`

### 腾讯翻译（备用）

1. 注册 [腾讯云](https://cloud.tencent.com/)
2. 开通「机器翻译 TMT」
3. 获取 SecretId 和 SecretKey，填入 `.env`

## 运行

```bash
python main.py
```

启动后按 `Ctrl+Alt+T` 唤出翻译面板。关闭窗口会最小化到系统托盘，右键托盘图标可退出。

## 快捷键

| 快捷键 | 功能 |
|--------|------|
| `Ctrl+Alt+T` | 唤出/隐藏翻译面板 |

可在「设置」对话框中自定义快捷键。

## 界面预览

- 深色主题：底色 `#0f0f14`，暖金点缀 `#c8a55a`
- 窗口尺寸：1000×700，圆角 14px
- 支持窗口拖动、失焦自动隐藏

## 项目结构

```
TranslationTool/
├── main.py              # 入口
├── config.py            # 配置管理（.env + settings.json）
├── core/
│   ├── language.py      # 语种定义、检测、API 代码映射
│   ├── translator.py    # 翻译引擎（百度 + 腾讯）
│   └── history.py       # 翻译历史存储
├── ui/
│   ├── main_window.py   # 主翻译面板
│   ├── settings_dialog.py # 设置对话框
│   ├── styles.py        # 深色主题 QSS
│   └── tray.py          # 系统托盘图标
├── .env.example         # API 密钥模板
└── requirements.txt     # Python 依赖
```

## 注意事项

- `.env` 包含 API 密钥，已加入 `.gitignore`，不要提交到版本控制
- `keyboard` 库需要管理员权限才能注册全局热键
- 翻译请求超时 5 秒，网络不佳时会自动切换翻译源
