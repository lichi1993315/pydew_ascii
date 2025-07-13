import pygame

class EmojiColorizer:
    """
    Emoji着色工具类
    使用pygame混合模式对emoji进行着色
    """
    
    @staticmethod
    def colorize_emoji(font, emoji_text, target_color, blend_mode=pygame.BLEND_RGBA_MULT):
        """
        对emoji进行着色
        
        Args:
            font: pygame字体对象
            emoji_text: emoji字符串
            target_color: 目标颜色 (R, G, B) 或 (R, G, B, A)
            blend_mode: 混合模式，默认为乘法混合
            
        Returns:
            着色后的Surface对象
        """
        # 1. 渲染原始emoji（使用白色，保持原始亮度）
        original_surface = font.render(emoji_text, True, (255, 255, 255))
        
        # 2. 创建颜色遮罩表面
        color_surface = pygame.Surface(original_surface.get_size(), pygame.SRCALPHA)
        color_surface.fill(target_color)
        
        # 3. 创建结果表面
        result_surface = original_surface.copy()
        
        # 4. 应用颜色混合
        result_surface.blit(color_surface, (0, 0), special_flags=blend_mode)
        
        return result_surface
    
    @staticmethod
    def colorize_emoji_advanced(font, emoji_text, target_color, intensity=1.0):
        """
        高级emoji着色，支持强度控制
        
        Args:
            font: pygame字体对象
            emoji_text: emoji字符串
            target_color: 目标颜色 (R, G, B)
            intensity: 着色强度 (0.0-1.0)，0.0=原色，1.0=完全着色
            
        Returns:
            着色后的Surface对象
        """
        # 1. 渲染原始emoji
        original_surface = font.render(emoji_text, True, (255, 255, 255))
        
        # 2. 创建颜色遮罩，根据强度调整alpha
        color_surface = pygame.Surface(original_surface.get_size(), pygame.SRCALPHA)
        alpha = int(255 * intensity)
        color_with_alpha = (*target_color, alpha)
        color_surface.fill(color_with_alpha)
        
        # 3. 创建结果表面
        result_surface = original_surface.copy()
        
        # 4. 使用BLEND_ALPHA_SDL2混合模式，更自然的颜色混合
        result_surface.blit(color_surface, (0, 0), special_flags=pygame.BLEND_ALPHA_SDL2)
        
        return result_surface
    
    @staticmethod
    def create_colored_emoji_variants(font, emoji_text, color_palette):
        """
        创建emoji的多种颜色变体
        
        Args:
            font: pygame字体对象
            emoji_text: emoji字符串
            color_palette: 颜色调色板 [(R,G,B), (R,G,B), ...]
            
        Returns:
            颜色变体Surface列表
        """
        variants = []
        for color in color_palette:
            colored_emoji = EmojiColorizer.colorize_emoji(font, emoji_text, color)
            variants.append(colored_emoji)
        
        return variants
    
    @staticmethod
    def get_mood_colors():
        """
        获取预定义的情绪颜色
        """
        return {
            'happy': (255, 255, 100),      # 黄色
            'sad': (100, 100, 255),        # 蓝色
            'angry': (255, 100, 100),      # 红色
            'calm': (100, 255, 100),       # 绿色
            'excited': (255, 150, 100),    # 橙色
            'mysterious': (150, 100, 255), # 紫色
            'golden': (255, 215, 0),       # 金色
            'silver': (192, 192, 192),     # 银色
            'fire': (255, 69, 0),          # 火红色
            'ice': (173, 216, 230),        # 冰蓝色
        }

# 使用示例：
def example_usage():
    """
    emoji着色使用示例
    """
    pygame.init()
    screen = pygame.display.set_mode((800, 600))
    
    # 加载字体
    try:
        font = pygame.font.Font("NotoColorEmoji.ttf", 48)
    except:
        font = pygame.font.Font(None, 48)
    
    # 获取情绪颜色
    mood_colors = EmojiColorizer.get_mood_colors()
    
    # 创建不同颜色的猫咪emoji
    cat_emoji = "🐱"
    
    # 方法1：基础着色
    red_cat = EmojiColorizer.colorize_emoji(font, cat_emoji, mood_colors['angry'])
    blue_cat = EmojiColorizer.colorize_emoji(font, cat_emoji, mood_colors['sad'])
    
    # 方法2：高级着色（带强度控制）
    golden_cat = EmojiColorizer.colorize_emoji_advanced(font, cat_emoji, mood_colors['golden'], 0.7)
    
    # 方法3：批量创建颜色变体
    color_palette = [mood_colors['happy'], mood_colors['calm'], mood_colors['fire']]
    cat_variants = EmojiColorizer.create_colored_emoji_variants(font, cat_emoji, color_palette)
    
    # 渲染到屏幕
    screen.fill((50, 50, 50))
    screen.blit(red_cat, (100, 100))
    screen.blit(blue_cat, (200, 100))
    screen.blit(golden_cat, (300, 100))
    
    # 显示变体
    for i, variant in enumerate(cat_variants):
        screen.blit(variant, (100 + i * 100, 200))
    
    pygame.display.flip()

if __name__ == "__main__":
    example_usage() 