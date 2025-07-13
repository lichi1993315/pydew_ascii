#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试文本换行功能
"""

import pygame
import sys
import os

# 添加代码路径
sys.path.append('code')

from src.utils.font_manager import FontManager

def test_text_wrapping():
    """测试文本换行功能"""
    pygame.init()
    
    # 创建测试窗口
    screen = pygame.display.set_mode((600, 400))
    pygame.display.set_caption('Text Wrapping Test')
    
    # 初始化字体
    font_manager = FontManager.get_instance()
    font = font_manager.load_chinese_font(16, "test_font")
    
    # 测试文本
    test_texts = [
        "小黑对世界充满好奇，总是想要探索新的地方和事物。喜欢冒险，但有时会因为太好奇而惹麻烦。",
        "这是一段很长的中文文本，用来测试文本换行功能是否正常工作。",
        "Test English text wrapping functionality with some longer sentences."
    ]
    
    # 测试宽度
    test_widths = [200, 250, 300]
    
    print("🔤 文本换行测试")
    print("=" * 50)
    
    for i, text in enumerate(test_texts):
        for j, width in enumerate(test_widths):
            # 测试文本宽度
            full_width = font.size(text)[0]
            print(f"文本 {i+1}, 宽度限制 {width}:")
            print(f"  原文: {text}")
            print(f"  原始宽度: {full_width}")
            
            # 简单的换行算法测试
            words = text.split()
            lines = []
            current_line = ""
            
            for word in words:
                test_line = current_line + (" " if current_line else "") + word
                if font.size(test_line)[0] <= width:
                    current_line = test_line
                else:
                    if current_line:
                        lines.append(current_line)
                    current_line = word
            
            if current_line:
                lines.append(current_line)
            
            print(f"  分割成 {len(lines)} 行:")
            for k, line in enumerate(lines):
                line_width = font.size(line)[0]
                print(f"    第{k+1}行: '{line}' (宽度: {line_width})")
            
            print()
    
    print("✅ 文本换行测试完成")
    print("现在请运行游戏测试猫咪详情UI中的文本换行")
    
    pygame.quit()

if __name__ == "__main__":
    test_text_wrapping()