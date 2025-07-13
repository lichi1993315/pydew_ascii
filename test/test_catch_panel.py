#!/usr/bin/env python3
"""
测试鱼获面板功能
"""

import pygame
import sys
import os

# 添加src目录到Python路径
current_dir = os.path.dirname(os.path.abspath(__file__))
src_dir = os.path.join(current_dir, 'src')
sys.path.insert(0, src_dir)

from src.ui.catch_result_panel import CatchResultPanel

def test_catch_panel():
    """测试鱼获面板"""
    pygame.init()
    
    # 设置屏幕
    screen_width = 800
    screen_height = 600
    screen = pygame.display.set_mode((screen_width, screen_height))
    pygame.display.set_caption("鱼获面板测试")
    clock = pygame.time.Clock()
    
    # 创建鱼获面板实例
    catch_panel = CatchResultPanel(screen_width, screen_height)
    
    # 测试数据
    test_fish = {
        'type': 'fish',
        'name': '黄金鲤鱼',
        'ascii_char': '🐟',
        'rarity': 'rare',
        'length': 45,
        'price': 150,
        'id': 'golden_carp'
    }
    
    test_cat = {
        'type': 'cat',
        'name': '小橘',
        'ascii_char': '🐱',
        'rarity': 'epic',
        'breed': '橘猫',
        'personality': '活泼好动，喜欢到处跑跳，很喜欢和人玩耍',
        'color': (255, 200, 100),
        'rarity_name': '史诗'
    }
    
    current_test = 0
    test_data = [test_fish, test_cat]
    
    print("🎣 鱼获面板测试开始！")
    print("操作说明:")
    print("- 数字键1：显示鱼类面板")
    print("- 数字键2：显示猫咪面板")
    print("- 空格键/回车/ESC：关闭面板")
    print("- 鼠标点击面板外区域：关闭面板")
    print("- Q键退出测试")
    
    running = True
    while running:
        dt = clock.tick(60) / 1000.0  # 转换为秒
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_q:
                    running = False
                elif event.key == pygame.K_1:
                    # 显示鱼类面板
                    catch_panel.show_catch_result(test_fish)
                    print("🐟 显示鱼类面板")
                elif event.key == pygame.K_2:
                    # 显示猫咪面板
                    catch_panel.show_catch_result(test_cat)
                    print("🐱 显示猫咪面板")
            
            # 让面板处理输入
            if catch_panel.handle_input(event):
                print("📝 面板已关闭")
        
        # 更新面板
        catch_panel.update(dt)
        
        # 渲染
        screen.fill((50, 100, 150))  # 蓝色背景代表水
        
        # 绘制说明文字
        font = pygame.font.Font(None, 24)
        instructions = [
            "鱼获面板测试",
            "按 1 - 显示鱼类面板",
            "按 2 - 显示猫咪面板", 
            "按 Q - 退出测试",
            "",
            "面板激活时:",
            "空格/回车/ESC - 关闭面板",
            "点击面板外区域 - 关闭面板"
        ]
        
        y_offset = 20
        for instruction in instructions:
            if instruction:  # 跳过空行
                text = font.render(instruction, True, (255, 255, 255))
                screen.blit(text, (20, y_offset))
            y_offset += 25
        
        # 渲染面板
        catch_panel.render(screen)
        
        pygame.display.flip()
    
    pygame.quit()
    print("测试结束")

if __name__ == "__main__":
    test_catch_panel()