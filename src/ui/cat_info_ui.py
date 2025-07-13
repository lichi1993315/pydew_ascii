import pygame
import math
import unicodedata
from typing import Optional, Dict, List
from datetime import datetime
from src.utils.font_manager import FontManager

class TextRenderer:
    """统一的文本渲染引擎，处理文本换行、容器大小和渲染"""
    
    def __init__(self):
        self.debug_mode = False
    
    def calculate_char_width(self, char: str, font: pygame.font.Font) -> int:
        """计算单个字符的宽度，针对中文字符和emoji优化"""
        try:
            # 检查是否是emoji字符
            if ord(char[0]) >= 0x1F000:  # 基本emoji范围
                return font.size(char)[0] if font.size(char)[0] > 0 else 20  # emoji默认宽度
            elif unicodedata.east_asian_width(char) in ('F', 'W'):
                # 全角字符（中文、日文等）
                return font.size(char)[0]
            else:
                # 半角字符
                return font.size(char)[0]
        except:
            # 回退：使用字体计算
            return font.size(char)[0] if font.size(char)[0] > 0 else 10
    
    def wrap_text_advanced(self, text: str, max_width: int, font: pygame.font.Font) -> List[str]:
        """高级文本换行算法，支持中文和emoji"""
        if not text:
            return [""]
        
        lines = []
        current_line = ""
        current_width = 0
        
        i = 0
        while i < len(text):
            char = text[i]
            char_width = self.calculate_char_width(char, font)
            
            # 检查是否需要换行
            if current_width + char_width > max_width and current_line:
                # 当前行已满，开始新行
                lines.append(current_line.strip())
                current_line = char
                current_width = char_width
            else:
                # 添加字符到当前行
                current_line += char
                current_width += char_width
            
            i += 1
        
        # 添加最后一行
        if current_line:
            lines.append(current_line.strip())
        
        return lines if lines else [""]
    
    def calculate_text_size(self, text: str, font: pygame.font.Font, max_width: int) -> tuple:
        """计算文本在给定宽度限制下的实际尺寸 (width, height)"""
        lines = self.wrap_text_advanced(text, max_width, font)
        if not lines:
            return (0, 0)
        
        # 计算最大行宽
        max_line_width = 0
        for line in lines:
            line_width = font.size(line)[0]
            max_line_width = max(max_line_width, line_width)
        
        # 计算总高度
        line_height = font.get_height()
        total_height = len(lines) * line_height
        
        return (min(max_line_width, max_width), total_height)
    
    def render_text_with_background(self, surface: pygame.Surface, text: str, 
                                  font: pygame.font.Font, text_color: tuple, 
                                  bg_color: tuple, pos: tuple, max_width: int,
                                  padding: int = 5, line_spacing: int = 2) -> tuple:
        """渲染带背景的文本，返回实际占用的矩形区域 (x, y, width, height)"""
        lines = self.wrap_text_advanced(text, max_width - 2 * padding, font)
        if not lines:
            return (*pos, 0, 0)
        
        # 计算背景尺寸
        text_width, text_height = self.calculate_text_size(text, font, max_width - 2 * padding)
        bg_width = text_width + 2 * padding
        bg_height = text_height + 2 * padding
        
        # 绘制背景
        bg_rect = pygame.Rect(pos[0], pos[1], bg_width, bg_height)
        pygame.draw.rect(surface, bg_color, bg_rect)
        pygame.draw.rect(surface, (200, 200, 200), bg_rect, 1)  # 边框
        
        # 绘制文本
        line_height = font.get_height()
        text_x = pos[0] + padding
        text_y = pos[1] + padding
        
        for i, line in enumerate(lines):
            if line.strip():  # 只渲染非空行
                line_surface = font.render(line, True, text_color)
                surface.blit(line_surface, (text_x, text_y + i * (line_height + line_spacing)))
        
        # 调试模式：绘制边界
        if self.debug_mode:
            pygame.draw.rect(surface, (255, 0, 0), bg_rect, 2)
        
        return (pos[0], pos[1], bg_width, bg_height)
    
    def render_multiline_text(self, surface: pygame.Surface, text: str,
                            font: pygame.font.Font, color: tuple, pos: tuple,
                            max_width: int, line_spacing: int = 2) -> int:
        """渲染多行文本，返回实际高度"""
        lines = self.wrap_text_advanced(text, max_width, font)
        if not lines:
            return 0
        
        line_height = font.get_height()
        
        for i, line in enumerate(lines):
            if line.strip():  # 只渲染非空行
                line_surface = font.render(line, True, color)
                surface.blit(line_surface, (pos[0], pos[1] + i * (line_height + line_spacing)))
        
        return len(lines) * (line_height + line_spacing)

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
        
        # 文本渲染引擎
        self.text_renderer = TextRenderer()
        
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
        
        desc_height = self.text_renderer.render_multiline_text(
            surface=surface,
            text=personality_desc,
            font=self.normal_font,
            color=self.colors['text'],
            pos=(desc_x, desc_y),
            max_width=desc_max_width,
            line_spacing=2
        )
        
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
        panel_margin = self.left_panel_x - self.panel_x + 20
        max_content_width = self.left_panel_width - 60  # 留出足够边距
        
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
            surface.blit(speaker_surface, (panel_margin + 20, current_y))
            
            # 对话内容（使用新的文本渲染引擎）
            message = entry['message']
            
            # 使用TextRenderer渲染带背景的文本
            bg_rect = self.text_renderer.render_text_with_background(
                surface=surface,
                text=message,
                font=self.small_font,
                text_color=(255, 255, 255),
                bg_color=self.colors['tab_active'],
                pos=(panel_margin + 20, current_y + 20),
                max_width=max_content_width,
                padding=8,
                line_spacing=2
            )
            
            # 更新Y位置
            current_y += bg_rect[3] + 30  # 背景高度 + 间距
    
    def _render_dialogue_content(self, surface, content_rect, tab_type):
        """渲染对话内容区域，返回内容总高度"""
        # 获取对话历史 - 包括与玩家的对话和猫猫之间的对话
        all_dialogues = []
        
        # 1. 获取与玩家的对话历史
        if hasattr(self, 'chat_ai') and self.chat_ai:
            cat_id = self.current_cat.npc_id
            if tab_type == "recent":
                player_history = self.chat_ai._get_recent_conversation_context(cat_id, 3)
            else:
                player_history = self.chat_ai._get_recent_conversation_context(cat_id, 10)
            
            # 转换为统一格式
            for entry in player_history:
                all_dialogues.append({
                    'type': 'player_chat',
                    'timestamp': entry.get('timestamp', ''),
                    'speaker': entry['speaker'],
                    'message': entry['message']
                })
        
        # 2. 获取猫猫之间的对话历史
        if hasattr(self.current_cat, 'get_cat_conversation_history'):
            cat_conversations = self.current_cat.get_cat_conversation_history()
            
            # 转换为统一格式
            for conv in cat_conversations:
                all_dialogues.append({
                    'type': 'cat_conversation',
                    'timestamp': conv.get('timestamp', ''),
                    'narrator': conv.get('narrator', ''),
                    'dialogue': conv.get('dialogue', [])
                })
        
        # 按时间排序
        all_dialogues.sort(key=lambda x: x.get('timestamp', ''), reverse=True)
        
        # 限制显示数量
        if tab_type == "recent":
            all_dialogues = all_dialogues[:5]
        else:
            all_dialogues = all_dialogues[:15]
        
        if not all_dialogues:
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
        
        for dialogue in all_dialogues:
            if dialogue['type'] == 'player_chat':
                # 渲染与玩家的对话
                entry_height = self._render_player_chat_entry(surface, dialogue, current_y, margin_x, content_rect)
            elif dialogue['type'] == 'cat_conversation':
                # 渲染猫猫之间的对话
                entry_height = self._render_cat_conversation_entry(surface, dialogue, current_y, margin_x, content_rect)
            else:
                entry_height = 0
            
            current_y += entry_height
            total_height += entry_height
        
        # 恢复剪切区域
        surface.set_clip(original_clip)
        
        return total_height
    
    def _render_player_chat_entry(self, surface, entry, current_y, margin_x, content_rect):
        """渲染与玩家的对话条目"""
        from datetime import datetime
        
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
            msg_height = self.text_renderer.render_multiline_text(
                surface=surface,
                text=message,
                font=self.normal_font,
                color=self.colors['text'],
                pos=(msg_rect.x, msg_rect.y),
                max_width=msg_rect.width,
                line_spacing=2
            )
        else:
            # 不在可见区域，只计算高度
            message = entry['message']
            _, msg_height = self.text_renderer.calculate_text_size(message, self.normal_font, content_rect.width - 80)
        
        return max(60, msg_height + 20)
    
    def _render_cat_conversation_entry(self, surface, conversation, current_y, margin_x, content_rect):
        """渲染猫猫之间对话的条目"""
        from datetime import datetime
        
        total_height = 0
        
        # 只在可见区域内渲染
        if current_y + 100 >= content_rect.top and current_y <= content_rect.bottom:
            # 渲染时间戳
            timestamp = conversation.get('timestamp', '')
            if timestamp:
                try:
                    dt = datetime.fromisoformat(timestamp)
                    time_str = dt.strftime("%m-%d %H:%M")
                except:
                    time_str = ""
            else:
                time_str = ""
            
            if time_str:
                time_surface = self.small_font.render(time_str, True, self.colors['subtitle'])
                surface.blit(time_surface, (content_rect.right - 80, current_y + 5))
            
            # 渲染旁白（如果有）
            narrator = conversation.get('narrator', '')
            narrator_height = 0
            if narrator:
                narrator_text = f"📖 {narrator}"
                narrator_max_width = content_rect.width - 60  # 留出边距
                
                # 只渲染文本，不要背景
                narrator_height = self.text_renderer.render_multiline_text(
                    surface=surface,
                    text=narrator_text,
                    font=self.small_font,
                    color=self.colors['subtitle'],
                    pos=(margin_x, current_y + 25),
                    max_width=narrator_max_width,
                    line_spacing=2
                )
                
            # 渲染对话内容
            # 确保对话在旁白之后正确定位
            dialogue_start_y = current_y + 25  # 时间戳行下方
            if narrator_height > 0:
                dialogue_start_y += narrator_height + 15  # 旁白高度 + 额外间距
            
            dialogue_y = dialogue_start_y
            
            # 重新计算total_height
            total_height = dialogue_start_y - current_y
            for i, dialogue_entry in enumerate(conversation.get('dialogue', [])):
                speaker = dialogue_entry.get('speaker', '')
                text = dialogue_entry.get('text', '')
                
                # 确定说话者是否是当前猫咪
                is_current_cat = (speaker == self.current_cat.cat_name)
                
                if is_current_cat:
                    # 当前猫咪
                    speaker_color = self.current_cat.char_color
                    avatar_char = self.current_cat.ascii_char
                    text_x = margin_x + 40
                    avatar_x = margin_x + 20
                else:
                    # 其他猫咪 - 需要根据名字找到对应的猫咪
                    other_cat = self._find_cat_by_name(speaker)
                    if other_cat:
                        speaker_color = other_cat.char_color
                        avatar_char = other_cat.ascii_char
                    else:
                        speaker_color = (200, 150, 100)  # 默认颜色
                        avatar_char = "🐱"  # 默认头像
                    text_x = margin_x + 40
                    avatar_x = margin_x + 20
                
                # 绘制小头像
                pygame.draw.circle(surface, speaker_color, (avatar_x, dialogue_y + 10), 8)
                try:
                    # 优先使用emoji字体
                    char_surface = self.emoji_font.render(avatar_char, True, (255, 255, 255))
                    if char_surface.get_width() == 0:
                        # emoji字体失败时使用小字体
                        char_surface = self.small_font.render(avatar_char, True, (255, 255, 255))
                        if char_surface.get_width() == 0:
                            # 最后的回退选项
                            char_surface = self.small_font.render("🐱", True, (255, 255, 255))
                except:
                    char_surface = self.small_font.render("🐱", True, (255, 255, 255))
                
                char_rect = char_surface.get_rect(center=(avatar_x, dialogue_y + 10))
                surface.blit(char_surface, char_rect)
                
                # 说话者名字
                speaker_surface = self.small_font.render(f"{speaker}:", True, self.colors['text'])
                surface.blit(speaker_surface, (text_x, dialogue_y))
                
                # 对话文本 - 使用TextRenderer支持动态换行
                text_max_width = content_rect.width - 100  # 给头像和边距留空间
                
                # 使用TextRenderer渲染多行文本
                text_height = self.text_renderer.render_multiline_text(
                    surface=surface,
                    text=text,
                    font=self.small_font,
                    color=self.colors['text'],
                    pos=(text_x, dialogue_y + 18),
                    max_width=text_max_width,
                    line_spacing=2
                )
                
                dialogue_y += max(25, text_height + 18 + 5)  # 18是名字的高度
                total_height += max(25, text_height + 18 + 5)
        else:
            # 不在可见区域，估算高度（使用TextRenderer）
            narrator = conversation.get('narrator', '')
            dialogue_entries = conversation.get('dialogue', [])
            
            # 估算旁白高度
            narrator_height = 0
            if narrator:
                narrator_text = f"📖 {narrator}"
                narrator_max_width = content_rect.width - 60
                _, narrator_height = self.text_renderer.calculate_text_size(narrator_text, self.small_font, narrator_max_width)
            
            # 计算对话起始位置（与可见区域逻辑一致）
            dialogue_start_offset = 25  # 时间戳行下方
            if narrator_height > 0:
                dialogue_start_offset += narrator_height + 15  # 旁白高度 + 额外间距
            
            # 估算对话高度
            dialogue_height = 0
            for dialogue_entry in dialogue_entries:
                text = dialogue_entry.get('text', '')
                text_max_width = content_rect.width - 100
                _, text_height = self.text_renderer.calculate_text_size(text, self.small_font, text_max_width)
                entry_height = max(25, text_height + 18 + 5)
                dialogue_height += entry_height
            
            total_height = dialogue_start_offset + dialogue_height
        
        return total_height + 20  # 添加底部间距
    
    def _find_cat_by_name(self, cat_name):
        """根据猫咪名字查找猫咪对象"""
        # 通过current_cat的cat_manager找到所有猫咪
        if hasattr(self.current_cat, 'cat_manager') and self.current_cat.cat_manager:
            for cat in self.current_cat.cat_manager.cats:
                if cat.cat_name == cat_name:
                    return cat
        return None
    
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