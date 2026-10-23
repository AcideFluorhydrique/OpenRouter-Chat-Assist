# -*- coding: utf-8 -*-
"""
Created on Thu Aug  14 14:43:23 2025

@author: GeoYWang
"""

# openrouter_chat.py

import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox
import tkinter.font as tkfont
import threading
import json
import os
import urllib.request
import webbrowser
from openai import OpenAI
from datetime import datetime
from markdown_render import render_markdown

class ChatApp:
    def __init__(self, root):
        self.root = root
        self.root.title("OpenRouter Chat Assistant")
        self.root.geometry("800x700")
        self.root.minsize(600, 500)
        
        # 配置文件路径
        self.config_file = "chat_config.json"
        self.chat_history = []
        self.client = None
        
        # 主题配置
        self.current_theme = "light"
        self.themes = {
            "light": {
                "bg": "#ffffff",
                "fg": "#000000",
                "select_bg": "#0078d4",
                "select_fg": "#ffffff", 
                "entry_bg": "#ffffff",
                "entry_fg": "#000000",
                "chat_bg": "#ffffff",
                "frame_bg": "#f8f9fa",
                "border": "#e9ecef",
                "button_bg": "#f8f9fa",
                "button_fg": "#495057",
                "button_active_bg": "#e9ecef"
            },
            "dark": {
                "bg": "#212529",
                "fg": "#f8f9fa", 
                "select_bg": "#495057",
                "select_fg": "#ffffff",
                "entry_bg": "#343a40",
                "entry_fg": "#f8f9fa",
                "chat_bg": "#2d3436",
                "frame_bg": "#212529",
                "border": "#495057",
                "button_bg": "#343a40",
                "button_fg": "#f8f9fa", 
                "button_active_bg": "#495057"
            }
        }
        
        # 加载配置
        self.load_config()
        
        # 创建自定义样式
        self.setup_styles()
        
        # 创建界面
        self.create_widgets()
        
        # 应用主题
        self.apply_theme()
        
        # 初始化客户端
        if self.api_key:
            self.init_client()

    def setup_styles(self):
        """设置自定义样式"""
        self.style = ttk.Style()
        
        # 定义自定义样式
        self.style.theme_create("custom_light", parent="clam", settings={
            "TLabelframe": {
                "configure": {"background": "#f8f9fa", "bordercolor": "#e9ecef", "lightcolor": "#f8f9fa", "darkcolor": "#e9ecef"}
            },
            "TLabelframe.Label": {
                "configure": {"background": "#f8f9fa", "foreground": "#495057"}
            },
            "TFrame": {
                "configure": {"background": "#f8f9fa"}
            },
            "TButton": {
                "configure": {"background": "#f8f9fa", "foreground": "#495057", "bordercolor": "#e9ecef"},
                "map": {"background": [("active", "#e9ecef")]}
            },
            "TLabel": {
                "configure": {"background": "#f8f9fa", "foreground": "#495057"}
            },
            "TEntry": {
                "configure": {"fieldbackground": "#ffffff", "foreground": "#000000", "bordercolor": "#e9ecef"}
            },
            "TCombobox": {
                "configure": {"fieldbackground": "#ffffff", "foreground": "#000000", "bordercolor": "#e9ecef"}
            }
        })
        
        self.style.theme_create("custom_dark", parent="clam", settings={
            "TLabelframe": {
                "configure": {"background": "#212529", "bordercolor": "#495057", "lightcolor": "#212529", "darkcolor": "#495057"}
            },
            "TLabelframe.Label": {
                "configure": {"background": "#212529", "foreground": "#f8f9fa"}
            },
            "TFrame": {
                "configure": {"background": "#212529"}
            },
            "TButton": {
                "configure": {"background": "#343a40", "foreground": "#f8f9fa", "bordercolor": "#495057"},
                "map": {"background": [("active", "#495057")]}
            },
            "TLabel": {
                "configure": {"background": "#212529", "foreground": "#f8f9fa"}
            },
            "TEntry": {
                "configure": {"fieldbackground": "#343a40", "foreground": "#f8f9fa", "bordercolor": "#495057"}
            },
            "TCombobox": {
                "configure": {"fieldbackground": "#343a40", "foreground": "#f8f9fa", "bordercolor": "#495057"}
            }
        })

    def load_config(self):
        """加载配置文件"""
        default_config = {
            "api_key": "",
            "base_url": "https://openrouter.ai/api/v1",
            "model": "openrouter/free",
            "max_tokens": 4096,
            "temperature": 0.7,
            "theme": "light"
        }
        
        try:
            if os.path.exists(self.config_file):
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    config = json.load(f)
                    for key, value in default_config.items():
                        if key not in config:
                            config[key] = value
            else:
                config = default_config
        except Exception as e:
            config = default_config
            print(f"配置文件加载失败: {e}")
        
        self.api_key = config["api_key"]
        self.base_url = config["base_url"] 
        self.model = config["model"]
        self.max_tokens = config["max_tokens"]
        self.temperature = config["temperature"]
        self.current_theme = config.get("theme", "light")

    def save_config(self):
        """保存配置文件"""
        config = {
            "api_key": self.api_key,
            "base_url": self.base_url,
            "model": self.model,
            "max_tokens": self.max_tokens,
            "temperature": self.temperature,
            "theme": self.current_theme
        }
        try:
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(config, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"配置文件保存失败: {e}")

    def create_widgets(self):
        """创建界面组件"""
        # 主框架
        main_frame = ttk.Frame(self.root)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # 顶部设置框架
        settings_frame = ttk.LabelFrame(main_frame, text="设置", padding="5")
        settings_frame.pack(fill=tk.X, pady=(0, 10))
        
        # 第一行：API Key 和模型选择
        row1_frame = ttk.Frame(settings_frame)
        row1_frame.pack(fill=tk.X, pady=(0, 5))
        
        ttk.Label(row1_frame, text="API Key:").pack(side=tk.LEFT)
        self.api_key_var = tk.StringVar(value=self.api_key)
        api_key_entry = ttk.Entry(row1_frame, textvariable=self.api_key_var, show="*", width=30)
        api_key_entry.pack(side=tk.LEFT, padx=(5, 20))
        
        ttk.Label(row1_frame, text="模型:").pack(side=tk.LEFT)
        self.model_var = tk.StringVar(value=self.model)
        # 可编辑：模型列表会变动，允许直接输入任意模型 ID
        self.model_combo = ttk.Combobox(row1_frame, textvariable=self.model_var, width=40)
        self.model_combo['values'] = ("openrouter/free",)
        self.model_combo.pack(side=tk.LEFT, padx=(5, 0))

        # 第二行：按钮和状态
        row2_frame = ttk.Frame(settings_frame)
        row2_frame.pack(fill=tk.X)

        connect_btn = ttk.Button(row2_frame, text="连接", command=self.connect_api)
        connect_btn.pack(side=tk.LEFT)

        # 刷新模型列表
        refresh_btn = ttk.Button(row2_frame, text="刷新模型", command=self.refresh_models)
        refresh_btn.pack(side=tk.LEFT, padx=(10, 0))

        self.free_only_var = tk.BooleanVar(value=True)
        free_only_check = ttk.Checkbutton(row2_frame, text="仅免费", variable=self.free_only_var,
                                          command=self.refresh_models)
        free_only_check.pack(side=tk.LEFT, padx=(5, 0))
        
        # 主题切换按钮
        self.theme_btn = ttk.Button(row2_frame, text="🌙 深色", command=self.toggle_theme)
        self.theme_btn.pack(side=tk.LEFT, padx=(10, 0))
        
        # 状态标签
        self.status_label = ttk.Label(row2_frame, text="未连接")
        self.status_label.pack(side=tk.LEFT, padx=(20, 0))
        
        # 聊天显示区域
        chat_frame = ttk.LabelFrame(main_frame, text="聊天记录", padding="5")
        chat_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 10))
        
        self.chat_display = scrolledtext.ScrolledText(
            chat_frame, 
            wrap=tk.WORD, 
            state=tk.DISABLED,
            font=("Microsoft YaHei", 10),
            height=20
        )
        self.chat_display.pack(fill=tk.BOTH, expand=True)
        
        # 输入框架
        input_frame = ttk.LabelFrame(main_frame, text="输入消息", padding="5")
        input_frame.pack(fill=tk.X)
        
        # 输入区域容器
        input_container = ttk.Frame(input_frame)
        input_container.pack(fill=tk.BOTH, expand=True)
        
        # 消息输入框
        self.message_entry = tk.Text(
            input_container, 
            height=4,
            font=("Microsoft YaHei", 10),
            wrap=tk.WORD
        )
        self.message_entry.pack(fill=tk.BOTH, side=tk.LEFT, expand=True)
        
        # 发送按钮框架
        button_frame = ttk.Frame(input_container)
        button_frame.pack(side=tk.RIGHT, fill=tk.Y, padx=(10, 0))
        
        # 发送按钮
        self.send_button = ttk.Button(button_frame, text="发送\n(Ctrl+Enter)", command=self.send_message)
        self.send_button.pack(fill=tk.X, pady=(0, 5))
        
        # 清空按钮
        clear_button = ttk.Button(button_frame, text="清空历史", command=self.clear_chat)
        clear_button.pack(fill=tk.X)
        
        # 绑定快捷键
        self.message_entry.bind("<Control-Return>", lambda e: self.send_message())
        
        # 配置聊天显示的标签样式
        self.setup_chat_tags()

        # 启动时从 OpenRouter 拉取当前模型列表
        self.refresh_models()

    def refresh_models(self):
        """在后台线程中从 OpenRouter 获取模型列表"""
        free_only = self.free_only_var.get()
        threading.Thread(target=self.fetch_models, args=(free_only,), daemon=True).start()

    def fetch_models(self, free_only):
        """获取模型列表（/models 接口无需 API Key）"""
        try:
            url = self.base_url.rstrip('/') + "/models"
            with urllib.request.urlopen(url, timeout=15) as resp:
                data = json.load(resp)["data"]
            # 新模型排在前面
            data.sort(key=lambda m: m.get("created", 0), reverse=True)
            if free_only:
                ids = [m["id"] for m in data
                       if m["id"].endswith(":free") or m["id"] == "openrouter/free"]
            else:
                ids = [m["id"] for m in data]
            self.root.after(0, lambda: self.update_model_list(ids))
        except Exception as e:
            self.root.after(0, lambda: self.add_message("错误", f"获取模型列表失败: {e}", "error"))

    def update_model_list(self, ids):
        """更新模型下拉框"""
        if "openrouter/free" in ids:
            ids.remove("openrouter/free")
            ids.insert(0, "openrouter/free")
        self.model_combo['values'] = ids
        self.add_message("系统", f"已获取 {len(ids)} 个模型", "system")

    def setup_chat_tags(self):
        """设置聊天显示的标签样式和Markdown支持"""
        text_font = "Microsoft YaHei"
        code_font = "Consolas"
        math_font = "Cambria"
        
        # 基础标签
        self.chat_display.tag_configure("user", foreground="#0066cc", font=(text_font, 10, "bold"))
        self.chat_display.tag_configure("assistant", foreground="#00aa00", font=(text_font, 10))
        self.chat_display.tag_configure("error", foreground="#cc0000", font=(text_font, 10))
        self.chat_display.tag_configure("timestamp", foreground="#888888", font=(text_font, 8))
        self.chat_display.tag_configure("system", foreground="#666666", font=(text_font, 9, "italic"))
        
        # Markdown标签样式
        self.chat_display.tag_configure("h1", font=(text_font, 16, "bold"), spacing1=10, spacing3=5)
        self.chat_display.tag_configure("h2", font=(text_font, 14, "bold"), spacing1=8, spacing3=4)
        self.chat_display.tag_configure("h3", font=(text_font, 12, "bold"), spacing1=6, spacing3=3)
        self.chat_display.tag_configure("bold", font=(text_font, 10, "bold"))
        self.chat_display.tag_configure("italic", font=(text_font, 10, "italic"))
        self.chat_display.tag_configure("bold_italic", font=(text_font, 10, "bold italic"))
        self.chat_display.tag_configure("strike", overstrike=True)
        self.chat_display.tag_configure("code_inline", font=(code_font, 9), background="#f6f8fa")
        self.chat_display.tag_configure("code_block", font=(code_font, 9), background="#f6f8fa", lmargin1=20, lmargin2=20)
        self.chat_display.tag_configure("math", font=(math_font, 11), foreground="#6f42c1")
        self.chat_display.tag_configure("math_block", font=(math_font, 12), foreground="#6f42c1",
                                        justify=tk.CENTER, spacing1=4, spacing3=4)
        self.chat_display.tag_configure("math_grid", font=(code_font, 11), foreground="#6f42c1",
                                        lmargin1=40, lmargin2=40, spacing1=4, spacing3=4)
        for level in range(4):
            self.chat_display.tag_configure(f"list{level}", lmargin1=20 + 20 * level, lmargin2=34 + 20 * level)
        self.chat_display.tag_configure("table", lmargin1=20, lmargin2=20)
        self.chat_display.tag_configure("table_header", font=(text_font, 10, "bold"))
        self.chat_display.tag_configure("hr", foreground="#bbbbbb")
        self.chat_display.tag_configure("quote", font=(text_font, 10, "italic"), foreground="#666666", lmargin1=20, lmargin2=20)
        self.chat_display.tag_configure("link", foreground="#0366d6", underline=True)
        self.chat_display.tag_bind("link", "<Button-1>", self.open_link)
        self.chat_display.tag_bind("link", "<Enter>", lambda e: self.chat_display.config(cursor="hand2"))
        self.chat_display.tag_bind("link", "<Leave>", lambda e: self.chat_display.config(cursor=""))
        
        # 表格列宽按表头粗体字测量
        self.table_font = tkfont.Font(family=text_font, size=10, weight="bold")

    def open_link(self, event):
        """点击链接时用浏览器打开"""
        index = self.chat_display.index(f"@{event.x},{event.y}")
        for tag in self.chat_display.tag_names(index):
            if tag.startswith("url:"):
                webbrowser.open(tag[4:])
                break

    def parse_and_insert_markdown(self, content, base_tag="assistant"):
        """解析并插入Markdown格式的内容（含数学公式）"""
        self.chat_display.config(state=tk.NORMAL)
        
        for text, tags in render_markdown(content, measure=self.table_font.measure):
            for tag in tags:
                # 表格制表位
                if tag.startswith("tbl:") and tag[4:]:
                    self.chat_display.tag_configure(tag, tabs=tag[4:].split(","))
            self.chat_display.insert(tk.END, text, (base_tag,) + tags)
        
        self.chat_display.config(state=tk.DISABLED)

    def toggle_theme(self):
        """切换主题"""
        self.current_theme = "dark" if self.current_theme == "light" else "light"
        self.apply_theme()
        self.save_config()

    def apply_theme(self):
        """应用主题样式"""
        theme = self.themes[self.current_theme]
        
        # 应用ttk主题
        if self.current_theme == "light":
            self.style.theme_use("custom_light")
            self.theme_btn.config(text="🌙 深色")
        else:
            self.style.theme_use("custom_dark")
            self.theme_btn.config(text="☀️ 浅色")
        
        # 配置根窗口
        self.root.configure(bg=theme["bg"])
        
        # 配置聊天显示区域
        self.chat_display.config(
            bg=theme["chat_bg"],
            fg=theme["fg"],
            insertbackground=theme["fg"],
            selectbackground=theme["select_bg"],
            selectforeground=theme["select_fg"]
        )
        
        # 配置输入框
        self.message_entry.config(
            bg=theme["entry_bg"],
            fg=theme["entry_fg"],
            insertbackground=theme["fg"],
            selectbackground=theme["select_bg"],
            selectforeground=theme["select_fg"]
        )
        
        # 重新配置聊天标签颜色以适应主题
        if self.current_theme == "dark":
            self.chat_display.tag_configure("user", foreground="#87CEEB", font=("Microsoft YaHei", 10, "bold"))
            self.chat_display.tag_configure("assistant", foreground="#90EE90", font=("Microsoft YaHei", 10))
            self.chat_display.tag_configure("error", foreground="#FF6B6B", font=("Microsoft YaHei", 10))
            self.chat_display.tag_configure("system", foreground="#BBBBBB", font=("Microsoft YaHei", 9, "italic"))
            self.chat_display.tag_configure("code_inline", background="#404040")
            self.chat_display.tag_configure("code_block", background="#404040")
            self.chat_display.tag_configure("math", foreground="#d2a8ff")
            self.chat_display.tag_configure("math_block", foreground="#d2a8ff")
            self.chat_display.tag_configure("math_grid", foreground="#d2a8ff")
            self.chat_display.tag_configure("link", foreground="#58a6ff")
            self.chat_display.tag_configure("quote", foreground="#aaaaaa")
        else:
            self.setup_chat_tags()

    def connect_api(self):
        """连接 API"""
        self.api_key = self.api_key_var.get().strip()
        self.model = self.model_var.get().strip()
        
        if not self.api_key:
            messagebox.showerror("错误", "请输入有效的 API Key")
            return
            
        self.save_config()
        
        if self.init_client():
            self.status_label.config(text="✅ 已连接")
            self.add_message("系统", f"已连接到 {self.model}", "system")
        else:
            self.status_label.config(text="❌ 连接失败")

    def init_client(self):
        """初始化 OpenAI 客户端"""
        try:
            self.client = OpenAI(
                base_url=self.base_url,
                api_key=self.api_key
            )
            return True
        except Exception as e:
            self.add_message("错误", f"客户端初始化失败: {str(e)}", "error")
            return False

    def add_message(self, role, content, tag="assistant"):
        """添加消息到聊天显示区域"""
        self.chat_display.config(state=tk.NORMAL)
        
        # 添加时间戳
        timestamp = datetime.now().strftime("%H:%M:%S")
        self.chat_display.insert(tk.END, f"[{timestamp}] ", "timestamp")
        
        # 添加角色标识
        if role == "用户":
            self.chat_display.insert(tk.END, f"{role}: ", "user")
            self.chat_display.insert(tk.END, f"{content}\n\n")
        elif role == "助手":
            self.chat_display.insert(tk.END, f"{role}: \n", "assistant")
            # 使用Markdown解析器处理AI回复
            self.parse_and_insert_markdown(content, "assistant")
            self.chat_display.insert(tk.END, "\n")
        else:
            self.chat_display.insert(tk.END, f"{role}: ", tag)
            self.chat_display.insert(tk.END, f"{content}\n\n")
        
        # 滚动到底部
        self.chat_display.see(tk.END)
        self.chat_display.config(state=tk.DISABLED)

    def send_message(self):
        """发送消息"""
        if not self.client:
            messagebox.showerror("错误", "请先连接 API")
            return
            
        message = self.message_entry.get("1.0", tk.END).strip()
        if not message:
            return
            
        # 清空输入框
        self.message_entry.delete("1.0", tk.END)
        
        # 添加用户消息到显示区域
        self.add_message("用户", message, "user")
        
        # 添加到聊天历史
        self.chat_history.append({"role": "user", "content": message})
        
        # 禁用发送按钮，防止重复发送
        self.send_button.config(state="disabled", text="发送中...")
        
        # 在新线程中调用 API
        threading.Thread(target=self.call_api, daemon=True).start()

    def call_api(self):
        """调用 API 获取回复"""
        try:
            # 限制聊天历史长度，避免 token 超限
            recent_history = self.chat_history[-10:]
            
            # 调用 API
            completion = self.client.chat.completions.create(
                model=self.model,
                messages=recent_history,
                max_tokens=self.max_tokens,
                temperature=self.temperature
            )
            
            # 获取回复
            # 推理模型可能把 max_tokens 全用在思考上，content 为空
            response = completion.choices[0].message.content
            if not response:
                raise RuntimeError("模型返回了空内容（可能是 max_tokens 不足）")

            # 添加助手回复到聊天历史
            self.chat_history.append({"role": "assistant", "content": response})
            
            # 在主线程中更新 UI
            self.root.after(0, lambda: self.handle_api_response(response))
            
        except Exception as e:
            error_msg = f"API 调用失败: {str(e)}"
            self.root.after(0, lambda: self.handle_api_error(error_msg))

    def handle_api_response(self, response):
        """处理 API 响应"""
        self.add_message("助手", response, "assistant")
        self.send_button.config(state="normal", text="发送\n(Ctrl+Enter)")

    def handle_api_error(self, error_msg):
        """处理 API 错误"""
        self.add_message("错误", error_msg, "error")
        self.send_button.config(state="normal", text="发送\n(Ctrl+Enter)")

    def clear_chat(self):
        """清空聊天记录"""
        if messagebox.askyesno("确认", "确定要清空所有聊天记录吗？"):
            self.chat_display.config(state=tk.NORMAL)
            self.chat_display.delete("1.0", tk.END)
            self.chat_display.config(state=tk.DISABLED)
            self.chat_history = []
            self.add_message("系统", "聊天记录已清空", "system")

def main():
    """主函数"""
    try:
        root = tk.Tk()
        app = ChatApp(root)
        root.mainloop()
        
    except Exception as e:
        messagebox.showerror("启动错误", f"应用启动失败:\n{str(e)}")

if __name__ == "__main__":
    main()
