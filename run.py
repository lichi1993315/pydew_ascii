#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
PyDew 游戏启动脚本
放在项目根目录，方便用户直接运行游戏
"""

import sys
import os
import traceback

# 设置Windows控制台UTF-8编码，解决emoji字符显示问题
if os.name == 'nt':  # Windows系统
    try:
        # 设置控制台代码页为UTF-8
        os.system('chcp 65001 > nul')
        # 设置Python输出编码为UTF-8
        sys.stdout.reconfigure(encoding='utf-8')
        sys.stderr.reconfigure(encoding='utf-8')
    except Exception as e:
        pass  # 忽略设置失败的情况

# 设置UTF-8编码输出，避免emoji显示问题
import locale
if sys.platform.startswith('win'):
    try:
        # 在Windows上尝试设置UTF-8编码
        locale.setlocale(locale.LC_ALL, 'en_US.UTF-8')
    except:
        try:
            locale.setlocale(locale.LC_ALL, 'C.UTF-8')
        except:
            pass  # 如果都失败，继续使用默认编码

# 确保可以导入src目录下的包
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

def main():
    """启动游戏"""
    try:
        # 尝试导入并运行游戏（基于PROJECT_STRUCTURE_GUIDE.md结构）
        from main import main as game_main
        game_main()
    except ImportError as e:
        print("ERROR: Import failed:", str(e))
        print("\nFull error details:")
        traceback.print_exc()
        print("\nPlease install game dependencies:")
        print("  pip install -r requirements.txt")
        print("Or install in development mode:")
        print("  pip install -e .")
        sys.exit(1)
    except Exception as e:
        print("ERROR: Game failed to start:", str(e))
        print("\nFull error details:")
        traceback.print_exc()
        sys.exit(1)

if __name__ == '__main__':
    main() 