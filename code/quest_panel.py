import pygame
from typing import List
from font_manager import FontManager

class QuestPanel:
    """任务面板UI"""
    
    def __init__(self):
        self.is_active = False
        self.font_manager = FontManager.get_instance()
        
        # 字体设置
        self.title_font = self.font_manager.load_chinese_font(32, "quest_title_font")
        self.header_font = self.font_manager.load_chinese_font(24, "quest_header_font")
        self.text_font = self.font_manager.load_chinese_font(18, "quest_text_font")
        self.small_font = self.font_manager.load_chinese_font(16, "quest_small_font")
        
        # 颜色设置
        self.colors = {
            'background': (0, 0, 0, 180),        # 半透明黑色背景
            'border': (255, 255, 255),           # 白色边框
            'title': (255, 215, 0),              # 金色标题
            'active_header': (0, 255, 0),        # 绿色活跃任务标题
            'completed_header': (128, 128, 128), # 灰色已完成任务标题
            'quest_title': (255, 255, 255),      # 白色任务标题
            'quest_desc': (200, 200, 200),       # 浅灰色任务描述
            'quest_progress': (100, 255, 100),   # 浅绿色任务进度
            'reward': (255, 255, 100),           # 黄色奖励
            'completed': (100, 255, 100),        # 绿色已完成标记
        }
        
        # 面板设置
        self.panel_width = 800
        self.panel_height = 600
        self.margin = 20
        self.line_spacing = 25
        
    def toggle(self):
        """切换任务面板显示状态"""
        self.is_active = not self.is_active
        print(f"[任务面板] 面板状态: {'开启' if self.is_active else '关闭'}")
    
    def render(self, surface, player):
        """渲染任务面板"""
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
        panel_surface.set_alpha(180)
        
        # 绘制边框
        pygame.draw.rect(panel_surface, self.colors['border'], 
                        (0, 0, self.panel_width, self.panel_height), 3)
        
        # 绘制标题
        title_text = self.title_font.render("任务面板", True, self.colors['title'])
        title_rect = title_text.get_rect(centerx=self.panel_width//2, y=self.margin)
        panel_surface.blit(title_text, title_rect)
        
        # 当前Y位置
        current_y = title_rect.bottom + self.margin
        
        # 绘制活跃任务
        current_y = self._render_active_quests(panel_surface, player, current_y)
        
        # 添加分隔线
        if player.active_quests and player.completed_quests:
            pygame.draw.line(panel_surface, self.colors['border'], 
                           (self.margin, current_y), 
                           (self.panel_width - self.margin, current_y), 2)
            current_y += self.margin
        
        # 绘制已完成任务
        current_y = self._render_completed_quests(panel_surface, player, current_y)
        
        # 绘制操作提示
        hint_text = self.small_font.render("按 Q 键关闭任务面板", True, self.colors['quest_desc'])
        hint_rect = hint_text.get_rect(centerx=self.panel_width//2, 
                                     y=self.panel_height - self.margin - hint_text.get_height())
        panel_surface.blit(hint_text, hint_rect)
        
        # 将面板绘制到主屏幕
        surface.blit(panel_surface, (panel_x, panel_y))
    
    def _render_active_quests(self, surface, player, start_y):
        """渲染活跃任务"""
        current_y = start_y
        
        # 活跃任务标题
        header_text = self.header_font.render("进行中的任务", True, self.colors['active_header'])
        surface.blit(header_text, (self.margin, current_y))
        current_y += header_text.get_height() + 10
        
        if not player.active_quests:
            no_quest_text = self.text_font.render("暂无进行中的任务", True, self.colors['quest_desc'])
            surface.blit(no_quest_text, (self.margin * 2, current_y))
            current_y += no_quest_text.get_height() + self.line_spacing
        else:
            for quest in player.active_quests:
                current_y = self._render_quest_item(surface, quest, player, current_y, is_active=True)
        
        return current_y + self.margin
    
    def _render_completed_quests(self, surface, player, start_y):
        """渲染已完成任务"""
        current_y = start_y
        
        # 已完成任务标题
        header_text = self.header_font.render("已完成的任务", True, self.colors['completed_header'])
        surface.blit(header_text, (self.margin, current_y))
        current_y += header_text.get_height() + 10
        
        if not player.completed_quests:
            no_quest_text = self.text_font.render("暂无已完成的任务", True, self.colors['quest_desc'])
            surface.blit(no_quest_text, (self.margin * 2, current_y))
            current_y += no_quest_text.get_height() + self.line_spacing
        else:
            # 显示最近完成的5个任务
            recent_completed = player.completed_quests[-5:] if len(player.completed_quests) > 5 else player.completed_quests
            for quest in recent_completed:
                current_y = self._render_quest_item(surface, quest, player, current_y, is_active=False)
        
        return current_y
    
    def _render_quest_item(self, surface, quest, player, start_y, is_active=True):
        """渲染单个任务项目"""
        current_y = start_y
        indent = self.margin * 2
        
        # 任务标题
        title_color = self.colors['quest_title'] if is_active else self.colors['completed']
        title_prefix = "◆ " if is_active else "✓ "
        title_text = self.text_font.render(f"{title_prefix}{quest.title}", True, title_color)
        surface.blit(title_text, (indent, current_y))
        current_y += title_text.get_height() + 5
        
        # 任务描述
        desc_text = self.small_font.render(f"  {quest.description}", True, self.colors['quest_desc'])
        surface.blit(desc_text, (indent + 20, current_y))
        current_y += desc_text.get_height() + 5
        
        if is_active:
            # 显示任务进度
            progress_info = self._get_quest_progress(quest, player)
            if progress_info:
                for progress_line in progress_info:
                    progress_text = self.small_font.render(f"  进度: {progress_line}", True, self.colors['quest_progress'])
                    surface.blit(progress_text, (indent + 20, current_y))
                    current_y += progress_text.get_height() + 3
        
        # 显示奖励
        reward_text = self._format_rewards(quest.rewards)
        if reward_text:
            reward_surface = self.small_font.render(f"  奖励: {reward_text}", True, self.colors['reward'])
            surface.blit(reward_surface, (indent + 20, current_y))
            current_y += reward_surface.get_height() + 5
        
        return current_y + 10
    
    def _get_quest_progress(self, quest, player):
        """获取任务进度信息"""
        progress_info = []
        
        for objective_type, params in quest.objectives.items():
            if objective_type == "fishing_attempts":
                required_num = params.get("num", 1)
                current = player.fishing_contest_stats["total_attempts"]
                progress_info.append(f"钓鱼次数: {current}/{required_num}")
            
            elif objective_type == "catch_fish":
                minimum_length = params.get("minimum_length", 0)
                minimum_rarity = params.get("minimum_rarity", None)
                
                if minimum_length > 0:
                    current = player.fishing_contest_stats["max_fish_length"]
                    progress_info.append(f"最大鱼长度: {current}cm/{minimum_length}cm")
                elif minimum_rarity:
                    # 计算满足稀有度要求的鱼数量
                    rarity_levels = {"common": 1, "uncommon": 2, "rare": 3, "epic": 4, "legendary": 5}
                    min_level = rarity_levels.get(minimum_rarity, 3)
                    current_count = 0
                    
                    for fish in player.fish_inventory:
                        fish_rarity_level = rarity_levels.get(fish.get("rarity", "common"), 1)
                        if fish_rarity_level >= min_level:
                            current_count += 1
                    
                    # 检查历史统计
                    if minimum_rarity == "rare":
                        current_count = max(current_count, player.fishing_contest_stats["rare_fish_count"])
                    
                    progress_info.append(f"稀有鱼({minimum_rarity}+): {current_count}/{required_num}")
            
            elif objective_type == "talk_to_npc":
                target = params.get("target", "")
                if target == "fisherman":
                    status = "已完成" if player.fishing_contest_stats["fisherman_talked"] else "未完成"
                    progress_info.append(f"与渔夫对话: {status}")
                elif target == "trader":
                    status = "已完成" if player.fishing_contest_stats["trader_talked"] else "未完成" 
                    progress_info.append(f"与商人对话: {status}")
                elif target == "farmer":
                    status = "已完成" if player.fishing_contest_stats["farmer_talked"] else "未完成"
                    progress_info.append(f"与农民对话: {status}")
            
            elif objective_type == "sell_fish":
                fish_type = params.get("fish_type", "all")
                # if fish_type == "all":
                status = "已完成" if player.fishing_contest_stats["trader_sold"] else "未完成"
                progress_info.append(f"向商人出售鱼类: {status}")
                # 可以添加特定鱼类出售
        
        return progress_info
    
    def _format_rewards(self, rewards):
        """格式化奖励信息"""
        reward_parts = []
        
        if 'money' in rewards:
            reward_parts.append(f"{rewards['money']}金币")
        
        if 'items' in rewards:
            for item, count in rewards['items'].items():
                reward_parts.append(f"{item} x{count}")
        
        if 'relationship' in rewards:
            reward_parts.append(f"关系 +{rewards['relationship']}")
        
        return ", ".join(reward_parts) if reward_parts else "无" 