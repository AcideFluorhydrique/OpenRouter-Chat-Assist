[🇨🇳中文](./README.md) | [🇬🇧English](./README.en.md)

---


# OpenRouter Chat Assistant

这是一个使用 Python 和 Tkinter 构建的简洁桌面聊天客户端，通过 OpenRouter API 连接多种大型语言模型。

![应用截图](圖片.png)

## ✨ 主要功能

* **多模型支持**: 启动时从 OpenRouter 实时获取模型列表（可只看免费模型），也可直接输入任意模型 ID。默认使用 `openrouter/free` 自动路由到可用的免费模型。
* **主题切换**: 支持浅色和深色主题一键切换，并自动保存你的偏好。
* **Markdown渲染**: 支持标题、粗体、斜体、代码块、列表（含编号与嵌套）、表格和链接；LaTeX 数学公式（`$…$`、`$$…$$`、`\[…\]`、矩阵、分段函数）会转换为可读的 Unicode 形式。
* **配置持久化**: 自动保存API Key、所选模型和主题到本地 `chat_config.json` 文件中。
* **跨平台**: 基于Python和Tkinter，理论上可以在Windows、macOS和Linux上运行。
* **一键构建**: 提供 `build.py` 脚本，可以轻松将应用打包成单个可执行文件 (portable)。GitHub Actions 会自动构建 Windows `.exe`，推送 `v*` 标签时发布到 Releases。

## 🛠️ 安装与运行 (从源代码)

如果你想从源代码运行此应用，请按照以下步骤操作。

**1. 克隆仓库**
```bash
git clone [https://github.com/AcideFluorhydrique/OpenRouter-Chat-Assist.git](https://github.com/AcideFluorhydrique/OpenRouter-Chat-Assist.git)
cd your-repository-name
```

**2. 安装依赖**
项目依赖项已在 `requirements.txt` 中列出。运行以下命令进行安装：
```bash
pip install -r requirements.txt
```

**3. 运行应用**
```bash
python openrouter_chat.py
```

**4. 配置**
* 首次运行时，界面会提示你输入 OpenRouter API Key。
* 您可以在 [OpenRouter.ai](https://openrouter.ai/) 获取你的免费API Key。
* 输入Key并点击 "连接" 按钮后，即可开始聊天。

## 📦 构建可执行文件

如果你想创建一个独立的可执行文件（`.exe`），可以直接运行提供的构建脚本。

```bash
python build.py
```

脚本会自动安装依赖并使用 PyInstaller 进行打包。构建成功后，你可以在 `dist/` 目录下找到 `OpenRouterChat.exe` 文件。

## 📂 文件结构

```
.
├── openrouter_chat.py   # 主应用GUI和逻辑代码
├── markdown_render.py   # Markdown / 数学公式渲染
├── build.py             # PyInstaller构建脚本
├── requirements.txt     # 项目依赖
└── README.md            # 项目说明文件
```
