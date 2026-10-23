[🇨🇳中文](./README.md) | [🇬🇧English](./README.en.md)


---

# OpenRouter Chat Assistant

This is a simple desktop chat client built with Python and Tkinter, connecting to various large language models via the OpenRouter API.

![Application Screenshot](image.png)

## ✨ Key Features

* **Multi-Model Support**: Fetches the current model list from OpenRouter at startup (optionally free models only), or type any model ID. Defaults to `openrouter/free`, which routes to an available free model.
* **Theme Switching**: Easily toggle between light and dark themes, with preferences automatically saved.
* **Markdown Rendering**: Headings, bold, italic, code blocks, lists (numbered and nested), tables and links; LaTeX math (`$…$`, `$$…$$`, `\[…\]`, matrices, cases) is converted to readable Unicode.
* **Configuration Persistence**: Automatically saves API Key, selected model, and theme to a local `chat_config.json` file.
* **Cross-Platform**: Built with Python and Tkinter, theoretically compatible with Windows, macOS, and Linux.
* **One-Click Build**: Includes a `build.py` script to easily package the application into a single executable file (portable). GitHub Actions builds the Windows `.exe` automatically and publishes it to Releases when a `v*` tag is pushed.

## 🛠️ Installation and Running (From Source)

To run the application from source code, follow these steps:

**1. Clone the Repository**

```bash
git clone https://github.com/AcideFluorhydrique/OpenRouter-Chat-Assist.git
cd OpenRouter-Chat-Assist
```





**2. Install Dependencies**
The project dependencies are listed in requirements.txt. Install them with:
```bash
pip install -r requirements.txt
```

**3. Run the Application**
```bash
python openrouter_chat.py
```

**4. Configuration**
* On first launch, the interface will prompt you to enter your OpenRouter API Key.
* You can obtain a free API Key from [OpenRouter.ai](https://openrouter.ai/).
* Enter the key and click the "连接" button to start chatting.

## 📦 uilding an Executable

To create a standalone executable (`.exe`), run the provided build script:

```bash
python build.py
```


The script will automatically install dependencies and use PyInstaller to package the application. Once built, find the `OpenRouterChat.exe` file in the `dist/` directory.

## 📂 File Structure

```
.
├── openrouter_chat.py   # Main application GUI and logic code
├── markdown_render.py   # Markdown / math formula rendering
├── build.py             # PyInstaller build script
├── requirements.txt     # Project dependencies
└── README.md            # Project documentation
```
