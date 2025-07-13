import pygame
import random
import math
from ..settings import *
from ..rendering.ascii_sprites import ASCIINPC

class CatNPC(ASCIINPC):
    """猫咪NPC类 - 继承自ASCIINPC并添加移动功能"""
    
    def __init__(self, pos, npc_id, npc_manager, groups, cat_name, cat_personality, collision_sprites=None):
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
        self.movement_state = "idle"  # idle, moving, sitting
        self.state_timer = 0
        
        # 猫猫社交相关属性
        self.social_interaction_distance = 80  # 社交互动距离
        self.nearby_cats = []  # 附近的猫咪列表
        self.current_conversation_partner = None  # 当前对话伙伴
        self.conversation_cooldown = 0  # 对话冷却时间
        self.conversation_cooldown_max = 30  # 30秒冷却
        self.last_conversation_time = 0
        
        # 猫猫对话历史（用于存储猫猫之间的对话）
        self.cat_conversations = {}  # {other_cat_id: [conversation_entries...]}
        
        # ASCII字符设定
        self.ascii_char = random.choice(['🐈', '🐱', '😺', '😸', '😻', '😽'])  # 随机猫咪字符
        self.char_color = random.choice([
            (255, 200, 100),  # 橙猫
            (200, 200, 200),  # 灰猫
            (255, 255, 255),  # 白猫
            (100, 100, 100),  # 黑猫
            (150, 100, 50),   # 棕猫
            (255, 150, 150),  # 粉猫
        ])
        
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
        # 根据状态显示不同字符
        if self.movement_state == "sitting":
            display_char = "🐱"  # 坐着的猫
        elif self.movement_state == "moving":
            # 根据移动方向显示不同字符
            if abs(self.direction.x) > abs(self.direction.y):
                display_char = "🐈" if self.direction.x > 0 else "🐈"
            else:
                display_char = "🐈" if self.direction.y > 0 else "🐈"
        else:  # idle
            display_char = self.ascii_char
        
        # 更新ASCII渲染 - 直接在image上渲染
        self.image.fill((0, 0, 0, 0))  # 清除
        from ..rendering.ascii_renderer import ASCIIRenderer
        renderer = ASCIIRenderer()
        
        # 使用render_ascii方法直接在image表面上渲染猫咪本体
        renderer.render_ascii(
            self.image,      # 目标表面
            display_char,    # 字符
            self.char_color, # 颜色
            (0, 0),         # 位置
            TILE_SIZE       # 大小
        )
        
        # 渲染头顶emoji（如果有的话）
        if self.head_emoji_system['current_emoji']:
            emoji = self.head_emoji_system['current_emoji']
            emoji_size = TILE_SIZE // 3  # emoji比猫咪小，使用1/3大小
            # 将emoji放在猫咪上方，但确保在image范围内
            emoji_pos = (TILE_SIZE // 2 - emoji_size // 2, 0)  # 水平居中，垂直在最上方
            
            # 渲染emoji
            renderer.render_ascii(
                self.image,         # 目标表面
                emoji,              # emoji字符
                (255, 255, 255),    # 白色
                emoji_pos,          # 位置（猫咪上方）
                emoji_size          # 大小
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
            "color": self.char_color,
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

class CatManager:
    """猫咪管理器"""
    
    def __init__(self):
        self.cats = []
        self.cat_names = [
            "小橘", "小白", "小黑", "小灰", "小花",
            "咪咪", "喵喵", "球球", "毛毛", "糖糖"
        ]
        
        self.cat_personalities = [
            "活泼好动，喜欢到处跑跳",
            "温顺安静，喜欢晒太阳",
            "好奇心强，喜欢探索新事物",
            "慵懒可爱，总是想睡觉",
            "聪明机灵，会各种小把戏",
            "粘人撒娇，喜欢被摸摸",
            "独立自主，有自己的想法",
            "贪吃小猫，对食物很敏感",
            "胆小害羞，容易受到惊吓",
            "淘气捣蛋，喜欢恶作剧"
        ]
    
    def create_cats(self, all_sprites, collision_sprites, npc_sprites, npc_manager, player_pos=None):
        """创建所有猫咪NPC"""
        
        # 如果没有提供玩家位置，使用默认中心位置
        if player_pos is None:
            player_pos = (800, 800)  # 地图中心附近
        
        print(f"[CatManager] 开始创建猫咪，玩家位置: {player_pos}")
        
        for i in range(10):
            cat_name = self.cat_names[i]
            cat_personality = self.cat_personalities[i]
            
            # 智能选择spawn位置
            spawn_pos = self._find_valid_spawn_position(
                player_pos, collision_sprites, attempt_id=i
            )
            
            if spawn_pos is None:
                print(f"[CatManager] 警告: 无法为猫咪 {cat_name} 找到有效位置，跳过创建")
                continue
            
            # 创建猫咪NPC ID
            cat_id = f"cat_{i+1:02d}"
            
            # 创建猫咪NPC
            cat = CatNPC(
                pos=spawn_pos,
                npc_id=cat_id,
                npc_manager=npc_manager,
                groups=[all_sprites, npc_sprites],  # 不加入collision_sprites，猫咪可以重叠
                cat_name=cat_name,
                cat_personality=cat_personality,
                collision_sprites=collision_sprites  # 传递碰撞精灵组
            )
            
            # 给猫咪设置管理器引用，用于找到其他猫咪
            cat.cat_manager = self
            
            self.cats.append(cat)
            print(f"[CatManager] 创建猫咪: {cat_name} ({cat_id}) 位置: {spawn_pos}")
        
        print(f"[CatManager] 成功创建 {len(self.cats)} 只猫咪")
    
    def _find_valid_spawn_position(self, player_pos, collision_sprites, attempt_id=0):
        """寻找有效的spawn位置"""
        player_x, player_y = player_pos
        
        # 定义搜索参数
        min_distance_from_player = 100  # 距离玩家最小距离
        max_distance_from_player = 400  # 距离玩家最大距离
        max_attempts = 50  # 最大尝试次数
        
        # 预定义的候选区域（相对于玩家位置的偏移）
        candidate_offsets = [
            # 四个主要方向
            (200, 0), (-200, 0), (0, 200), (0, -200),
            # 对角线方向
            (150, 150), (-150, 150), (150, -150), (-150, -150),
            # 更远的位置
            (300, 100), (-300, 100), (100, 300), (-100, 300),
            (300, -100), (-300, -100), (100, -300), (-100, -300),
            # 额外的随机方向
            (250, 50), (-250, 50), (50, 250), (-50, 250),
        ]
        
        # 首先尝试预定义的候选位置
        for i, (dx, dy) in enumerate(candidate_offsets):
            if i > attempt_id * 3:  # 为每只猫使用不同的起始位置
                break
                
            candidate_x = player_x + dx
            candidate_y = player_y + dy
            
            # 添加一些随机偏移
            candidate_x += random.randint(-30, 30)
            candidate_y += random.randint(-30, 30)
            
            if self._is_spawn_position_valid(candidate_x, candidate_y, player_pos, collision_sprites):
                return (candidate_x, candidate_y)
        
        # 如果预定义位置都不行，随机搜索
        for attempt in range(max_attempts):
            # 在玩家周围的环形区域内随机选择
            angle = random.uniform(0, 2 * math.pi)
            distance = random.uniform(min_distance_from_player, max_distance_from_player)
            
            candidate_x = player_x + math.cos(angle) * distance
            candidate_y = player_y + math.sin(angle) * distance
            
            if self._is_spawn_position_valid(candidate_x, candidate_y, player_pos, collision_sprites):
                return (candidate_x, candidate_y)
        
        # 如果还是找不到，尝试更大的搜索范围
        print(f"[CatManager] 扩大搜索范围寻找spawn位置...")
        for attempt in range(max_attempts):
            angle = random.uniform(0, 2 * math.pi)
            distance = random.uniform(max_distance_from_player, max_distance_from_player * 2)
            
            candidate_x = player_x + math.cos(angle) * distance
            candidate_y = player_y + math.sin(angle) * distance
            
            if self._is_spawn_position_valid(candidate_x, candidate_y, player_pos, collision_sprites):
                return (candidate_x, candidate_y)
        
        print(f"[CatManager] 警告: 无法找到有效的spawn位置")
        return None
    
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