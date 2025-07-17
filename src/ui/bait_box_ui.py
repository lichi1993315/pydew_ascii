#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
鱼饵箱UI - 显示昆虫收集和鱼饵制作界面
"""

import pygame
from src.settings import *
from src.systems.bait_system import get_bait_system
from src.utils.font_manager import get_font_manager

class BaitBoxUI:
    """鱼饵箱用户界面"""
    
    def __init__(self, screen_width, screen_height):
        self.screen_width = screen_width
        self.screen_height = screen_height
        self.font_manager = get_font_manager()
        
        # 获取鱼饵系统
        self.bait_system = get_bait_system()
        
        # UI状态
        self.is_visible = False
        self.selected_bait_id = None
        
        # UI尺寸和位置
        self.ui_width = 600
        self.ui_height = 500
        self.ui_x = (screen_width - self.ui_width) // 2
        self.ui_y = (screen_height - self.ui_height) // 2
        
        # 按钮尺寸
        self.button_width = 120
        self.button_height = 40
        
        # 滚动相关
        self.scroll_offset = 0
        self.item_height = 60
        
        # 颜色定义
        self.bg_color = (40, 40, 40, 220)
        self.panel_color = (60, 60, 60)
        self.button_color = (80, 80, 80)
        self.button_hover_color = (100, 100, 100)
        self.text_color = (255, 255, 255)
        self.highlight_color = (255, 255, 0)
        
    def toggle_visibility(self):
        """切换界面可见性"""
        self.is_visible = not self.is_visible
        if self.is_visible:
            print("[鱼饵箱UI] 打开鱼饵箱")
        else:
            print("[鱼饵箱UI] 关闭鱼饵箱")
    
    def handle_event(self, event):
        """处理事件"""
        if not self.is_visible:
            return False
        
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE or event.key == pygame.K_b:
                self.toggle_visibility()
                return True
        
        elif event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:  # 左键
                mouse_pos = pygame.mouse.get_pos()
                
                # 检查是否点击了UI外部
                if not self._is_point_in_ui(mouse_pos):
                    self.toggle_visibility()
                    return True
                
                # 检查制作按钮
                if self._handle_craft_button_click(mouse_pos):
                    return True
                
                # 检查鱼饵选择
                if self._handle_bait_selection_click(mouse_pos):
                    return True
        
        elif event.type == pygame.MOUSEWHEEL:
            if self.is_visible:
                self.scroll_offset -= event.y * 30
                self.scroll_offset = max(0, self.scroll_offset)
                return True
        
        return False
    
    def _is_point_in_ui(self, pos):
        """检查点是否在UI区域内"""
        x, y = pos
        return (self.ui_x <= x <= self.ui_x + self.ui_width and
                self.ui_y <= y <= self.ui_y + self.ui_height)
    
    def _handle_craft_button_click(self, mouse_pos):
        """处理制作按钮点击"""
        if not self.selected_bait_id:
            return False
        
        # 制作按钮位置
        button_x = self.ui_x + self.ui_width - self.button_width - 20
        button_y = self.ui_y + self.ui_height - self.button_height - 20
        
        if (button_x <= mouse_pos[0] <= button_x + self.button_width and
            button_y <= mouse_pos[1] <= button_y + self.button_height):
            
            # 尝试制作鱼饵
            if self.bait_system.craft_bait(self.selected_bait_id):
                print(f"[鱼饵制作] 成功制作了 {self.bait_system.bait_types[self.selected_bait_id].name}")
            else:
                print(f"[鱼饵制作] 制作失败，材料不足或已达上限")
            
            return True
        
        return False
    
    def _handle_bait_selection_click(self, mouse_pos):
        """处理鱼饵选择点击"""
        # 可制作鱼饵列表区域
        list_x = self.ui_x + 20
        list_y = self.ui_y + 100
        list_width = self.ui_width - 40
        
        craftable_baits = self.bait_system.get_craftable_baits()
        
        for i, bait_id in enumerate(craftable_baits):
            item_y = list_y + i * self.item_height - self.scroll_offset
            
            # 检查是否在可见区域
            if item_y < self.ui_y + 80 or item_y > self.ui_y + self.ui_height - 100:
                continue
            
            if (list_x <= mouse_pos[0] <= list_x + list_width and
                item_y <= mouse_pos[1] <= item_y + self.item_height):
                
                self.selected_bait_id = bait_id
                print(f"[鱼饵选择] 选择了 {self.bait_system.bait_types[bait_id].name}")
                return True
        
        return False
    
    def draw(self, screen):
        """绘制界面"""
        if not self.is_visible:
            return
        
        # 创建半透明背景
        overlay = pygame.Surface((self.screen_width, self.screen_height))
        overlay.set_alpha(128)
        overlay.fill((0, 0, 0))
        screen.blit(overlay, (0, 0))
        
        # 绘制主面板
        pygame.draw.rect(screen, self.panel_color, 
                        (self.ui_x, self.ui_y, self.ui_width, self.ui_height))
        pygame.draw.rect(screen, (255, 255, 255), 
                        (self.ui_x, self.ui_y, self.ui_width, self.ui_height), 2)
        
        # 绘制标题
        title_font = self.font_manager.get_font(24)
        title_text = title_font.render("鱼饵箱", True, self.text_color)
        title_rect = title_text.get_rect(center=(self.ui_x + self.ui_width // 2, self.ui_y + 30))
        screen.blit(title_text, title_rect)
        
        # 绘制昆虫库存
        self._draw_insect_inventory(screen)
        
        # 绘制可制作鱼饵列表
        self._draw_craftable_baits(screen)
        
        # 绘制制作按钮
        self._draw_craft_button(screen)
        
        # 绘制当前鱼饵库存
        self._draw_bait_inventory(screen)
    
    def _draw_insect_inventory(self, screen):
        """绘制昆虫库存"""
        font = self.font_manager.get_font(16)
        
        # 标题
        title_text = font.render("昆虫库存：", True, self.text_color)
        screen.blit(title_text, (self.ui_x + 20, self.ui_y + 60))
        
        # 昆虫列表 - 从工作台获取
        from src.systems.bait_workbench import get_bait_workbench
        workbench = get_bait_workbench()
        
        x_offset = 120
        y_offset = 60
        
        insect_storage = workbench.insect_storage if workbench else {}
        
        for i, (insect_id, count) in enumerate(insect_storage.items()):
            insect = self.bait_system.insect_types[insect_id]
            
            # 计算位置
            col = i % 4
            row = i // 4
            x = self.ui_x + 20 + col * x_offset
            y = self.ui_y + y_offset + row * 25
            
            # 绘制昆虫信息
            insect_text = f"{insect.ascii_char} {insect.name}: {count}"
            text_surface = font.render(insect_text, True, self.text_color)
            screen.blit(text_surface, (x, y))
    
    def _draw_craftable_baits(self, screen):
        """绘制可制作鱼饵列表"""
        font = self.font_manager.get_font(16)
        small_font = self.font_manager.get_font(12)
        
        # 标题
        title_text = font.render("可制作鱼饵：", True, self.text_color)
        screen.blit(title_text, (self.ui_x + 20, self.ui_y + 120))
        
        # 列表区域
        list_x = self.ui_x + 20
        list_y = self.ui_y + 150
        list_width = self.ui_width - 40
        list_height = 200
        
        # 绘制列表背景
        pygame.draw.rect(screen, (30, 30, 30), (list_x, list_y, list_width, list_height))
        pygame.draw.rect(screen, (100, 100, 100), (list_x, list_y, list_width, list_height), 1)
        
        # 获取可制作鱼饵
        craftable_baits = self.bait_system.get_craftable_baits()
        
        if not craftable_baits:
            no_bait_text = font.render("没有可制作的鱼饵", True, (150, 150, 150))
            text_rect = no_bait_text.get_rect(center=(list_x + list_width // 2, list_y + list_height // 2))
            screen.blit(no_bait_text, text_rect)
            return
        
        # 绘制鱼饵列表
        for i, bait_id in enumerate(craftable_baits):
            item_y = list_y + i * self.item_height - self.scroll_offset
            
            # 检查是否在可见区域
            if item_y < list_y - self.item_height or item_y > list_y + list_height:
                continue
            
            bait_type = self.bait_system.bait_types[bait_id]
            
            # 绘制选择高亮
            if self.selected_bait_id == bait_id:
                pygame.draw.rect(screen, (80, 80, 80), 
                               (list_x + 2, item_y, list_width - 4, self.item_height))
            
            # 绘制鱼饵信息
            bait_text = f"{bait_type.ascii_char} {bait_type.name}"
            text_surface = font.render(bait_text, True, self.text_color)
            screen.blit(text_surface, (list_x + 10, item_y + 5))
            
            # 绘制稀有度
            rarity_color = self._get_rarity_color(bait_type.rarity)
            rarity_text = small_font.render(f"[{bait_type.rarity}]", True, rarity_color)
            screen.blit(rarity_text, (list_x + 10, item_y + 25))
            
            # 绘制配方
            recipe = self.bait_system.bait_recipes[bait_id]
            recipe_text = "需要: "
            for insect_id, count in recipe.items():
                insect_name = self.bait_system.insect_types[insect_id].name
                recipe_text += f"{insect_name}x{count} "
            
            recipe_surface = small_font.render(recipe_text, True, (200, 200, 200))
            screen.blit(recipe_surface, (list_x + 150, item_y + 5))
            
            # 绘制当前库存
            current_count = self.bait_system.get_bait_count(bait_id)
            max_count = bait_type.max_stack
            stock_text = f"库存: {current_count}/{max_count}"
            stock_surface = small_font.render(stock_text, True, (180, 180, 180))
            screen.blit(stock_surface, (list_x + 150, item_y + 25))
    
    def _draw_craft_button(self, screen):
        """绘制制作按钮"""
        button_x = self.ui_x + self.ui_width - self.button_width - 20
        button_y = self.ui_y + self.ui_height - self.button_height - 20
        
        # 检查是否可以制作
        can_craft = (self.selected_bait_id and 
                    self.bait_system.can_craft_bait(self.selected_bait_id))
        
        # 按钮颜色
        if can_craft:
            button_color = self.button_color
            text_color = self.text_color
        else:
            button_color = (50, 50, 50)
            text_color = (100, 100, 100)
        
        # 绘制按钮
        pygame.draw.rect(screen, button_color, 
                        (button_x, button_y, self.button_width, self.button_height))
        pygame.draw.rect(screen, (200, 200, 200), 
                        (button_x, button_y, self.button_width, self.button_height), 2)
        
        # 绘制按钮文字
        font = self.font_manager.get_font(16)
        button_text = font.render("制作", True, text_color)
        text_rect = button_text.get_rect(center=(button_x + self.button_width // 2, 
                                                button_y + self.button_height // 2))
        screen.blit(button_text, text_rect)
    
    def _draw_bait_inventory(self, screen):
        """绘制当前鱼饵库存"""
        font = self.font_manager.get_font(14)
        
        # 标题
        title_text = font.render("当前鱼饵库存：", True, self.text_color)
        screen.blit(title_text, (self.ui_x + 20, self.ui_y + 370))
        
        # 鱼饵列表
        y_offset = 395
        col_width = 140
        
        for i, (bait_id, count) in enumerate(self.bait_system.bait_inventory.items()):
            bait_type = self.bait_system.bait_types[bait_id]
            
            # 计算位置
            col = i % 4
            row = i // 4
            x = self.ui_x + 20 + col * col_width
            y = self.ui_y + y_offset + row * 20
            
            # 绘制鱼饵信息
            bait_text = f"{bait_type.ascii_char} {bait_type.name}: {count}/{bait_type.max_stack}"
            text_surface = font.render(bait_text, True, self.text_color)
            screen.blit(text_surface, (x, y))
    
    def _get_rarity_color(self, rarity):
        """获取稀有度颜色"""
        rarity_colors = {
            'common': (255, 255, 255),
            'uncommon': (30, 255, 0),
            'rare': (0, 112, 255),
            'epic': (163, 53, 238),
            'legendary': (255, 128, 0)
        }
        return rarity_colors.get(rarity, (255, 255, 255))