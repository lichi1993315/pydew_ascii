#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
PyDew 游戏启动脚本
放在项目根目录，方便用户直接运行游戏
"""

import sys
import os
import traceback

# 确保可以导入src目录下的包
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

def main():
    """启动游戏"""
    try:
        # 尝试导入并运行游戏（基于PROJECT_STRUCTURE_GUIDE.md结构）
        from main import main as game_main
        game_main()
    except ImportError as e:
        print("❌ 导入错误:", e)
        print("\n完整错误信息:")
        traceback.print_exc()
        print("\n请确保已安装游戏依赖:")
        print("  pip install -r requirements.txt")
        print("或者进行开发安装:")
        print("  pip install -e .")
        sys.exit(1)
    except Exception as e:
        print("❌ 游戏启动失败:", e)
        print("\n完整错误信息:")
        traceback.print_exc()
        sys.exit(1)

if __name__ == '__main__':
    main() 