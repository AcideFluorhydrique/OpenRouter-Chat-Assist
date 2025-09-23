# -*- coding: utf-8 -*-
"""
Created on Thu Aug  14 14:43:23 2025

@author: GeoYWang
"""

# openrouter_chat.py

import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox
import threading
import json
import os
import re
from openai import OpenAI
from datetime import datetime

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
            "model": "openai/gpt-oss-20b:free",
            "max_tokens": 1000,
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
        model_combo = ttk.Combobox(row1_frame, textvariable=self.model_var, width=25, state="readonly")
        model_combo['values'] = (
            "openai/gpt-oss-20b:free", 
            "x-ai/grok-4-fast:free",
            "deepseek/deepseek-chat-v3-0324:free",
            "deepseek/deepseek-r1-0528:free",
            "qwen/qwen3-coder:free",
            "qwen/qwen3-235b-a22b:free",
            "moonshotai/kimi-k2:free",
            "mistralai/mistral-small-3.2-24b-instruct:free",
            "mistralai/devstral-small-2505:free",
            "tencent/hunyuan-a13b-instruct:free",
            "z-ai/glm-4.5-air:free",
            "meta-llama/llama-3.3-70b-instruct:free",
            "cognitivecomputations/dolphin-mistral-24b-venice-edition:free",
        )
        model_combo.pack(side=tk.LEFT, padx=(5, 0))
        
        # 第二行：按钮和状态
        row2_frame = ttk.Frame(settings_frame)
        row2_frame.pack(fill=tk.X)
        
        connect_btn = ttk.Button(row2_frame, text="连接", command=self.connect_api)
        connect_btn.pack(side=tk.LEFT)
        
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

    def setup_chat_tags(self):
        """设置聊天显示的标签样式和Markdown支持"""
        # 基础标签
        self.chat_display.tag_configure("user", foreground="#0066cc", font=("Microsoft YaHei", 10, "bold"))
        self.chat_display.tag_configure("assistant", foreground="#00aa00", font=("Microsoft YaHei", 10))
        self.chat_display.tag_configure("error", foreground="#cc0000", font=("Microsoft YaHei", 10))
        self.chat_display.tag_configure("timestamp", foreground="#888888", font=("Microsoft YaHei", 8))
        self.chat_display.tag_configure("system", foreground="#666666", font=("Microsoft YaHei", 9, "italic"))
        
        # Markdown标签样式
        self.chat_display.tag_configure("h1", font=("Microsoft YaHei", 16, "bold"), spacing1=10, spacing3=5)
        self.chat_display.tag_configure("h2", font=("Microsoft YaHei", 14, "bold"), spacing1=8, spacing3=4)
        self.chat_display.tag_configure("h3", font=("Microsoft YaHei", 12, "bold"), spacing1=6, spacing3=3)
        self.chat_display.tag_configure("bold", font=("Microsoft YaHei", 10, "bold"))
        self.chat_display.tag_configure("italic", font=("Microsoft YaHei", 10, "italic"))
        self.chat_display.tag_configure("code_inline", font=("Consolas", 9), background="#f6f8fa")
        self.chat_display.tag_configure("code_block", font=("Consolas", 9), background="#f6f8fa", lmargin1=20, lmargin2=20)
        self.chat_display.tag_configure("list_item", lmargin1=20, lmargin2=30)
        self.chat_display.tag_configure("table_header", font=("Microsoft YaHei", 10, "bold"), background="#f0f0f0")
        self.chat_display.tag_configure("table_cell", font=("Microsoft YaHei", 10))
        self.chat_display.tag_configure("quote", font=("Microsoft YaHei", 10, "italic"), foreground="#666666", lmargin1=20, lmargin2=20)

    def parse_and_insert_markdown(self, content, base_tag="assistant"):
        """解析并插入Markdown格式的内容"""
        self.chat_display.config(state=tk.NORMAL)
        
        lines = content.split('\n')
        i = 0
        
        while i < len(lines):
            line = lines[i]
            
            # 处理标题
            if line.startswith('### '):
                self.chat_display.insert(tk.END, line[4:] + '\n', ("h3", base_tag))
            elif line.startswith('## '):
                self.chat_display.insert(tk.END, line[3:] + '\n', ("h2", base_tag))
            elif line.startswith('# '):
                self.chat_display.insert(tk.END, line[2:] + '\n', ("h1", base_tag))
            
            # 处理代码块
            elif line.strip().startswith('```'):
                # 找到代码块结束
                code_lines = []
                i += 1
                while i < len(lines) and not lines[i].strip().startswith('```'):
                    code_lines.append(lines[i])
                    i += 1
                
                if code_lines:
                    self.chat_display.insert(tk.END, '\n'.join(code_lines) + '\n', ("code_block", base_tag))
            
            # 处理表格
            elif '|' in line and line.strip().startswith('|') and line.strip().endswith('|'):
                # 这是表格行
                table_lines = [line]
                # 收集连续的表格行
                while i + 1 < len(lines) and '|' in lines[i + 1] and lines[i + 1].strip().startswith('|'):
                    i += 1
                    table_lines.append(lines[i])
                
                # 渲染表格
                for j, table_line in enumerate(table_lines):
                    # 跳过分隔行（包含 --- 的行）
                    if '---' in table_line:
                        continue
                        
                    cells = [cell.strip() for cell in table_line.split('|')[1:-1]]  # 去掉首尾的空元素
                    cell_content = ' | '.join(cells)
                    
                    if j == 0:  # 表头
                        self.chat_display.insert(tk.END, cell_content + '\n', ("table_header", base_tag))
                    else:
                        self.chat_display.insert(tk.END, cell_content + '\n', ("table_cell", base_tag))
            
            # 处理引用
            elif line.startswith('> '):
                self.chat_display.insert(tk.END, line[2:] + '\n', ("quote", base_tag))
            
            # 处理列表
            elif re.match(r'^[\-\*\+]\s+', line) or re.match(r'^\d+\.\s+', line):
                # 提取列表项内容
                match = re.match(r'^([\-\*\+]|\d+\.)\s+(.*)', line)
                if match:
                    bullet, content_text = match.groups()
                    self.chat_display.insert(tk.END, f"• {content_text}\n", ("list_item", base_tag))
                else:
                    self.chat_display.insert(tk.END, line + '\n', base_tag)
            
            # 处理普通段落（包含行内格式）
            else:
                self.parse_inline_markdown(line + '\n', base_tag)
            
            i += 1
        
        self.chat_display.config(state=tk.DISABLED)

    def parse_inline_markdown(self, text, base_tag):
        """解析行内Markdown格式"""
        # 处理粗体 **text**
        parts = re.split(r'(\*\*[^*]+\*\*)', text)
        for part in parts:
            if part.startswith('**') and part.endswith('**'):
                self.chat_display.insert(tk.END, part[2:-2], ("bold", base_tag))
            else:
                # 处理斜体 *text*
                italic_parts = re.split(r'(\*[^*]+\*)', part)
                for italic_part in italic_parts:
                    if italic_part.startswith('*') and italic_part.endswith('*') and len(italic_part) > 2:
                        self.chat_display.insert(tk.END, italic_part[1:-1], ("italic", base_tag))
                    else:
                        # 处理行内代码 `code`
                        code_parts = re.split(r'(`[^`]+`)', italic_part)
                        for code_part in code_parts:
                            if code_part.startswith('`') and code_part.endswith('`'):
                                self.chat_display.insert(tk.END, code_part[1:-1], ("code_inline", base_tag))
                            else:
                                self.chat_display.insert(tk.END, code_part, base_tag)

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
            self.chat_display.tag_configure("table_header", background="#404040")
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
            response = completion.choices[0].message.content
            
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
