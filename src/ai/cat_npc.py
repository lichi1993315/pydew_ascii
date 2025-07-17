import pygame
import random
import math
from ..settings import *
from ..rendering.ascii_sprites import ASCIINPC
from ..utils.emoji_colorizer import EmojiColorizer  # 导入emoji着色工具
from ..systems.cat_event_system import CatEventSystem  # 导入事件系统
from ..data.cat_data import get_cat_data_manager, CatInfo  # 导入统一猫咪数据
from ..systems.bait_workbench import get_bait_workbench

class CatNPC(ASCIINPC):
    """猫咪NPC类 - 继承自ASCIINPC并添加移动功能"""
    
    def __init__(self, pos, npc_id, npc_manager, groups, cat_name, cat_personality, collision_sprites=None, cat_info=None):
        super().__init__(pos, npc_id, npc_manager, groups)
        
        # 猫咪特有属性
        self.cat_name = cat_name
        self.cat_personality = cat_personality
        
        # 碰撞检测系统（参考玩家系统）
        self.collision_sprites = collision_sprites
        self.pos = pygame.math.Vector2(self.rect.center)  # 精确位置
        
        # 创建hitbox用于碰撞检测
        hitbox_size = TILE_SIZE // 2  # 猫咪比玩家小一点
        self.hitbox = pygame.Rect(0, 0, hitbox_size, hitbox_size)
        self.hitbox.center = self.rect.center
        
        # 移动相关属性
        self.move_speed = random.uniform(20, 40)  # 随机移动速度
        self.direction = pygame.math.Vector2(0, 0)
        self.target_pos = None
        self.movement_timer = 0
        self.movement_interval = random.uniform(2, 5)  # 2-5秒更换一次移动目标
        self.idle_time = 0
        self.max_idle_time = random.uniform(3, 8)  # 3-8秒闲置时间
        
        # 移动边界（游戏世界边界）- 更保守的边界
        self.world_bounds = pygame.Rect(64, 64, 1472, 1472)  # 留出边界缓冲
        
        # 移动状态
        self.movement_state = "idle"  # idle, moving, sitting, moving_to_workbench
        self.state_timer = 0
        
        # 工作台相关属性
        self.caught_insect = None  # 抓到的昆虫信息
        self.workbench_target = None  # 目标工作台
        
        # 猫猫社交相关属性
        self.social_interaction_distance = 80  # 社交互动距离
        self.nearby_cats = []  # 附近的猫咪列表
        self.current_conversation_partner = None  # 当前对话伙伴
        self.conversation_cooldown = 0  # 对话冷却时间
        self.conversation_cooldown_max = 30  # 30秒冷却
        self.last_conversation_time = 0
        
        # 猫猫对话历史（用于存储猫猫之间的对话）
        self.cat_conversations = {}  # {other_cat_id: [conversation_entries...]}
        
        # 使用统一猫咪数据的ASCII字符和颜色，如果没有则使用默认值
        if cat_info:
            self.ascii_char = cat_info.ascii_char
            self.skin_color = cat_info.color
            self.char_color = cat_info.color
        else:
            # 备用随机设定
            self.ascii_char = random.choice(['🐈', '🐱', '😺', '😸', '😻', '😽', '🐈‍⬛', '🐅', '🦝', '🦊', '🐩', '🐕‍🦺', '🦮','🐉', '🦓','🐖','🐐','🐇','🦘','🦛','🐫','🐂','🦌'])
            self.skin_colors = [
                (255, 200, 100),  # 橙猫
                (200, 200, 200),  # 灰猫
                (255, 255, 255),  # 白猫
                (100, 100, 100),  # 黑猫
                (150, 100, 50),   # 棕猫
                (255, 150, 150),  # 粉猫
                (255, 220, 177),  # 浅橙色
                (139, 69, 19),    # 巧克力色
                (255, 192, 203),  # 粉色
                (230, 230, 250),  # 薰衣草色
                (255, 215, 0),    # 金色
                (128, 128, 128),  # 深灰
            ]
            self.skin_color = random.choice(self.skin_colors)  # 随机选择皮肤颜色
            self.char_color = self.skin_color
        
        print(f"[CatNPC] {cat_name} 的皮肤颜色: {self.skin_color}")  # 调试输出

        self.head_emoji_font = None  # 缓存头顶emoji字体
        self.sprite_emoji_font = None
        
        # 着色后的emoji表面缓存
        self.colored_emoji_cache = {}  # 缓存不同状态的着色emoji表面
        self._initialize_colored_emojis()  # 初始化着色emoji
        
        # 头顶emoji字体缓存
        
        
        # 猫咪心情系统
        self.mood = "neutral"  # neutral, happy, sad, excited, sleepy, playful
        self.mood_timer = 0.0
        self.mood_duration = random.uniform(10.0, 30.0)  # 心情持续时间
        
        # 猫咪照护系统
        self.mood_value = 50              # 心情值 (0-100)
        self.energy_value = 100           # 精力值 (0-100)
        self.sleep_state = "awake"        # 睡眠状态: awake, sleeping
        self.owned_cat_bed = None         # 拥有的猫窝
        self.last_interaction_time = 0    # 最后与玩家互动时间
        self.mood_decay_timer = 0.0       # 心情衰减计时器
        self.energy_decay_timer = 0.0     # 精力衰减计时器
        self.sleep_location = None        # 睡眠位置
        self.leaving_warning_timer = 0.0  # 离开警告计时器
        self.leaving_warning_shown = False # 是否已显示离开警告
        
        # 头顶emoji系统
        self.head_emoji_system = {
            'current_emoji': None,
            'emoji_timer': 0,
            'emoji_duration': 0,
            'emoji_display_chance': 0.01,  # 1%概率每帧显示emoji
            'emoji_min_duration': 2.0,  # 最小显示2秒
            'emoji_max_duration': 5.0,  # 最大显示5秒
        }
        
        # 行为对应的emoji表
        self.behavior_emojis = {
            'idle': ['😴', '💤', '🤔', '😌', '🥱'],
            'moving': ['🚶', '🏃', '👀', '🎯', '🔍'],
            'sitting': ['🧘', '😊', '☀️', '🌸', '💭'],
            'chatting': ['💬', '🗣️', '💕', '😸', '👋'],
            'exploring': ['🔍', '👀', '🗺️', '🎯', '❓'],
            'happy': ['😸', '😻', '😺', '💕', '✨'],
            'sleepy': ['😴', '💤', '🥱', '😪', '💙'],
        }
        
        # 设置初始移动目标
        self._set_random_target()
    
    def _initialize_colored_emojis(self):
        """初始化着色emoji表面缓存"""
        # 获取字体管理器
        from ..utils.font_manager import FontManager
        font_manager = FontManager.get_instance()
        
        # 定义所有可能的猫咪状态emoji
        emoji_states = {
            'sitting': '🐱',
            'moving': '🐈',
            'idle': self.ascii_char,
            'default': self.ascii_char
        }
        
        # 为每个状态的emoji着色并缓存
        for state, emoji in emoji_states.items():
            try:
                # 创建emoji字体
                self.sprite_emoji_font = font_manager.load_emoji_font(TILE_SIZE // 4, f"cat_body_{self.cat_name}_{state}")
                
                # 使用EmojiColorizer为猫咪着色
                colored_surface = EmojiColorizer.colorize_emoji(
                    self.sprite_emoji_font, 
                    emoji, 
                    self.skin_color
                )
                
                # 缓存着色后的表面
                self.colored_emoji_cache[state] = colored_surface
                
            except Exception as e:
                print(f"[CatNPC] {self.cat_name} 预着色失败 ({state}): {e}")
                # 如果着色失败，存储None，稍后使用回退方法
                self.colored_emoji_cache[state] = None
        
        # 预加载头顶emoji字体
        try:
            emoji_size = TILE_SIZE // 6
            self.head_emoji_font = font_manager.load_emoji_font(emoji_size, f"cat_emoji_{self.cat_name}")
            print(f"[CatNPC] {self.cat_name} 头顶emoji字体预加载成功")
        except Exception as e:
            print(f"[CatNPC] {self.cat_name} 头顶emoji字体预加载失败: {e}")
            self.head_emoji_font = None
        
        # 输出初始化总结
        cached_states = [state for state, surface in self.colored_emoji_cache.items() if surface is not None]
        print(f"[CatNPC] {self.cat_name} 初始化完成: {len(cached_states)}/{len(self.colored_emoji_cache)} 状态已缓存")
    
    def _update_workbench_movement(self, dt):
        """更新前往工作台的移动逻辑"""
        if self.target_pos is None or self.workbench_target is None:
            return
        
        current_pos = pygame.math.Vector2(self.rect.center)
        distance_to_target = current_pos.distance_to(self.target_pos)
        
        # 如果接近工作台
        if distance_to_target < 40:
            self._deliver_insect_to_workbench()
            return
        
        # 计算朝向工作台的方向
        direction = (self.target_pos - current_pos)
        if direction.magnitude() > 0:
            self.direction = direction.normalize()
        
        # 移动（使用与普通移动相同的逻辑）
        self.pos.x += self.direction.x * self.move_speed * dt
        self.hitbox.centerx = round(self.pos.x)
        self.rect.centerx = self.hitbox.centerx
        self.collision('horizontal')
        
        self.pos.y += self.direction.y * self.move_speed * dt
        self.hitbox.centery = round(self.pos.y)
        self.rect.centery = self.hitbox.centery
        self.collision('vertical')
    
    def _update_bed_movement(self, dt):
        """更新前往猫窝的移动逻辑"""
        if self.target_pos is None:
            return
        
        current_pos = pygame.math.Vector2(self.rect.center)
        distance_to_target = current_pos.distance_to(self.target_pos)
        
        # 如果接近猫窝
        if distance_to_target < 40:
            self._arrive_at_bed()
            return
        
        # 计算朝向猫窝的方向
        direction = (self.target_pos - current_pos)
        if direction.magnitude() > 0:
            self.direction = direction.normalize()
        
        # 移动（使用与普通移动相同的逻辑）
        self.pos.x += self.direction.x * self.move_speed * dt
        self.hitbox.centerx = round(self.pos.x)
        self.rect.centerx = self.hitbox.centerx
        self.collision('horizontal')
        
        self.pos.y += self.direction.y * self.move_speed * dt
        self.hitbox.centery = round(self.pos.y)
        self.rect.centery = self.hitbox.centery
        self.collision('vertical')
    
    def _arrive_at_bed(self):
        """到达猫窝"""
        self.movement_state = "sleeping"
        self.target_pos = None
        self.direction = pygame.math.Vector2(0, 0)
        print(f"🐱 {self.cat_name} 到达猫窝，开始睡觉")
    
    def _deliver_insect_to_workbench(self):
        """将虫子送到工作台"""
        if self.caught_insect and self.workbench_target:
            # 将虫子添加到工作台存储
            self.workbench_target.add_insect(self.caught_insect['id'], 1)
            
            print(f"🐱 {self.cat_name} 将 {self.caught_insect['name']} 放到了工作台")
            
            # 显示满足的表情
            self.force_head_emoji('😊', 2.0)
            
            # 清除虫子和工作台目标
            self.caught_insect = None
            self.workbench_target = None
            self.target_pos = None
            
            # 返回正常状态
            self.movement_state = "idle"
            self.state_timer = random.uniform(2, 5)  # 休息一会儿
    
    def _set_random_target(self):
        """设置随机移动目标"""
        # 在附近选择一个随机位置
        current_x, current_y = self.rect.center
        
        # 尝试多次找到有效的移动目标
        max_attempts = 10
        for attempt in range(max_attempts):
            # 移动范围限制在当前位置的200像素内
            max_distance = 200
            angle = random.uniform(0, 2 * math.pi)
            distance = random.uniform(50, max_distance)
            
            target_x = current_x + math.cos(angle) * distance
            target_y = current_y + math.sin(angle) * distance
            
            # 确保目标在世界边界内
            target_x = max(self.world_bounds.left + 32, min(self.world_bounds.right - 32, target_x))
            target_y = max(self.world_bounds.top + 32, min(self.world_bounds.bottom - 32, target_y))
            
            # 检查目标位置是否有障碍物
            if self._is_position_valid(target_x, target_y):
                self.target_pos = pygame.math.Vector2(target_x, target_y)
                
                # 计算方向向量
                target_vector = self.target_pos - pygame.math.Vector2(self.rect.center)
                if target_vector.length() > 0:
                    self.direction = target_vector.normalize()
                else:
                    self.direction = pygame.math.Vector2(0, 0)
                
                print(f"[CatNPC] {self.cat_name} 设置新目标: {self.target_pos}")
                return
        
        # 如果所有尝试都失败，选择一个简单的方向
        self._set_fallback_target()
    
    def _is_position_valid(self, x, y):
        """检查位置是否有效（无障碍物）"""
        if not self.collision_sprites:
            return True
            
        # 创建临时hitbox来检查碰撞
        temp_hitbox = pygame.Rect(0, 0, self.hitbox.width, self.hitbox.height)
        temp_hitbox.center = (x, y)
        
        for sprite in self.collision_sprites.sprites():
            if hasattr(sprite, 'hitbox'):
                if sprite.hitbox.colliderect(temp_hitbox):
                    return False
            elif sprite.rect.colliderect(temp_hitbox):
                return False
        
        return True
    
    def _set_fallback_target(self):
        """设置回退目标（简单的方向移动）"""
        current_x, current_y = self.rect.center
        
        # 选择四个基本方向之一
        directions = [
            (1, 0),   # 右
            (-1, 0),  # 左
            (0, 1),   # 下
            (0, -1),  # 上
            (1, 1),   # 右下
            (-1, 1),  # 左下
            (1, -1),  # 右上
            (-1, -1)  # 左上
        ]
        
        dx, dy = random.choice(directions)
        target_x = current_x + dx * 100
        target_y = current_y + dy * 100
        
        # 确保在边界内
        target_x = max(self.world_bounds.left + 32, min(self.world_bounds.right - 32, target_x))
        target_y = max(self.world_bounds.top + 32, min(self.world_bounds.bottom - 32, target_y))
        
        self.target_pos = pygame.math.Vector2(target_x, target_y)
        self.direction = pygame.math.Vector2(dx, dy).normalize()
        
        print(f"[CatNPC] {self.cat_name} 使用回退目标: {self.target_pos}")
    
    def _choose_movement_state(self):
        """选择移动状态"""
        # 随机选择下一个状态
        states = ["idle", "moving", "sitting"]
        weights = [40, 50, 10]  # idle 40%, moving 50%, sitting 10%
        
        self.movement_state = random.choices(states, weights=weights)[0]
        
        if self.movement_state == "idle":
            self.state_timer = random.uniform(2, 6)
            self.direction = pygame.math.Vector2(0, 0)
        elif self.movement_state == "moving":
            self.state_timer = random.uniform(3, 8)
            self._set_random_target()
        elif self.movement_state == "sitting":
            self.state_timer = random.uniform(5, 12)
            self.direction = pygame.math.Vector2(0, 0)
        
        print(f"[CatNPC] {self.cat_name} 切换状态: {self.movement_state} ({self.state_timer:.1f}s)")
    
    def update(self, dt):
        """更新猫咪NPC"""
        super().update(dt)
        
        # 更新状态计时器
        self.state_timer -= dt
        
        # 更新对话冷却时间
        if self.conversation_cooldown > 0:
            self.conversation_cooldown -= dt
        
        
        # 状态切换
        if self.state_timer <= 0:
            self._choose_movement_state()
        
        # 根据状态执行行为
        if self.movement_state == "moving":
            self._update_movement(dt)
        elif self.movement_state == "moving_to_workbench":
            self._update_workbench_movement(dt)
        elif self.movement_state == "moving_to_bed":
            self._update_bed_movement(dt)
        elif self.movement_state == "idle":
            # 闲置状态，偶尔小幅度移动
            if random.random() < 0.01:  # 1%概率小移动
                small_move = pygame.math.Vector2(
                    random.uniform(-10, 10), 
                    random.uniform(-10, 10)
                )
                new_pos = pygame.math.Vector2(self.rect.center) + small_move
                
                # 边界检查和碰撞检查
                if (self.world_bounds.contains(pygame.Rect(new_pos.x-16, new_pos.y-16, 32, 32)) and
                    self._is_position_valid(new_pos.x, new_pos.y)):
                    self.pos = new_pos
                    self.rect.center = new_pos
                    self.hitbox.center = new_pos
        # sitting状态不移动
        
        # 更新社交互动
        self._update_social_interactions(dt)
        
        # 更新头顶emoji系统
        self._update_head_emoji_system(dt)
        
        # 更新猫咪照护系统
        self._update_care_system(dt)
        
        # 更新ASCII字符显示
        self._update_ascii_display()
    
    def _update_movement(self, dt):
        """更新移动逻辑"""
        if self.target_pos is None:
            return
        
        current_pos = pygame.math.Vector2(self.rect.center)
        distance_to_target = current_pos.distance_to(self.target_pos)
        
        # 如果接近目标，选择新目标
        if distance_to_target < 20:
            self._set_random_target()
            return
        
        # 规范化方向向量
        if self.direction.magnitude() > 0:
            self.direction = self.direction.normalize()
        
        # 水平移动（参考玩家移动逻辑）
        self.pos.x += self.direction.x * self.move_speed * dt
        self.hitbox.centerx = round(self.pos.x)
        self.rect.centerx = self.hitbox.centerx
        self.collision('horizontal')
        
        # 垂直移动
        self.pos.y += self.direction.y * self.move_speed * dt
        self.hitbox.centery = round(self.pos.y)
        self.rect.centery = self.hitbox.centery
        self.collision('vertical')
        
        # 检查是否卡住了（如果碰撞导致无法接近目标）
        new_distance = pygame.math.Vector2(self.rect.center).distance_to(self.target_pos)
        if new_distance >= distance_to_target - 1:  # 如果距离没有减少
            self.stuck_counter = getattr(self, 'stuck_counter', 0) + 1
            if self.stuck_counter > 60:  # 1秒后重新选择目标（假设60FPS）
                self._set_random_target()
                self.stuck_counter = 0
        else:
            self.stuck_counter = 0
    
    def collision(self, direction):
        """碰撞检测方法（参考玩家系统）"""
        if not self.collision_sprites:
            return
            
        for sprite in self.collision_sprites.sprites():
            if hasattr(sprite, 'hitbox'):
                if sprite.hitbox.colliderect(self.hitbox):
                    if direction == 'horizontal':
                        if self.direction.x > 0:  # 向右移动
                            self.hitbox.right = sprite.hitbox.left
                        if self.direction.x < 0:  # 向左移动
                            self.hitbox.left = sprite.hitbox.right
                        self.rect.centerx = self.hitbox.centerx
                        self.pos.x = self.hitbox.centerx
                        
                        # 碰到障碍物，重新选择目标
                        if random.random() < 0.1:  # 10%概率重新选择目标
                            self._set_random_target()
                    
                    if direction == 'vertical':
                        if self.direction.y > 0:  # 向下移动
                            self.hitbox.bottom = sprite.hitbox.top
                        if self.direction.y < 0:  # 向上移动
                            self.hitbox.top = sprite.hitbox.bottom
                        self.rect.centery = self.hitbox.centery
                        self.pos.y = self.hitbox.centery
                        
                        # 碰到障碍物，重新选择目标
                        if random.random() < 0.1:  # 10%概率重新选择目标
                            self._set_random_target()
            elif sprite.rect.colliderect(self.hitbox):
                # 对于没有hitbox的碰撞体，使用rect
                if direction == 'horizontal':
                    if self.direction.x > 0:
                        self.hitbox.right = sprite.rect.left
                    if self.direction.x < 0:
                        self.hitbox.left = sprite.rect.right
                    self.rect.centerx = self.hitbox.centerx
                    self.pos.x = self.hitbox.centerx
                    
                if direction == 'vertical':
                    if self.direction.y > 0:
                        self.hitbox.bottom = sprite.rect.top
                    if self.direction.y < 0:
                        self.hitbox.top = sprite.rect.bottom
                    self.rect.centery = self.hitbox.centery
                    self.pos.y = self.hitbox.centery
    
    def _update_head_emoji_system(self, dt):
        """更新头顶emoji系统"""
        # 更新emoji计时器
        if self.head_emoji_system['current_emoji']:
            self.head_emoji_system['emoji_timer'] -= dt
            # 如果时间到了，清除emoji
            if self.head_emoji_system['emoji_timer'] <= 0:
                self.head_emoji_system['current_emoji'] = None
        
        # 如果当前没有emoji，随机决定是否显示新emoji
        if not self.head_emoji_system['current_emoji']:
            if random.random() < self.head_emoji_system['emoji_display_chance']:
                self._trigger_behavior_emoji()
        
        # 特殊情况：如果正在对话，强制显示对话emoji
        if self.current_conversation_partner:
            if (not self.head_emoji_system['current_emoji'] or 
                self.head_emoji_system['current_emoji'] != '💬'):
                self._set_head_emoji('💬', 3.0)  # 对话时显示3秒
    
    def _trigger_behavior_emoji(self):
        """根据当前行为触发对应emoji"""
        current_behavior = self.movement_state
        
        # 特殊行为状态映射
        if self.current_conversation_partner:
            current_behavior = 'chatting'
        elif self.movement_state == 'moving' and random.random() < 0.3:
            current_behavior = 'exploring'
        elif random.random() < 0.1:  # 10%概率显示心情emoji
            current_behavior = random.choice(['happy', 'sleepy'])
        
        # 从对应行为的emoji列表中随机选择
        if current_behavior in self.behavior_emojis:
            emoji_list = self.behavior_emojis[current_behavior]
            selected_emoji = random.choice(emoji_list)
            
            # 设置显示时间
            duration = random.uniform(
                self.head_emoji_system['emoji_min_duration'],
                self.head_emoji_system['emoji_max_duration']
            )
            
            self._set_head_emoji(selected_emoji, duration)
    
    def _set_head_emoji(self, emoji, duration):
        """设置头顶emoji"""
        self.head_emoji_system['current_emoji'] = emoji
        self.head_emoji_system['emoji_timer'] = duration
        self.head_emoji_system['emoji_duration'] = duration
        
        # Debug输出
        print(f"[CatNPC] {self.cat_name} 显示emoji: {emoji} ({duration:.1f}s)")
    
    def _update_ascii_display(self):
        """更新ASCII字符显示"""
        # # 根据状态确定要使用的emoji状态
        # if self.movement_state == "sitting":
        #     emoji_state = "sitting"
        #     display_char = "🐱"  # 坐着的猫
        # elif self.movement_state == "moving":
        #     emoji_state = "moving"
        #     display_char = "🐈"  # 移动的猫
        # else:  # idle
        emoji_state = "idle"
        display_char = self.ascii_char
        
        # 更新ASCII渲染 - 使用缓存的着色结果
        self.image.fill((0, 0, 0, 0))  # 清除
        
        # 尝试使用缓存的着色表面
        cached_surface = self.colored_emoji_cache.get(emoji_state)
        
        if cached_surface is not None:
            # 使用缓存的着色表面
            cat_rect = cached_surface.get_rect(center=(TILE_SIZE//2, TILE_SIZE//2))
            self.image.blit(cached_surface, cat_rect)
        else:
            # 如果没有缓存，使用回退方法
            from ..rendering.ascii_renderer import ASCIIRenderer
            renderer = ASCIIRenderer()
            renderer.render_ascii(
                self.image,      # 目标表面
                display_char,    # 字符
                self.skin_color, # 颜色
                (0, 0),         # 位置
                TILE_SIZE       # 大小
            )
        
        # 渲染头顶emoji（如果有的话）
        if self.head_emoji_system['current_emoji']:
            emoji = self.head_emoji_system['current_emoji']
            emoji_size = TILE_SIZE // 6
            
            # 将emoji放在猫咪上方，但确保在image范围内
            emoji_pos = (TILE_SIZE // 2 - emoji_size // 2, 0)  # 水平居中，垂直在最上方
            
            # 使用缓存的字体渲染emoji
            if self.head_emoji_font:
                from ..rendering.ascii_renderer import ASCIIRenderer
                renderer = ASCIIRenderer()
                renderer.render_ascii(
                    self.image,         # 目标表面
                    emoji,              # emoji字符
                    (255, 255, 255),    # 白色
                    emoji_pos,          # 位置（猫咪上方）
                    emoji_size,         # 大小
                    self.head_emoji_font  # 使用缓存的字体
                )
    
    def get_interaction_text(self):
        """获取交互提示文本"""
        return f"按 T 键与小猫 {self.cat_name} 互动"
    
    def get_cat_status(self):
        """获取猫咪状态信息"""
        return {
            "name": self.cat_name,
            "personality": self.cat_personality,
            "state": self.movement_state,
            "position": self.rect.center,
            "ascii_char": self.ascii_char,
            "color": self.skin_color,  # 使用新的skin_color属性
            "head_emoji": self.head_emoji_system['current_emoji'],
            "emoji_timer": self.head_emoji_system['emoji_timer'],
            "is_chatting": bool(self.current_conversation_partner)
        }
    
    def force_head_emoji(self, emoji, duration=3.0):
        """强制设置头顶emoji（用于调试或特殊情况）"""
        self._set_head_emoji(emoji, duration)
    
    def clear_head_emoji(self):
        """立即清除头顶emoji"""
        self.head_emoji_system['current_emoji'] = None
        self.head_emoji_system['emoji_timer'] = 0
    
    def _update_social_interactions(self, dt):
        """更新社交互动逻辑"""
        # 如果在对话冷却期，跳过社交检测
        if self.conversation_cooldown > 0:
            return
        
        # 检测附近的猫咪
        nearby_cats = self._find_nearby_cats()
        self.nearby_cats = nearby_cats
        
        # 如果有附近的猫咪且不在对话中，尝试开始对话
        if nearby_cats and not self.current_conversation_partner:
            # 随机选择一只猫开始对话（低概率）
            if random.random() < 0.002:  # 0.2%的概率每帧，约每10秒一次机会
                selected_cat = random.choice(nearby_cats)
                self._initiate_conversation_with_cat(selected_cat)
    
    def _find_nearby_cats(self):
        """查找附近的猫咪"""
        nearby_cats = []
        current_pos = pygame.math.Vector2(self.rect.center)
        
        # 通过CatManager找到所有其他猫咪
        if hasattr(self, 'cat_manager') and self.cat_manager:
            for cat in self.cat_manager.cats:
                if cat != self:  # 不包括自己
                    cat_pos = pygame.math.Vector2(cat.rect.center)
                    distance = current_pos.distance_to(cat_pos)
                    
                    if distance <= self.social_interaction_distance:
                        nearby_cats.append(cat)
        
        return nearby_cats
    
    def _initiate_conversation_with_cat(self, other_cat):
        """与另一只猫开始对话"""
        import time
        import threading
        import asyncio
        
        # 防止重复对话
        if (self.current_conversation_partner or 
            other_cat.current_conversation_partner or
            other_cat.conversation_cooldown > 0):
            return
        
        print(f"[CatNPC] {self.cat_name} 开始与 {other_cat.cat_name} 对话")
        
        # 设置对话状态
        self.current_conversation_partner = other_cat
        other_cat.current_conversation_partner = self
        
        # 立即显示对话emoji
        self._set_head_emoji('💬', 5.0)  # 对话期间显示5秒
        other_cat._set_head_emoji('💬', 5.0)
        
        # 对话心情奖励
        self.add_mood(5, "猫咪间对话")
        other_cat.add_mood(5, "猫咪间对话")
        self.consume_energy(2, "对话活动")
        other_cat.consume_energy(2, "对话活动")
        
        # 设置冷却期
        self.conversation_cooldown = self.conversation_cooldown_max
        other_cat.conversation_cooldown = other_cat.conversation_cooldown_max
        
        # 异步生成对话
        def generate_cat_conversation():
            try:
                # 创建新的事件循环
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
                
                # 生成猫猫之间的对话
                conversation = loop.run_until_complete(
                    self._generate_cat_to_cat_conversation(other_cat)
                )
                
                # 保存对话到双方的历史记录
                self._save_cat_conversation(other_cat, conversation)
                other_cat._save_cat_conversation(self, conversation)
                
                loop.close()
                
            except Exception as e:
                print(f"[CatNPC] 生成猫猫对话失败: {e}")
            finally:
                # 重置对话状态
                self.current_conversation_partner = None
                other_cat.current_conversation_partner = None
                
                # 清除对话emoji（如果当前是对话emoji的话）
                if self.head_emoji_system['current_emoji'] == '💬':
                    self.head_emoji_system['current_emoji'] = None
                if other_cat.head_emoji_system['current_emoji'] == '💬':
                    other_cat.head_emoji_system['current_emoji'] = None
        
        # 启动对话生成线程
        conversation_thread = threading.Thread(target=generate_cat_conversation)
        conversation_thread.daemon = True
        conversation_thread.start()
    
    async def _generate_cat_to_cat_conversation(self, other_cat):
        """生成猫猫之间的AI对话"""
        from .chat_ai import get_chat_ai
        
        chat_ai = get_chat_ai()
        
        # 构建对话提示
        conversation_prompt = f"""
你需要为两只猫咪生成一段自然的对话场景。

猫咪A: {self.cat_name}
性格: {self.cat_personality}

猫咪B: {other_cat.cat_name}  
性格: {other_cat.cat_personality}

请生成一段包含以下内容的对话：
1. 一段旁白描述两只猫相遇的情景
2. 3-4轮简短的对话交流
3. 对话要符合各自的性格特点
4. 使用可爱的猫语风格（适当使用"喵"）

格式要求：
旁白：[旁白内容]
{self.cat_name}：[对话内容]
{other_cat.cat_name}：[对话内容]
{self.cat_name}：[对话内容]
{other_cat.cat_name}：[对话内容]

请确保对话简短自然，每句话不超过30字。
"""
        
        try:
            # 使用临时的NPC ID进行AI对话生成
            temp_npc_id = f"cat_conversation_{self.npc_id}_{other_cat.npc_id}"
            response = await chat_ai.generate_npc_response(temp_npc_id, conversation_prompt)
            
            # 解析对话内容
            conversation_data = self._parse_conversation_response(response)
            return conversation_data
            
        except Exception as e:
            print(f"[CatNPC] AI对话生成失败: {e}")
            # 回退到预设对话
            return self._generate_fallback_conversation(other_cat)
    
    def _parse_conversation_response(self, response):
        """解析AI生成的对话内容"""
        import re
        from datetime import datetime
        
        lines = response.strip().split('\n')
        conversation_data = {
            'timestamp': datetime.now().isoformat(),
            'narrator': '',
            'dialogue': []
        }
        
        for line in lines:
            line = line.strip()
            if not line:
                continue
                
            # 匹配旁白
            narrator_match = re.match(r'旁白[：:](.+)', line)
            if narrator_match:
                conversation_data['narrator'] = narrator_match.group(1).strip()
                continue
            
            # 匹配对话
            dialogue_match = re.match(r'([^：:]+)[：:](.+)', line)
            if dialogue_match:
                speaker = dialogue_match.group(1).strip()
                text = dialogue_match.group(2).strip()
                conversation_data['dialogue'].append({
                    'speaker': speaker,
                    'text': text
                })
        
        return conversation_data
    
    def _generate_fallback_conversation(self, other_cat):
        """生成回退对话"""
        from datetime import datetime
        
        fallback_conversations = [
            {
                'narrator': f'{self.cat_name}和{other_cat.cat_name}在阳光下相遇了',
                'dialogue': [
                    {'speaker': self.cat_name, 'text': '喵～你好呀'},
                    {'speaker': other_cat.cat_name, 'text': '喵喵～今天天气真好'},
                    {'speaker': self.cat_name, 'text': '一起晒太阳吧，喵'},
                    {'speaker': other_cat.cat_name, 'text': '好呀～喵'}
                ]
            },
            {
                'narrator': f'{self.cat_name}好奇地靠近了{other_cat.cat_name}',
                'dialogue': [
                    {'speaker': self.cat_name, 'text': '你在干什么呢，喵？'},
                    {'speaker': other_cat.cat_name, 'text': '在观察蝴蝶，喵～'},
                    {'speaker': self.cat_name, 'text': '哇，好漂亮，喵！'},
                    {'speaker': other_cat.cat_name, 'text': '对吧～我们一起看，喵'}
                ]
            }
        ]
        
        conversation = random.choice(fallback_conversations)
        conversation['timestamp'] = datetime.now().isoformat()
        return conversation
    
    def _save_cat_conversation(self, other_cat, conversation_data):
        """保存猫猫对话到历史记录"""
        other_cat_id = other_cat.npc_id
        
        if other_cat_id not in self.cat_conversations:
            self.cat_conversations[other_cat_id] = []
        
        self.cat_conversations[other_cat_id].append(conversation_data)
        
        # 限制历史记录长度
        if len(self.cat_conversations[other_cat_id]) > 10:
            self.cat_conversations[other_cat_id] = self.cat_conversations[other_cat_id][-10:]
        
        print(f"[CatNPC] {self.cat_name} 保存了与 {other_cat.cat_name} 的对话")
    
    def get_cat_conversation_history(self, other_cat_id=None):
        """获取猫猫对话历史"""
        if other_cat_id:
            return self.cat_conversations.get(other_cat_id, [])
        else:
            # 返回所有对话历史
            all_conversations = []
            for cat_id, conversations in self.cat_conversations.items():
                all_conversations.extend(conversations)
            # 按时间排序
            all_conversations.sort(key=lambda x: x['timestamp'])
            return all_conversations
    
    # ========== 猫咪照护系统方法 ==========
    
    def _update_care_system(self, dt):
        """更新猫咪照护系统"""
        # 更新计时器
        self.mood_decay_timer += dt
        self.energy_decay_timer += dt
        
        # 每60秒更新一次心情值
        if self.mood_decay_timer >= 60.0:
            self._update_mood_value()
            self.mood_decay_timer = 0.0
        
        # 每60秒更新一次精力值
        if self.energy_decay_timer >= 60.0:
            self._update_energy_value()
            self.energy_decay_timer = 0.0
        
        # 检查睡眠状态
        self._check_sleep_state()
        
        # 检查离开条件
        self._check_leaving_condition()
    
    def _update_mood_value(self):
        """更新心情值"""
        # 心情下降机制
        mood_change = 0
        
        # 无猫窝时：每分钟-2心情值
        if self.owned_cat_bed is None:
            mood_change -= 2
            print(f"🐱 {self.cat_name} 因为没有猫窝心情下降 -2")
        
        # 精力值过低时：每分钟-1心情值
        if self.energy_value < 30:
            mood_change -= 1
            print(f"🐱 {self.cat_name} 因为精力不足心情下降 -1")
        
        # 长时间未与玩家互动：每5分钟-1心情值
        import time
        current_time = time.time()
        if current_time - self.last_interaction_time > 300:  # 5分钟
            mood_change -= 1
            print(f"🐱 {self.cat_name} 因为缺乏互动心情下降 -1")
        
        # 应用心情变化
        self.mood_value = max(0, min(100, self.mood_value + mood_change))
        
        # 更新心情状态
        self._update_mood_state()
    
    def _update_energy_value(self):
        """更新精力值"""
        if self.sleep_state == "sleeping":
            # 睡眠恢复精力
            if self.owned_cat_bed and self.sleep_location == "cat_bed":
                # 在猫窝睡觉：+20精力值/分钟
                energy_gain = 20
                mood_gain = 2  # 同时恢复心情
                self.mood_value = min(100, self.mood_value + mood_gain)
                print(f"🐱 {self.cat_name} 在猫窝睡觉，精力+{energy_gain}，心情+{mood_gain}")
            else:
                # 地面睡觉：+10精力值/分钟
                energy_gain = 10
                print(f"🐱 {self.cat_name} 在地面睡觉，精力+{energy_gain}")
            
            self.energy_value = min(100, self.energy_value + energy_gain)
        else:
            # 正常活动消耗精力
            energy_loss = 1
            
            # 移动时额外消耗
            if self.movement_state == "moving":
                energy_loss += 1
            
            self.energy_value = max(0, self.energy_value - energy_loss)
        
        # 更新精力状态效果
        self._update_energy_effects()
    
    def _update_mood_state(self):
        """根据心情值更新心情状态"""
        if self.mood_value >= 80:
            self.mood = "happy"
            self.mood_status = "😸 开心"
            self.mood_effect = "抓虫效率+20%"
        elif self.mood_value >= 60:
            self.mood = "normal"
            self.mood_status = "😊 正常"
            self.mood_effect = "无特殊效果"
        elif self.mood_value >= 40:
            self.mood = "neutral"
            self.mood_status = "😐 一般"
            self.mood_effect = "抓虫效率-10%"
        elif self.mood_value >= 20:
            self.mood = "sad"
            self.mood_status = "😿 沮丧"
            self.mood_effect = "抓虫效率-20%，移动速度-10%"
        else:
            self.mood = "depressed"
            self.mood_status = "😭 极度沮丧"
            self.mood_effect = "即将离开"
    
    def _update_energy_effects(self):
        """更新精力值对行为的影响"""
        if self.energy_value < 50:
            # 疲劳状态：移动速度-20%
            self.move_speed = max(10, self.move_speed * 0.8)
    
    def _check_sleep_state(self):
        """检查睡眠状态"""
        if self.sleep_state == "awake" and self.energy_value <= 30:
            # 精力不足，需要睡眠
            self._enter_sleep_state()
        elif self.sleep_state == "sleeping" and self.energy_value >= 80:
            # 精力恢复，结束睡眠
            self._exit_sleep_state()
    
    def _enter_sleep_state(self):
        """进入睡眠状态"""
        self.sleep_state = "sleeping"
        self.movement_state = "sleeping"
        self.direction = pygame.math.Vector2(0, 0)
        
        # 寻找睡眠地点
        self._find_sleep_location()
        
        # 显示睡眠表情
        self.force_head_emoji('💤', 300)  # 显示5分钟
        
        print(f"🐱 {self.cat_name} 感到疲劳，开始睡觉")
    
    def _exit_sleep_state(self):
        """退出睡眠状态"""
        self.sleep_state = "awake"
        self.movement_state = "idle"
        
        # 释放猫窝
        if self.sleep_location == "cat_bed" and self.owned_cat_bed:
            self.owned_cat_bed.release()
            self.owned_cat_bed = None
        
        self.sleep_location = None
        
        # 睡眠奖励
        self.mood_value = min(100, self.mood_value + 5)
        
        # 清除睡眠表情
        self.clear_head_emoji()
        
        print(f"🐱 {self.cat_name} 睡醒了，心情+5")
    
    def _find_sleep_location(self):
        """寻找睡眠地点"""
        # 优先选择自己的猫窝
        from ..systems.cat_bed import get_cat_bed_manager
        cat_bed_manager = get_cat_bed_manager()
        
        my_cat_bed = cat_bed_manager.get_cat_bed_by_owner(self.npc_id)
        
        if my_cat_bed and my_cat_bed.can_be_used_by(self):
            # 移动到猫窝位置
            self.target_pos = my_cat_bed.bed_pos.copy()
            self.movement_state = "moving_to_bed"
            my_cat_bed.occupy(self)
            self.sleep_location = "cat_bed"
            print(f"🐱 {self.cat_name} 前往自己的猫窝睡觉")
        else:
            # 在当前位置睡觉
            self.sleep_location = "ground"
            print(f"🐱 {self.cat_name} 在地面睡觉")
    
    def _check_leaving_condition(self):
        """检查离开条件"""
        if self.mood_value == 0:
            if not self.leaving_warning_shown:
                # 显示离开警告
                self.leaving_warning_shown = True
                self.leaving_warning_timer = 300.0  # 5分钟警告
                print(f"⚠️ {self.cat_name} 心情极度低落，将在5分钟后离开！")
                
                # 显示离开警告通知
                if hasattr(self, 'cat_manager') and self.cat_manager.event_notification_manager:
                    self.cat_manager.event_notification_manager.add_notification(
                        f"⚠️ {self.cat_name} 心情极度低落，将在5分钟后离开！",
                        duration=10.0,
                        notification_type="warning"
                    )
            else:
                # 倒计时离开
                self.leaving_warning_timer -= 1.0
                if self.leaving_warning_timer <= 0:
                    self._leave_game()
        else:
            # 心情恢复，取消离开警告
            if self.leaving_warning_shown:
                self.leaving_warning_shown = False
                self.leaving_warning_timer = 0.0
                print(f"😊 {self.cat_name} 心情好转，取消离开")
    
    def _leave_game(self):
        """猫咪离开游戏"""
        print(f"😿 {self.cat_name} 因为心情太差离开了游戏世界")
        
        # 显示离开通知
        if hasattr(self, 'cat_manager') and self.cat_manager.event_notification_manager:
            self.cat_manager.event_notification_manager.add_notification(
                f"😿 {self.cat_name} 因为心情太差离开了游戏世界",
                duration=10.0,
                notification_type="cat_leave"
            )
        
        # 从猫咪管理器中移除
        if hasattr(self, 'cat_manager') and self in self.cat_manager.cats:
            self.cat_manager.cats.remove(self)
        
        # 从精灵组中移除
        self.kill()
    
    def add_mood(self, amount, reason=""):
        """增加心情值"""
        old_mood = self.mood_value
        self.mood_value = min(100, self.mood_value + amount)
        print(f"🐱 {self.cat_name} 心情+{amount} ({reason}): {old_mood} → {self.mood_value}")
        self._update_mood_state()
    
    def consume_energy(self, amount, reason=""):
        """消耗精力值"""
        old_energy = self.energy_value
        self.energy_value = max(0, self.energy_value - amount)
        print(f"🐱 {self.cat_name} 精力-{amount} ({reason}): {old_energy} → {self.energy_value}")
    
    def update_interaction_time(self):
        """更新最后互动时间"""
        import time
        self.last_interaction_time = time.time()
    
    def get_care_status(self):
        """获取照护状态信息"""
        return {
            "mood_value": self.mood_value,
            "energy_value": self.energy_value,
            "sleep_state": self.sleep_state,
            "mood_status": getattr(self, 'mood_status', '😊 正常'),
            "mood_effect": getattr(self, 'mood_effect', '无特殊效果'),
            "has_cat_bed": self.owned_cat_bed is not None,
            "leaving_warning": self.leaving_warning_shown,
            "leaving_time": self.leaving_warning_timer if self.leaving_warning_shown else 0
        }

class CatManager:
    """猫咪管理器"""
    
    def __init__(self):
        self.cats = []
        
        # 使用统一的猫咪数据管理器
        self.cat_data_manager = get_cat_data_manager()
        
        # 初始化事件系统
        self.event_system = CatEventSystem()
        self.event_check_timer = 0
        self.event_check_interval = 1.0  # 每秒检查一次事件
        self.event_notification_manager = None  # 将在level中设置
        
        # 昆虫捕捉系统
        self.insect_catch_timer = 0
        self.insect_catch_interval = 5.0  # 每5秒检查一次昆虫捕捉
        self.last_insect_catch_time = 0
    
    def create_cats(self, all_sprites, collision_sprites, npc_sprites, npc_manager, player_pos=None, initial_cats=0):
        """创建猫咪NPC
        
        Args:
            initial_cats: 初始创建的猫咪数量，默认为0（通过钓鱼获得）
        """
        # 存储游戏对象引用，用于后续动态添加猫咪
        self.all_sprites = all_sprites
        self.collision_sprites = collision_sprites
        self.npc_sprites = npc_sprites
        self.npc_manager = npc_manager
        
        # 如果没有提供玩家位置，使用默认中心位置
        if player_pos is None:
            player_pos = (800, 800)  # 地图中心附近
        
        self.last_player_pos = player_pos
        
        print(f"[CatManager] 初始化猫咪管理器，初始猫咪数量: {initial_cats}")
        
        # 创建指定数量的初始猫咪
        for i in range(initial_cats):
            self._create_single_cat(player_pos, i)
        
        print(f"[CatManager] 成功创建 {len(self.cats)} 只初始猫咪")
    
    def _create_single_cat(self, player_pos, cat_index=None):
        """创建单只猫咪"""
        # 从统一数据管理器获取随机猫咪信息
        cat_info = self.cat_data_manager.get_random_cat()
        
        cat_name = cat_info.name
        cat_personality = cat_info.personality
        
        # 智能选择spawn位置
        spawn_pos = self._find_valid_spawn_position(
            player_pos, self.collision_sprites, attempt_id=cat_index
        )
        
        if spawn_pos is None:
            print(f"[CatManager] 警告: 无法为猫咪 {cat_name} 找到有效位置，跳过创建")
            return None
        
        # 创建猫咪NPC ID - 使用猫咪名字确保与统一数据系统一致
        cat_id = f"cat_{cat_name}"
        
        # 创建猫咪NPC
        cat = CatNPC(
            pos=spawn_pos,
            npc_id=cat_id,
            npc_manager=self.npc_manager,
            groups=[self.all_sprites, self.npc_sprites],  # 不加入collision_sprites，猫咪可以重叠
            cat_name=cat_name,
            cat_personality=cat_personality,
            collision_sprites=self.collision_sprites,  # 传递碰撞精灵组
            cat_info=cat_info  # 传递统一的猫咪信息
        )
        
        # 给猫咪设置管理器引用，用于找到其他猫咪
        cat.cat_manager = self
        
        self.cats.append(cat)
        print(f"[CatManager] 创建猫咪: {cat_name} ({cat_id}) 位置: {spawn_pos}")
        
        return cat
    
    def add_new_cat_from_fishing(self, player_pos):
        """从钓鱼获得新猫咪"""
        print(f"[CatManager] 🎣 从钓鱼中获得新猫咪！")
        
        # 更新玩家位置
        self.last_player_pos = player_pos
        
        # 创建新猫咪
        new_cat = self._create_single_cat(player_pos)
        
        if new_cat:
            print(f"[CatManager] 🐱 新猫咪 {new_cat.cat_name} 加入了游戏世界！")
            
            # 让新猫咪显示开心的emoji
            new_cat.force_head_emoji('😍', 8.0)  # 显示8秒开心表情
            
            return new_cat
        else:
            print(f"[CatManager] ERROR: Failed to create new cat")
            return None
    
    def get_cat_count(self):
        """获取当前猫咪数量"""
        return len(self.cats)
    
    def _find_valid_spawn_position(self, player_pos, collision_sprites, attempt_id=0):
        """寻找有效的spawn位置"""
        player_x, player_y = player_pos
        
        # 定义搜索参数
        min_distance_from_player = 50  # 距离玩家最小距离
        max_distance_from_player = 150  # 距离玩家最大距离
        max_attempts = 100  # 增加尝试次数
        
        # 按照距离从近到远的顺序定义搜索圈
        search_rings = [
            (50, 80),   # 第一圈:50-80
            (80, 100),  # 第二圈:80-100
            (100, 120), # 第三圈:100-120
            (120, 150)  # 第四圈:120-150
        ]
        
        # 在每个搜索圈内尝试多个角度
        angles = [i * (math.pi/8) for i in range(16)]  # 将圆分成16等份
        
        # 按圈搜索
        for min_r, max_r in search_rings:
            # 在当前圈内尝试所有角度
            for angle in angles:
                # 在min_r和max_r之间随机选择距离
                distance = random.uniform(min_r, max_r)
                
                # 计算坐标
                candidate_x = player_x + math.cos(angle) * distance
                candidate_y = player_y + math.sin(angle) * distance
                
                # 添加小范围随机偏移,避免猫咪位置过于规则
                candidate_x += random.randint(-10, 10)
                candidate_y += random.randint(-10, 10)
                
                if self._is_spawn_position_valid(candidate_x, candidate_y, player_pos, collision_sprites):
                    return (candidate_x, candidate_y)
        
        # 如果上述方法都失败了,进行网格搜索
        grid_size = 20  # 20x20的网格
        for x_offset in range(-max_distance_from_player, max_distance_from_player+1, grid_size):
            for y_offset in range(-max_distance_from_player, max_distance_from_player+1, grid_size):
                candidate_x = player_x + x_offset
                candidate_y = player_y + y_offset
                
                # 检查是否在最大范围内
                distance = math.sqrt(x_offset**2 + y_offset**2)
                if min_distance_from_player <= distance <= max_distance_from_player:
                    if self._is_spawn_position_valid(candidate_x, candidate_y, player_pos, collision_sprites):
                        return (candidate_x, candidate_y)
        
        # 如果还是找不到,放宽限制重试一次
        print("[CatManager] 正在放宽限制重新搜索...")
        for angle in range(0, 360, 10):  # 每10度搜索一次
            rad = math.radians(angle)
            for dist in range(50, 151, 10):  # 每10单位距离搜索一次
                candidate_x = player_x + math.cos(rad) * dist
                candidate_y = player_y + math.sin(rad) * dist
                
                # 临时放宽碰撞检测
                if self._is_spawn_position_valid(candidate_x, candidate_y, player_pos, None):
                    print(f"[CatManager] 在放宽限制后找到位置: ({int(candidate_x)}, {int(candidate_y)})")
                    return (candidate_x, candidate_y)
        
        # 如果实在找不到,返回一个固定位置
        print("[CatManager] 警告: 无法找到理想位置,使用默认位置")
        return (player_x - 100, player_y - 100)
    
    def _is_spawn_position_valid(self, x, y, player_pos, collision_sprites):
        """检查spawn位置是否有效"""
        
        # 1. 基本边界检查（保守的地图边界）
        map_bounds = pygame.Rect(100, 100, 1400, 1400)  # 比实际地图小一点
        position_rect = pygame.Rect(x - 32, y - 32, 64, 64)
        if not map_bounds.contains(position_rect):
            return False
        
        # 2. 与玩家距离检查
        player_x, player_y = player_pos
        distance_to_player = math.sqrt((x - player_x)**2 + (y - player_y)**2)
        
        # 不能太近也不能太远
        if distance_to_player < 100 or distance_to_player > 800:
            return False
        
        # 3. 碰撞检测 - 检查是否与障碍物重叠
        if collision_sprites:
            # 创建临时hitbox检查碰撞
            temp_hitbox = pygame.Rect(x - 16, y - 16, 32, 32)  # 猫咪的hitbox大小
            
            for sprite in collision_sprites.sprites():
                if hasattr(sprite, 'hitbox'):
                    if sprite.hitbox.colliderect(temp_hitbox):
                        return False
                elif hasattr(sprite, 'rect'):
                    if sprite.rect.colliderect(temp_hitbox):
                        return False
        
        # 4. 与已存在的猫咪距离检查（避免太密集）
        min_cat_distance = 80
        for existing_cat in self.cats:
            cat_x, cat_y = existing_cat.rect.center
            distance = math.sqrt((x - cat_x)**2 + (y - cat_y)**2)
            if distance < min_cat_distance:
                return False
        
        return True
    
    def get_cat_statistics(self):
        """获取猫咪统计信息"""
        if not self.cats:
            return {}
        
        stats = {
            "total_cats": len(self.cats),
            "states": {},
            "average_position": [0, 0]
        }
        
        total_x, total_y = 0, 0
        
        for cat in self.cats:
            # 统计状态
            state = cat.movement_state
            stats["states"][state] = stats["states"].get(state, 0) + 1
            
            # 计算平均位置
            total_x += cat.rect.centerx
            total_y += cat.rect.centery
        
        stats["average_position"] = [
            total_x // len(self.cats), 
            total_y // len(self.cats)
        ]
        
        return stats
    
    def find_nearest_cat(self, position, max_distance=100):
        """找到最近的猫咪"""
        nearest_cat = None
        min_distance = float('inf')
        
        for cat in self.cats:
            distance = math.sqrt(
                (position[0] - cat.rect.centerx) ** 2 +
                (position[1] - cat.rect.centery) ** 2
            )
            
            if distance < max_distance and distance < min_distance:
                min_distance = distance
                nearest_cat = cat
        
        return nearest_cat, min_distance if nearest_cat else None
    
    def update(self, dt):
        """更新猫咪管理器，包括事件系统检查和昆虫捕捉"""
        # 更新事件检查计时器
        self.event_check_timer += dt
        
        if self.event_check_timer >= self.event_check_interval:
            self.event_check_timer = 0
            self._check_cat_events()
        
        # 更新昆虫捕捉计时器
        self.insect_catch_timer += dt
        
        if self.insect_catch_timer >= self.insect_catch_interval:
            self.insect_catch_timer = 0
            self._check_insect_catching()
    
    def _check_cat_events(self):
        """检查猫咪事件"""
        if len(self.cats) < 2:
            return  # 需要至少2只猫才能触发事件
        
        # 找到聚集在一起的猫咪群组
        cat_groups = self._find_nearby_cat_groups()
        
        for group in cat_groups:
            if len(group) >= 2:
                # 准备事件参与者数据
                nearby_cats = []
                for cat in group:
                    cat_data = {
                        'id': f"cat_{cat.cat_name}",
                        'name': cat.cat_name,
                        'personality': cat.cat_personality,
                        'position': cat.rect.center
                    }
                    nearby_cats.append(cat_data)
                
                # 检查事件触发
                event_result = self.event_system.check_event_trigger(nearby_cats)
                
                if event_result and event_result.success:
                    self._handle_event_result(event_result)
    
    def _find_nearby_cat_groups(self):
        """找到附近的猫咪群组"""
        groups = []
        processed_cats = set()
        
        for cat in self.cats:
            if cat in processed_cats:
                continue
            
            # 找到这只猫附近的所有猫咪
            group = [cat]
            processed_cats.add(cat)
            
            for other_cat in self.cats:
                if other_cat in processed_cats:
                    continue
                
                distance = math.sqrt(
                    (cat.rect.centerx - other_cat.rect.centerx) ** 2 +
                    (cat.rect.centery - other_cat.rect.centery) ** 2
                )
                
                if distance <= self.event_system.proximity_threshold:
                    group.append(other_cat)
                    processed_cats.add(other_cat)
            
            if len(group) >= 2:
                groups.append(group)
        
        return groups
    
    def _handle_event_result(self, event_result):
        """处理事件结果"""
        # 显示事件通知
        if self.event_notification_manager:
            self.event_notification_manager.add_event_notification(event_result.message)
        
        # 显示关系变化通知
        for relationship_key, changes in event_result.relationship_changes.items():
            if self.event_notification_manager:
                cat_ids = relationship_key.split('-')
                if len(cat_ids) == 2:
                    cat1_name = cat_ids[0].replace('cat_', '')
                    cat2_name = cat_ids[1].replace('cat_', '')
                    self.event_notification_manager.add_relationship_notification(
                        cat1_name, cat2_name, changes
                    )
        
        # 给参与事件的猫咪心情奖励
        for participant_id in event_result.participants:
            # 通过ID找到对应的猫咪
            for cat in self.cats:
                if cat.npc_id == participant_id:
                    cat.add_mood(10, "猫咪聚集事件")
                    break
        
        # 打印调试信息
        print(f"[CatManager] 触发事件: {event_result.message}")
        for participant in event_result.participants:
            print(f"[CatManager] 参与者: {participant}")
    
    def _check_insect_catching(self):
        """检查猫咪昆虫捕捉"""
        if not self.cats:
            return
        
        from ..systems.bait_system import get_bait_system
        bait_system = get_bait_system()
        
        # 每只猫都有机会抓昆虫
        for cat in self.cats:
            # 每只猫每次检查有20%的基础概率尝试抓昆虫
            if random.random() < 0.2:
                self._cat_try_catch_insect(cat, bait_system)
    
    def _cat_try_catch_insect(self, cat, bait_system):
        """单只猫尝试抓昆虫"""
        # 根据昆虫的捕获概率随机选择一种昆虫
        insect_types = bait_system.insect_types
        
        # 创建加权随机选择列表
        weighted_insects = []
        for insect_id, insect in insect_types.items():
            # 使用概率作为权重，概率越高越容易被选中
            weight = int(insect.catch_probability * 100)
            weighted_insects.extend([insect_id] * weight)
        
        if not weighted_insects:
            return
        
        # 随机选择一种昆虫
        selected_insect_id = random.choice(weighted_insects)
        selected_insect = insect_types[selected_insect_id]
        
        # 根据昆虫的捕获概率决定是否成功抓到
        if random.random() <= selected_insect.catch_probability:
            # 成功抓到昆虫，但不直接放入鱼饵系统
            # 而是让猫咪先持有，然后移动到工作台
            cat.caught_insect = {
                'id': selected_insect_id,
                'name': selected_insect.name,
                'ascii_char': selected_insect.ascii_char
            }
            
            # 猫咪显示开心表情和心情奖励
            cat.force_head_emoji('😸', 3.0)
            cat.add_mood(3, "成功抓虫")
            cat.consume_energy(5, "抓虫活动")
            
            print(f"🐱 {cat.cat_name} 抓到了 {selected_insect.name}！正在前往工作台...")
            
            # 设置猫咪移动到工作台
            self._send_cat_to_workbench(cat)
            
            # 如果有事件通知管理器，显示通知
            if self.event_notification_manager:
                self.event_notification_manager.add_notification(
                    f"🐱 {cat.cat_name} 抓到了 {selected_insect.ascii_char} {selected_insect.name}！",
                    duration=3.0,
                    notification_type="insect_catch"
                )
    
    def _send_cat_to_workbench(self, cat):
        """让猫咪移动到工作台"""
        
        workbench = get_bait_workbench()
        
        if workbench:
            # 设置猫咪的目标位置为工作台
            cat.target_pos = workbench.workbench_pos.copy()
            cat.movement_state = "moving_to_workbench"
            cat.workbench_target = workbench
            
            print(f"🐱 {cat.cat_name} 开始前往工作台 ({workbench.workbench_pos.x}, {workbench.workbench_pos.y})")
        else:
            print(f"⚠️ 找不到工作台，{cat.cat_name} 无法送虫子")
            # 如果没有工作台，直接放入鱼饵系统（回退机制）
            if hasattr(cat, 'caught_insect') and cat.caught_insect:
                from ..systems.bait_system import get_bait_system
                bait_system = get_bait_system()
                bait_system.add_insect(cat.caught_insect['id'], 1)
                cat.caught_insect = None

    def set_event_notification_manager(self, notification_manager):
        """设置事件通知管理器"""
        self.event_notification_manager = notification_manager
    
    def get_relationship_summary(self, cat1_name, cat2_name):
        """获取两只猫的关系摘要"""
        cat1_id = f"cat_{cat1_name}"
        cat2_id = f"cat_{cat2_name}"
        return self.event_system.get_relationship_summary(cat1_id, cat2_id)
    
    def get_cat_compatibility(self, cat1_name, cat2_name):
        """获取两只猫的兼容性分数"""
        cat1_id = f"cat_{cat1_name}"
        cat2_id = f"cat_{cat2_name}"
        return self.event_system.get_cat_compatibility(cat1_id, cat2_id)
    
    def debug_print_relationships(self):
        """调试：打印所有关系"""
        self.event_system.debug_print_relationships()