import pygame
from typing import List, Optional
from src.systems.npc_system import DialogueLine
from src.utils.font_manager import FontManager

class DialogueUI:
    """对话界面管理器"""
	
    def __init__(self, screen_size: tuple):
        self.screen_size = screen_size
        
        # 使用统一的阿里妈妈字体
        font_manager = FontManager.get_instance()
        self.font = font_manager.load_chinese_font(24, "dialogue_font")
        self.title_font = font_manager.load_chinese_font(32, "dialogue_title_font")
        
        # 对话框参数
        self.dialogue_box_height = 200
        self.dialogue_box_width = screen_size[0] - 40
        self.dialogue_box_x = 20
        self.dialogue_box_y = screen_size[1] - self.dialogue_box_height - 20

        # 当前对话状态
        self.current_dialogue = None
        self.current_choice_index = 0
        self.is_dialogue_active = False

        # 颜色设置
        self.bg_color = (50, 50, 50, 230)  # 半透明背景
        self.text_color = (255, 255, 255)
        self.choice_color = (200, 200, 255)
        self.selected_choice_color = (255, 255, 100)
        self.border_color = (100, 100, 100)
    
    def start_dialogue(self, dialogue_lines: List[DialogueLine]):
        """开始对话"""
        if dialogue_lines:
            self.current_dialogue = dialogue_lines[0]
            self.current_choice_index = 0
            self.is_dialogue_active = True
    
    def end_dialogue(self):
        """结束对话"""
        self.current_dialogue = None
        self.is_dialogue_active = False
        self.current_choice_index = 0
    
    def handle_input(self, key):
        """处理输入"""
        if not self.is_dialogue_active or not self.current_dialogue:
            return None
        
        # 如果有选择项
        if self.current_dialogue.choices:
            if key == pygame.K_UP:
                self.current_choice_index = max(0, self.current_choice_index - 1)
            elif key == pygame.K_DOWN:
                self.current_choice_index = min(
                    len(self.current_dialogue.choices) - 1, 
                    self.current_choice_index + 1
                )
            elif key == pygame.K_RETURN or key == pygame.K_SPACE:
                # 返回选择的索引
                choice_index = self.current_choice_index
                self.end_dialogue()
                return choice_index
        else:
            # 没有选择项，按任意键继续
            if key == pygame.K_RETURN or key == pygame.K_SPACE:
                self.end_dialogue()
                return -1  # 表示对话结束
        
        return None
    
    def render(self, screen):
        """渲染对话界面"""
        if not self.is_dialogue_active or not self.current_dialogue:
            return
        
        # 创建对话框表面
        dialogue_surface = pygame.Surface(
            (self.dialogue_box_width, self.dialogue_box_height), 
            pygame.SRCALPHA
        )
        dialogue_surface.fill(self.bg_color)
        
        # 绘制边框
        pygame.draw.rect(
            dialogue_surface, 
            self.border_color, 
            (0, 0, self.dialogue_box_width, self.dialogue_box_height), 
            2
        )
        
        # 渲染说话者名称
        speaker_text = self.title_font.render(
            self.current_dialogue.speaker, 
            True, 
            self.selected_choice_color
        )
        dialogue_surface.blit(speaker_text, (10, 10))
        
        # 渲染对话内容
        dialogue_text = self.current_dialogue.text
        text_y = 45
        
        # 处理长文本换行
        words = dialogue_text.split(' ')
        lines = []
        current_line = ""
        
        for word in words:
            test_line = current_line + (" " if current_line else "") + word
            text_width = self.font.size(test_line)[0]
            
            if text_width <= self.dialogue_box_width - 40:
                current_line = test_line
            else:
                if current_line:
                    lines.append(current_line)
                current_line = word
        
        if current_line:
            lines.append(current_line)
        
        # 渲染文本行
        for line in lines:
            text_surface = self.font.render(line, True, self.text_color)
            dialogue_surface.blit(text_surface, (20, text_y))
            text_y += 25
        
        # 渲染选择项
        if self.current_dialogue.choices:
            text_y += 10
            choice_title = self.font.render("选择:", True, self.choice_color)
            dialogue_surface.blit(choice_title, (20, text_y))
            text_y += 25
            
            for i, choice in enumerate(self.current_dialogue.choices):
                # 选中的选项高亮显示
                color = self.selected_choice_color if i == self.current_choice_index else self.choice_color
                
                # 添加选择指示符
                prefix = "► " if i == self.current_choice_index else "  "
                choice_text = f"{prefix}{i+1}. {choice}"
                
                choice_surface = self.font.render(choice_text, True, color)
                dialogue_surface.blit(choice_surface, (20, text_y))
                text_y += 25
        else:
            # 显示继续提示
            continue_text = self.font.render(
                "按 SPACE 或 ENTER 继续...", 
                True, 
                self.choice_color
            )
            dialogue_surface.blit(
                continue_text, 
                (20, self.dialogue_box_height - 30)
            )
        
        # 将对话框绘制到主屏幕
        screen.blit(dialogue_surface, (self.dialogue_box_x, self.dialogue_box_y))
    
    def is_active(self) -> bool:
        """检查对话是否活跃"""
        return self.is_dialogue_active 