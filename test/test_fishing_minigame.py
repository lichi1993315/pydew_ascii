#!/usr/bin/env python3
"""
测试钓鱼小游戏功能
"""

import pygame
import sys
import os

# 添加src目录到Python路径
current_dir = os.path.dirname(os.path.abspath(__file__))
src_dir = os.path.join(current_dir, 'src')
sys.path.insert(0, src_dir)

from src.ui.fishing_minigame import FishingMinigame

def test_fishing_minigame():
    """测试钓鱼小游戏"""
    pygame.init()
    
    # 设置屏幕
    screen_width = 800
    screen_height = 600
    screen = pygame.display.set_mode((screen_width, screen_height))
    pygame.display.set_caption("钓鱼小游戏测试")
    clock = pygame.time.Clock()
    
    # 创建钓鱼小游戏实例
    fishing_game = FishingMinigame(screen_width, screen_height)
    
    # 启动游戏
    fishing_game.start_game()
    
    print("🎣 钓鱼小游戏测试开始！")
    print("操作说明:")
    print("- 鱼处于力竭状态(蓝色)时：按住鼠标左键收线")
    print("- 鱼处于挣扎状态(红色)时：不要按鼠标，让体力恢复")
    print("- 目标：将鱼拉到进度条顶部的绿色区域")
    print("- 注意：体力耗尽会失败！")
    print("按ESC退出测试")
    
    running = True
    while running:
        dt = clock.tick(60) / 1000.0  # 转换为秒
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False
                elif event.key == pygame.K_r:
                    # R键重新开始游戏
                    fishing_game.start_game()
                    print("🔄 游戏重新开始！")
            
            # 让钓鱼小游戏处理输入
            fishing_game.handle_input(event)
        
        # 更新游戏逻辑
        fishing_game.update(dt)
        
        # 检查游戏结果
        result = fishing_game.get_result()
        if result:
            if result == "success":
                print("🎉 恭喜！钓鱼成功！")
                print("按R键重新开始，ESC退出")
            elif result == "failure":
                print("💥 失败！体力耗尽...")
                print("按R键重新开始，ESC退出")
        
        # 渲染
        screen.fill((50, 100, 150))  # 蓝色背景代表水
        fishing_game.render(screen)
        
        # 添加说明文字
        font = pygame.font.Font(None, 24)
        if fishing_game.is_active:
            instruction = "按住鼠标收线 | ESC退出"
        else:
            instruction = "按R重新开始 | ESC退出"
        
        text = font.render(instruction, True, (255, 255, 255))
        screen.blit(text, (10, 10))
        
        # 显示游戏状态
        if fishing_game.is_active:
            fish_pos_text = f"鱼的位置: {fishing_game.fish_position:.2f}"
            stamina_text = f"体力: {fishing_game.stamina:.2f}"
            state_text = f"鱼的状态: {fishing_game.fish_state}"
            
            y_offset = 40
            for text_content in [fish_pos_text, stamina_text, state_text]:
                text_surface = font.render(text_content, True, (255, 255, 255))
                screen.blit(text_surface, (10, y_offset))
                y_offset += 25
        
        pygame.display.flip()
    
    pygame.quit()
    print("测试结束")

if __name__ == "__main__":
    test_fishing_minigame()