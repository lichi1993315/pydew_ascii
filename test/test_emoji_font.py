#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试字体是否支持emoji渲染
"""

import pygame
import sys
import os

def test_emoji_rendering():
    """测试emoji渲染"""
    pygame.init()
    
    # 创建测试窗口
    screen = pygame.display.set_mode((400, 300))
    pygame.display.set_caption('Emoji Font Test')
    
    # 测试的emoji
    test_emoji = "🐈"
    test_chars = ["🐱", "😺", "😸", "😻", "😽", "🐈"]
    
    # 字体路径
    font_path = "font/NotoEmoji-Bold.ttf"
    
    # 检查字体文件是否存在
    if not os.path.exists(font_path):
        print(f"❌ 字体文件不存在: {font_path}")
        return False
    
    try:
        # 加载字体
        font = pygame.font.Font(font_path, 32)
        print(f"✅ 成功加载字体: {font_path}")
        
        # 测试单个emoji
        print(f"\n🔍 测试emoji: {test_emoji}")
        
        try:
            # 尝试渲染emoji
            surface = font.render(test_emoji, True, (255, 255, 255))
            print(f"✅ 成功渲染emoji: {test_emoji}")
            print(f"   渲染尺寸: {surface.get_size()}")
            
            # 检查渲染结果是否为空白
            if surface.get_width() > 0 and surface.get_height() > 0:
                print("✅ 渲染结果有有效尺寸")
            else:
                print("❌ 渲染结果尺寸为0")
                
        except Exception as e:
            print(f"❌ 渲染emoji失败: {e}")
            return False
        
        # 测试所有猫咪emoji
        print(f"\n🔍 测试所有猫咪emoji:")
        success_count = 0
        
        for emoji in test_chars:
            try:
                surface = font.render(emoji, True, (255, 255, 255))
                if surface.get_width() > 0 and surface.get_height() > 0:
                    print(f"✅ {emoji} - 成功 (尺寸: {surface.get_size()})")
                    success_count += 1
                else:
                    print(f"❌ {emoji} - 失败 (尺寸为0)")
            except Exception as e:
                print(f"❌ {emoji} - 异常: {e}")
        
        print(f"\n📊 测试结果: {success_count}/{len(test_chars)} 个emoji成功渲染")
        
        # 创建可视化测试
        screen.fill((50, 50, 50))
        
        # 渲染测试文本
        title_font = pygame.font.Font(None, 24)
        title_text = title_font.render("Emoji Font Test - AlimamaShuHeiTi-Bold.ttf", True, (255, 255, 255))
        screen.blit(title_text, (10, 10))
        
        # 渲染所有测试emoji
        y_offset = 50
        for i, emoji in enumerate(test_chars):
            try:
                emoji_surface = font.render(emoji, True, (255, 200, 100))
                screen.blit(emoji_surface, (50 + i * 50, y_offset))
                
                # 显示emoji代码
                code_text = title_font.render(f"U+{ord(emoji):04X}", True, (200, 200, 200))
                screen.blit(code_text, (30 + i * 50, y_offset + 40))
                
            except Exception as e:
                # 如果渲染失败，显示错误标记
                error_text = title_font.render("❌", True, (255, 100, 100))
                screen.blit(error_text, (50 + i * 50, y_offset))
        
        # 显示说明
        info_text = title_font.render("Press SPACE to continue, ESC to quit", True, (200, 200, 200))
        screen.blit(info_text, (10, 250))
        
        pygame.display.flip()
        
        # 等待用户输入
        waiting = True
        while waiting:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    waiting = False
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        waiting = False
                    elif event.key == pygame.K_SPACE:
                        waiting = False
        
        return success_count > 0
        
    except Exception as e:
        print(f"❌ 加载字体失败: {e}")
        return False
    
    finally:
        pygame.quit()

def test_fallback_fonts():
    """测试系统备用字体"""
    pygame.init()
    
    print("\n🔍 测试系统备用字体:")
    
    # 常见的支持emoji的字体
    fallback_fonts = [
        None,  # 系统默认字体
        "segoe-ui-emoji",
        "apple-color-emoji", 
        "noto-color-emoji",
        "symbola",
    ]
    
    test_emoji = "🐈"
    
    for font_name in fallback_fonts:
        try:
            if font_name is None:
                font = pygame.font.Font(None, 32)
                font_desc = "系统默认字体"
            else:
                font = pygame.font.SysFont(font_name, 32)
                font_desc = font_name
            
            # 测试渲染
            surface = font.render(test_emoji, True, (255, 255, 255))
            if surface.get_width() > 0 and surface.get_height() > 0:
                print(f"✅ {font_desc} - 支持emoji (尺寸: {surface.get_size()})")
            else:
                print(f"❌ {font_desc} - 不支持emoji")
                
        except Exception as e:
            print(f"❌ {font_desc} - 加载失败: {e}")
    
    pygame.quit()

if __name__ == "__main__":
    print("🐈 Emoji字体支持测试")
    print("=" * 50)
    
    # 测试主要字体
    main_result = test_emoji_rendering()
    
    # 测试备用字体
    test_fallback_fonts()
    
    print("\n" + "=" * 50)
    if main_result:
        print("✅ AlimamaShuHeiTi-Bold.ttf 支持猫咪emoji渲染")
    else:
        print("❌ AlimamaShuHeiTi-Bold.ttf 不支持猫咪emoji渲染")
        print("💡 建议使用系统备用字体或回退到ASCII字符")