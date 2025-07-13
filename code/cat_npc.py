import pygame
import random
import math
from settings import *
from ascii_sprites import ASCIINPC

class CatNPC(ASCIINPC):
    """猫咪NPC类 - 继承自ASCIINPC并添加移动功能"""
    
    def __init__(self, pos, npc_id, npc_manager, groups, cat_name, cat_personality):
        super().__init__(pos, npc_id, npc_manager, groups)
        
        # 猫咪特有属性
        self.cat_name = cat_name
        self.cat_personality = cat_personality
        
        # 移动相关属性
        self.move_speed = random.uniform(20, 40)  # 随机移动速度
        self.direction = pygame.math.Vector2(0, 0)
        self.target_pos = None
        self.movement_timer = 0
        self.movement_interval = random.uniform(2, 5)  # 2-5秒更换一次移动目标
        self.idle_time = 0
        self.max_idle_time = random.uniform(3, 8)  # 3-8秒闲置时间
        
        # 移动边界（游戏世界边界）
        self.world_bounds = pygame.Rect(0, 0, 1600, 1600)  # 假设游戏世界边界
        
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
        
        # 设置初始移动目标
        self._set_random_target()
    
    def _set_random_target(self):
        """设置随机移动目标"""
        # 在附近选择一个随机位置
        current_x, current_y = self.rect.center
        
        # 移动范围限制在当前位置的200像素内
        max_distance = 200
        angle = random.uniform(0, 2 * math.pi)
        distance = random.uniform(50, max_distance)
        
        target_x = current_x + math.cos(angle) * distance
        target_y = current_y + math.sin(angle) * distance
        
        # 确保目标在世界边界内
        target_x = max(self.world_bounds.left + 32, min(self.world_bounds.right - 32, target_x))
        target_y = max(self.world_bounds.top + 32, min(self.world_bounds.bottom - 32, target_y))
        
        self.target_pos = pygame.math.Vector2(target_x, target_y)
        
        # 计算方向向量
        target_vector = self.target_pos - pygame.math.Vector2(self.rect.center)
        if target_vector.length() > 0:
            self.direction = target_vector.normalize()
        else:
            self.direction = pygame.math.Vector2(0, 0)
        
        print(f"[CatNPC] {self.cat_name} 设置新目标: {self.target_pos}")
    
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
                
                # 边界检查
                if self.world_bounds.contains(pygame.Rect(new_pos.x-16, new_pos.y-16, 32, 32)):
                    self.rect.center = new_pos
        # sitting状态不移动
        
        # 更新社交互动
        self._update_social_interactions(dt)
        
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
        
        # 移动向目标
        movement = self.direction * self.move_speed * dt
        new_pos = current_pos + movement
        
        # 边界检查
        new_rect = pygame.Rect(new_pos.x - 16, new_pos.y - 16, 32, 32)
        if self.world_bounds.contains(new_rect):
            self.rect.center = new_pos
        else:
            # 碰到边界，选择新目标
            self._set_random_target()
    
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
        from ascii_renderer import ASCIIRenderer
        renderer = ASCIIRenderer()
        
        # 使用render_ascii方法直接在image表面上渲染
        renderer.render_ascii(
            self.image,      # 目标表面
            display_char,    # 字符
            self.char_color, # 颜色
            (0, 0),         # 位置
            TILE_SIZE       # 大小
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
            "color": self.char_color
        }
    
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
        
        # 启动对话生成线程
        conversation_thread = threading.Thread(target=generate_cat_conversation)
        conversation_thread.daemon = True
        conversation_thread.start()
    
    async def _generate_cat_to_cat_conversation(self, other_cat):
        """生成猫猫之间的AI对话"""
        from chat_ai import get_chat_ai
        
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
    
    def create_cats(self, all_sprites, collision_sprites, npc_sprites, npc_manager):
        """创建所有猫咪NPC"""
        # 定义猫咪的生成位置（避开建筑和重要区域）
        spawn_areas = [
            (600, 400),   # 池塘附近
            (800, 600),   # 农田区域
            (1000, 800),  # 开阔地带
            (500, 1000),  # 南部区域
            (1200, 400),  # 东部区域
            (400, 800),   # 西部区域
            (900, 1200),  # 东南区域
            (700, 300),   # 北部区域
            (1100, 1000), # 东南角
            (300, 600),   # 西部中央
        ]
        
        for i in range(10):
            cat_name = self.cat_names[i]
            cat_personality = self.cat_personalities[i]
            spawn_pos = spawn_areas[i]
            
            # 添加一些随机偏移
            actual_pos = (
                spawn_pos[0] + random.randint(-50, 50),
                spawn_pos[1] + random.randint(-50, 50)
            )
            
            # 创建猫咪NPC ID
            cat_id = f"cat_{i+1:02d}"
            
            # 创建猫咪NPC
            cat = CatNPC(
                pos=actual_pos,
                npc_id=cat_id,
                npc_manager=npc_manager,
                groups=[all_sprites, npc_sprites],  # 不加入collision_sprites，猫咪可以重叠
                cat_name=cat_name,
                cat_personality=cat_personality
            )
            
            # 给猫咪设置管理器引用，用于找到其他猫咪
            cat.cat_manager = self
            
            self.cats.append(cat)
            print(f"[CatManager] 创建猫咪: {cat_name} ({cat_id}) 位置: {actual_pos}")
        
        print(f"[CatManager] 成功创建 {len(self.cats)} 只猫咪")
    
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