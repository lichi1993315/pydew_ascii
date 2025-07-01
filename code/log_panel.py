import pygame
from typing import List
from font_manager import FontManager

class LogPanel:
    """日志面板UI - 显示玩家历史行为记录"""
    
    def __init__(self):
        self.is_active = False
        self.font_manager = FontManager.get_instance()
        
        # 字体设置
        self.title_font = self.font_manager.load_chinese_font(32, "log_title_font")
        self.header_font = self.font_manager.load_chinese_font(20, "log_header_font")
        self.text_font = self.font_manager.load_chinese_font(16, "log_text_font")
        self.small_font = self.font_manager.load_chinese_font(14, "log_small_font")
        
        # 颜色设置
        self.colors = {
            'background': (0, 0, 0, 200),        # 半透明黑色背景
            'border': (255, 255, 255),           # 白色边框
            'title': (100, 200, 255),            # 蓝色标题
            'fishing': (100, 150, 255),          # 蓝色钓鱼行为
            'dialogue': (255, 200, 100),         # 橙色对话行为
            'shop': (100, 255, 100),             # 绿色商店行为
            'quest': (255, 255, 100),            # 黄色任务行为
            'farming': (150, 255, 150),          # 浅绿色农业行为
            'tool_use': (200, 150, 255),         # 紫色工具使用
            'tool_switch': (255, 150, 200),      # 粉色工具切换
            'seed_switch': (200, 255, 150),      # 浅绿色种子切换
            'sleep': (150, 150, 255),            # 浅蓝色睡眠
            'default': (200, 200, 200),          # 默认灰色
            'timestamp': (150, 150, 150),        # 时间戳颜色
            'details': (180, 180, 180),          # 详情颜色
        }
        
        # 面板设置
        self.panel_width = 900
        self.panel_height = 700
        self.margin = 20
        self.line_spacing = 18
        
        # 滚动设置
        self.scroll_offset = 0
        self.max_visible_lines = 25
        self.scroll_speed = 3
        
        # 筛选设置
        self.filter_type = None  # 当前筛选类型
        self.available_filters = [
            None, 'fishing', 'dialogue', 'shop', 'quest', 
            'farming', 'tool_use', 'tool_switch', 'seed_switch'
        ]
        self.current_filter_index = 0
        
    def toggle(self):
        """切换日志面板显示状态"""
        self.is_active = not self.is_active
        if self.is_active:
            self.scroll_offset = 0  # 重置滚动位置
        print(f"[日志面板] 面板状态: {'开启' if self.is_active else '关闭'}")
    
    def handle_input(self, keys):
        """处理输入事件"""
        if not self.is_active:
            return
            
        # 滚动控制
        if keys[pygame.K_UP] or keys[pygame.K_w]:
            self.scroll_offset = max(0, self.scroll_offset - self.scroll_speed)
        elif keys[pygame.K_DOWN] or keys[pygame.K_s]:
            self.scroll_offset += self.scroll_speed
            
        # 筛选器切换（Tab键）
        if keys[pygame.K_TAB]:
            self.current_filter_index = (self.current_filter_index + 1) % len(self.available_filters)
            self.filter_type = self.available_filters[self.current_filter_index]
            self.scroll_offset = 0  # 重置滚动
            
        # 重置到顶部（Home键）
        if keys[pygame.K_HOME]:
            self.scroll_offset = 0
            
        # 跳转到底部（End键）
        if keys[pygame.K_END]:
            self.scroll_offset = 999999  # 设置一个很大的值，后面会被限制
    
    def render(self, surface, player):
        """渲染日志面板"""
        if not self.is_active:
            return
        
        screen_width = surface.get_width()
        screen_height = surface.get_height()
        
        # 计算面板位置（居中）
        panel_x = (screen_width - self.panel_width) // 2
        panel_y = (screen_height - self.panel_height) // 2
        
        # 创建面板背景
        panel_surface = pygame.Surface((self.panel_width, self.panel_height))
        panel_surface.fill((0, 0, 0))
        panel_surface.set_alpha(200)
        
        # 绘制边框
        pygame.draw.rect(panel_surface, self.colors['border'], 
                        (0, 0, self.panel_width, self.panel_height), 3)
        
        # 绘制标题和筛选信息
        current_y = self._render_header(panel_surface, player)
        
        # 绘制日志内容
        current_y = self._render_log_content(panel_surface, player, current_y)
        
        # 绘制操作提示
        self._render_controls_hint(panel_surface)
        
        # 将面板绘制到主屏幕
        surface.blit(panel_surface, (panel_x, panel_y))
    
    def _render_header(self, surface, player):
        """渲染标题和统计信息"""
        current_y = self.margin
        
        # 主标题
        title_text = self.title_font.render("行为日志", True, self.colors['title'])
        title_rect = title_text.get_rect(centerx=self.panel_width//2, y=current_y)
        surface.blit(title_text, title_rect)
        current_y = title_rect.bottom + 10
        
        # 统计信息
        stats = player.get_behavior_statistics()
        stats_text = self.text_font.render(
            f"总记录: {stats['total_behaviors']} 条 | 游戏时长: {stats['session_duration']}", 
            True, self.colors['default']
        )
        stats_rect = stats_text.get_rect(centerx=self.panel_width//2, y=current_y)
        surface.blit(stats_text, stats_rect)
        current_y = stats_rect.bottom + 5
        
        # 筛选信息
        filter_name = self.filter_type if self.filter_type else "全部"
        filter_text = self.small_font.render(f"当前筛选: {filter_name} (Tab键切换)", True, self.colors['default'])
        filter_rect = filter_text.get_rect(centerx=self.panel_width//2, y=current_y)
        surface.blit(filter_text, filter_rect)
        current_y = filter_rect.bottom + 15
        
        # 分隔线
        pygame.draw.line(surface, self.colors['border'], 
                        (self.margin, current_y), 
                        (self.panel_width - self.margin, current_y), 2)
        
        return current_y + 10
    
    def _render_log_content(self, surface, player, start_y):
        """渲染日志内容"""
        current_y = start_y
        content_height = self.panel_height - start_y - 80  # 留出底部提示空间
        
        # 获取筛选后的日志
        filtered_logs = self._get_filtered_logs(player)
        
        if not filtered_logs:
            no_log_text = self.text_font.render("暂无日志记录", True, self.colors['default'])
            no_log_rect = no_log_text.get_rect(centerx=self.panel_width//2, y=current_y + 50)
            surface.blit(no_log_text, no_log_rect)
            return current_y
        
        # 计算可见区域
        total_log_height = len(filtered_logs) * self.line_spacing
        max_scroll = max(0, total_log_height - content_height + self.line_spacing)
        self.scroll_offset = min(self.scroll_offset, max_scroll)
        
        # 计算显示的日志范围
        start_index = max(0, self.scroll_offset // self.line_spacing)
        visible_count = min(self.max_visible_lines, len(filtered_logs) - start_index)
        
        # 渲染可见的日志
        for i in range(visible_count):
            log_index = start_index + i
            if log_index >= len(filtered_logs):
                break
                
            log = filtered_logs[log_index]
            current_y = self._render_log_item(surface, log, current_y, log_index + 1)
            
            # 检查是否超出可见区域
            if current_y > start_y + content_height:
                break
        
        # 绘制滚动条
        if total_log_height > content_height:
            self._render_scrollbar(surface, start_y, content_height, total_log_height)
        
        return current_y
    
    def _render_log_item(self, surface, log, start_y, index):
        """渲染单个日志项"""
        current_y = start_y
        indent = self.margin + 10
        
        # 获取行为类型对应的颜色
        behavior_color = self.colors.get(log['type'], self.colors['default'])
        
        # 渲染序号和时间戳
        time_text = self.small_font.render(
            f"{index:3d}. [{log['timestamp']}]", 
            True, self.colors['timestamp']
        )
        surface.blit(time_text, (indent, current_y))
        
        # 渲染行为类型和描述
        action_text = self.text_font.render(
            f"{log['type']}: {log['action']}", 
            True, behavior_color
        )
        surface.blit(action_text, (indent + 200, current_y))
        current_y += self.line_spacing
        
        # 渲染详细信息（如果有）
        if log['details']:
            details = self._format_log_details(log['details'])
            if details:
                detail_text = self.small_font.render(
                    f"    {details}", 
                    True, self.colors['details']
                )
                surface.blit(detail_text, (indent + 20, current_y))
                current_y += self.line_spacing - 3
        
        return current_y
    
    def _format_log_details(self, details):
        """格式化日志详情"""
        detail_parts = []
        
        # 根据不同的详情类型格式化显示
        if 'fish_caught' in details:
            detail_parts.append(f"鱼类: {details['fish_caught']}({details.get('fish_length', 0)}cm)")
        
        if 'npc_name' in details:
            detail_parts.append(f"NPC: {details['npc_name']}")
            
        if 'player_choice' in details and details['player_choice']:
            detail_parts.append(f"选择: {details['player_choice']}")
        
        if 'total_price' in details:
            transaction = details.get('transaction_type', 'unknown')
            detail_parts.append(f"{'收入' if transaction == 'sell' else '支出'}: {details['total_price']}金币")
        
        if 'quest_title' in details:
            detail_parts.append(f"任务: {details['quest_title']}")
        
        if 'tool_name' in details:
            detail_parts.append(f"工具: {details['tool_name']}")
        
        if 'new_tool' in details and 'old_tool' in details:
            detail_parts.append(f"从{details['old_tool']}切换到{details['new_tool']}")
        
        if 'new_seed' in details and 'old_seed' in details:
            detail_parts.append(f"从{details['old_seed']}切换到{details['new_seed']}")
        
        return " | ".join(detail_parts)
    
    def _get_filtered_logs(self, player):
        """获取筛选后的日志列表"""
        if self.filter_type is None:
            return player.behavior_history.copy()
        else:
            return [log for log in player.behavior_history if log['type'] == self.filter_type]
    
    def _render_scrollbar(self, surface, content_start_y, content_height, total_height):
        """渲染滚动条"""
        scrollbar_width = 8
        scrollbar_x = self.panel_width - self.margin - scrollbar_width
        
        # 滚动条背景
        scrollbar_bg_rect = pygame.Rect(scrollbar_x, content_start_y, scrollbar_width, content_height)
        pygame.draw.rect(surface, (50, 50, 50), scrollbar_bg_rect)
        
        # 滚动条滑块
        visible_ratio = content_height / total_height
        thumb_height = max(20, int(content_height * visible_ratio))
        scroll_ratio = self.scroll_offset / max(1, total_height - content_height)
        thumb_y = content_start_y + int((content_height - thumb_height) * scroll_ratio)
        
        thumb_rect = pygame.Rect(scrollbar_x, thumb_y, scrollbar_width, thumb_height)
        pygame.draw.rect(surface, (150, 150, 150), thumb_rect)
    
    def _render_controls_hint(self, surface):
        """渲染操作提示"""
        hints = [
            "L键: 关闭面板 | ↑↓/WS: 滚动 | Tab: 切换筛选 | Home/End: 跳转到顶部/底部"
        ]
        
        y_offset = self.panel_height - self.margin - 20
        for hint in hints:
            hint_text = self.small_font.render(hint, True, self.colors['default'])
            hint_rect = hint_text.get_rect(centerx=self.panel_width//2, y=y_offset)
            surface.blit(hint_text, hint_rect)
            y_offset += hint_text.get_height() + 5 