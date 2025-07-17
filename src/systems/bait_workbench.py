#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
鱼饵工作台系统
"""

import pygame
from src.settings import *
from src.rendering.ascii_sprites import ASCIIInteraction
from src.utils.font_manager import FontManager
class BaitWorkbench(ASCIIInteraction):
    """鱼饵工作台 - 继承自ASCIIInteraction"""
    
    def __init__(self, pos, groups):
        # ASCIIInteraction需要pos, size, groups, name参数
        super().__init__(pos, (64, 64), groups, "bait_workbench")
        
        # 工作台特有属性
        self.ascii_char = '🛠️'  # 锤子符号表示工作台
        self.char_color = (139, 69, 19)  # 棕色
        self.bg_color = (205, 133, 63)  # 浅棕色背景
        
        # 工作台库存 - 存储猫咪收集的昆虫
        self.insect_storage = {}  # {insect_id: count}
        
        # 工作台位置（供猫咪寻路用）
        self.workbench_pos = pygame.math.Vector2(pos)
        
        # 重新渲染ASCII表示
        self.render_ascii()
    
    def render_ascii(self):
        """渲染工作台的ASCII表示"""
        font_manager = FontManager.get_instance()
        font = font_manager.load_emoji_font(TILE_SIZE, "ascii_emoji_renderer")
        
        # 创建背景
        self.image = pygame.Surface((TILE_SIZE, TILE_SIZE))
        self.image.fill(self.bg_color)
        
        # 渲染工作台符号
        text_surface = font.render(self.ascii_char, True, self.char_color)
        text_rect = text_surface.get_rect(center=(TILE_SIZE//2, TILE_SIZE//2))
        self.image.blit(text_surface, text_rect)
        
        # 添加边框
        pygame.draw.rect(self.image, (101, 67, 33), (0, 0, TILE_SIZE, TILE_SIZE), 2)
    
    def add_insect(self, insect_id: str, count: int = 1):
        """添加昆虫到工作台存储"""
        current_count = self.insect_storage.get(insect_id, 0)
        self.insect_storage[insect_id] = current_count + count
        print(f"[鱼饵工作台] 添加昆虫: {insect_id} x{count} (总计: {self.insect_storage[insect_id]})")
    
    def get_insect_count(self, insect_id: str) -> int:
        """获取指定昆虫的数量"""
        return self.insect_storage.get(insect_id, 0)
    
    def consume_insect(self, insect_id: str, count: int = 1) -> bool:
        """消耗昆虫（制作鱼饵时使用）"""
        current_count = self.insect_storage.get(insect_id, 0)
        if current_count >= count:
            self.insect_storage[insect_id] = current_count - count
            if self.insect_storage[insect_id] <= 0:
                del self.insect_storage[insect_id]
            return True
        return False
    
    def get_storage_summary(self) -> str:
        """获取存储摘要"""
        if not self.insect_storage:
            return "工作台存储：空"
        
        from src.systems.bait_system import get_bait_system
        bait_system = get_bait_system()
        
        summary = "工作台存储：\n"
        for insect_id, count in self.insect_storage.items():
            if insect_id in bait_system.insect_types:
                insect_name = bait_system.insect_types[insect_id].name
                summary += f"  {insect_name}: {count}\n"
        
        return summary.strip()

# 全局工作台实例
_bait_workbench = None

def get_bait_workbench():
    """获取鱼饵工作台单例"""
    global _bait_workbench
    return _bait_workbench

def set_bait_workbench(workbench):
    """设置鱼饵工作台单例"""
    global _bait_workbench
    _bait_workbench = workbench