# Integration Guide

## 环境要求

- Python 3.8+
- Windows 10/11
- 管理员权限（`keyboard` 库需要）

## 安装步骤

```bash
cd TranslationTool
pip install -r requirements.txt
```

## API 密钥配置

### 百度翻译 API

1. 访问 https://fanyi-api.baidu.com/ 注册账号
2. 实名认证后开通「通用翻译 API」服务
3. 在控制台获取 **APP ID** 和 **密钥**
4. 编辑 `.env`：

```
BAIDU_APP_ID=你的APP_ID
BAIDU_SECRET_KEY=你的密钥
```

**免费额度**：标准版每月 5 万字符，高级版 100 万字符。

### 腾讯翻译 API

1. 访问 https://cloud.tencent.com/ 注册账号
2. 控制台搜索「机器翻译」，开通 TMT 服务
3. 访问管理 → API 密钥管理，获取 **SecretId** 和 **SecretKey**
4. 编辑 `.env`：

```
TENCENT_SECRET_ID=你的SecretId
TENCENT_SECRET_KEY=你的SecretKey
```

**免费额度**：每月 500 万字符。

### 完整 .env 示例

```env
BAIDU_APP_ID=你的百度APP_ID
BAIDU_SECRET_KEY=你的百度密钥
TENCENT_SECRET_ID=你的腾讯SecretId
TENCENT_SECRET_KEY=你的腾讯SecretKey
```

## 运行

```bash
python main.py
```

启动后：
- 按 `Ctrl+Alt+T` 唤出翻译面板
- 输入文本自动翻译
- 关闭窗口最小化到系统托盘
- 右键托盘图标 → 退出程序

## 设置

点击面板右上角「设置」按钮：

| 设置项 | 说明 |
|--------|------|
| 全局唤醒快捷键 | 按下想要的组合键即可录制 |
| 翻译完成后自动复制 | 开启后翻译结果自动复制到剪贴板 |

设置保存在 `settings.json`，重启后保留。

## 翻译源选择

面板底部下拉框可选择：

| 选项 | 行为 |
|------|------|
| 自动切换 | 先尝试百度，失败自动切腾讯 |
| 百度翻译 | 仅使用百度 API |
| 腾讯翻译 | 仅使用腾讯 API |

选择会保存到 `settings.json`。

## 故障排查

| 问题 | 原因 | 解决 |
|------|------|------|
| 提示「百度API未配置」 | `.env` 缺少密钥 | 填入正确的 APP ID 和密钥 |
| 提示「请求超时」 | 网络问题 | 检查网络连接，或切换翻译源 |
| 热键无反应 | 权限不足 | 以管理员身份运行 |
| 翻译结果为空 | 文本过长或含特殊字符 | 尝试缩短文本 |
| 窗口不显示 | 多显示器问题 | 检查任务栏，或删除 `settings.json` 重置 |

## 打包为 EXE

```bash
pip install pyinstaller
pyinstaller --onefile --windowed --icon=icon.ico main.py
```

打包后 `.env` 需放在 EXE 同目录。
