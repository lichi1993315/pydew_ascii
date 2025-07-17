#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
背包UI系统 - 处理物品选择和放置
"""

import pygame
from ..settings import *
from ..utils.font_manager import FontManager
from ..systems.timer import Timer

class InventoryUI:
    """背包UI类"""
    
    def __init__(self, player):
        self.player = player
        self.display_surface = pygame.display.get_surface()
        
        # 字体设置
        font_manager = FontManager.get_instance()
        self.font = font_manager.load_chinese_font(24, "inventory_font")
        self.title_font = font_manager.load_chinese_font(30, "inventory_title_font")
        
        # UI状态
        self.is_open = False
        self.selected_category = "cat_bed"  # 目前只支持猫窝
        self.selected_item_index = 0
        self.placement_mode = False
        self.selected_item_data = None
        
        # UI尺寸
        self.width = 600
        self.height = 400
        self.padding = 20
        self.item_height = 40
        self.spacing = 10
        
        # 计算UI位置
        self.ui_rect = pygame.Rect(
            (SCREEN_WIDTH - self.width) // 2,
            (SCREEN_HEIGHT - self.height) // 2,
            self.width,
            self.height
        )
        
        # 输入控制
        self.input_timer = Timer(200)
        
        # 放置相关
        self.placement_preview_pos = None
        self.placement_valid = False
        
    def toggle(self):
        """切换背包显示状态"""
        self.is_open = not self.is_open
        if self.is_open:
            self.placement_mode = False
            self.selected_item_index = 0
            self.update_item_list()
        
    def update_item_list(self):
        """更新物品列表"""
        self.item_list = []
        
        # 获取猫窝库存
        if hasattr(self.player, 'cat_bed_inventory'):
            for bed_type, bed_list in self.player.cat_bed_inventory.items():
                for bed_data in bed_list:
                    from ..settings import CAT_BED_TYPES
                    bed_config = CAT_BED_TYPES.get(bed_type, {})
                    
                    self.item_list.append({
                        'type': 'cat_bed',
                        'bed_type': bed_type,
                        'bed_data': bed_data,
                        'name': bed_config.get('name', bed_type),
                        'ascii_char': bed_config.get('ascii_char', '🛏️'),
                        'description': bed_config.get('description', ''),
                        'owner_name': bed_data.get('owner_cat', '未知'),
                        'owner_id': bed_data.get('owner_id', '')
                    })
        
        # 确保选中索引有效
        if self.selected_item_index >= len(self.item_list):
            self.selected_item_index = 0
    
    def handle_input(self, keys):
        """处理输入"""
        if not self.is_open:
            return
        
        self.input_timer.update()
        
        if not self.input_timer.active:
            if self.placement_mode:
                self.handle_placement_input(keys)
            else:
                self.handle_menu_input(keys)
    
    def handle_menu_input(self, keys):
        """处理菜单输入"""
        # 上下选择
        if keys[pygame.K_UP] and self.selected_item_index > 0:
            self.selected_item_index -= 1
            self.input_timer.activate()
        
        elif keys[pygame.K_DOWN] and self.selected_item_index < len(self.item_list) - 1:
            self.selected_item_index += 1
            self.input_timer.activate()
        
        # 确认选择
        elif keys[pygame.K_RETURN] and self.item_list:
            self.enter_placement_mode()
            self.input_timer.activate()
        
        # 关闭背包
        elif keys[pygame.K_ESCAPE] or keys[pygame.K_b]:
            self.toggle()
            self.input_timer.activate()
    
    def handle_placement_input(self, keys):
        """处理放置模式输入"""
        # 确认放置
        if keys[pygame.K_RETURN] and self.placement_valid:
            self.place_item()
            self.input_timer.activate()
        
        # 取消放置
        elif keys[pygame.K_ESCAPE]:
            self.exit_placement_mode()
            self.input_timer.activate()
    
    def enter_placement_mode(self):
        """进入放置模式"""
        if self.item_list and self.selected_item_index < len(self.item_list):
            self.placement_mode = True
            self.selected_item_data = self.item_list[self.selected_item_index]
            print(f"[InventoryUI] 进入放置模式: {self.selected_item_data['name']}")
    
    def exit_placement_mode(self):
        """退出放置模式"""
        self.placement_mode = False
        self.selected_item_data = None
        self.placement_preview_pos = None
        self.placement_valid = False
        print("[InventoryUI] 退出放置模式")
    
    def update_placement_preview(self, mouse_pos):
        """更新放置预览"""
        if not self.placement_mode:
            return
        
        # 将鼠标位置转换为网格位置
        grid_x = (mouse_pos[0] // TILE_SIZE) * TILE_SIZE
        grid_y = (mouse_pos[1] // TILE_SIZE) * TILE_SIZE
        
        self.placement_preview_pos = (grid_x, grid_y)
        
        # 检查放置位置是否有效
        self.placement_valid = self.is_placement_valid(grid_x, grid_y)
    
    def is_placement_valid(self, x, y):
        """检查放置位置是否有效"""
        # 检查是否在游戏世界范围内
        if x < 0 or y < 0 or x >= 1600 or y >= 1600:
            return False
        
        # 检查是否与其他物体冲突
        placement_rect = pygame.Rect(x, y, TILE_SIZE, TILE_SIZE)
        
        # 检查是否与玩家碰撞
        if placement_rect.colliderect(self.player.rect):
            return False
        
        # 检查是否与其他交互对象冲突
        for sprite in self.player.interaction:
            if placement_rect.colliderect(sprite.rect):
                return False
        
        # 检查是否与碰撞对象冲突
        for sprite in self.player.collision_sprites:
            if placement_rect.colliderect(sprite.rect):
                return False
        
        return True
    
    def place_item(self):
        """放置物品"""
        if not self.placement_mode or not self.placement_valid or not self.selected_item_data:
            return
        
        # 创建猫窝
        if self.selected_item_data['type'] == 'cat_bed':
            self.place_cat_bed()
    
    def place_cat_bed(self):
        """放置猫窝"""
        from ..systems.cat_bed import CatBed, get_cat_bed_manager
        
        bed_data = self.selected_item_data['bed_data']
        bed_type = self.selected_item_data['bed_type']
        
        # 创建猫窝实例
        cat_bed = CatBed(
            pos=self.placement_preview_pos,
            bed_type=bed_type,
            owner_cat_id=bed_data['owner_id'],
            owner_cat_name=bed_data['owner_cat'],
            groups=[self.player.interaction]  # 添加到交互组
        )
        
        # 添加到猫窝管理器
        cat_bed_manager = get_cat_bed_manager()
        cat_bed_manager.add_cat_bed(cat_bed)
        
        # 从背包中移除
        self.remove_item_from_inventory(self.selected_item_data)
        
        print(f"[InventoryUI] 放置了 {self.selected_item_data['name']} 在位置 {self.placement_preview_pos}")
        
        # 退出放置模式
        self.exit_placement_mode()
        self.toggle()  # 关闭背包
    
    def remove_item_from_inventory(self, item_data):
        """从背包中移除物品"""
        if item_data['type'] == 'cat_bed':
            bed_type = item_data['bed_type']
            bed_data = item_data['bed_data']
            
            if bed_type in self.player.cat_bed_inventory:
                if bed_data in self.player.cat_bed_inventory[bed_type]:
                    self.player.cat_bed_inventory[bed_type].remove(bed_data)
                    
                    # 如果列表为空，移除该类型
                    if not self.player.cat_bed_inventory[bed_type]:
                        del self.player.cat_bed_inventory[bed_type]
            
            # 更新物品列表
            self.update_item_list()
    
    def render(self):
        """渲染背包界面"""
        if not self.is_open:
            return
        
        # 渲染背景
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
        overlay.set_alpha(128)
        overlay.fill((0, 0, 0))
        self.display_surface.blit(overlay, (0, 0))
        
        # 渲染主面板
        pygame.draw.rect(self.display_surface, (240, 240, 240), self.ui_rect)
        pygame.draw.rect(self.display_surface, (0, 0, 0), self.ui_rect, 3)
        
        # 渲染标题
        title_text = self.title_font.render("背包 - 猫窝", True, (0, 0, 0))
        title_rect = title_text.get_rect(centerx=self.ui_rect.centerx, y=self.ui_rect.y + 20)
        self.display_surface.blit(title_text, title_rect)
        
        # 渲染物品列表
        if self.item_list:
            start_y = self.ui_rect.y + 80
            
            for i, item in enumerate(self.item_list):
                item_y = start_y + i * (self.item_height + self.spacing)
                
                # 选中高亮
                if i == self.selected_item_index:
                    highlight_rect = pygame.Rect(
                        self.ui_rect.x + 10,
                        item_y - 5,
                        self.ui_rect.width - 20,
                        self.item_height
                    )
                    pygame.draw.rect(self.display_surface, (200, 220, 255), highlight_rect)
                    pygame.draw.rect(self.display_surface, (0, 0, 0), highlight_rect, 2)
                
                # 渲染物品信息
                item_text = f"{item['ascii_char']} {item['name']} (给 {item['owner_name']})"
                text_surface = self.font.render(item_text, True, (0, 0, 0))
                text_rect = text_surface.get_rect(x=self.ui_rect.x + 20, y=item_y)
                self.display_surface.blit(text_surface, text_rect)
        
        else:
            # 没有物品时显示提示
            no_items_text = self.font.render("背包中没有猫窝", True, (128, 128, 128))
            no_items_rect = no_items_text.get_rect(center=(self.ui_rect.centerx, self.ui_rect.centery))
            self.display_surface.blit(no_items_text, no_items_rect)
        
        # 渲染操作提示
        if self.item_list:
            hint_text = "↑↓选择  回车确认  ESC/B键关闭"
        else:
            hint_text = "ESC/B键关闭"
        
        hint_surface = self.font.render(hint_text, True, (80, 80, 80))
        hint_rect = hint_surface.get_rect(centerx=self.ui_rect.centerx, y=self.ui_rect.bottom - 40)
        self.display_surface.blit(hint_surface, hint_rect)
    
    def render_placement_preview(self):
        """渲染放置预览"""
        if not self.placement_mode or not self.placement_preview_pos:
            return
        
        # 渲染放置预览
        preview_rect = pygame.Rect(
            self.placement_preview_pos[0],
            self.placement_preview_pos[1],
            TILE_SIZE,
            TILE_SIZE
        )
        
        # 预览颜色
        if self.placement_valid:
            preview_color = (0, 255, 0, 100)  # 绿色透明
        else:
            preview_color = (255, 0, 0, 100)  # 红色透明
        
        # 创建透明表面
        preview_surface = pygame.Surface((TILE_SIZE, TILE_SIZE))
        preview_surface.set_alpha(100)
        preview_surface.fill(preview_color[:3])
        
        self.display_surface.blit(preview_surface, preview_rect)
        
        # 渲染边框
        border_color = (0, 255, 0) if self.placement_valid else (255, 0, 0)
        pygame.draw.rect(self.display_surface, border_color, preview_rect, 2)
        
        # 渲染物品图标
        if self.selected_item_data:
            try:
                font_manager = FontManager.get_instance()
                icon_font = font_manager.load_emoji_font(TILE_SIZE//2, "placement_icon")
                icon_surface = icon_font.render(self.selected_item_data['ascii_char'], True, (0, 0, 0))
                icon_rect = icon_surface.get_rect(center=preview_rect.center)
                self.display_surface.blit(icon_surface, icon_rect)
            except:
                # 备用渲染
                fallback_font = pygame.font.Font(None, 24)
                text_surface = fallback_font.render("BED", True, (0, 0, 0))
                text_rect = text_surface.get_rect(center=preview_rect.center)
                self.display_surface.blit(text_surface, text_rect)
        
        # 渲染操作提示
        if self.placement_valid:
            hint_text = "回车确认放置  ESC取消"
        else:
            hint_text = "无法在此位置放置  ESC取消"
        
        hint_surface = self.font.render(hint_text, True, (255, 255, 255))
        hint_rect = hint_surface.get_rect(centerx=SCREEN_WIDTH//2, y=50)
        
        # 渲染提示背景
        bg_rect = hint_rect.inflate(20, 10)
        pygame.draw.rect(self.display_surface, (0, 0, 0), bg_rect)
        pygame.draw.rect(self.display_surface, (255, 255, 255), bg_rect, 2)
        
        self.display_surface.blit(hint_surface, hint_rect)
    
    def update(self, dt):
        """更新背包系统"""
        if self.is_open:
            # 更新放置预览位置
            if self.placement_mode:
                mouse_pos = pygame.mouse.get_pos()
                self.update_placement_preview(mouse_pos)
    
    def is_placement_mode_active(self):
        """检查是否在放置模式"""
        return self.placement_mode