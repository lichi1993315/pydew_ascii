#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
猫咪Spawn位置可视化调试工具
帮助可视化查看猫咪的生成位置是否合理
"""

import sys
sys.path.append('code')

import pygame
import math
from cat_npc import CatManager
from ascii_sprites import ASCIIGeneric
from settings import *

class SpawnVisualizer:
    """Spawn位置可视化器"""
    
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((1600, 900))
        pygame.display.set_caption("猫咪Spawn位置可视化器")
        self.clock = pygame.time.Clock()
        self.font = pygame.font.Font(None, 24)
        
        # 缩放因子（用于在小屏幕上显示大地图）
        self.scale = 0.5
        self.map_size = 1600
        self.scaled_size = int(self.map_size * self.scale)
        
        # 颜色定义
        self.colors = {
            'background': (50, 50, 50),
            'player': (0, 255, 0),
            'cat': (255, 100, 100),
            'obstacle': (100, 100, 100),
            'spawn_area': (255, 255, 0, 50),
            'text': (255, 255, 255),
            'grid': (80, 80, 80)
        }
        
        # 游戏对象
        self.player_pos = (800, 800)
        self.cats = []
        self.obstacles = []
        
        # 创建测试环境
        self.setup_test_environment()
    
    def setup_test_environment(self):
        """设置测试环境"""
        # 创建精灵组
        self.all_sprites = pygame.sprite.Group()
        self.collision_sprites = pygame.sprite.Group()
        self.npc_sprites = pygame.sprite.Group()
        
        # 创建障碍物
        obstacle_layouts = [
            # 房屋1
            [(1300, 1000), (1350, 1000), (1400, 1000), (1450, 1000),
             (1300, 1050), (1450, 1050),
             (1300, 1100), (1450, 1100),
             (1300, 1150), (1350, 1150), (1400, 1150), (1450, 1150)],
            
            # 房屋2
            [(700, 600), (750, 600), (800, 600),
             (700, 650), (800, 650),
             (700, 700), (750, 700), (800, 700)],
            
            # 围栏
            [(400, 400), (450, 400), (500, 400), (550, 400),
             (400, 450), (550, 450),
             (400, 500), (550, 500),
             (400, 550), (450, 550), (500, 550), (550, 550)],
        ]
        
        for layout in obstacle_layouts:
            for x, y in layout:
                obstacle = ASCIIGeneric((x, y), "wall", [self.all_sprites, self.collision_sprites])
                self.obstacles.append((x, y))
        
        print(f"创建了 {len(self.obstacles)} 个障碍物")
    
    def spawn_cats(self):
        """生成猫咪"""
        # 清除现有猫咪
        for cat in self.cats:
            if hasattr(cat, 'kill'):
                cat.kill()
        self.cats.clear()
        
        # 创建猫咪管理器
        cat_manager = CatManager()
        cat_manager.create_cats(
            self.all_sprites,
            self.collision_sprites,
            self.npc_sprites,
            None,
            player_pos=self.player_pos
        )
        
        self.cats = cat_manager.cats
        print(f"生成了 {len(self.cats)} 只猫咪")
    
    def world_to_screen(self, world_pos):
        """世界坐标转屏幕坐标"""
        x, y = world_pos
        screen_x = int(x * self.scale)
        screen_y = int(y * self.scale)
        return (screen_x, screen_y)
    
    def screen_to_world(self, screen_pos):
        """屏幕坐标转世界坐标"""
        x, y = screen_pos
        world_x = int(x / self.scale)
        world_y = int(y / self.scale)
        return (world_x, world_y)
    
    def draw_grid(self):
        """绘制网格"""
        grid_size = int(64 * self.scale)  # TILE_SIZE缩放
        
        for x in range(0, self.scaled_size, grid_size):
            pygame.draw.line(self.screen, self.colors['grid'], 
                           (x, 0), (x, self.scaled_size), 1)
        
        for y in range(0, self.scaled_size, grid_size):
            pygame.draw.line(self.screen, self.colors['grid'], 
                           (0, y), (self.scaled_size, y), 1)
    
    def draw_obstacles(self):
        """绘制障碍物"""
        for obstacle_pos in self.obstacles:
            screen_pos = self.world_to_screen(obstacle_pos)
            size = int(TILE_SIZE * self.scale)
            rect = pygame.Rect(screen_pos[0], screen_pos[1], size, size)
            pygame.draw.rect(self.screen, self.colors['obstacle'], rect)
    
    def draw_spawn_area(self):
        """绘制spawn区域"""
        player_screen = self.world_to_screen(self.player_pos)
        
        # 绘制最小和最大spawn距离
        min_radius = int(100 * self.scale)  # 最小距离
        max_radius = int(400 * self.scale)  # 最大距离
        
        # 创建透明表面
        temp_surface = pygame.Surface((self.scaled_size, self.scaled_size), pygame.SRCALPHA)
        
        # 绘制环形spawn区域
        pygame.draw.circle(temp_surface, self.colors['spawn_area'], 
                         player_screen, max_radius)
        pygame.draw.circle(temp_surface, self.colors['background'], 
                         player_screen, min_radius)
        
        self.screen.blit(temp_surface, (0, 0))
    
    def draw_player(self):
        """绘制玩家"""
        screen_pos = self.world_to_screen(self.player_pos)
        pygame.draw.circle(self.screen, self.colors['player'], screen_pos, 8)
        
        # 绘制玩家标签
        text = self.font.render("Player", True, self.colors['text'])
        self.screen.blit(text, (screen_pos[0] + 10, screen_pos[1] - 10))
    
    def draw_cats(self):
        """绘制猫咪"""
        for i, cat in enumerate(self.cats):
            cat_pos = cat.rect.center
            screen_pos = self.world_to_screen(cat_pos)
            
            # 绘制猫咪
            pygame.draw.circle(self.screen, self.colors['cat'], screen_pos, 6)
            
            # 绘制到玩家的连线
            player_screen = self.world_to_screen(self.player_pos)
            pygame.draw.line(self.screen, (100, 100, 255), 
                           player_screen, screen_pos, 1)
            
            # 绘制距离文本
            distance = math.sqrt((cat_pos[0] - self.player_pos[0])**2 + 
                               (cat_pos[1] - self.player_pos[1])**2)
            distance_text = f"{distance:.0f}"
            text_surface = self.font.render(distance_text, True, self.colors['text'])
            self.screen.blit(text_surface, (screen_pos[0] + 8, screen_pos[1] - 8))
    
    def draw_info(self):
        """绘制信息面板"""
        info_x = self.scaled_size + 10
        info_texts = [
            "猫咪Spawn可视化器",
            "",
            f"玩家位置: {self.player_pos}",
            f"猫咪数量: {len(self.cats)}",
            "",
            "操作说明:",
            "点击 - 移动玩家位置",
            "SPACE - 重新生成猫咪",
            "R - 重置玩家到中心",
            "Q - 退出",
            "",
            "图例:",
            "🟢 绿色圆圈 - 玩家",
            "🔴 红色圆圈 - 猫咪",
            "⬜ 灰色方块 - 障碍物",
            "🟡 黄色区域 - 生成范围",
            "💙 蓝线 - 玩家到猫咪距离",
        ]
        
        for i, text in enumerate(info_texts):
            if text.startswith("🟢") or text.startswith("🔴") or text.startswith("⬜") or text.startswith("🟡") or text.startswith("💙"):
                color = self.colors['text']
            elif text == "猫咪Spawn可视化器":
                color = (255, 255, 0)
            elif text == "操作说明:" or text == "图例:":
                color = (150, 255, 150)
            else:
                color = self.colors['text']
            
            text_surface = self.font.render(text, True, color)
            self.screen.blit(text_surface, (info_x, 10 + i * 25))
    
    def handle_events(self):
        """处理事件"""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False
            
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_q:
                    return False
                elif event.key == pygame.K_SPACE:
                    self.spawn_cats()
                elif event.key == pygame.K_r:
                    self.player_pos = (800, 800)
                    self.spawn_cats()
            
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:  # 左键点击
                    mouse_pos = pygame.mouse.get_pos()
                    if mouse_pos[0] < self.scaled_size and mouse_pos[1] < self.scaled_size:
                        self.player_pos = self.screen_to_world(mouse_pos)
                        self.spawn_cats()
        
        return True
    
    def run(self):
        """运行可视化器"""
        print("🎮 启动猫咪Spawn可视化器")
        print("操作说明:")
        print("  - 点击地图移动玩家位置")
        print("  - 按SPACE重新生成猫咪")
        print("  - 按R重置玩家到中心")
        print("  - 按Q退出")
        
        # 初始生成猫咪
        self.spawn_cats()
        
        running = True
        while running:
            running = self.handle_events()
            
            # 清屏
            self.screen.fill(self.colors['background'])
            
            # 绘制所有元素
            self.draw_grid()
            self.draw_spawn_area()
            self.draw_obstacles()
            self.draw_player()
            self.draw_cats()
            self.draw_info()
            
            # 更新显示
            pygame.display.flip()
            self.clock.tick(60)
        
        pygame.quit()
        print("👋 可视化器已关闭")

def main():
    """主函数"""
    visualizer = SpawnVisualizer()
    visualizer.run()

if __name__ == "__main__":
    main()