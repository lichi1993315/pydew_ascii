import pygame
import math
from ..settings import *
from ..utils.font_manager import FontManager
from ..utils.emoji_colorizer import EmojiColorizer

class CatchResultPanel:
    """
    鱼获结果面板 - 显示钓到的鱼或猫的详细信息
    """
    
    def __init__(self, screen_width, screen_height):
        self.screen_width = screen_width
        self.screen_height = screen_height
        
        # 面板状态
        self.is_active = False
        self.catch_data = None
        self.show_timer = 0.0
        self.show_duration = 8.0  # 显示8秒
        
        # UI尺寸和位置
        self.panel_width = 320
        self.panel_height = 480
        self.panel_x = (screen_width - self.panel_width) // 2
        self.panel_y = (screen_height - self.panel_height) // 2
        
        # 字体
        font_manager = FontManager.get_instance()
        self.title_font = font_manager.load_chinese_font(24, "catch_title")
        self.text_font = font_manager.load_chinese_font(18, "catch_text")
        self.small_font = font_manager.load_chinese_font(14, "catch_small")
        
        # 背景样式
        self.bg_color = (250, 248, 230)  # 米色背景
        self.border_color = (180, 140, 100)  # 棕色边框
        self.shadow_color = (0, 0, 0, 100)  # 半透明阴影
        
        # 动画
        self.scale_factor = 0.0
        self.target_scale = 1.0
        self.scale_speed = 8.0
        
    def show_catch_result(self, catch_data):
        """显示钓鱼结果
        
        Args:
            catch_data: 钓到的物品数据，包含type, name, rarity等信息
        """
        self.is_active = True
        self.catch_data = catch_data
        self.show_timer = self.show_duration
        self.scale_factor = 0.0
        
        print(f"[CatchResultPanel] 显示钓鱼结果: {catch_data}")
    
    def hide_panel(self):
        """隐藏面板"""
        self.is_active = False
        self.catch_data = None
        self.show_timer = 0.0
        self.scale_factor = 0.0
    
    def update(self, dt):
        """更新面板状态"""
        if not self.is_active:
            return
        
        # 更新显示计时器
        self.show_timer -= dt
        if self.show_timer <= 0:
            self.hide_panel()
            return
        
        # 更新缩放动画
        if self.scale_factor < self.target_scale:
            self.scale_factor += self.scale_speed * dt
            if self.scale_factor > self.target_scale:
                self.scale_factor = self.target_scale
    
    def handle_input(self, event):
        """处理输入事件"""
        if not self.is_active:
            return False
        
        if event.type == pygame.KEYDOWN:
            if event.key in [pygame.K_SPACE, pygame.K_RETURN, pygame.K_ESCAPE]:
                self.hide_panel()
                return True
        
        elif event.type == pygame.MOUSEBUTTONDOWN:
            # 点击面板外区域关闭
            mouse_x, mouse_y = event.pos
            scaled_width = self.panel_width * self.scale_factor
            scaled_height = self.panel_height * self.scale_factor
            scaled_x = self.screen_width // 2 - scaled_width // 2
            scaled_y = self.screen_height // 2 - scaled_height // 2
            
            panel_rect = pygame.Rect(scaled_x, scaled_y, scaled_width, scaled_height)
            if not panel_rect.collidepoint(mouse_x, mouse_y):
                self.hide_panel()
                return True
        
        return False
    
    def render(self, surface):
        """渲染面板"""
        if not self.is_active or not self.catch_data:
            return
        
        # 计算缩放后的尺寸和位置
        scaled_width = int(self.panel_width * self.scale_factor)
        scaled_height = int(self.panel_height * self.scale_factor)
        scaled_x = self.screen_width // 2 - scaled_width // 2
        scaled_y = self.screen_height // 2 - scaled_height // 2
        
        if scaled_width <= 0 or scaled_height <= 0:
            return
        
        # 创建半透明背景遮罩
        overlay = pygame.Surface((self.screen_width, self.screen_height))
        overlay.set_alpha(150)
        overlay.fill((0, 0, 0))
        surface.blit(overlay, (0, 0))
        
        # 创建面板表面
        panel_surface = pygame.Surface((self.panel_width, self.panel_height), pygame.SRCALPHA)
        
        # 绘制阴影
        shadow_rect = pygame.Rect(5, 5, self.panel_width - 5, self.panel_height - 5)
        shadow_surface = pygame.Surface((shadow_rect.width, shadow_rect.height))
        shadow_surface.set_alpha(100)
        shadow_surface.fill((0, 0, 0))
        panel_surface.blit(shadow_surface, shadow_rect)
        
        # 绘制主背景
        main_rect = pygame.Rect(0, 0, self.panel_width - 5, self.panel_height - 5)
        pygame.draw.rect(panel_surface, self.bg_color, main_rect)
        pygame.draw.rect(panel_surface, self.border_color, main_rect, 3)
        
        # 获取数据类型
        catch_type = self.catch_data.get('type', 'fish')
        
        if catch_type == 'fish':
            self._render_fish_info(panel_surface)
        elif catch_type == 'cat':
            self._render_cat_info(panel_surface)
        elif catch_type == 'trash':
            self._render_trash_info(panel_surface)
        
        # 缩放并绘制到屏幕
        if self.scale_factor > 0:
            scaled_surface = pygame.transform.scale(panel_surface, (scaled_width, scaled_height))
            surface.blit(scaled_surface, (scaled_x, scaled_y))
    
    def _render_fish_info(self, panel_surface):
        """渲染鱼类信息"""
        y_offset = 20
        
        # 鱼类emoji图像
        emoji = self.catch_data.get('ascii_char', '🐟')
        emoji_size = 80
        
        try:
            font_manager = FontManager.get_instance()
            emoji_font = font_manager.load_emoji_font(emoji_size, "catch_emoji")
            
            # 根据稀有度着色
            rarity_colors = {
                'common': (120, 120, 120),    # 灰色
                'uncommon': (100, 200, 100),  # 绿色
                'rare': (100, 150, 255),      # 蓝色
                'epic': (200, 100, 255),      # 紫色
                'legendary': (255, 215, 0)    # 金色
            }
            
            rarity = self.catch_data.get('rarity', 'common')
            emoji_color = rarity_colors.get(rarity, (255, 255, 255))
            
            # 使用emoji着色功能
            emoji_surface = EmojiColorizer.colorize_emoji(emoji_font, emoji, emoji_color)
            emoji_rect = emoji_surface.get_rect(center=(self.panel_width // 2, y_offset + 60))
            panel_surface.blit(emoji_surface, emoji_rect)
            
        except Exception as e:
            print(f"[CatchResultPanel] Emoji渲染失败: {e}")
            # 回退到文字显示
            emoji_surface = self.title_font.render(emoji, True, (100, 100, 100))
            emoji_rect = emoji_surface.get_rect(center=(self.panel_width // 2, y_offset + 60))
            panel_surface.blit(emoji_surface, emoji_rect)
        
        y_offset += 140
        
        # 鱼的品种名称
        fish_name = self.catch_data.get('name', '未知鱼类')
        name_surface = self.title_font.render(fish_name, True, (60, 60, 60))
        name_rect = name_surface.get_rect(center=(self.panel_width // 2, y_offset))
        panel_surface.blit(name_surface, name_rect)
        y_offset += 40
        
        # 稀有度标签
        rarity_names = {
            'common': '普通',
            'uncommon': '常见', 
            'rare': '稀有',
            'epic': '史诗',
            'legendary': '传说'
        }
        rarity_text = rarity_names.get(rarity, rarity)
        
        # 稀有度背景色
        rarity_bg_colors = {
            'common': (160, 160, 160),
            'uncommon': (100, 200, 100),
            'rare': (100, 150, 255),
            'epic': (200, 100, 255),
            'legendary': (255, 215, 0)
        }
        
        rarity_bg = rarity_bg_colors.get(rarity, (160, 160, 160))
        rarity_rect = pygame.Rect(self.panel_width // 2 - 40, y_offset - 5, 80, 25)
        pygame.draw.rect(panel_surface, rarity_bg, rarity_rect)
        pygame.draw.rect(panel_surface, (255, 255, 255), rarity_rect, 2)
        
        rarity_surface = self.text_font.render(rarity_text, True, (255, 255, 255))
        rarity_text_rect = rarity_surface.get_rect(center=rarity_rect.center)
        panel_surface.blit(rarity_surface, rarity_text_rect)
        y_offset += 50
        
        # 鱼的长度
        length = self.catch_data.get('length', 0)
        length_text = f"{length} cm"
        length_surface = self.text_font.render(length_text, True, (80, 80, 80))
        length_rect = length_surface.get_rect(center=(self.panel_width // 2, y_offset))
        panel_surface.blit(length_surface, length_rect)
        y_offset += 35
        
        # 价值
        price = self.catch_data.get('price', 0)
        price_text = f"价值: {price} 金币"
        price_surface = self.text_font.render(price_text, True, (200, 150, 0))
        price_rect = price_surface.get_rect(center=(self.panel_width // 2, y_offset))
        panel_surface.blit(price_surface, price_rect)
        y_offset += 45
        
        # 详细描述
        description = self.catch_data.get('description', '描述描述描述！')
        self._render_multiline_text(panel_surface, description, y_offset, 
                                   self.panel_width - 40, self.small_font, (100, 100, 100))
        
        # 操作提示
        hint_text = "按空格键或点击继续"
        hint_surface = self.small_font.render(hint_text, True, (150, 150, 150))
        hint_rect = hint_surface.get_rect(center=(self.panel_width // 2, self.panel_height - 25))
        panel_surface.blit(hint_surface, hint_rect)
    
    def _render_cat_info(self, panel_surface):
        """渲染猫咪信息"""
        y_offset = 20
        
        # 猫咪emoji图像
        emoji = self.catch_data.get('ascii_char', '🐱')
        emoji_size = 80
        
        try:
            font_manager = FontManager.get_instance()
            emoji_font = font_manager.load_emoji_font(emoji_size, "catch_emoji")
            
            # 使用猫咪的皮肤颜色
            cat_color = self.catch_data.get('color', (255, 200, 100))
            
            # 使用emoji着色功能
            emoji_surface = EmojiColorizer.colorize_emoji(emoji_font, emoji, cat_color)
            emoji_rect = emoji_surface.get_rect(center=(self.panel_width // 2, y_offset + 60))
            panel_surface.blit(emoji_surface, emoji_rect)
            
        except Exception as e:
            print(f"[CatchResultPanel] Cat emoji渲染失败: {e}")
            # 回退到文字显示
            emoji_surface = self.title_font.render(emoji, True, cat_color)
            emoji_rect = emoji_surface.get_rect(center=(self.panel_width // 2, y_offset + 60))
            panel_surface.blit(emoji_surface, emoji_rect)
        
        y_offset += 140
        
        # 猫咪名称
        cat_name = self.catch_data.get('name', '小猫咪')
        name_surface = self.title_font.render(cat_name, True, (60, 60, 60))
        name_rect = name_surface.get_rect(center=(self.panel_width // 2, y_offset))
        panel_surface.blit(name_surface, name_rect)
        y_offset += 40
        
        # 稀有度标签
        rarity = self.catch_data.get('rarity', 'common')
        rarity_names = {
            'common': '普通',
            'uncommon': '常见',
            'rare': '稀有', 
            'epic': '史诗',
            'legendary': '传说'
        }
        rarity_text = rarity_names.get(rarity, rarity)
        
        # 稀有度背景色
        rarity_bg_colors = {
            'common': (160, 160, 160),
            'uncommon': (100, 200, 100),
            'rare': (100, 150, 255),
            'epic': (200, 100, 255),
            'legendary': (255, 215, 0)
        }
        
        rarity_bg = rarity_bg_colors.get(rarity, (160, 160, 160))
        rarity_rect = pygame.Rect(self.panel_width // 2 - 40, y_offset - 5, 80, 25)
        pygame.draw.rect(panel_surface, rarity_bg, rarity_rect)
        pygame.draw.rect(panel_surface, (255, 255, 255), rarity_rect, 2)
        
        rarity_surface = self.text_font.render(rarity_text, True, (255, 255, 255))
        rarity_text_rect = rarity_surface.get_rect(center=rarity_rect.center)
        panel_surface.blit(rarity_surface, rarity_text_rect)
        y_offset += 50
        
        # 猫咪品种（如果有的话）
        breed = self.catch_data.get('breed', '田园猫')
        breed_text = f"品种: {breed}"
        breed_surface = self.text_font.render(breed_text, True, (80, 80, 80))
        breed_rect = breed_surface.get_rect(center=(self.panel_width // 2, y_offset))
        panel_surface.blit(breed_surface, breed_rect)
        y_offset += 35
        
        # 性格标签
        personality_tag = "宠物性格"
        tag_surface = self.small_font.render(personality_tag, True, (150, 100, 200))
        tag_rect = tag_surface.get_rect(center=(self.panel_width // 2, y_offset))
        panel_surface.blit(tag_surface, tag_rect)
        y_offset += 25
        
        # 详细性格描述
        personality = self.catch_data.get('personality', '性格温和，很亲人')
        self._render_multiline_text(panel_surface, personality, y_offset,
                                   self.panel_width - 40, self.small_font, (100, 100, 100))
        
        # 操作提示
        hint_text = "按空格键或点击继续"
        hint_surface = self.small_font.render(hint_text, True, (150, 150, 150))
        hint_rect = hint_surface.get_rect(center=(self.panel_width // 2, self.panel_height - 25))
        panel_surface.blit(hint_surface, hint_rect)
    
    def _render_trash_info(self, panel_surface):
        """渲染垃圾物品信息"""
        y_offset = 20
        
        # 物品emoji图像
        emoji = self.catch_data.get('ascii_char', '🗑️')
        emoji_size = 80
        
        try:
            font_manager = FontManager.get_instance()
            emoji_font = font_manager.load_emoji_font(emoji_size, "catch_emoji")
            
            # 根据物品类别着色
            category_colors = {
                'trash': (120, 120, 120),      # 灰色 - 垃圾
                'natural': (100, 200, 100),    # 绿色 - 自然物品
                'treasure': (255, 215, 0)      # 金色 - 宝物
            }
            
            category = self.catch_data.get('category', 'trash')
            emoji_color = category_colors.get(category, (120, 120, 120))
            
            # 使用emoji着色功能
            emoji_surface = EmojiColorizer.colorize_emoji(emoji_font, emoji, emoji_color)
            emoji_rect = emoji_surface.get_rect(center=(self.panel_width // 2, y_offset + 60))
            panel_surface.blit(emoji_surface, emoji_rect)
            
        except Exception as e:
            print(f"[CatchResultPanel] Trash emoji渲染失败: {e}")
            # 回退到文字显示
            emoji_surface = self.title_font.render(emoji, True, (100, 100, 100))
            emoji_rect = emoji_surface.get_rect(center=(self.panel_width // 2, y_offset + 60))
            panel_surface.blit(emoji_surface, emoji_rect)
        
        y_offset += 140
        
        # 物品名称
        item_name = self.catch_data.get('name', '未知物品')
        name_surface = self.title_font.render(item_name, True, (60, 60, 60))
        name_rect = name_surface.get_rect(center=(self.panel_width // 2, y_offset))
        panel_surface.blit(name_surface, name_rect)
        y_offset += 40
        
        # 物品类别标签
        category_names = {
            'trash': '垃圾',
            'natural': '自然物品',
            'treasure': '宝物'
        }
        category_text = category_names.get(category, category)
        
        # 类别背景色
        category_bg_colors = {
            'trash': (120, 120, 120),
            'natural': (100, 200, 100),
            'treasure': (255, 215, 0)
        }
        
        category_bg = category_bg_colors.get(category, (120, 120, 120))
        category_rect = pygame.Rect(self.panel_width // 2 - 50, y_offset - 5, 100, 25)
        pygame.draw.rect(panel_surface, category_bg, category_rect)
        pygame.draw.rect(panel_surface, (255, 255, 255), category_rect, 2)
        
        category_surface = self.text_font.render(category_text, True, (255, 255, 255))
        category_text_rect = category_surface.get_rect(center=category_rect.center)
        panel_surface.blit(category_surface, category_text_rect)
        y_offset += 40
        
        # 稀有度标签
        rarity = self.catch_data.get('rarity', 'common')
        rarity_names = {
            'common': '普通',
            'uncommon': '常见',
            'rare': '稀有',
            'epic': '史诗',
            'legendary': '传说'
        }
        rarity_text = rarity_names.get(rarity, rarity)
        
        # 稀有度背景色
        rarity_bg_colors = {
            'common': (160, 160, 160),
            'uncommon': (100, 200, 100),
            'rare': (100, 150, 255),
            'epic': (200, 100, 255),
            'legendary': (255, 215, 0)
        }
        
        rarity_bg = rarity_bg_colors.get(rarity, (160, 160, 160))
        rarity_rect = pygame.Rect(self.panel_width // 2 - 40, y_offset - 5, 80, 25)
        pygame.draw.rect(panel_surface, rarity_bg, rarity_rect)
        pygame.draw.rect(panel_surface, (255, 255, 255), rarity_rect, 2)
        
        rarity_surface = self.text_font.render(rarity_text, True, (255, 255, 255))
        rarity_text_rect = rarity_surface.get_rect(center=rarity_rect.center)
        panel_surface.blit(rarity_surface, rarity_text_rect)
        y_offset += 50
        
        # 价值
        value = self.catch_data.get('value', 0)
        if value > 0:
            value_text = f"价值: +{value} 金币"
            value_color = (0, 180, 0)  # 绿色表示收益
        elif value < 0:
            value_text = f"处理费: {abs(value)} 金币"
            value_color = (200, 100, 0)  # 橙色表示费用
        else:
            value_text = "无商业价值"
            value_color = (150, 150, 150)  # 灰色表示无价值
        
        value_surface = self.text_font.render(value_text, True, value_color)
        value_rect = value_surface.get_rect(center=(self.panel_width // 2, y_offset))
        panel_surface.blit(value_surface, value_rect)
        y_offset += 45
        
        # 详细描述
        description = self.catch_data.get('description', '一个神秘的物品。')
        self._render_multiline_text(panel_surface, description, y_offset, 
                                   self.panel_width - 40, self.small_font, (100, 100, 100))
        
        # 操作提示
        hint_text = "按空格键或点击继续"
        hint_surface = self.small_font.render(hint_text, True, (150, 150, 150))
        hint_rect = hint_surface.get_rect(center=(self.panel_width // 2, self.panel_height - 25))
        panel_surface.blit(hint_surface, hint_rect)
    
    def _get_fish_description(self, fish_name, rarity, length):
        """生成鱼类描述"""
        descriptions = {
            'common': [
                "常见的淡水鱼类，肉质鲜美。",
                "在当地水域经常能见到的鱼种。",
                "普通但营养丰富的鱼类。"
            ],
            'uncommon': [
                "比较少见的鱼类，有一定的观赏价值。",
                "不常见的品种，深受钓鱼爱好者喜爱。",
                "颇具特色的鱼类，味道独特。"
            ],
            'rare': [
                "稀有的鱼类，具有很高的收藏价值。",
                "珍贵的品种，在市场上很受欢迎。",
                "难得一见的鱼类，运气真不错！"
            ],
            'epic': [
                "史诗级的珍稀鱼类，可遇不可求。",
                "传说中的鱼种，具有神奇的特性。",
                "极其珍贵的鱼类，价值连城。"
            ],
            'legendary': [
                "传说级的神话鱼类，千载难逢！",
                "古老传说中的神秘鱼种。",
                "传奇中的王者之鱼，无价之宝！"
            ]
        }
        
        base_desc = descriptions.get(rarity, descriptions['common'])[0]
        
        # 根据长度添加额外描述
        if length > 80:
            base_desc += " 体型巨大，非常罕见！"
        elif length > 50:
            base_desc += " 体型较大，品质优良。"
        elif length < 15:
            base_desc += " 虽然体型娇小，但同样珍贵。"
        
        return base_desc
    
    def _render_multiline_text(self, surface, text, y_start, max_width, font, color):
        """渲染多行文本"""
        words = text.split()
        lines = []
        current_line = ""
        
        for word in words:
            test_line = current_line + word + " "
            test_surface = font.render(test_line, True, color)
            
            if test_surface.get_width() <= max_width:
                current_line = test_line
            else:
                if current_line:
                    lines.append(current_line.strip())
                current_line = word + " "
        
        if current_line:
            lines.append(current_line.strip())
        
        # 渲染每一行
        line_height = font.get_height() + 2
        for i, line in enumerate(lines):
            line_surface = font.render(line, True, color)
            line_rect = line_surface.get_rect(center=(self.panel_width // 2, y_start + i * line_height))
            surface.blit(line_surface, line_rect)