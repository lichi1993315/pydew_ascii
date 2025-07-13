import pygame
import asyncio
from typing import List, Optional, Callable
from src.utils.font_manager import FontManager
from datetime import datetime

class ChatPanel:
    """聊天面板UI - 显示在屏幕左下角"""
    
    def __init__(self, screen_width: int, screen_height: int):
        self.screen_width = screen_width
        self.screen_height = screen_height
        self.is_active = False
        self.is_input_active = False
        
        # AI回复系统
        self.message_callback: Optional[Callable] = None  # 当玩家发送消息时的回调函数
        self.pending_ai_response = False  # 是否在等待AI回复
        
        # 游戏回调系统
        self.spawn_cat_callback: Optional[Callable] = None  # 生成猫咪的回调函数
        
        # 字体管理器
        self.font_manager = FontManager.get_instance()
        self.message_font = self.font_manager.load_chinese_font(16, "chat_message_font")
        self.input_font = self.font_manager.load_chinese_font(18, "chat_input_font")
        self.timestamp_font = self.font_manager.load_chinese_font(12, "chat_timestamp_font")
        
        # 颜色设置
        self.colors = {
            'background': (0, 0, 0, 180),        # 半透明黑色背景
            'input_background': (40, 40, 40),    # 输入框背景
            'border': (100, 100, 100),           # 边框颜色
            'input_border': (150, 150, 150),     # 输入框边框
            'input_active_border': (255, 255, 255), # 激活输入框边框
            'message_text': (255, 255, 255),     # 消息文本
            'input_text': (255, 255, 255),       # 输入文本
            'timestamp': (150, 150, 150),        # 时间戳
            'system_message': (255, 255, 100),   # 系统消息
            'cursor': (255, 255, 255),           # 输入光标
        }
        
        # 面板设置
        self.panel_width = 400
        self.panel_height = 300
        self.panel_x = 20
        self.panel_y = screen_height - self.panel_height - 20
        
        # 输入框设置
        self.input_height = 30
        self.input_margin = 10
        self.input_rect = pygame.Rect(
            self.panel_x + self.input_margin,
            self.panel_y + self.panel_height - self.input_height - self.input_margin,
            self.panel_width - 2 * self.input_margin,
            self.input_height
        )
        
        # 消息区域设置
        self.message_area_height = self.panel_height - self.input_height - 3 * self.input_margin
        self.message_area_rect = pygame.Rect(
            self.panel_x + self.input_margin,
            self.panel_y + self.input_margin,
            self.panel_width - 2 * self.input_margin,
            self.message_area_height
        )
        
        # 消息历史
        self.messages = []
        self.max_messages = 50
        self.scroll_offset = 0
        self.line_height = 20
        
        # 输入状态
        self.input_text = ""
        self.cursor_position = 0
        self.cursor_blink_timer = 0
        self.cursor_visible = True
        
        # 滚动设置
        self.scroll_speed = 3
        self.auto_scroll = True  # 是否自动滚动到底部
        self.user_scrolled = False  # 用户是否手动滚动过
        
        # 添加欢迎消息
        self.add_system_message("聊天系统已启动 - 按 Enter 键开始输入")
        
    def toggle(self):
        """切换聊天面板显示状态"""
        self.is_active = not self.is_active
        if not self.is_active:
            self.is_input_active = False
            self.input_text = ""
            self.cursor_position = 0
        print(f"[聊天面板] 面板状态: {'开启' if self.is_active else '关闭'}")
    
    def toggle_input(self):
        """切换输入状态"""
        if self.is_active:
            self.is_input_active = not self.is_input_active
            if not self.is_input_active:
                self.input_text = ""
                self.cursor_position = 0
            print(f"[聊天面板] 输入状态: {'激活' if self.is_input_active else '关闭'}")
    
    def add_message(self, message: str, sender: str = "玩家"):
        """添加聊天消息"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        self.messages.append({
            'text': message,
            'sender': sender,
            'timestamp': timestamp,
            'type': 'message'
        })
        
        # 限制消息数量
        if len(self.messages) > self.max_messages:
            self.messages.pop(0)
        
        # 自动滚动到最新消息
        self.scroll_to_bottom()
        
        print(f"[聊天面板] {sender}: {message}")
        
        # 检查是否是特殊命令
        if sender == "玩家" and message.startswith("/"):
            self._handle_chat_command(message)
            return
        
        # 如果是玩家消息且设置了回调函数，触发AI回复
        if sender == "玩家":
            print(f"[聊天面板] 检查AI回复条件: message_callback={self.message_callback is not None}, pending_ai_response={self.pending_ai_response}")
            if self.message_callback and not self.pending_ai_response:
                print(f"[聊天面板] 触发AI回复处理")
                self.pending_ai_response = True
                self.message_callback(message)
            elif self.pending_ai_response:
                print(f"[聊天面板] 跳过AI回复 - 正在等待之前的回复")
            elif not self.message_callback:
                print(f"[聊天面板] 跳过AI回复 - 没有设置回调函数")
    
    def add_system_message(self, message: str):
        """添加系统消息"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        self.messages.append({
            'text': message,
            'sender': "系统",
            'timestamp': timestamp,
            'type': 'system'
        })
        
        # 限制消息数量
        if len(self.messages) > self.max_messages:
            self.messages.pop(0)
        
        # 自动滚动到最新消息
        self.scroll_to_bottom()
        
        print(f"[聊天面板] 系统: {message}")
    
    def scroll_to_bottom(self):
        """滚动到底部"""
        if self.auto_scroll and not self.user_scrolled:
            total_lines = self._calculate_total_display_lines()
            visible_lines = self.message_area_height // self.line_height
            self.scroll_offset = max(0, total_lines - visible_lines)
    
    def _calculate_total_display_lines(self) -> int:
        """计算所有消息需要的总显示行数"""
        total_lines = 0
        max_width = self.panel_width - 2 * self.input_margin
        
        for message in self.messages:
            # 构建显示文本
            display_text = f"[{message['sender']}] {message['text']}"
            
            # 计算文本换行后的行数
            wrapped_lines = self._wrap_text(display_text, max_width)
            total_lines += len(wrapped_lines)
            
            # 时间戳行
            total_lines += 1
            
        return total_lines
    
    def scroll_up(self):
        """向上滚动"""
        self.scroll_offset = max(0, self.scroll_offset - self.scroll_speed)
        self.user_scrolled = True
        self.auto_scroll = False
    
    def scroll_down(self):
        """向下滚动"""
        total_lines = self._calculate_total_display_lines()
        visible_lines = self.message_area_height // self.line_height
        max_scroll = max(0, total_lines - visible_lines)
        
        self.scroll_offset = min(max_scroll, self.scroll_offset + self.scroll_speed)
        
        # 如果滚动到底部，重新启用自动滚动
        if self.scroll_offset >= max_scroll:
            self.auto_scroll = True
            self.user_scrolled = False
    
    def scroll_to_top(self):
        """滚动到顶部"""
        self.scroll_offset = 0
        self.user_scrolled = True
        self.auto_scroll = False
    
    def force_scroll_to_bottom(self):
        """强制滚动到底部"""
        total_lines = self._calculate_total_display_lines()
        visible_lines = self.message_area_height // self.line_height
        self.scroll_offset = max(0, total_lines - visible_lines)
        self.auto_scroll = True
        self.user_scrolled = False
    
    def handle_input(self, event):
        """处理输入事件"""
        if not self.is_active:
            return False
        
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_RETURN:
                if self.is_input_active:
                    # 发送消息
                    if self.input_text.strip():
                        self.add_message(self.input_text.strip())
                        self.input_text = ""
                        self.cursor_position = 0
                    self.is_input_active = False
                else:
                    # 激活输入
                    self.is_input_active = True
                return True
            
            elif event.key == pygame.K_ESCAPE:
                if self.is_input_active:
                    # 取消输入
                    self.is_input_active = False
                    self.input_text = ""
                    self.cursor_position = 0
                    return True
                else:
                    # 关闭面板
                    self.toggle()
                    return True
            
            elif self.is_input_active:
                # 处理文本输入
                if event.key == pygame.K_BACKSPACE:
                    if self.cursor_position > 0:
                        self.input_text = (self.input_text[:self.cursor_position-1] + 
                                         self.input_text[self.cursor_position:])
                        self.cursor_position -= 1
                elif event.key == pygame.K_DELETE:
                    if self.cursor_position < len(self.input_text):
                        self.input_text = (self.input_text[:self.cursor_position] + 
                                         self.input_text[self.cursor_position+1:])
                elif event.key == pygame.K_LEFT:
                    self.cursor_position = max(0, self.cursor_position - 1)
                elif event.key == pygame.K_RIGHT:
                    self.cursor_position = min(len(self.input_text), self.cursor_position + 1)
                elif event.key == pygame.K_HOME:
                    self.cursor_position = 0
                elif event.key == pygame.K_END:
                    self.cursor_position = len(self.input_text)
                return True
            
            # 处理滚动（只有在非输入状态下才能滚动）
            elif not self.is_input_active:
                if event.key == pygame.K_PAGEUP or event.key == pygame.K_UP:
                    self.scroll_up()
                    return True
                elif event.key == pygame.K_PAGEDOWN or event.key == pygame.K_DOWN:
                    self.scroll_down()
                    return True
                elif event.key == pygame.K_HOME:
                    self.scroll_to_top()
                    return True
                elif event.key == pygame.K_END:
                    self.force_scroll_to_bottom()
                    return True
        
        elif event.type == pygame.TEXTINPUT and self.is_input_active:
            # 处理文本输入
            if len(self.input_text) < 100:  # 限制输入长度
                self.input_text = (self.input_text[:self.cursor_position] + 
                                 event.text + 
                                 self.input_text[self.cursor_position:])
                self.cursor_position += len(event.text)
            return True
        
        elif event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:  # 左键点击
                if self.input_rect.collidepoint(event.pos):
                    self.is_input_active = True
                    return True
                elif pygame.Rect(self.panel_x, self.panel_y, self.panel_width, self.panel_height).collidepoint(event.pos):
                    return True  # 消费点击事件，防止传递到游戏
            elif event.button == 4:  # 鼠标滚轮向上
                if pygame.Rect(self.panel_x, self.panel_y, self.panel_width, self.panel_height).collidepoint(event.pos):
                    self.scroll_up()
                    return True
            elif event.button == 5:  # 鼠标滚轮向下
                if pygame.Rect(self.panel_x, self.panel_y, self.panel_width, self.panel_height).collidepoint(event.pos):
                    self.scroll_down()
                    return True
        
        return False
    
    def update(self, dt):
        """更新聊天面板状态"""
        if not self.is_active:
            return
        
        # 更新光标闪烁
        self.cursor_blink_timer += dt
        if self.cursor_blink_timer >= 0.5:
            self.cursor_visible = not self.cursor_visible
            self.cursor_blink_timer = 0
    
    def render(self, surface):
        """渲染聊天面板"""
        if not self.is_active:
            return
        
        # 创建面板背景
        panel_surface = pygame.Surface((self.panel_width, self.panel_height), pygame.SRCALPHA)
        panel_surface.fill(self.colors['background'])
        
        # 绘制边框
        pygame.draw.rect(panel_surface, self.colors['border'], 
                        (0, 0, self.panel_width, self.panel_height), 2)
        
        # 渲染消息区域
        self._render_messages(panel_surface)
        
        # 渲染输入框
        self._render_input_box(panel_surface)
        
        # 渲染状态指示器
        self._render_status_indicator(panel_surface)
        
        # 将面板绘制到主屏幕
        surface.blit(panel_surface, (self.panel_x, self.panel_y))
    
    def _render_messages(self, surface):
        """渲染消息列表"""
        if not self.messages:
            return
        
        # 创建虚拟的行列表，包含所有展开的消息行
        display_lines = []
        max_width = self.panel_width - 2 * self.input_margin
        
        for message in self.messages:
            # 渲染消息文本颜色
            if message['type'] == 'system':
                text_color = self.colors['system_message']
            elif message['type'] == 'thinking':
                text_color = (180, 180, 180)  # 灰色表示思考中
            else:
                text_color = self.colors['message_text']
            
            # 构建显示文本
            display_text = f"[{message['sender']}] {message['text']}"
            
            # 处理长消息换行
            wrapped_lines = self._wrap_text(display_text, max_width)
            
            # 添加消息行
            for line in wrapped_lines:
                display_lines.append({
                    'type': 'message',
                    'text': line,
                    'color': text_color
                })
            
            # 添加时间戳行
            display_lines.append({
                'type': 'timestamp',
                'text': f"  {message['timestamp']}",
                'color': self.colors['timestamp']
            })
        
        # 计算可见区域
        visible_lines = self.message_area_height // self.line_height
        total_lines = len(display_lines)
        
        # 确保滚动偏移不超出范围
        max_scroll_offset = max(0, total_lines - visible_lines)
        self.scroll_offset = min(self.scroll_offset, max_scroll_offset)
        
        # 计算显示的行范围
        start_line = self.scroll_offset
        end_line = min(start_line + visible_lines, total_lines)
        
        # 渲染可见的行
        current_y = self.input_margin
        
        for line_index in range(start_line, end_line):
            if line_index >= len(display_lines):
                break
                
            line_data = display_lines[line_index]
            
            if line_data['type'] == 'message':
                text_surface = self.message_font.render(line_data['text'], True, line_data['color'])
            else:  # timestamp
                text_surface = self.timestamp_font.render(line_data['text'], True, line_data['color'])
            
            surface.blit(text_surface, (self.input_margin, current_y))
            current_y += self.line_height
        
        # 渲染滚动条
        if total_lines > visible_lines:
            self._render_scrollbar(surface, total_lines, visible_lines)
    
    def _render_scrollbar(self, surface, total_lines: int, visible_lines: int):
        """渲染滚动条"""
        scrollbar_width = 6
        scrollbar_x = self.panel_width - self.input_margin - scrollbar_width
        scrollbar_y = self.input_margin
        scrollbar_height = self.message_area_height
        
        # 滚动条背景
        scrollbar_bg_rect = pygame.Rect(scrollbar_x, scrollbar_y, scrollbar_width, scrollbar_height)
        pygame.draw.rect(surface, (40, 40, 40), scrollbar_bg_rect)
        pygame.draw.rect(surface, (100, 100, 100), scrollbar_bg_rect, 1)
        
        # 计算滑块大小和位置
        if total_lines > 0:
            # 滑块高度与可见内容比例成正比
            thumb_height = max(10, int(scrollbar_height * visible_lines / total_lines))
            
            # 滑块位置与滚动偏移成正比
            max_scroll = total_lines - visible_lines
            if max_scroll > 0:
                scroll_ratio = self.scroll_offset / max_scroll
                thumb_y = scrollbar_y + int((scrollbar_height - thumb_height) * scroll_ratio)
            else:
                thumb_y = scrollbar_y
            
            # 绘制滑块
            thumb_rect = pygame.Rect(scrollbar_x + 1, thumb_y, scrollbar_width - 2, thumb_height)
            pygame.draw.rect(surface, (150, 150, 150), thumb_rect)
            pygame.draw.rect(surface, (180, 180, 180), thumb_rect, 1)
    
    def _render_input_box(self, surface):
        """渲染输入框"""
        input_x = self.input_margin
        input_y = self.panel_height - self.input_height - self.input_margin
        
        # 绘制输入框背景
        input_bg_rect = pygame.Rect(input_x, input_y, 
                                   self.panel_width - 2 * self.input_margin, 
                                   self.input_height)
        pygame.draw.rect(surface, self.colors['input_background'], input_bg_rect)
        
        # 绘制输入框边框
        border_color = (self.colors['input_active_border'] if self.is_input_active 
                       else self.colors['input_border'])
        pygame.draw.rect(surface, border_color, input_bg_rect, 2)
        
        # 渲染输入文本
        if self.input_text or self.is_input_active:
            text_surface = self.input_font.render(self.input_text, True, self.colors['input_text'])
            text_x = input_x + 5
            text_y = input_y + (self.input_height - text_surface.get_height()) // 2
            surface.blit(text_surface, (text_x, text_y))
            
            # 渲染光标
            if self.is_input_active and self.cursor_visible:
                cursor_x = text_x + self.input_font.size(self.input_text[:self.cursor_position])[0]
                cursor_y = text_y
                pygame.draw.line(surface, self.colors['cursor'], 
                               (cursor_x, cursor_y), 
                               (cursor_x, cursor_y + text_surface.get_height()), 2)
        else:
            # 渲染提示文本
            hint_text = "按 Enter 键开始输入..."
            hint_surface = self.input_font.render(hint_text, True, self.colors['timestamp'])
            text_x = input_x + 5
            text_y = input_y + (self.input_height - hint_surface.get_height()) // 2
            surface.blit(hint_surface, (text_x, text_y))
    
    def _render_status_indicator(self, surface):
        """渲染状态指示器"""
        # 在右上角显示状态
        if self.is_input_active:
            status_text = "输入中..."
            status_color = self.colors['system_message']
        elif not self.auto_scroll and self.user_scrolled:
            status_text = "查看历史"
            status_color = (255, 200, 100)  # 橙色表示在查看历史
        else:
            status_text = "聊天"
            status_color = self.colors['message_text']
        
        status_surface = self.timestamp_font.render(status_text, True, status_color)
        status_x = self.panel_width - status_surface.get_width() - 10
        status_y = 5
        surface.blit(status_surface, (status_x, status_y))
        
        # 显示滚动提示
        if len(self.messages) > 0 and not self.is_input_active:
            total_lines = self._calculate_total_display_lines()
            visible_lines = self.message_area_height // self.line_height
            
            if total_lines > visible_lines:
                # 显示滚动提示
                if self.auto_scroll:
                    hint_text = "滚轮↑查看历史"
                else:
                    hint_text = "End键回到底部"
                
                hint_surface = self.timestamp_font.render(hint_text, True, (120, 120, 120))
                hint_x = self.panel_width - hint_surface.get_width() - 10
                hint_y = 25
                surface.blit(hint_surface, (hint_x, hint_y))
    
    def _wrap_text(self, text, max_width):
        """文本换行处理"""
        words = text.split(' ')
        lines = []
        current_line = ""
        
        for word in words:
            test_line = current_line + (" " if current_line else "") + word
            text_width = self.message_font.size(test_line)[0]
            
            if text_width <= max_width:
                current_line = test_line
            else:
                if current_line:
                    lines.append(current_line)
                current_line = word
        
        if current_line:
            lines.append(current_line)
        
        return lines if lines else [text]
    
    def is_input_focused(self):
        """检查输入框是否获得焦点"""
        return self.is_active and self.is_input_active
    
    def set_message_callback(self, callback: Callable):
        """设置消息回调函数"""
        self.message_callback = callback
    
    def set_spawn_cat_callback(self, callback: Callable):
        """设置生成猫咪的回调函数"""
        self.spawn_cat_callback = callback
    
    def add_ai_response(self, message: str, sender: str):
        """添加AI回复消息"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        self.messages.append({
            'text': message,
            'sender': sender,
            'timestamp': timestamp,
            'type': 'message'
        })
        
        # 限制消息数量
        if len(self.messages) > self.max_messages:
            self.messages.pop(0)
        
        # 自动滚动到最新消息
        self.scroll_to_bottom()
        
        # 重置等待状态
        self.pending_ai_response = False
        
        print(f"[聊天面板] AI回复 {sender}: {message}")
        print(f"[聊天面板] 重置pending_ai_response状态为False")
    
    def show_typing_indicator(self, npc_name: str):
        """显示正在输入指示器"""
        if self.pending_ai_response:
            # 添加临时的"正在思考"消息
            self.add_thinking_message(npc_name)
    
    def add_thinking_message(self, npc_name: str):
        """添加临时的思考消息"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        thinking_message = {
            'text': "正在思考...",
            'sender': npc_name,
            'timestamp': timestamp,
            'type': 'thinking'  # 特殊类型，用于识别临时消息
        }
        self.messages.append(thinking_message)
        
        # 限制消息数量
        if len(self.messages) > self.max_messages:
            self.messages.pop(0)
        
        # 自动滚动到最新消息
        self.scroll_to_bottom()
        
        print(f"[聊天面板] {npc_name} 正在思考...")
    
    def replace_thinking_with_response(self, npc_name: str, response: str):
        """用实际回复替换思考消息"""
        # 找到最后一个该NPC的思考消息并替换
        for i in range(len(self.messages) - 1, -1, -1):
            msg = self.messages[i]
            if (msg['sender'] == npc_name and 
                msg['type'] == 'thinking' and 
                msg['text'] == "正在思考..."):
                
                # 替换为实际回复
                self.messages[i] = {
                    'text': response,
                    'sender': npc_name,
                    'timestamp': msg['timestamp'],
                    'type': 'message'
                }
                # 重置等待状态
                self.pending_ai_response = False
                print(f"[聊天面板] 替换思考消息为实际回复: {npc_name}: {response}")
                print(f"[聊天面板] 重置pending_ai_response状态为False")
                return
        
        # 如果没找到思考消息，直接添加回复
        self.add_ai_response(response, npc_name)
    
    def _handle_chat_command(self, command: str):
        """处理聊天命令"""
        command = command.lower().strip()
        
        if command == "/help":
            self.add_system_message("聊天命令帮助：")
            self.add_system_message("/help - 显示此帮助")
            self.add_system_message("/clear - 清除聊天记录")
            self.add_system_message("/history - 显示对话历史统计")
            self.add_system_message("/spawn - 随机生成一只猫咪")
            self.add_system_message("/test - 添加测试消息以测试滚动")
            self.add_system_message("滚动控制：")
            self.add_system_message("- 鼠标滚轮或↑↓键滚动")
            self.add_system_message("- Home键滚动到顶部，End键滚动到底部")
            
        elif command == "/clear":
            self.messages.clear()
            self.add_system_message("聊天记录已清除")
            # 同时清除AI的对话历史
            if hasattr(self, 'chat_ai_instance'):
                self.chat_ai_instance.clear_conversation_history()
            
        elif command == "/history":
            self._show_conversation_history()
            
        elif command == "/spawn":
            # 随机生成一只猫咪
            if self.spawn_cat_callback:
                try:
                    new_cat = self.spawn_cat_callback()
                    if new_cat:
                        self.add_system_message(f"🐱 成功生成新猫咪: {new_cat.cat_name}")
                        self.add_system_message(f"   性格: {new_cat.cat_personality}")
                        self.add_system_message(f"   颜色: {new_cat.skin_color}")
                        self.add_system_message(f"   表情: {new_cat.ascii_char}")
                        print(f"[聊天面板] 通过指令生成新猫咪: {new_cat.cat_name}")
                    else:
                        self.add_system_message("❌ 生成猫咪失败，请稍后重试")
                except Exception as e:
                    self.add_system_message(f"❌ 生成猫咪时发生错误: {e}")
                    print(f"[聊天面板] 生成猫咪错误: {e}")
            else:
                self.add_system_message("❌ 猫咪生成功能未启用")
        
        elif command == "/test":
            # 添加多条测试消息来测试滚动功能
            test_messages = [
                "这是第一条测试消息",
                "这是第二条测试消息，稍微长一点，用来测试文本换行功能",
                "第三条消息",
                "第四条消息：Hello World!",
                "第五条消息：你好世界！",
                "第六条消息：测试滚动功能",
                "第七条消息：这是一条非常非常长的消息，用来测试聊天面板的文本换行和滚动功能是否正常工作",
                "第八条消息",
                "第九条消息",
                "第十条消息：滚动测试完成"
            ]
            
            for i, msg in enumerate(test_messages):
                self.add_system_message(f"[测试{i+1}] {msg}")
            
        else:
            self.add_system_message(f"未知命令: {command}。输入 /help 查看可用命令。")
    
    def _show_conversation_history(self):
        """显示对话历史统计"""
        try:
            from ..ai.chat_ai import get_chat_ai
            chat_ai = get_chat_ai()
            
            if not chat_ai.conversation_history:
                self.add_system_message("暂无对话历史记录")
                return
            
            self.add_system_message("=== 对话历史统计 ===")
            for npc_id, history in chat_ai.conversation_history.items():
                summary = chat_ai.get_conversation_summary(npc_id)
                npc_name = chat_ai.npc_personalities.get(npc_id, {}).get("name", npc_id)
                
                self.add_system_message(f"{npc_name}: {summary['total_messages']}条消息")
                if summary['recent_topics']:
                    recent = ", ".join(summary['recent_topics'][:2])
                    self.add_system_message(f"  最近话题: {recent}")
                    
        except Exception as e:
            self.add_system_message(f"获取对话历史失败: {e}")
    
    def set_chat_ai_instance(self, chat_ai):
        """设置聊天AI实例引用"""
        self.chat_ai_instance = chat_ai