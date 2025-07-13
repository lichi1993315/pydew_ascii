#!/usr/bin/env python3
"""
Emoji着色功能测试脚本
展示如何使用EmojiColorizer来为emoji着色
"""

import pygame
import sys
import os

# 添加src目录到路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from src.utils.emoji_colorizer import EmojiColorizer

def test_emoji_colorizer():
    """测试emoji着色功能"""
    
    # 初始化pygame
    pygame.init()
    screen = pygame.display.set_mode((1000, 700))
    pygame.display.set_caption("Emoji着色测试")
    
    # 尝试加载emoji字体
    font = None
    font_paths = [
        "/System/Library/Fonts/Apple Color Emoji.ttc",  # macOS
        "C:/Windows/Fonts/seguiemj.ttf",                # Windows
        "/usr/share/fonts/truetype/noto/NotoColorEmoji.ttf",  # Linux
    ]
    
    for font_path in font_paths:
        try:
            if os.path.exists(font_path):
                font = pygame.font.Font(font_path, 48)
                print(f"✅ 成功加载emoji字体: {font_path}")
                break
        except:
            continue
    
    if not font:
        print("⚠️ 未找到emoji字体，使用默认字体")
        font = pygame.font.Font(None, 48)
    
    # 获取预定义颜色
    mood_colors = EmojiColorizer.get_mood_colors()
    
    # 测试emoji列表
    test_emojis = [
        ("🐱", "猫咪"),
        ("🐟", "鱼"),
        ("🌰", "栗子"),
        ("❤️", "心"),
        ("⭐", "星星"),
        ("🔥", "火"),
    ]
    
    # 为每个emoji创建不同颜色的变体
    emoji_surfaces = []
    
    for emoji, name in test_emojis:
        # 原版emoji
        try:
            original = font.render(emoji, True, (255, 255, 255))
        except:
            original = font.render("?", True, (255, 255, 255))
        
        # 创建不同心情的颜色变体
        variants = []
        colors_to_test = ['happy', 'sad', 'angry', 'calm', 'fire', 'ice']
        
        for mood in colors_to_test:
            if mood in mood_colors:
                try:
                    colored = EmojiColorizer.colorize_emoji(
                        font, emoji, mood_colors[mood]
                    )
                    variants.append((colored, mood))
                except Exception as e:
                    print(f"❌ {emoji}着色失败({mood}): {e}")
                    # 创建一个备用的彩色矩形
                    colored = pygame.Surface((48, 48))
                    colored.fill(mood_colors[mood])
                    variants.append((colored, mood))
        
        emoji_surfaces.append((original, variants, name))
    
    # 创建界面字体
    ui_font = pygame.font.Font(None, 24)
    title_font = pygame.font.Font(None, 36)
    
    # 主循环
    clock = pygame.time.Clock()
    running = True
    
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False
        
        # 清屏
        screen.fill((30, 30, 30))
        
        # 绘制标题
        title_text = title_font.render("Emoji着色效果展示", True, (255, 255, 255))
        screen.blit(title_text, (20, 20))
        
        subtitle_text = ui_font.render("按ESC退出", True, (200, 200, 200))
        screen.blit(subtitle_text, (20, 60))
        
        # 绘制emoji和它们的颜色变体
        y_offset = 100
        
        for original, variants, name in emoji_surfaces:
            # 绘制原版emoji和名称
            screen.blit(original, (20, y_offset))
            name_text = ui_font.render(f"{name} (原版)", True, (255, 255, 255))
            screen.blit(name_text, (80, y_offset + 15))
            
            # 绘制颜色变体
            x_offset = 200
            for colored_surface, mood in variants:
                screen.blit(colored_surface, (x_offset, y_offset))
                mood_text = ui_font.render(mood, True, (200, 200, 200))
                screen.blit(mood_text, (x_offset, y_offset + 55))
                x_offset += 80
            
            y_offset += 100
        
        # 绘制说明文字
        info_lines = [
            "这个演示展示了如何使用pygame混合模式为emoji着色",
            "不同的心情颜色：happy(黄), sad(蓝), angry(红), calm(绿), fire(橙红), ice(冰蓝)",
            "类似sky.py的全局着色，但这里是针对单个emoji表面的着色",
            "可以用于游戏中根据状态/稀有度/心情改变emoji颜色"
        ]
        
        info_y = 620
        for line in info_lines:
            info_text = ui_font.render(line, True, (180, 180, 180))
            screen.blit(info_text, (20, info_y))
            info_y += 20
        
        pygame.display.flip()
        clock.tick(60)
    
    pygame.quit()

if __name__ == "__main__":
    test_emoji_colorizer() 