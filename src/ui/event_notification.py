#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
猫猫事件通知UI
显示事件发生时的弹窗通知
"""

import pygame
import time
from typing import List, Optional
from src.utils.font_manager import FontManager
from src.settings import SCREEN_WIDTH, SCREEN_HEIGHT

class EventNotification:
    """单个事件通知"""
    
    def __init__(self, message: str, duration: float = 5.0, notification_type: str = "event"):
        self.message = message
        self.duration = duration
        self.notification_type = notification_type
        self.start_time = time.time()
        self.is_active = True
        
        # 动画属性
        self.alpha = 0
        self.target_alpha = 255
        self.fade_speed = 400  # alpha/秒
        self.y_offset = 0
        self.target_y = 0
        
        # 外观设置
        self.width = min(400, SCREEN_WIDTH - 40)
        self.height = 80
        self.margin = 10
        
        # 颜色设置
        self.colors = {
            "event": {
                "background": (50, 150, 200, 200),
                "border": (70, 170, 220),
                "text": (255, 255, 255)
            },
            "relationship": {
                "background": (200, 100, 150, 200),
                "border": (220, 120, 170),
                "text": (255, 255, 255)
            },
            "warning": {
                "background": (200, 150, 50, 200),
                "border": (220, 170, 70),
                "text": (255, 255, 255)
            }
        }
        
        # 字体
        self.font_manager = FontManager.get_instance()
        self.title_font = self.font_manager.load_chinese_font(18, "event_title_font")
        self.message_font = self.font_manager.load_chinese_font(14, "event_message_font")
    
    def update(self, dt: float, target_y: float) -> bool:
        """更新通知状态，返回是否应该继续显示"""
        current_time = time.time()
        
        # 更新目标位置
        self.target_y = target_y
        
        # 位置动画
        y_diff = self.target_y - self.y_offset
        if abs(y_diff) > 1:
            self.y_offset += y_diff * 5 * dt
        else:
            self.y_offset = self.target_y
        
        # 淡入动画
        if current_time - self.start_time < 0.5:  # 前0.5秒淡入
            self.alpha = min(255, self.alpha + self.fade_speed * dt)
        # 淡出动画
        elif current_time - self.start_time > self.duration - 1.0:  # 最后1秒淡出
            self.alpha = max(0, self.alpha - self.fade_speed * dt)
        else:
            self.alpha = 255
        
        # 检查是否应该移除
        if current_time - self.start_time > self.duration:
            self.is_active = False
            return False
        
        return True
    
    def render(self, surface: pygame.Surface, x: float):
        """渲染通知"""
        if not self.is_active or self.alpha <= 0:
            return
        
        # 创建通知表面
        notification_surface = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
        
        # 获取颜色
        colors = self.colors.get(self.notification_type, self.colors["event"])
        
        # 绘制背景
        bg_color = (*colors["background"][:3], int(colors["background"][3] * self.alpha / 255))
        background_rect = pygame.Rect(0, 0, self.width, self.height)
        pygame.draw.rect(notification_surface, bg_color, background_rect, border_radius=8)
        
        # 绘制边框
        border_color = (*colors["border"], int(self.alpha))
        pygame.draw.rect(notification_surface, border_color, background_rect, width=2, border_radius=8)
        
        # 绘制图标
        icon_text = "🎉" if self.notification_type == "event" else "💕" if self.notification_type == "relationship" else "⚠️"
        icon_surface = self.title_font.render(icon_text, True, (*colors["text"], int(self.alpha)))
        notification_surface.blit(icon_surface, (10, 8))
        
        # 绘制标题
        title = "猫猫事件" if self.notification_type == "event" else "关系变化" if self.notification_type == "relationship" else "提醒"
        title_surface = self.title_font.render(title, True, (*colors["text"], int(self.alpha)))
        notification_surface.blit(title_surface, (45, 8))
        
        # 绘制消息文本（支持换行）
        self._render_wrapped_text(notification_surface, self.message, 
                                (10, 35), self.width - 20, colors["text"], int(self.alpha))
        
        # 将通知表面绘制到主表面
        surface.blit(notification_surface, (x, self.y_offset))
    
    def _render_wrapped_text(self, surface: pygame.Surface, text: str, pos: tuple, 
                           max_width: int, color: tuple, alpha: int):
        """渲染支持换行的文本"""
        words = text.split(' ')
        lines = []
        current_line = ""
        
        for word in words:
            test_line = current_line + word + " " if current_line else word + " "
            test_surface = self.message_font.render(test_line, True, color)
            
            if test_surface.get_width() <= max_width:
                current_line = test_line
            else:
                if current_line:
                    lines.append(current_line.strip())
                current_line = word + " "
        
        if current_line:
            lines.append(current_line.strip())
        
        # 限制行数
        if len(lines) > 2:
            lines = lines[:2]
            if len(lines) == 2:
                lines[1] = lines[1][:20] + "..." if len(lines[1]) > 20 else lines[1]
        
        # 渲染每一行
        y_offset = 0
        for line in lines:
            if line.strip():
                line_surface = self.message_font.render(line, True, (*color, alpha))
                surface.blit(line_surface, (pos[0], pos[1] + y_offset))
                y_offset += 18

class EventNotificationManager:
    """事件通知管理器"""
    
    def __init__(self):
        self.notifications: List[EventNotification] = []
        self.max_notifications = 5
        self.notification_spacing = 90
        self.start_x = SCREEN_WIDTH - 420
        self.start_y = 50
    
    def add_notification(self, message: str, duration: float = 5.0, 
                        notification_type: str = "event"):
        """添加新通知"""
        # 移除过多的旧通知
        if len(self.notifications) >= self.max_notifications:
            self.notifications.pop(0)
        
        notification = EventNotification(message, duration, notification_type)
        self.notifications.append(notification)
    
    def add_event_notification(self, event_message: str):
        """添加事件通知"""
        self.add_notification(event_message, duration=6.0, notification_type="event")
    
    def add_relationship_notification(self, cat1_name: str, cat2_name: str, 
                                    relationship_changes: dict):
        """添加关系变化通知"""
        changes = []
        for key, value in relationship_changes.items():
            if abs(value) >= 5:  # 只显示显著变化
                if key == "friendship":
                    if value > 0:
                        changes.append(f"友好度+{value:.0f}")
                    else:
                        changes.append(f"友好度{value:.0f}")
                elif key == "romance":
                    if value > 0:
                        changes.append(f"恋爱度+{value:.0f}")
                    else:
                        changes.append(f"恋爱度{value:.0f}")
                elif key == "rivalry":
                    if value > 0:
                        changes.append(f"竞争度+{value:.0f}")
                elif key == "cooperation":
                    if value > 0:
                        changes.append(f"合作度+{value:.0f}")
        
        if changes:
            message = f"{cat1_name} ↔ {cat2_name}: {', '.join(changes)}"
            self.add_notification(message, duration=4.0, notification_type="relationship")
    
    def update(self, dt: float):
        """更新所有通知"""
        # 更新现有通知
        active_notifications = []
        for i, notification in enumerate(self.notifications):
            target_y = self.start_y + i * self.notification_spacing
            if notification.update(dt, target_y):
                active_notifications.append(notification)
        
        self.notifications = active_notifications
    
    def render(self, surface: pygame.Surface):
        """渲染所有通知"""
        for notification in self.notifications:
            notification.render(surface, self.start_x)
    
    def clear_all(self):
        """清除所有通知"""
        self.notifications.clear()
    
    def has_notifications(self) -> bool:
        """检查是否有活跃通知"""
        return len(self.notifications) > 0