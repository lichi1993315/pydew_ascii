#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试猫咪emoji渲染
"""

import pygame
import sys
import os

# 添加代码路径
sys.path.append('code')

from src.utils.font_manager import FontManager
from src.rendering.ascii_renderer import ASCIIRenderer

def test_cat_emoji_rendering():
    """测试猫咪emoji渲染"""
    pygame.init()
    
    # 创建测试窗口
    screen = pygame.display.set_mode((600, 400))
    pygame.display.set_caption('Cat Emoji Rendering Test')
    
    # 初始化字体管理器和ASCII渲染器
    font_manager = FontManager.get_instance()
    ascii_renderer = ASCIIRenderer()
    
    # 测试的猫咪emoji
    cat_emojis = ["🐈", "🐱", "😺", "😸", "😻", "😽"]
    
    print("🐈 测试猫咪emoji渲染:")
    print("=" * 50)
    
    # 测试emoji字体加载
    emoji_font = font_manager.load_emoji_font(32, "test_emoji")
    print(f"Emoji字体加载结果: {emoji_font is not None}")
    
    # 测试每个emoji的渲染
    for i, emoji in enumerate(cat_emojis):
        try:
            test_surface = emoji_font.render(emoji, True, (255, 255, 255))
            if test_surface.get_width() > 0:
                print(f"✅ {emoji} - 渲染成功 (尺寸: {test_surface.get_size()})")
            else:
                print(f"❌ {emoji} - 渲染失败 (宽度为0)")
        except Exception as e:
            print(f"❌ {emoji} - 渲染异常: {e}")
    
    # 创建可视化测试
    running = True
    clock = pygame.time.Clock()
    
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False
        
        # 清屏
        screen.fill((50, 50, 80))
        
        # 绘制标题
        title_font = font_manager.load_chinese_font(24, "test_title")
        title_text = title_font.render("猫咪Emoji渲染测试", True, (255, 255, 255))
        screen.blit(title_text, (20, 20))
        
        # 绘制说明
        desc_font = font_manager.load_chinese_font(16, "test_desc")
        desc_text = desc_font.render("使用ASCII渲染器渲染猫咪emoji - 按ESC退出", True, (200, 200, 200))
        screen.blit(desc_text, (20, 60))
        
        # 使用ASCII渲染器绘制emoji
        y_start = 100
        for i, emoji in enumerate(cat_emojis):
            x = 50 + (i % 3) * 150
            y = y_start + (i // 3) * 100
            
            # 使用ASCII渲染器
            ascii_renderer.render_ascii(screen, emoji, (255, 200, 100), (x, y), 48)
            
            # 绘制emoji标签
            label_text = desc_font.render(f"Cat {i+1}", True, (200, 200, 200))
            screen.blit(label_text, (x, y + 60))
        
        # 绘制原始字符对比
        contrast_y = 280
        contrast_text = desc_font.render("原始字符渲染对比:", True, (255, 255, 255))
        screen.blit(contrast_text, (20, contrast_y))
        
        for i, emoji in enumerate(cat_emojis[:3]):
            x = 50 + i * 100
            y = contrast_y + 30
            
            try:
                # 直接使用emoji字体渲染
                emoji_surface = emoji_font.render(emoji, True, (255, 150, 150))
                screen.blit(emoji_surface, (x, y))
            except:
                # 失败时显示错误
                error_text = desc_font.render("ERROR", True, (255, 100, 100))
                screen.blit(error_text, (x, y))
        
        pygame.display.flip()
        clock.tick(60)
    
    pygame.quit()
    print("\n测试完成!")

if __name__ == "__main__":
    test_cat_emoji_rendering()