#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
猫窝系统 - 为猫咪提供专属休息场所
"""

import pygame
from src.settings import *
from src.rendering.ascii_sprites import ASCIIInteraction
from src.utils.font_manager import FontManager

class CatBed(ASCIIInteraction):
    """猫窝类 - 继承自ASCIIInteraction"""
    
    def __init__(self, pos, bed_type, owner_cat_id, owner_cat_name, groups):
        # ASCIIInteraction需要pos, size, groups, name参数
        super().__init__(pos, (64, 64), groups, f"cat_bed_{owner_cat_id}")
        
        # 猫窝属性
        self.bed_type = bed_type
        self.owner_cat_id = owner_cat_id
        self.owner_cat_name = owner_cat_name
        self.is_occupied = False
        self.occupying_cat = None
        
        # 根据类型设置属性
        bed_configs = {
            'simple_cat_bed': {
                'name': '简易猫窝',
                'ascii_char': '🛏️',
                'color': (139, 69, 19),
                'energy_restoration': 15,
                'mood_bonus': 1,
                'bg_color': (205, 133, 63)
            },
            'comfort_cat_bed': {
                'name': '舒适猫窝',
                'ascii_char': '🏠',
                'color': (160, 82, 45),
                'energy_restoration': 20,
                'mood_bonus': 2,
                'bg_color': (222, 184, 135)
            },
            'luxury_cat_bed': {
                'name': '豪华猫窝',
                'ascii_char': '🏰',
                'color': (255, 215, 0),
                'energy_restoration': 25,
                'mood_bonus': 3,
                'bg_color': (255, 228, 181)
            }
        }
        
        config = bed_configs.get(bed_type, bed_configs['simple_cat_bed'])
        self.bed_name = config['name']
        self.ascii_char = config['ascii_char']
        self.char_color = config['color']
        self.energy_restoration = config['energy_restoration']
        self.mood_bonus = config['mood_bonus']
        self.bg_color = config['bg_color']
        
        # 猫窝位置（供猫咪寻路用）
        self.bed_pos = pygame.math.Vector2(pos)
        
        # 重新渲染ASCII表示
        self.render_ascii()
        
        print(f"[CatBed] 创建 {self.bed_name} 给 {owner_cat_name} (ID: {owner_cat_id})")
    
    def render_ascii(self):
        """渲染猫窝的ASCII表示"""
        font_manager = FontManager.get_instance()
        font = font_manager.load_emoji_font(TILE_SIZE, f"cat_bed_{self.owner_cat_id}")
        
        # 创建背景
        self.image = pygame.Surface((TILE_SIZE, TILE_SIZE))
        self.image.fill(self.bg_color)
        
        # 渲染猫窝符号
        try:
            text_surface = font.render(self.ascii_char, True, self.char_color)
            text_rect = text_surface.get_rect(center=(TILE_SIZE//2, TILE_SIZE//2))
            self.image.blit(text_surface, text_rect)
        except Exception as e:
            print(f"[CatBed] 渲染猫窝符号失败: {e}")
            # 回退到简单文本
            fallback_font = pygame.font.Font(None, TILE_SIZE//2)
            text_surface = fallback_font.render("BED", True, self.char_color)
            text_rect = text_surface.get_rect(center=(TILE_SIZE//2, TILE_SIZE//2))
            self.image.blit(text_surface, text_rect)
        
        # 添加边框
        pygame.draw.rect(self.image, self.char_color, (0, 0, TILE_SIZE, TILE_SIZE), 2)
        
        # 如果被占用，添加特殊标识
        if self.is_occupied:
            overlay = pygame.Surface((TILE_SIZE, TILE_SIZE))
            overlay.set_alpha(100)
            overlay.fill((255, 255, 0))  # 黄色覆盖表示占用
            self.image.blit(overlay, (0, 0))
    
    def can_be_used_by(self, cat):
        """检查是否可以被指定猫咪使用"""
        return (cat.npc_id == self.owner_cat_id and 
                not self.is_occupied and 
                cat.sleep_state == "awake")
    
    def occupy(self, cat):
        """猫咪占用猫窝"""
        if self.can_be_used_by(cat):
            self.is_occupied = True
            self.occupying_cat = cat
            cat.owned_cat_bed = self
            cat.sleep_location = "cat_bed"
            
            # 重新渲染以显示占用状态
            self.render_ascii()
            
            print(f"[CatBed] {cat.cat_name} 开始使用自己的 {self.bed_name}")
            return True
        return False
    
    def release(self):
        """释放猫窝"""
        if self.is_occupied:
            cat = self.occupying_cat
            self.is_occupied = False
            self.occupying_cat = None
            
            # 重新渲染以显示空闲状态
            self.render_ascii()
            
            print(f"[CatBed] {cat.cat_name} 离开了 {self.bed_name}")
            return True
        return False
    
    def get_restoration_rate(self):
        """获取恢复速度"""
        return {
            'energy': self.energy_restoration,
            'mood': self.mood_bonus
        }
    
    def get_bed_info(self):
        """获取猫窝信息"""
        return {
            'bed_type': self.bed_type,
            'bed_name': self.bed_name,
            'owner_cat_id': self.owner_cat_id,
            'owner_cat_name': self.owner_cat_name,
            'is_occupied': self.is_occupied,
            'occupying_cat': self.occupying_cat.cat_name if self.occupying_cat else None,
            'energy_restoration': self.energy_restoration,
            'mood_bonus': self.mood_bonus,
            'position': self.bed_pos
        }
    
    def update(self, dt):
        """更新猫窝状态"""
        # 检查占用的猫咪是否还在睡觉
        if self.is_occupied and self.occupying_cat:
            if self.occupying_cat.sleep_state != "sleeping":
                self.release()

# 全局猫窝管理器
class CatBedManager:
    """猫窝管理器"""
    
    def __init__(self):
        self.cat_beds = []  # 所有猫窝列表
        self.cat_bed_by_owner = {}  # 按主人ID索引的猫窝
        
    def add_cat_bed(self, cat_bed):
        """添加猫窝"""
        self.cat_beds.append(cat_bed)
        self.cat_bed_by_owner[cat_bed.owner_cat_id] = cat_bed
        print(f"[CatBedManager] 添加猫窝: {cat_bed.bed_name} 给 {cat_bed.owner_cat_name}")
    
    def remove_cat_bed(self, cat_bed):
        """移除猫窝"""
        if cat_bed in self.cat_beds:
            self.cat_beds.remove(cat_bed)
            if cat_bed.owner_cat_id in self.cat_bed_by_owner:
                del self.cat_bed_by_owner[cat_bed.owner_cat_id]
            cat_bed.kill()  # 从精灵组中移除
            print(f"[CatBedManager] 移除猫窝: {cat_bed.bed_name}")
    
    def get_cat_bed_by_owner(self, owner_cat_id):
        """通过主人ID获取猫窝"""
        return self.cat_bed_by_owner.get(owner_cat_id)
    
    def find_nearest_cat_bed(self, position, max_distance=200):
        """找到最近的猫窝"""
        nearest_bed = None
        min_distance = float('inf')
        
        for cat_bed in self.cat_beds:
            distance = pygame.math.Vector2(position).distance_to(cat_bed.bed_pos)
            if distance < max_distance and distance < min_distance:
                min_distance = distance
                nearest_bed = cat_bed
        
        return nearest_bed, min_distance if nearest_bed else None
    
    def get_all_cat_beds(self):
        """获取所有猫窝"""
        return self.cat_beds.copy()
    
    def get_cat_bed_count(self):
        """获取猫窝数量"""
        return len(self.cat_beds)
    
    def get_occupied_bed_count(self):
        """获取被占用的猫窝数量"""
        return sum(1 for bed in self.cat_beds if bed.is_occupied)
    
    def update(self, dt):
        """更新所有猫窝"""
        for cat_bed in self.cat_beds:
            cat_bed.update(dt)

# 全局猫窝管理器实例
_cat_bed_manager = None

def get_cat_bed_manager():
    """获取猫窝管理器单例"""
    global _cat_bed_manager
    if _cat_bed_manager is None:
        _cat_bed_manager = CatBedManager()
    return _cat_bed_manager