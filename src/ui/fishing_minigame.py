import pygame
import random
import math
from ..settings import *
from ..utils.font_manager import FontManager
from ..utils.emoji_colorizer import EmojiColorizer

class FishingMinigame:
    """
    钓鱼小游戏
    
    支持根据稀有度显示不同的emoji：
    - 鱼类：🐟(普通) 🐠(稀有) 🐡(史诗) 🦈(传说)
    - 猫类：🐱(普通) 😸(稀有) 😻(史诗) 🦁(传说)
    
    使用方法：
    catch_target = {'type': 'fish', 'rarity': 'rare'}  # 或 'cat'
    minigame.start_game(catch_target)
    """
    
    def __init__(self, screen_width, screen_height):
        self.screen_width = screen_width
        self.screen_height = screen_height
        
        # 游戏状态
        self.is_active = False
        self.game_result = None  # 'success', 'failure', None
        
        # 钓到的目标信息
        self.catch_target = None  # 钓到的目标信息 {'type': 'fish'/'cat', 'rarity': 'common'/'rare'/'epic'/'legendary'}
        self.target_emoji = "🐟"  # 当前显示的emoji
        
        # UI位置和尺寸
        self.ui_width = 120
        self.ui_height = 400
        self.ui_x = (screen_width - self.ui_width) // 2
        self.ui_y = (screen_height - self.ui_height) // 2
        
        # 进度条 (左侧较宽的条)
        self.progress_bar_width = 60
        self.progress_bar_height = self.ui_height - 40
        self.progress_bar_x = self.ui_x + 10
        self.progress_bar_y = self.ui_y + 20
        
        # 体力条 (右侧较细的条)
        self.stamina_bar_width = 20
        self.stamina_bar_height = self.ui_height - 40
        self.stamina_bar_x = self.ui_x + self.ui_width - 30
        self.stamina_bar_y = self.ui_y + 20
        
        # 游戏参数
        self.fish_position = 0.0  # 鱼的位置 (0.0 = 底部, 1.0 = 顶部)
        self.stamina = 1.0  # 体力 (0.0 - 1.0)
        self.is_key_pressed = False  # 空格键是否被按住
        
        # 鱼的状态
        self.fish_state = "exhausted"  # "struggling" 或 "exhausted"
        self.state_timer = 0.0
        self.state_duration = 0.0
        
        # 游戏设置
        self.reel_speed = 0.3  # 收线速度 (每秒)
        self.sink_speed = 0.15  # 鱼下沉速度 (每秒)
        self.stamina_drain_struggling = 0.8  # 挣扎时体力消耗速度
        self.stamina_drain_exhausted = 0.2  # 力竭时体力消耗速度
        self.stamina_recovery = 0.3  # 体力恢复速度
        
        # 字体
        font_manager = FontManager.get_instance()
        self.font = font_manager.load_chinese_font(16, "fishing_minigame")
        
        # 初始化鱼的状态
        self._switch_fish_state()
        
    def _get_emoji_by_target(self, target):
        """根据目标信息获取对应的emoji"""
        if not target:
            return "🐟"
            
        target_type = target.get('type', 'fish')
        rarity = target.get('rarity', 'common')
        
        if target_type == 'fish':
            # 鱼类emoji按稀有度
            fish_emojis = {
                'common': "🐟",      # 普通鱼
                'uncommon': "🐠",      # 热带鱼
                'rare': "🐬",        # 海豚
                'epic': "🦈",        # 鲨鱼
                'legendary': "🐋"     # 鲸鱼
            }
            return fish_emojis.get(rarity, "🐟")
        
        elif target_type == 'cat':
            # 猫类emoji按稀有度
            cat_emojis = {
                'common': "🐱",      # 普通猫脸
                'uncommon': "😸",        # 开心猫
                'rare': "😸",        # 开心猫
                'epic': "😻",        # 心眼猫
                'legendary': "🦁"     # 狮子
            }
            return cat_emojis.get(rarity, "🐱")
        
        return "🐟"  # 默认返回普通鱼
        
    def start_game(self, catch_target=None):
        """开始钓鱼小游戏
        
        Args:
            catch_target: 钓到的目标信息，格式为 {'type': 'fish'/'cat', 'rarity': 'common'/'rare'/'epic'/'legendary'}
        """
        self.is_active = True
        self.game_result = None
        self.fish_position = 0.0
        self.stamina = 1.0
        self.is_key_pressed = False
        self.fish_state = "exhausted"
        self.state_timer = 0.0
        self.catch_target = catch_target or {'type': 'fish', 'rarity': 'common'}
        self.target_emoji = self._get_emoji_by_target(self.catch_target)
        self._switch_fish_state()
        print(f"[钓鱼小游戏] 游戏开始！钓到的目标: {self.catch_target}, emoji: {self.target_emoji}")
        
    def end_game(self, result):
        """结束钓鱼小游戏"""
        self.is_active = False
        self.game_result = result
        print(f"[钓鱼小游戏] 游戏结束: {result}")
        
    def handle_input(self, event):
        """处理输入事件"""
        if not self.is_active:
            return False
            
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE:  # 空格键
                self.is_key_pressed = True
                return True
                
        elif event.type == pygame.KEYUP:
            if event.key == pygame.K_SPACE:  # 空格键
                self.is_key_pressed = False
                return True
                
        return False
        
    def _switch_fish_state(self):
        """切换鱼的状态"""
        if self.fish_state == "struggling":
            self.fish_state = "exhausted"
            self.state_duration = random.uniform(1.5, 3.0)  # 力竭状态持续1.5-3秒
        else:
            self.fish_state = "struggling"
            self.state_duration = random.uniform(0.8, 2.0)  # 挣扎状态持续0.8-2秒
            
        self.state_timer = 0.0
        print(f"[钓鱼小游戏] 鱼的状态切换为: {self.fish_state}")
        
    def update(self, dt):
        """更新游戏逻辑"""
        if not self.is_active:
            return
            
        # 更新鱼的状态计时器
        self.state_timer += dt
        if self.state_timer >= self.state_duration:
            self._switch_fish_state()
            
        # 更新鱼的位置
        if self.is_key_pressed:
            # 玩家按住空格键，鱼向上移动
            self.fish_position += self.reel_speed * dt
        else:
            # 玩家松开空格键，鱼向下沉
            self.fish_position -= self.sink_speed * dt
            
        # 限制鱼的位置范围
        self.fish_position = max(0.0, min(1.0, self.fish_position))
        
        # 更新体力
        if self.is_key_pressed:
            if self.fish_state == "struggling":
                # 挣扎状态下按空格键，体力快速下降
                self.stamina -= self.stamina_drain_struggling * dt
            else:
                # 力竭状态下按空格键，体力缓慢下降
                self.stamina -= self.stamina_drain_exhausted * dt
        else:
            # 松开空格键，体力恢复
            self.stamina += self.stamina_recovery * dt
            
        # 限制体力范围
        self.stamina = max(0.0, min(1.0, self.stamina))
        
        # 检查游戏结束条件
        if self.stamina <= 0.0:
            # 体力耗尽，钓鱼失败
            self.end_game("failure")
        elif self.fish_position >= 1.0:
            # 鱼到达顶部，钓鱼成功
            self.end_game("success")
            
    def render(self, surface):
        """渲染钓鱼小游戏UI"""
        if not self.is_active:
            return
            
        # 绘制半透明背景
        overlay = pygame.Surface((self.screen_width, self.screen_height))
        overlay.set_alpha(128)
        overlay.fill((0, 0, 0))
        surface.blit(overlay, (0, 0))
        
        # 绘制主UI背景
        ui_rect = pygame.Rect(self.ui_x, self.ui_y, self.ui_width, self.ui_height)
        pygame.draw.rect(surface, (40, 40, 40), ui_rect)
        pygame.draw.rect(surface, (100, 100, 100), ui_rect, 3)
        
        # 绘制进度条
        self._draw_progress_bar(surface)
        
        # 绘制体力条
        self._draw_stamina_bar(surface)
        
        # 绘制鱼
        self._draw_fish(surface)
        
        # 绘制状态提示
        self._draw_status_text(surface)
        
    def _draw_progress_bar(self, surface):
        """绘制进度条"""
        # 进度条背景
        progress_rect = pygame.Rect(
            self.progress_bar_x, 
            self.progress_bar_y, 
            self.progress_bar_width, 
            self.progress_bar_height
        )
        pygame.draw.rect(surface, (20, 20, 20), progress_rect)
        pygame.draw.rect(surface, (80, 80, 80), progress_rect, 2)
        
        # 绘制刻度线
        for i in range(1, 10):
            y = self.progress_bar_y + (self.progress_bar_height * i / 10)
            start_x = self.progress_bar_x + 5
            end_x = self.progress_bar_x + self.progress_bar_width - 5
            pygame.draw.line(surface, (60, 60, 60), (start_x, y), (end_x, y), 1)
            
        # 绘制成功区域 (顶部20%)
        success_height = self.progress_bar_height * 0.2
        success_rect = pygame.Rect(
            self.progress_bar_x + 2,
            self.progress_bar_y + 2,
            self.progress_bar_width - 4,
            success_height
        )
        pygame.draw.rect(surface, (0, 100, 0, 50), success_rect)
        
    def _draw_stamina_bar(self, surface):
        """绘制体力条"""
        # 体力条背景
        stamina_rect = pygame.Rect(
            self.stamina_bar_x, 
            self.stamina_bar_y, 
            self.stamina_bar_width, 
            self.stamina_bar_height
        )
        pygame.draw.rect(surface, (20, 20, 20), stamina_rect)
        pygame.draw.rect(surface, (80, 80, 80), stamina_rect, 2)
        
        # 体力填充
        if self.stamina > 0:
            stamina_fill_height = self.stamina_bar_height * self.stamina
            stamina_fill_rect = pygame.Rect(
                self.stamina_bar_x + 2,
                self.stamina_bar_y + self.stamina_bar_height - stamina_fill_height + 2,
                self.stamina_bar_width - 4,
                stamina_fill_height - 4
            )
            
            # 根据体力值改变颜色
            if self.stamina > 0.6:
                color = (0, 200, 0)  # 绿色
            elif self.stamina > 0.3:
                color = (200, 200, 0)  # 黄色
            else:
                color = (200, 0, 0)  # 红色
                
            pygame.draw.rect(surface, color, stamina_fill_rect)
            
    def _draw_fish(self, surface):
        """绘制目标emoji（鱼或猫）"""
        # 计算目标的Y位置 (从底部到顶部)
        fish_y = self.progress_bar_y + self.progress_bar_height * (1.0 - self.fish_position)
        fish_x = self.progress_bar_x + self.progress_bar_width // 2
        
        # 使用预设的目标emoji
        display_emoji = self.target_emoji
        
        # 根据状态选择颜色（用于回退渲染）
        if self.fish_state == "struggling":
            fallback_color = (255, 100, 100)  # 红色
        else:
            fallback_color = (100, 150, 255)  # 蓝色
            
        # 获取字体管理器
        font_manager = FontManager.get_instance()
        
        # 尝试使用emoji字体和着色，如果失败则使用普通字体
        try:
            emoji_font = font_manager.load_emoji_font(24, "fishing_target_emoji")
            
            # 根据稀有度获取颜色
            rarity_colors = {
                'common': (200, 200, 200),    # 灰色
                'rare': (100, 200, 255),      # 蓝色
                'epic': (200, 100, 255),      # 紫色
                'legendary': (255, 215, 0)    # 金色
            }
            
            if self.catch_target:
                rarity = self.catch_target.get('rarity', 'common')
                target_color = rarity_colors.get(rarity, (255, 255, 255))
                
                # 使用emoji着色功能
                fish_surface = EmojiColorizer.colorize_emoji(
                    emoji_font,
                    display_emoji,
                    target_color
                )
            else:
                # 没有目标信息，使用默认渲染
                fish_surface = emoji_font.render(display_emoji, True, (255, 255, 255))
            
        except Exception as e:
            # 如果emoji字体加载失败，使用普通字体渲染
            print(f"[FishingMinigame] Emoji着色失败: {e}")
            fish_surface = self.font.render(display_emoji, True, fallback_color)
        
        # 计算emoji的位置（居中）
        fish_rect = fish_surface.get_rect()
        fish_rect.center = (fish_x, int(fish_y))
        
        # 如果是挣扎状态，添加抖动效果
        if self.fish_state == "struggling":
            import math
            shake_offset = int(math.sin(self.state_timer * 15) * 2)  # 抖动幅度为2像素
            fish_rect.x += shake_offset
            fish_rect.y += shake_offset
        
        # 绘制目标emoji
        surface.blit(fish_surface, fish_rect)
        
    def _draw_status_text(self, surface):
        """绘制状态文字"""
        # 获取目标类型和稀有度信息
        target_type = self.catch_target.get('type', 'fish') if self.catch_target else 'fish'
        rarity = self.catch_target.get('rarity', 'common') if self.catch_target else 'common'
        
        # 根据目标类型显示不同的状态文本
        if target_type == 'cat':
            if self.fish_state == "struggling":
                state_text = "小猫在挣扎!"
                state_color = (255, 100, 100)
            else:
                state_text = "小猫累了"
                state_color = (100, 150, 255)
        else:  # fish
            if self.fish_state == "struggling":
                state_text = "鱼在挣扎!"
                state_color = (255, 100, 100)
            else:
                state_text = "鱼力竭了"
                state_color = (100, 150, 255)
        
        # 添加稀有度标识
        rarity_colors = {
            'common': (200, 200, 200),    # 灰色
            'rare': (100, 200, 255),      # 蓝色
            'epic': (200, 100, 255),      # 紫色
            'legendary': (255, 200, 0)    # 金色
        }
        
        rarity_names = {
            'common': "普通",
            'rare': "稀有",
            'epic': "史诗",
            'legendary': "传说"
        }
        
        # 渲染状态文字
        text_surface = self.font.render(state_text, True, state_color)
        text_rect = text_surface.get_rect()
        text_rect.centerx = self.ui_x + self.ui_width // 2
        text_rect.y = self.ui_y - 50
        surface.blit(text_surface, text_rect)
        
        # 渲染稀有度文字
        rarity_text = f"{rarity_names.get(rarity, rarity)} {target_type}"
        rarity_surface = self.font.render(rarity_text, True, rarity_colors.get(rarity, (200, 200, 200)))
        rarity_rect = rarity_surface.get_rect()
        rarity_rect.centerx = self.ui_x + self.ui_width // 2
        rarity_rect.y = self.ui_y - 30
        surface.blit(rarity_surface, rarity_rect)
        
        # 操作提示
        if self.fish_state == "struggling":
            hint_text = "不要按空格键!"
            hint_color = (255, 200, 100)
        else:
            if target_type == 'cat':
                hint_text = "按住空格键拉小猫"
            else:
                hint_text = "按住空格键收线"
            hint_color = (100, 255, 100)
            
        hint_surface = self.font.render(hint_text, True, hint_color)
        hint_rect = hint_surface.get_rect()
        hint_rect.centerx = self.ui_x + self.ui_width // 2
        hint_rect.y = self.ui_y + self.ui_height + 10
        surface.blit(hint_surface, hint_rect)
        
    def get_result(self):
        """获取游戏结果"""
        return self.game_result
        
    def reset_result(self):
        """重置游戏结果"""
        self.game_result = None
        
    def get_catch_target(self):
        """获取钓到的目标信息"""
        return self.catch_target