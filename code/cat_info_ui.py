import pygame
import math
from typing import Optional, Dict, List
from datetime import datetime
from font_manager import FontManager

class CatInfoUI:
    """猫咪详细信息UI界面"""
    
    def __init__(self, screen_width: int, screen_height: int):
        self.screen_width = screen_width
        self.screen_height = screen_height
        self.is_active = False
        self.current_cat = None
        
        # 字体管理器
        self.font_manager = FontManager.get_instance()
        self.title_font = self.font_manager.load_chinese_font(24, "cat_info_title")
        self.normal_font = self.font_manager.load_chinese_font(16, "cat_info_normal")
        self.small_font = self.font_manager.load_chinese_font(14, "cat_info_small")
        self.large_font = self.font_manager.load_chinese_font(18, "cat_info_large")
        self.emoji_font = self.font_manager.load_emoji_font(32, "cat_info_emoji")
        
        # 颜色配置
        self.colors = {
            'background': (240, 248, 255, 220),    # 淡蓝色半透明背景
            'panel_bg': (255, 255, 255, 240),     # 白色面板背景
            'border': (100, 149, 237),            # 边框蓝色
            'title': (25, 25, 112),               # 深蓝色标题
            'text': (51, 51, 51),                 # 深灰色文本
            'subtitle': (105, 105, 105),          # 灰色副标题
            'affection_bg': (220, 220, 220),      # 好感度背景
            'affection_fill': (255, 105, 180),    # 好感度填充（粉色）
            'tab_active': (100, 149, 237),        # 激活标签页
            'tab_inactive': (176, 196, 222),      # 非激活标签页
            'dialogue_bg': (248, 248, 255),       # 对话背景
            'dialogue_border': (211, 211, 211),   # 对话边框
        }
        
        # UI布局配置
        self.panel_width = 800
        self.panel_height = 500
        self.panel_x = (screen_width - self.panel_width) // 2
        self.panel_y = (screen_height - self.panel_height) // 2
        
        # 左侧面板配置
        self.left_panel_width = 350
        self.left_panel_x = self.panel_x + 20
        self.left_panel_y = self.panel_y + 20
        
        # 右侧面板配置
        self.right_panel_width = 400
        self.right_panel_x = self.panel_x + self.left_panel_width + 40
        self.right_panel_y = self.panel_y + 20
        
        # 头像配置
        self.avatar_size = 80
        self.avatar_x = self.left_panel_x + 20
        self.avatar_y = self.left_panel_y + 20
        
        # 当前选中的标签页
        self.current_tab = "recent"  # "recent" 或 "history"
        
        # 滚动配置
        self.scroll_offset = 0
        self.scroll_speed = 3
        
    def show_cat_info(self, cat_sprite, chat_ai):
        """显示猫咪详细信息"""
        self.is_active = True
        self.current_cat = cat_sprite
        self.chat_ai = chat_ai
        self.scroll_offset = 0
        # print(f"[CatInfoUI] 显示猫咪信息: {cat_sprite.cat_name}")
    
    def hide_cat_info(self):
        """隐藏猫咪详细信息"""
        self.is_active = False
        self.current_cat = None
        # print("[CatInfoUI] 隐藏猫咪信息")
    
    def handle_input(self, event):
        """处理输入事件"""
        if not self.is_active:
            return False
        
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE or event.key == pygame.K_t:
                self.hide_cat_info()
                return True
            elif event.key == pygame.K_1:
                self.current_tab = "recent"
                return True
            elif event.key == pygame.K_2:
                self.current_tab = "history"
                return True
            elif event.key == pygame.K_UP:
                self.scroll_offset = max(0, self.scroll_offset - self.scroll_speed)
                return True
            elif event.key == pygame.K_DOWN:
                # 需要计算最大滚动距离
                if hasattr(self, 'max_scroll_offset'):
                    self.scroll_offset = min(self.max_scroll_offset, self.scroll_offset + self.scroll_speed)
                else:
                    self.scroll_offset += self.scroll_speed
                return True
        
        elif event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:  # 左键点击
                # 检查是否点击了标签页
                tab_rect = pygame.Rect(self.right_panel_x, self.right_panel_y + 10, 100, 30)
                if tab_rect.collidepoint(event.pos):
                    self.current_tab = "recent"
                    return True
                
                tab_rect = pygame.Rect(self.right_panel_x + 110, self.right_panel_y + 10, 100, 30)
                if tab_rect.collidepoint(event.pos):
                    self.current_tab = "history"
                    return True
                
                # 检查是否点击在面板外（关闭面板）
                panel_rect = pygame.Rect(self.panel_x, self.panel_y, self.panel_width, self.panel_height)
                if not panel_rect.collidepoint(event.pos):
                    self.hide_cat_info()
                    return True
            
            elif event.button == 4:  # 鼠标滚轮向上
                self.scroll_offset = max(0, self.scroll_offset - self.scroll_speed)
                return True
            elif event.button == 5:  # 鼠标滚轮向下
                # 需要计算最大滚动距离
                if hasattr(self, 'max_scroll_offset'):
                    self.scroll_offset = min(self.max_scroll_offset, self.scroll_offset + self.scroll_speed)
                else:
                    self.scroll_offset += self.scroll_speed
                return True
        
        return True  # 消费所有事件，防止传递到游戏
    
    def render(self, surface):
        """渲染猫咪信息界面"""
        if not self.is_active or not self.current_cat:
            return
        
        # 绘制半透明背景
        overlay = pygame.Surface((self.screen_width, self.screen_height), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 120))
        surface.blit(overlay, (0, 0))
        
        # 绘制主面板
        panel_surface = pygame.Surface((self.panel_width, self.panel_height), pygame.SRCALPHA)
        panel_surface.fill(self.colors['panel_bg'])
        pygame.draw.rect(panel_surface, self.colors['border'], 
                        (0, 0, self.panel_width, self.panel_height), 3)
        
        # 渲染左侧面板
        self._render_left_panel(panel_surface)
        
        # 渲染右侧面板
        self._render_right_panel(panel_surface)
        
        # 将面板绘制到主屏幕
        surface.blit(panel_surface, (self.panel_x, self.panel_y))
        
        # 绘制关闭提示
        hint_text = "按 ESC 或 T 键关闭"
        hint_surface = self.small_font.render(hint_text, True, self.colors['subtitle'])
        hint_x = self.panel_x + self.panel_width - hint_surface.get_width() - 10
        hint_y = self.panel_y - 25
        surface.blit(hint_surface, (hint_x, hint_y))
    
    def _render_left_panel(self, surface):
        """渲染左侧面板"""
        # 绘制猫咪头像（圆形）
        avatar_center = (self.avatar_x - self.panel_x + self.avatar_size // 2, 
                        self.avatar_y - self.panel_y + self.avatar_size // 2)
        pygame.draw.circle(surface, self.colors['border'], avatar_center, self.avatar_size // 2 + 2)
        pygame.draw.circle(surface, self.current_cat.char_color, avatar_center, self.avatar_size // 2)
        
        # 在头像中心绘制猫咪ASCII字符（使用emoji字体）
        try:
            char_surface = self.emoji_font.render(self.current_cat.ascii_char, True, (255, 255, 255))
            if char_surface.get_width() == 0:
                # 如果emoji字体失败，回退到标题字体
                char_surface = self.title_font.render(self.current_cat.ascii_char, True, (255, 255, 255))
        except:
            # 完全失败时使用备用字符
            char_surface = self.title_font.render("🐱", True, (255, 255, 255))
        
        char_rect = char_surface.get_rect(center=avatar_center)
        surface.blit(char_surface, char_rect)
        
        # 猫咪名字和信息 - 与头像对齐
        info_x = self.avatar_x - self.panel_x + self.avatar_size + 20
        info_y = self.avatar_y - self.panel_y + 10  # 与头像顶部对齐
        
        # 名字
        name_text = f"{self.current_cat.cat_name}"
        name_surface = self.title_font.render(name_text, True, self.colors['title'])
        surface.blit(name_surface, (info_x, info_y))
        
        # 品种信息
        breed_text = f"品种: 猫子猫"
        breed_surface = self.normal_font.render(breed_text, True, self.colors['text'])
        surface.blit(breed_surface, (info_x, info_y + 30))
        
        # 好感度信息
        affection_text = f"好感度: 60/100"
        affection_surface = self.normal_font.render(affection_text, True, self.colors['text'])
        surface.blit(affection_surface, (info_x, info_y + 55))
        
        # 好感度进度条
        progress_x = info_x
        progress_y = info_y + 75
        progress_width = 150
        progress_height = 8
        
        # 背景
        pygame.draw.rect(surface, self.colors['affection_bg'], 
                        (progress_x, progress_y, progress_width, progress_height))
        # 填充 (60%)
        fill_width = int(progress_width * 0.6)
        pygame.draw.rect(surface, self.colors['affection_fill'], 
                        (progress_x, progress_y, fill_width, progress_height))
        
        # 宠物性格标题
        personality_y = info_y + 110
        personality_title = self.large_font.render("宠物性格", True, self.colors['title'])
        surface.blit(personality_title, (self.left_panel_x - self.panel_x + 20, personality_y))
        
        # 宠物性格描述 - 修复换行
        personality_desc = self._get_cat_personality_description()
        desc_y = personality_y + 35
        desc_x = self.left_panel_x - self.panel_x + 20
        desc_max_width = self.left_panel_width - 40
        
        # 添加调试信息
        # print(f"[CatInfoUI] 宠物性格描述: {personality_desc[:50]}...")
        # print(f"[CatInfoUI] 描述区域: x={desc_x}, y={desc_y}, max_width={desc_max_width}")
        
        # 绘制背景区域用于调试（可选）
        # pygame.draw.rect(surface, (255, 0, 0, 50), 
        #                 (desc_x, desc_y, desc_max_width, 100), 1)
        
        desc_height = self._render_multiline_text_improved(surface, personality_desc, 
                                   (desc_x, desc_y), desc_max_width, 
                                   self.normal_font, self.colors['text'])
        
        # 近期对话标题
        recent_y = desc_y + desc_height + 20
        recent_title = self.large_font.render("近期对话", True, self.colors['title'])
        surface.blit(recent_title, (self.left_panel_x - self.panel_x + 20, recent_y))
        
        # 渲染最近的对话记录
        self._render_recent_dialogues(surface, recent_y + 35)
    
    def _render_right_panel(self, surface):
        """渲染右侧面板"""
        # 绘制标签页
        tab_y = self.right_panel_y - self.panel_y + 10
        
        # 近期对话标签
        recent_color = self.colors['tab_active'] if self.current_tab == "recent" else self.colors['tab_inactive']
        pygame.draw.rect(surface, recent_color, 
                        (self.right_panel_x - self.panel_x, tab_y, 100, 30))
        recent_text = self.normal_font.render("近期对话", True, (255, 255, 255))
        surface.blit(recent_text, (self.right_panel_x - self.panel_x + 20, tab_y + 8))
        
        # 历史对话标签
        history_color = self.colors['tab_active'] if self.current_tab == "history" else self.colors['tab_inactive']
        pygame.draw.rect(surface, history_color, 
                        (self.right_panel_x - self.panel_x + 110, tab_y, 100, 30))
        history_text = self.normal_font.render("历史对话", True, (255, 255, 255))
        surface.blit(history_text, (self.right_panel_x - self.panel_x + 130, tab_y + 8))
        
        # 对话内容区域
        content_y = tab_y + 40
        content_rect = pygame.Rect(self.right_panel_x - self.panel_x, content_y, 
                                  self.right_panel_width - 30, self.panel_height - content_y - 20)  # 为滚动条留出空间
        pygame.draw.rect(surface, self.colors['dialogue_bg'], content_rect)
        pygame.draw.rect(surface, self.colors['dialogue_border'], content_rect, 1)
        
        # 渲染对话内容
        total_content_height = 0
        if self.current_tab == "recent":
            total_content_height = self._render_dialogue_content(surface, content_rect, "recent")
        else:
            total_content_height = self._render_dialogue_content(surface, content_rect, "history")
        
        # 计算和设置最大滚动偏移
        if total_content_height > content_rect.height:
            self.max_scroll_offset = total_content_height - content_rect.height
            self.scroll_offset = min(self.scroll_offset, self.max_scroll_offset)
            # 渲染滚动条
            self._render_right_scrollbar(surface, content_rect, total_content_height)
        else:
            self.max_scroll_offset = 0
            self.scroll_offset = 0
    
    def _render_recent_dialogues(self, surface, start_y):
        """渲染最近对话记录（左侧面板）"""
        if not hasattr(self, 'chat_ai') or not self.chat_ai:
            return
        
        # 获取对话历史
        cat_id = self.current_cat.npc_id
        recent_history = self.chat_ai._get_recent_conversation_context(cat_id, 3)
        
        if not recent_history:
            no_dialogue_text = "对话尚未开始"
            text_surface = self.small_font.render(no_dialogue_text, True, self.colors['subtitle'])
            surface.blit(text_surface, (self.left_panel_x - self.panel_x + 20, start_y))
            return
        
        current_y = start_y
        for entry in recent_history[-2:]:  # 只显示最近2条
            # 时间戳
            timestamp = entry.get('timestamp', '')
            if timestamp:
                try:
                    dt = datetime.fromisoformat(timestamp)
                    time_str = dt.strftime("%m-%d %H:%M")
                except:
                    time_str = "未知时间"
            else:
                time_str = "未知时间"
            
            # 发言者和时间
            speaker_text = f"{entry['speaker']} 今天 ({time_str}) 22:08"
            speaker_surface = self.small_font.render(speaker_text, True, self.colors['subtitle'])
            surface.blit(speaker_surface, (self.left_panel_x - self.panel_x + 40, current_y))
            
            # 对话内容（蓝色背景框）- 支持换行
            message = entry['message']
            max_msg_width = self.left_panel_width - 80
            
            # 计算需要的行数
            wrapped_lines = self._wrap_text_to_lines(message, max_msg_width, self.small_font)
            line_count = len(wrapped_lines)
            
            # 绘制蓝色背景框（根据行数调整高度）
            msg_height = max(25, line_count * 18 + 10)
            msg_rect = pygame.Rect(self.left_panel_x - self.panel_x + 40, current_y + 20, 
                                  max_msg_width, msg_height)
            pygame.draw.rect(surface, self.colors['tab_active'], msg_rect)
            pygame.draw.rect(surface, self.colors['border'], msg_rect, 1)
            
            # 对话文本（多行）
            for i, line in enumerate(wrapped_lines):
                line_surface = self.small_font.render(line, True, (255, 255, 255))
                surface.blit(line_surface, (msg_rect.x + 8, msg_rect.y + 5 + i * 18))
            
            current_y += msg_height + 10
    
    def _render_dialogue_content(self, surface, content_rect, tab_type):
        """渲染对话内容区域，返回内容总高度"""
        if not hasattr(self, 'chat_ai') or not self.chat_ai:
            return 0
        
        # 获取对话历史
        cat_id = self.current_cat.npc_id
        if tab_type == "recent":
            history = self.chat_ai._get_recent_conversation_context(cat_id, 5)
        else:
            history = self.chat_ai._get_recent_conversation_context(cat_id, 20)
        
        if not history:
            no_dialogue_text = "暂无对话记录"
            text_surface = self.normal_font.render(no_dialogue_text, True, self.colors['subtitle'])
            text_x = content_rect.x + (content_rect.width - text_surface.get_width()) // 2
            text_y = content_rect.y + 50
            surface.blit(text_surface, (text_x, text_y))
            return 100  # 返回基本高度
        
        # 创建剪切区域
        original_clip = surface.get_clip()
        surface.set_clip(content_rect)
        
        # 渲染对话记录
        current_y = content_rect.y + 10 - self.scroll_offset
        margin_x = content_rect.x + 10
        total_height = 10  # 起始边距
        
        for entry in history:
            entry_start_y = current_y
            
            # 发言者头像和名字
            if entry['speaker'] == "玩家":
                speaker_color = (100, 149, 237)
                avatar_char = "@"
            else:
                speaker_color = self.current_cat.char_color
                avatar_char = self.current_cat.ascii_char
            
            # 只在可见区域内渲染
            if current_y + 60 >= content_rect.top and current_y <= content_rect.bottom:
                # 绘制头像
                pygame.draw.circle(surface, speaker_color, (margin_x + 15, current_y + 15), 12)
                try:
                    char_surface = self.emoji_font.render(avatar_char, True, (255, 255, 255))
                    if char_surface.get_width() == 0:
                        char_surface = self.small_font.render(avatar_char, True, (255, 255, 255))
                except:
                    char_surface = self.small_font.render("@", True, (255, 255, 255))
                
                char_rect = char_surface.get_rect(center=(margin_x + 15, current_y + 15))
                surface.blit(char_surface, char_rect)
                
                # 发言者名字
                speaker_surface = self.normal_font.render(entry['speaker'], True, self.colors['text'])
                surface.blit(speaker_surface, (margin_x + 35, current_y + 5))
                
                # 时间戳
                timestamp = entry.get('timestamp', '')
                if timestamp:
                    try:
                        dt = datetime.fromisoformat(timestamp)
                        time_str = dt.strftime("%H:%M")
                    except:
                        time_str = ""
                else:
                    time_str = ""
                
                if time_str:
                    time_surface = self.small_font.render(time_str, True, self.colors['subtitle'])
                    surface.blit(time_surface, (content_rect.right - 50, current_y + 8))
                
                # 对话内容
                message = entry['message']
                msg_rect = pygame.Rect(margin_x + 35, current_y + 25, 
                                      content_rect.width - 80, 0)
                
                # 计算消息高度并渲染
                msg_height = self._render_message_text(surface, message, msg_rect, current_y)
            else:
                # 不在可见区域，只计算高度
                message = entry['message']
                wrapped_lines = self._wrap_text_to_lines(message, content_rect.width - 80, self.normal_font)
                msg_height = len(wrapped_lines) * 20
            
            entry_height = max(60, msg_height + 20)
            current_y += entry_height
            total_height += entry_height
        
        # 恢复剪切区域
        surface.set_clip(original_clip)
        
        return total_height
    
    def _render_message_text(self, surface, message, rect, y_offset):
        """渲染消息文本，支持换行"""
        words = message.split()
        lines = []
        current_line = ""
        
        for word in words:
            test_line = current_line + (" " if current_line else "") + word
            if self.normal_font.size(test_line)[0] <= rect.width:
                current_line = test_line
            else:
                if current_line:
                    lines.append(current_line)
                current_line = word
        
        if current_line:
            lines.append(current_line)
        
        # 渲染每一行
        line_height = 20
        for i, line in enumerate(lines):
            line_surface = self.normal_font.render(line, True, self.colors['text'])
            surface.blit(line_surface, (rect.x, y_offset + 25 + i * line_height))
        
        return len(lines) * line_height
    
    def _render_multiline_text(self, surface, text, pos, max_width, font, color):
        """渲染多行文本，返回实际高度"""
        words = text.split()
        lines = []
        current_line = ""
        
        for word in words:
            test_line = current_line + (" " if current_line else "") + word
            if font.size(test_line)[0] <= max_width:
                current_line = test_line
            else:
                if current_line:
                    lines.append(current_line)
                current_line = word
        
        if current_line:
            lines.append(current_line)
        
        # 渲染每一行
        line_height = 22
        for i, line in enumerate(lines):
            line_surface = font.render(line, True, color)
            surface.blit(line_surface, (pos[0], pos[1] + i * line_height))
        
        # 返回实际占用的高度
        return len(lines) * line_height
    
    def _wrap_text_to_lines(self, text, max_width, font):
        """将文本按宽度分割成行"""
        words = text.split()
        lines = []
        current_line = ""
        
        for word in words:
            test_line = current_line + (" " if current_line else "") + word
            if font.size(test_line)[0] <= max_width:
                current_line = test_line
            else:
                if current_line:
                    lines.append(current_line)
                current_line = word
        
        if current_line:
            lines.append(current_line)
        
        return lines if lines else [text]
    
    def _render_multiline_text_improved(self, surface, text, pos, max_width, font, color):
        """改进的多行文本渲染，处理中文换行"""
        if not text:
            return 0
        
        # print(f"[CatInfoUI] 渲染多行文本: '{text}', 最大宽度: {max_width}")
        
        # 处理中文文本换行 - 按字符分割而不是按单词
        lines = []
        current_line = ""
        line_height = 22
        
        # 先尝试按单词分割
        words = text.split()
        for word in words:
            test_line = current_line + (" " if current_line else "") + word
            text_width = font.size(test_line)[0]
            
            if text_width <= max_width:
                current_line = test_line
            else:
                if current_line:
                    lines.append(current_line)
                    current_line = word
                else:
                    # 单个单词太长，按字符分割
                    for char in word:
                        test_char = current_line + char
                        if font.size(test_char)[0] <= max_width:
                            current_line = test_char
                        else:
                            if current_line:
                                lines.append(current_line)
                            current_line = char
        
        if current_line:
            lines.append(current_line)
        
        # print(f"[CatInfoUI] 分割后的行数: {len(lines)}")
        # for i, line in enumerate(lines):
            # print(f"[CatInfoUI] 第{i+1}行: '{line}' (宽度: {font.size(line)[0]})")
        
        # 渲染每一行
        for i, line in enumerate(lines):
            line_surface = font.render(line, True, color)
            line_y = pos[1] + i * line_height
            surface.blit(line_surface, (pos[0], line_y))
            # print(f"[CatInfoUI] 渲染第{i+1}行在位置: ({pos[0]}, {line_y})")
        
        total_height = len(lines) * line_height
        # print(f"[CatInfoUI] 总高度: {total_height}")
        return total_height
    
    def _render_right_scrollbar(self, surface, content_rect, total_content_height):
        """渲染右侧滚动条"""
        scrollbar_width = 8
        scrollbar_x = content_rect.right + 5
        scrollbar_y = content_rect.top
        scrollbar_height = content_rect.height
        
        # 滚动条背景
        scrollbar_bg_rect = pygame.Rect(scrollbar_x, scrollbar_y, scrollbar_width, scrollbar_height)
        pygame.draw.rect(surface, (60, 60, 60), scrollbar_bg_rect)
        pygame.draw.rect(surface, (120, 120, 120), scrollbar_bg_rect, 1)
        
        # 计算滑块大小和位置
        if total_content_height > content_rect.height:
            # 滑块高度与可见内容比例成正比
            thumb_height = max(20, int(scrollbar_height * content_rect.height / total_content_height))
            
            # 滑块位置与滚动偏移成正比
            max_scroll = total_content_height - content_rect.height
            if max_scroll > 0:
                scroll_ratio = self.scroll_offset / max_scroll
                thumb_y = scrollbar_y + int((scrollbar_height - thumb_height) * scroll_ratio)
            else:
                thumb_y = scrollbar_y
            
            # 绘制滑块
            thumb_rect = pygame.Rect(scrollbar_x + 1, thumb_y, scrollbar_width - 2, thumb_height)
            pygame.draw.rect(surface, (180, 180, 180), thumb_rect)
            pygame.draw.rect(surface, (200, 200, 200), thumb_rect, 1)
    
    def _get_cat_personality_description(self):
        """获取猫咪性格描述"""
        personality_descriptions = {
            "活泼好动，喜欢到处跑跳": "小吉总是充满活力，充满好奇心，而且喜欢玩耍。他大部分时间都在研究各种东西和到处奔跑，而怎么想都很难让它保持安静。下次能和他一起做些什么活动吗？",
            "温顺安静，喜欢晒太阳": "小白是一只非常温和安静的猫咪，喜欢在阳光下慵懒地休息。性格温顺，不喜欢太多的打扰。",
            "好奇心强，喜欢探索新事物": "小黑对世界充满好奇，总是想要探索新的地方和事物。喜欢冒险，但有时会因为太好奇而惹麻烦。",
            "慵懒可爱，总是想睡觉": "小灰是一只特别爱睡觉的猫咪，大部分时间都在打盹。动作缓慢，但非常可爱。",
            "聪明机灵，会各种小把戏": "小花是一只聪明的猫咪，学东西很快，还会一些有趣的小把戏。喜欢展示自己的聪明才智。",
            "粘人撒娇，喜欢被摸摸": "咪咪非常亲人，喜欢被抚摸和拥抱。总是缠着主人撒娇，是一只非常粘人的猫咪。",
            "独立自主，有自己的想法": "喵喵很独立，有自己的生活方式和想法。不太依赖别人，喜欢按照自己的节奏生活。",
            "贪吃小猫，对食物很敏感": "球球对食物特别敏感，总是在寻找好吃的。胃口很好，但也因此变得圆滚滚的。",
            "胆小害羞，容易受到惊吓": "毛毛比较胆小，容易受到惊吓。需要温柔对待，一旦熟悉了就会很亲近。",
            "淘气捣蛋，喜欢恶作剧": "糖糖是一只调皮的猫咪，喜欢恶作剧和制造小麻烦。虽然淘气，但非常有趣。"
        }
        
        return personality_descriptions.get(self.current_cat.cat_personality, 
                                          "这是一只可爱的猫咪，有着独特的性格。")