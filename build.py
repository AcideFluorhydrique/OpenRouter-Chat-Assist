# -*- coding: utf-8 -*-
"""
Created on Thu Aug  14 14:43:23 2025

@author: GeoYWang
"""

# build.py - 构建脚本

import os
import subprocess
import sys
def install_requirements():
    """安装依赖包"""
    print("正在安装依赖包...")
    try:
        # 修改：使用 sys.executable 代替硬编码的 "python3"，确保使用当前 Python 环境调用 pip
        subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])
        print("依赖包安装完成!")
    except subprocess.CalledProcessError as e:
        print(f"依赖包安装失败: {e}")
        return False
    return True

def build_executable():
    """构建可执行文件"""
    print("正在构建可执行文件...")
    
    # PyInstaller 命令参数
    cmd = [
        "pyinstaller",  # 假设 pyinstaller 已安装到 PATH；如果失败，可改为 [sys.executable, "-m", "PyInstaller", ...]
        "--onefile",                    # 打包成单个文件
        "--windowed",                   # Windows下不显示控制台窗口
        "--name=OpenRouterChat",        # 可执行文件名称
        "--distpath=dist",              # 输出目录
        "--workpath=build",             # 临时文件目录  
        "--specpath=.",                 # spec文件目录
        # "--add-data=chat_config.json;.", # 配置文件会自动创建
        "--icon=NONE",                  # 无图标
        "openrouter_chat.py"            # 主文件名
    ]
    
    try:
        subprocess.check_call(cmd)
        print("可执行文件构建完成!")
        print("可执行文件位置: dist/OpenRouterChat.exe")
        return True
    except subprocess.CalledProcessError as e:
        print(f"构建失败: {e}")
        return False

def main():
    print("OpenRouter 聊天软件构建工具")
    print("=" * 40)
    
    # 检查主文件是否存在
    if not os.path.exists("openrouter_chat.py"):
        print("错误: 找不到 openrouter_chat.py 文件")
        print("请确保该文件与构建脚本在同一目录下")
        return
    
    # 安装依赖
    if not install_requirements():
        return
    
    # 构建可执行文件
    if build_executable():
        print("\n构建成功!")
        print("你可以在 dist/ 目录下找到 OpenRouterChat.exe")
        print("这是一个 portable 版本，可以直接运行，无需安装 Python")
    else:
        print("\n构建失败!")

if __name__ == "__main__":
    main()


# 另存为 build.bat (Windows 批处理文件)
"""
@echo off
echo 正在构建 OpenRouter 聊天软件...
python build.py
pause
"""