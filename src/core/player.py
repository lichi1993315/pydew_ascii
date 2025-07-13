import pygame
from ..settings import *
from .support import *
from ..systems.timer import Timer
from ..systems.fish_system import FishSystem
from ..ui.log_panel import LogPanel
import datetime

class Player(pygame.sprite.Sprite):
	def __init__(self, pos, group, collision_sprites, tree_sprites, interaction, soil_layer, toggle_shop, quest_panel=None, ascii_mode=False, chat_panel=None):
		super().__init__(group)

		# ASCII模式设置
		
		from ..rendering.ascii_renderer import ASCIIRenderer
		self.ascii_renderer = ASCIIRenderer()
		# 创建ASCII表面 - 使用TILE_SIZE保持一致
		self.image = pygame.Surface((TILE_SIZE, TILE_SIZE), pygame.SRCALPHA)
		# ASCII字符映射
		self.ascii_chars = {
			# 基本移动
			'up': '^',
			'down': 'v', 
			'left': '<',
			'right': '>',
			
			# 闲置状态
			'up_idle': '^',
			'down_idle': '@',
			'left_idle': '@',
			'right_idle': '@',
			
			# 工具使用状态
			'up_hoe': '╨',
			'down_hoe': '╥',
			'left_hoe': '╞',
			'right_hoe': '╡',
			
			'up_axe': '┴',
			'down_axe': '┬',
			'left_axe': '├',
			'right_axe': '┤',
			
			'up_water': '╩',
			'down_water': '╦',
			'left_water': '╠',
			'right_water': '╣',
			
			# 钓鱼状态
			'up_fishing': 'Y',
			'down_fishing': 'Y',
			'left_fishing': 'Y',
			'right_fishing': 'Y',
		}
		

		self.status = 'down_idle'
		self.frame_index = 0
		
		# 钓鱼相关属性初始化（需要在render_ascii_player之前）
		self.is_fishing = False
		self.water_sprites = None  # 将在level中设置
		self.fish_system = FishSystem()  # 鱼类系统
		
		# 钓鱼状态机
		self.fishing_state = "idle"  # idle, casting, waiting, fish_hooked, minigame
		self.fishing_timer = 0.0
		self.fish_bite_time = 0.0  # 鱼上钩的时间
		self.bait_shake_timer = 0.0  # 鱼饵晃动计时器
		self.bait_position = None  # 鱼饵在水中的位置
		self.space_key_pressed = False  # 跟踪空格键状态，避免连续触发
		self.current_catch_target = None  # 当前钓到的目标信息

		# general setup
		self.render_ascii_player()
		
		self.rect = self.image.get_rect(center = pos)
		self.z = LAYERS['main']

		# movement attributes
		self.direction = pygame.math.Vector2()
		self.pos = pygame.math.Vector2(self.rect.center)
		self.speed = 200

		# collision - 使用TILE_SIZE统一碰撞盒尺寸
		hitbox_size = TILE_SIZE
		self.hitbox = pygame.Rect(0, 0, hitbox_size, hitbox_size)
		self.hitbox.center = self.rect.center
		self.collision_sprites = collision_sprites

		# timers 
		self.timers = {
			'tool use': Timer(350,self.use_tool),
			'tool switch': Timer(200),
			'seed use': Timer(350,self.use_seed),
			'seed switch': Timer(200),
			'fishing': Timer(2000,self.finish_fishing),  # 钓鱼需要2秒
			'log_panel': Timer(200),  # 日志面板切换冷却
			'quest_panel': Timer(200),  # 任务面板切换冷却
		}

		# tools 
		self.tools = ['hoe','axe','water']
		self.tool_index = 0
		self.selected_tool = self.tools[self.tool_index]

		# seeds 
		self.seeds = ['corn', 'tomato']
		self.seed_index = 0
		self.selected_seed = self.seeds[self.seed_index]

		# inventory
		self.item_inventory = {
			'wood':   20,
			'apple':  20,
			'corn':   20,
			'tomato': 20
		}
		# 鱼类库存 - 存储捕获的鱼的详细信息
		self.fish_inventory = []  # 每个元素是一个鱼的信息字典
		self.seed_inventory = {
		'corn': 5,
		'tomato': 5
		}
		self.money = 200

		# 任务系统
		self.active_quests = []  # 当前活跃的任务
		self.completed_quests = []  # 已完成的任务
		
		# 钓鱼大赛系统
		self.fishing_contest_stats = {
			"total_attempts": 0,          # 总钓鱼次数
			"max_fish_length": 0,         # 钓到的最长鱼长度
			"rare_fish_count": 0,         # 稀有鱼数量
			"fisherman_talked": False,    # 是否与渔夫对话过
			"farmer_talked": False,       # 是否与农民对话过
			"trader_talked": False,       # 是否与商人对话过
			"trader_sold": False,         # 是否向商人出售过
		}

		# 历史行为记录系统
		self.behavior_history = []  # 存储所有历史行为记录
		self.max_history_size = 500  # 最大历史记录数量，防止内存占用过多
		
		# 日志面板
		self.log_panel = LogPanel()
		
		# 任务面板
		self.quest_panel = quest_panel
		
		# 聊天面板引用
		self.chat_panel = chat_panel

		# interaction
		self.tree_sprites = tree_sprites
		self.interaction = interaction
		self.sleep = False
		self.soil_layer = soil_layer
		self.toggle_shop = toggle_shop
		
		

		# sound
		self.watering = None
		
		# 尝试加载音效文件
		try:
			if pygame.mixer.get_init():
				water_path = get_resource_path('assets/audio/water.mp3')
				self.watering = pygame.mixer.Sound(water_path)
				self.watering.set_volume(0.2)
		except (pygame.error, FileNotFoundError) as e:
			print(f"WARNING: Water audio loading failed: {e}")
			print("Game will run without sound effects")

	def get_current_timestamp(self):
		"""获取当前时间戳"""
		return datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

	def record_behavior(self, behavior_type, action, details=None):
		"""
		记录玩家行为
		
		Args:
			behavior_type (str): 行为类型 (fishing, dialogue, shop, quest, farming, tool_use, movement)
			action (str): 具体行为描述
			details (dict): 详细信息字典
		"""
		if details is None:
			details = {}
		
		behavior_record = {
			"timestamp": self.get_current_timestamp(),
			"type": behavior_type,
			"action": action,
			"details": details,
			"player_position": (self.rect.centerx, self.rect.centery),
			"player_money": self.money,
		}
		
		self.behavior_history.append(behavior_record)
		
		# 如果历史记录过多，删除最老的记录
		if len(self.behavior_history) > self.max_history_size:
			self.behavior_history.pop(0)
		
		# 打印记录（调试用）
		print(f"[行为记录] {behavior_record['timestamp']} - {behavior_type}: {action}")

	def record_fishing_behavior(self, fishing_action, result=None):
		"""记录钓鱼相关行为"""
		details = {
			"attempts_so_far": self.fishing_contest_stats["total_attempts"],
			"max_fish_length": self.fishing_contest_stats["max_fish_length"],
			"rare_fish_count": self.fishing_contest_stats["rare_fish_count"],
		}
		
		if result:
			details.update({
				"fish_caught": result.get('name', 'Unknown'),
				"fish_length": result.get('length', 0),
				"fish_rarity": result.get('rarity', 'common'),
				"fish_price": result.get('price', result.get('value', 0)),  # 兼容垃圾物品的value字段
				"fish_ascii": result.get('ascii_char', '?'),
				"catch_type": result.get('type', 'fish')  # 记录捕获类型
			})
		
		self.record_behavior("fishing", fishing_action, details)

	def record_dialogue_behavior(self, npc_name, npc_message, player_choice=None):
		"""记录对话行为"""
		details = {
			"npc_name": npc_name,
			"npc_message": npc_message,
			"player_choice": player_choice,
		}
		
		action = f"与{npc_name}对话"
		if player_choice:
			action += f"，选择了：{player_choice}"
		
		self.record_behavior("dialogue", action, details)

	def record_shop_behavior(self, transaction_type, item_name, quantity, price, shop_type="trader"):
		"""记录商店交易行为"""
		details = {
			"transaction_type": transaction_type,  # "buy" or "sell"
			"item_name": item_name,
			"quantity": quantity,
			"unit_price": price // quantity if quantity > 0 else 0,
			"total_price": price,
			"shop_type": shop_type,
			"money_before": self.money + (price if transaction_type == "sell" else -price),
			"money_after": self.money,
		}
		
		action = f"{'购买' if transaction_type == 'buy' else '出售'} {quantity}个 {item_name}，花费/获得 {price} 金币"
		self.record_behavior("shop", action, details)

	def record_quest_behavior(self, quest_action, quest_title, quest_details=None):
		"""记录任务相关行为"""
		details = {
			"quest_title": quest_title,
			"active_quests_count": len(self.active_quests),
			"completed_quests_count": len(self.completed_quests),
		}
		
		if quest_details:
			details.update(quest_details)
		
		self.record_behavior("quest", quest_action, details)

	def record_farming_behavior(self, farming_action, item_or_tool, position=None):
		"""记录农业相关行为"""
		details = {
			"tool_or_item": item_or_tool,
			"selected_tool": self.selected_tool,
			"selected_seed": self.selected_seed,
		}
		
		if position:
			details["target_position"] = position
		
		self.record_behavior("farming", farming_action, details)

	def record_tool_behavior(self, tool_action, tool_name, target=None):
		"""记录工具使用行为"""
		details = {
			"tool_name": tool_name,
			"tool_index": self.tool_index,
			"all_tools": self.tools.copy(),
		}
		
		if target:
			details["target"] = target
		
		self.record_behavior("tool_use", tool_action, details)

	def get_behavior_summary(self, behavior_type=None, limit=10):
		"""
		获取行为历史摘要
		
		Args:
			behavior_type (str): 筛选特定类型的行为，None表示所有类型
			limit (int): 返回最近的记录数量
		"""
		filtered_history = self.behavior_history
		
		if behavior_type:
			filtered_history = [record for record in self.behavior_history 
							  if record["type"] == behavior_type]
		
		# 返回最近的记录
		return filtered_history[-limit:] if limit else filtered_history

	def get_behavior_statistics(self):
		"""获取行为统计信息"""
		stats = {}
		for record in self.behavior_history:
			behavior_type = record["type"]
			stats[behavior_type] = stats.get(behavior_type, 0) + 1
		
		return {
			"total_behaviors": len(self.behavior_history),
			"by_type": stats,
			"session_duration": self.get_session_duration(),
		}

	def get_session_duration(self):
		"""计算游戏会话时长"""
		if not self.behavior_history:
			return "0分钟"
		
		first_record = self.behavior_history[0]["timestamp"]
		last_record = self.behavior_history[-1]["timestamp"]
		
		first_time = datetime.datetime.strptime(first_record, "%Y-%m-%d %H:%M:%S")
		last_time = datetime.datetime.strptime(last_record, "%Y-%m-%d %H:%M:%S")
		
		duration = last_time - first_time
		minutes = int(duration.total_seconds() / 60)
		
		return f"{minutes}分钟"

	def render_ascii_player(self):
		"""
		渲染ASCII玩家
		"""
		self.image.fill((0, 0, 0, 0))
		
		# 获取当前状态对应的字符
		char = self.ascii_chars.get(self.status, '@')
		color = self.ascii_renderer.color_map['player']
		
		
		# 渲染到图像中心 - 使用TILE_SIZE保持一致
		offset = TILE_SIZE // 4
		self.ascii_renderer.render_ascii(self.image, char, color, (offset, offset), TILE_SIZE // 2)

	def use_tool(self):
		if self.selected_tool == 'hoe':
			self.soil_layer.get_hit(self.target_pos)
			self.record_tool_behavior(f"使用{self.selected_tool}耕地", self.selected_tool, self.target_pos)
		
		if self.selected_tool == 'axe':
			for tree in self.tree_sprites.sprites():
				if tree.rect.collidepoint(self.target_pos):
					tree.damage()
					self.record_tool_behavior(f"使用{self.selected_tool}砍树", self.selected_tool, tree.rect.center)
		
		if self.selected_tool == 'water':
			self.soil_layer.water(self.target_pos)
			if self.watering:
				self.watering.play()
			self.record_tool_behavior(f"使用{self.selected_tool}浇水", self.selected_tool, self.target_pos)

	def get_target_pos(self):

		self.target_pos = self.rect.center + PLAYER_TOOL_OFFSET[self.status.split('_')[0]]

	def use_seed(self):
		if self.seed_inventory[self.selected_seed] > 0:
			self.soil_layer.plant_seed(self.target_pos, self.selected_seed)
			self.seed_inventory[self.selected_seed] -= 1
			self.record_farming_behavior(f"种植{self.selected_seed}种子", self.selected_seed, self.target_pos)
	
	def check_near_water(self):
		"""
		检测玩家是否在水边
		"""
		if not hasattr(self, 'water_sprites') or not self.water_sprites:
			return False
			
		# 检查玩家周围是否有水
		detection_radius = TILE_SIZE + 10  # 稍微扩大检测范围
		player_center = self.rect.center
		
		for water_sprite in self.water_sprites.sprites():
			# 计算玩家和水的距离
			water_center = water_sprite.rect.center
			distance = ((player_center[0] - water_center[0]) ** 2 + 
					   (player_center[1] - water_center[1]) ** 2) ** 0.5
			
			if distance <= detection_radius:
				return True
		return False
	
	def find_nearest_water_position(self):
		"""
		找到最近的水位置用于放置鱼饵
		"""
		if not hasattr(self, 'water_sprites') or not self.water_sprites:
			return None
		
		player_center = self.rect.center
		nearest_water = None
		min_distance = float('inf')
		
		for water_sprite in self.water_sprites.sprites():
			water_center = water_sprite.rect.center
			distance = ((player_center[0] - water_center[0]) ** 2 + 
					   (player_center[1] - water_center[1]) ** 2) ** 0.5
			
			if distance < min_distance:
				min_distance = distance
				nearest_water = water_sprite
		
		if nearest_water:
			# 返回水中心位置
			return nearest_water.rect.center
		return None
	
	def handle_fishing_input(self):
		"""
		开始钓鱼 - 投掷鱼饵
		"""
		if self.check_near_water() and self.fishing_state == "idle":
			# 找到最近的水位置放置鱼饵
			self.bait_position = self.find_nearest_water_position()
			
			# 调试信息：打印鱼饵位置
			if self.bait_position:
				print(f"🎣 鱼饵位置设置为: {self.bait_position}")
			else:
				print("❌ 鱼饵位置设置失败！")
			
			# 进入出杆状态
			self.is_fishing = True
			self.fishing_state = "casting"
			self.fishing_timer = 0.5  # 出杆动画时间0.5秒
			self.direction = pygame.math.Vector2()  # 停止移动
			print("🎣 出杆，投掷鱼饵到水中...")
			
			
			# 添加到聊天面板
			if hasattr(self, 'chat_panel') and self.chat_panel:
				self.chat_panel.add_system_message("🎣 投掷鱼饵到水中...")
		elif self.fishing_state == "waiting":
			self.cancel_fishing()
		elif self.fishing_state == "fish_hooked":
			self.try_hook_fish()
	
	def cancel_fishing(self):
		"""
		取消钓鱼 - 提前收杆
		"""
		if self.fishing_state in ["waiting"]:
			print("🎣 提前收杆，没有钓到鱼")
			if hasattr(self, 'chat_panel') and self.chat_panel:
				self.chat_panel.add_system_message("🎣 提前收杆，没有钓到鱼")
			self._reset_fishing_state()
	
	def try_hook_fish(self):
		"""
		尝试收杆 - 当鱼上钩时
		"""
		if self.fishing_state == "fish_hooked":
			# 在小游戏开始前确定钓到的目标
			self.current_catch_target = self.fish_system.catch_fish()
			
			if self.current_catch_target:
				# 转换为小游戏所需的格式
				if self.current_catch_target.get('type') == 'cat':
					catch_info = {
						'type': 'cat',
						'rarity': self.current_catch_target.get('rarity', 'common')
					}
				else:
					catch_info = {
						'type': 'fish', 
						'rarity': self.current_catch_target.get('rarity', 'common')
					}
				
				print(f"🎣 开始收杆，进入钓鱼小游戏！目标: {catch_info['type']} ({catch_info['rarity']})")
				if hasattr(self, 'chat_panel') and self.chat_panel:
					self.chat_panel.add_system_message("🎣 鱼上钩了！开始收杆...")
				
				# 启动钓鱼小游戏，传入目标信息
				self.fishing_state = "minigame"
				if hasattr(self, 'level') and self.level:
					self.level.fishing_minigame.start_game(catch_info)
				return True
			else:
				# 没有钓到任何东西，直接结束
				print("🎣 鱼跑掉了...")
				if hasattr(self, 'chat_panel') and self.chat_panel:
					self.chat_panel.add_system_message("🎣 鱼跑掉了...")
				self._reset_fishing_state()
				return False
		return False
	
	def _reset_fishing_state(self):
		"""
		重置钓鱼状态
		"""
		self.is_fishing = False
		self.fishing_state = "idle"
		self.fishing_timer = 0.0
		self.fish_bite_time = 0.0
		self.bait_shake_timer = 0.0
		self.bait_position = None  # 清除鱼饵位置
		self.current_catch_target = None  # 清除当前目标信息
	
	def update_fishing_state(self, dt):
		"""
		更新钓鱼状态机
		"""
		if not self.is_fishing:
			return
		
		if self.fishing_state == "casting":
			# 出杆阶段
			self.fishing_timer -= dt
			if self.fishing_timer <= 0:
				# 出杆完成，进入等待阶段
				self.fishing_state = "waiting"
				# 随机设置鱼上钩时间 (3-10秒)
				import random
				self.fish_bite_time = random.uniform(3.0, 10.0)
				self.fishing_timer = self.fish_bite_time
				print(f"🎣 鱼饵已投入水中，等待鱼上钩... (预计{self.fish_bite_time:.1f}秒)")
				if hasattr(self, 'chat_panel') and self.chat_panel:
					self.chat_panel.add_system_message(f"🎣 鱼饵已投入水中，等待鱼上钩...")
		
		elif self.fishing_state == "waiting":
			# 等待鱼上钩阶段
			self.fishing_timer -= dt
			if self.fishing_timer <= 0:
				# 鱼上钩了！
				self.fishing_state = "fish_hooked"
				self.bait_shake_timer = 0.0
				print("🎣 鱼饵开始晃动！鱼上钩了，快按空格键收杆！")
				if hasattr(self, 'chat_panel') and self.chat_panel:
					self.chat_panel.add_system_message("🎣 鱼饵晃动！鱼上钩了，快按空格键！")
		
		elif self.fishing_state == "fish_hooked":
			# 鱼上钩状态，等待玩家收杆
			self.bait_shake_timer += dt
			# 如果玩家10秒不操作，鱼会跑掉
			if self.bait_shake_timer > 10.0:
				print("🎣 鱼跑掉了...")
				if hasattr(self, 'chat_panel') and self.chat_panel:
					self.chat_panel.add_system_message("🎣 鱼跑掉了...")
				self._reset_fishing_state()
		
		elif self.fishing_state == "minigame":
			# 小游戏阶段，检查小游戏是否结束
			if hasattr(self, 'level') and self.level:
				if not self.level.fishing_minigame.is_active and self.level.fishing_minigame.get_result():
					self.finish_fishing()

	def finish_fishing(self):
		"""
		钓鱼结束
		"""
		if self.is_fishing:
			# 检查钓鱼小游戏结果
			minigame_result = None
			if hasattr(self, 'level') and self.level:
				minigame_result = self.level.fishing_minigame.get_result()
			
			# 如果小游戏还在进行，不结束钓鱼
			if hasattr(self, 'level') and self.level and self.level.fishing_minigame.is_active:
				return
			
			# 更新钓鱼次数
			self.fishing_contest_stats["total_attempts"] += 1
			
			# 根据小游戏结果决定是否获得已确定的目标
			caught_item = None
			if minigame_result == "success":
				# 小游戏成功，使用已确定的目标
				caught_item = self.current_catch_target
			elif minigame_result == "failure":
				# 小游戏失败，钓鱼失败
				print("钓鱼小游戏失败，没有钓到鱼...")
				caught_item = None
			else:
				# 没有小游戏结果（可能是旧的钓鱼方式），使用已确定的目标
				caught_item = self.current_catch_target
			
			# 重置小游戏结果
			if hasattr(self, 'level') and self.level:
				self.level.fishing_minigame.reset_result()
			
			if caught_item:
				if caught_item.get('type') == 'cat':
					# 钓到猫咪了！
					print(f"🎣✨ 奇迹发生了！你钓到了一只 {caught_item['name']}！")
					print(f"   {caught_item['ascii_char']} - {caught_item['personality']}")
					print(f"   稀有度: {caught_item['rarity_name']}")
					
					# 添加到聊天面板
					if hasattr(self, 'chat_panel') and self.chat_panel:
						self.chat_panel.add_system_message(f"🎣✨ 钓到了一只{caught_item['rarity_name']}猫咪: {caught_item['name']}！")
						self.chat_panel.add_system_message(f"🐱 {caught_item['personality']}")
					
					
					# 添加猫咪到游戏世界
					if hasattr(self, 'level') and self.level:
						new_cat = self.level.cat_manager.add_new_cat_from_fishing(self.rect.center)
						if new_cat:
							# 为新猫咪设置特殊属性
							new_cat.cat_name = caught_item['name']
							new_cat.cat_personality = caught_item['personality']
							new_cat.char_color = caught_item['color']
							print(f"🐱 {caught_item['name']} 已经加入你的农场！")
							
							# 添加成功消息
							if hasattr(self, 'chat_panel') and self.chat_panel:
								self.chat_panel.add_system_message(f"🏠 {caught_item['name']} 已经在农场安家了！")
						else:
							print("❌ 猫咪添加失败")
							if hasattr(self, 'chat_panel') and self.chat_panel:
								self.chat_panel.add_system_message("❌ 猫咪添加失败")
					else:
						print("⚠️ 无法访问游戏世界，猫咪添加失败")
					
					# 显示猫咪鱼获面板
					if hasattr(self, 'level') and self.level:
						self.level.catch_result_panel.show_catch_result(caught_item)
					
				elif caught_item.get('type') == 'trash':
					# 钓到垃圾物品了
					display_name = self.fish_system.get_fish_display_name(caught_item)
					
					# 根据物品类型显示不同的信息
					if caught_item['category'] == 'treasure':
						print(f"💎 太幸运了！钓到了 {display_name}！")
						if hasattr(self, 'chat_panel') and self.chat_panel:
							self.chat_panel.add_system_message(f"💎 太幸运了！钓到了{display_name}！")
							self.chat_panel.add_system_message(f"💰 价值: {caught_item['value']}金币")
					elif caught_item['category'] == 'natural':
						print(f"🌿 钓到了 {display_name}")
						if hasattr(self, 'chat_panel') and self.chat_panel:
							self.chat_panel.add_system_message(f"🌿 钓到了{display_name}")
							if caught_item['value'] > 0:
								self.chat_panel.add_system_message(f"💰 价值: {caught_item['value']}金币")
					else:
						print(f"🗑️ 钓到了 {display_name}...")
						if hasattr(self, 'chat_panel') and self.chat_panel:
							self.chat_panel.add_system_message(f"🗑️ 钓到了{display_name}...")
							if caught_item['value'] < 0:
								self.chat_panel.add_system_message(f"💸 处理成本: {abs(caught_item['value'])}金币")
					
					# 显示ASCII图案
					print(f"   {caught_item['ascii_char']}")
					
					# 直接影响金钱（不存储在库存中）
					self.money += caught_item['value']
					
					# 显示详细描述
					print(f"   {caught_item['description']}")
					if hasattr(self, 'chat_panel') and self.chat_panel:
						self.chat_panel.add_system_message(f"📝 {caught_item['description']}")
					
					# 显示物品鱼获面板
					if hasattr(self, 'level') and self.level:
						self.level.catch_result_panel.show_catch_result(caught_item)
					
				else:
					# 钓到鱼了
					self.fish_inventory.append(caught_item)
					display_name = self.fish_system.get_fish_display_name(caught_item)
					
					# 随机生成鱼的长度（基于鱼的类型和品质）
					base_length = {
						'carp': 25, 'salmon': 35, 'trout': 20, 'bass': 30,
						'minnow': 10, 'pike': 45, 'swordfish': 75, 'golden_carp': 60
					}.get(caught_item['id'], 25)
					
					# 根据品质调整长度
					quality_modifier = {
						'common': 1.0, 'uncommon': 1.2, 'rare': 1.5, 'epic': 2.0, 'legendary': 3.0
					}.get(caught_item['rarity'], 1.0)
					
					import random
					fish_length = int(base_length * quality_modifier * random.uniform(0.8, 1.3))
					caught_item['length'] = fish_length
					
					# 更新钓鱼大赛统计
					if fish_length > self.fishing_contest_stats["max_fish_length"]:
						self.fishing_contest_stats["max_fish_length"] = fish_length
						print(f"[钓鱼大赛] 新纪录！钓到了{fish_length}cm长的鱼！")
					
					if caught_item['rarity'] in ['rare', 'epic', 'legendary']:
						self.fishing_contest_stats["rare_fish_count"] += 1
					
					print(f"钓到了 {display_name}（{fish_length}cm）！售价: {caught_item['price']}金币")
					
					# 显示ASCII鱼类图案
					print(f"   {caught_item['ascii_char']}")
					
					# 显示鱼类描述
					print(f"   {caught_item['description']}")
					
					# 记录钓鱼成功行为
					if hasattr(self, 'chat_panel') and self.chat_panel:
						self.chat_panel.add_system_message(f"钓到了{display_name}")
						self.chat_panel.add_system_message(f"📏 长度: {fish_length}cm")
						self.chat_panel.add_system_message(f"💰 价值: {caught_item['price']}金币")
						self.chat_panel.add_system_message(f"📝 {caught_item['description']}")
					
					# 显示鱼类鱼获面板
					if hasattr(self, 'level') and self.level:
						self.level.catch_result_panel.show_catch_result(caught_item)
				
				# 检查任务进度
				self.check_quest_progress()
			else:
				print("没有钓到鱼...")
				if hasattr(self, 'chat_panel') and self.chat_panel:
					self.chat_panel.add_system_message("没有钓到鱼...")
			
			# 重置钓鱼状态
			self._reset_fishing_state()
	
	def get_total_fish_count(self):
		"""
		获取鱼类库存总数
		"""
		return len(self.fish_inventory)
	
	def get_total_fish_value(self):
		"""
		获取鱼类库存总价值
		"""
		return sum(fish['price'] for fish in self.fish_inventory)
	
	def sell_all_fish(self):
		"""
		出售所有鱼类
		"""
		total_value = self.get_total_fish_value()
		fish_count = self.get_total_fish_count()
		
		if fish_count > 0:
			# 记录出售行为（在金钱更新前）
			fish_details = [f"{fish.get('name', 'Unknown')}({fish.get('length', 0)}cm)" for fish in self.fish_inventory]
			self.record_shop_behavior("sell", f"鱼类组合包含{fish_details}", fish_count, total_value)
			
			self.money += total_value
			self.fish_inventory.clear()
			print(f"出售了 {fish_count} 条鱼，获得 {total_value} 金币")
			return total_value
		return 0

	def add_quest(self, quest):
		"""添加任务"""
		if quest not in self.active_quests:
			quest.is_active = True
			self.active_quests.append(quest)
			print(f"[任务系统] 接受新任务: {quest.title}")
			
			# 记录接受任务行为
			quest_details = {
				"quest_id": getattr(quest, 'quest_id', 'unknown'),
				"objectives": getattr(quest, 'objectives', {}),
				"rewards": getattr(quest, 'rewards', {}),
			}
			self.record_quest_behavior(f"接受任务: {quest.title}", quest.title, quest_details)
	
	def complete_quest(self, quest_id):
		"""完成任务"""
		for quest in self.active_quests:
			if quest.quest_id == quest_id:
				quest.is_completed = True
				quest.is_active = False
				self.active_quests.remove(quest)
				self.completed_quests.append(quest)
				
				# 记录完成任务行为（在奖励发放前）
				quest_details = {
					"quest_id": quest_id,
					"rewards_received": quest.rewards.copy(),
					"completion_time": self.get_current_timestamp(),
				}
				self.record_quest_behavior(f"完成任务: {quest.title}", quest.title, quest_details)
				
				# 发放奖励
				if 'money' in quest.rewards:
					self.money += quest.rewards['money']
				if 'items' in quest.rewards:
					for item, count in quest.rewards['items'].items():
						if item in self.item_inventory:
							self.item_inventory[item] += count
						elif item in self.seed_inventory:
							self.seed_inventory[item] += count
				
				print(f"[任务系统] 完成任务: {quest.title}")
				return True
		return False
	
	def check_quest_progress(self):
		"""检查任务进度"""
		for quest in self.active_quests:
			if not quest.is_completed:
				# 检查任务目标
				all_completed = True
				for objective_type, params in quest.objectives.items():
					if objective_type == "fishing_attempts":
						# 钓鱼次数
						required_num = params.get("num", 1)
						if self.fishing_contest_stats["total_attempts"] < required_num:
							all_completed = False
					
					elif objective_type == "catch_fish":
						# 钓鱼相关任务（长度、稀有度等）
						minimum_length = params.get("minimum_length", 0)
						minimum_rarity = params.get("minimum_rarity", None)
						required_num = 1
						
						current_count = 0
						
						# 检查长度要求
						if minimum_length > 0:
							if self.fishing_contest_stats["max_fish_length"] >= minimum_length:
								current_count += 1
						
						# 检查稀有度要求
						elif minimum_rarity:
							rarity_levels = {"common": 1, "uncommon": 2, "rare": 3, "epic": 4, "legendary": 5}
							min_level = rarity_levels.get(minimum_rarity, 1)
							
							# 计算满足稀有度要求的鱼数量
							for fish in self.fish_inventory:
								fish_rarity_level = rarity_levels.get(fish.get("rarity", "common"), 1)
								if fish_rarity_level >= min_level:
									current_count += 1
							
							# 还要检查历史统计
							if minimum_rarity == "rare" and self.fishing_contest_stats["rare_fish_count"] > 0:
								current_count = max(current_count, self.fishing_contest_stats["rare_fish_count"])
						
						if current_count < required_num:
							all_completed = False
					
					elif objective_type == "talk_to_npc":
						# 与NPC对话
						target = params.get("target", "")
						
						if target == "fisherman":
							if not self.fishing_contest_stats["fisherman_talked"]:
								all_completed = False
						# 可以在这里添加更多NPC对话检查
						elif target == "trader":
							if not self.fishing_contest_stats["trader_talked"]:
								all_completed = False
						elif target == "farmer":
							if not self.fishing_contest_stats["farmer_talked"]:
								all_completed = False
					elif objective_type == "sell_fish":
						# 出售鱼类
						fish_type = params.get("fish_type", "all")
						
						if fish_type == "all":
							if not self.fishing_contest_stats["trader_sold"]:
								all_completed = False
						# 可以在这里添加特定鱼类出售检查
				
				if all_completed:
					self.complete_quest(quest.quest_id)
	
	def get_current_quest_info(self):
		"""获取当前任务信息用于显示"""
		if not self.active_quests:
			return None
		
		quest = self.active_quests[0]  # 显示第一个活跃任务
		progress_info = []
		
		for objective_type, params in quest.objectives.items():
			if objective_type == "fishing_attempts":
				required_num = params.get("num", 1)
				current = self.fishing_contest_stats["total_attempts"]
				progress_info.append(f"钓鱼次数: {current}/{required_num}")
			
			elif objective_type == "catch_fish":
				minimum_length = params.get("minimum_length", 0)
				minimum_rarity = params.get("minimum_rarity", None)
				
				if minimum_length > 0:
					current = self.fishing_contest_stats["max_fish_length"]
					progress_info.append(f"最大鱼长度: {current}cm/{minimum_length}cm")
				elif minimum_rarity:
					# 计算满足稀有度要求的鱼数量
					rarity_levels = {"common": 1, "uncommon": 2, "rare": 3, "epic": 4, "legendary": 5}
					min_level = rarity_levels.get(minimum_rarity, 3)
					current_count = 0
					
					for fish in self.fish_inventory:
						fish_rarity_level = rarity_levels.get(fish.get("rarity", "common"), 1)
						if fish_rarity_level >= min_level:
							current_count += 1
					
					# 检查历史统计
					if minimum_rarity == "rare":
						current_count = max(current_count, self.fishing_contest_stats["rare_fish_count"])
					
					progress_info.append(f"稀有鱼({minimum_rarity}+): {current_count}/{required_num}")
			
			elif objective_type == "talk_to_npc":
				target = params.get("target", "")
				if target == "fisherman":
					status = "已完成" if self.fishing_contest_stats["fisherman_talked"] else "未完成"
					progress_info.append(f"与渔夫对话: {status}")
				# 可以添加更多NPC
			
			elif objective_type == "sell_fish":
				fish_type = params.get("fish_type", "all")
				# if fish_type == "all":
				status = "已完成" if self.fishing_contest_stats["trader_sold"] else "未完成"
				progress_info.append(f"向商人出售鱼类: {status}")
				# 可以添加特定鱼类出售
		
		return {
			'title': quest.title,
			'description': quest.description,
			'progress': progress_info
		}

	def animate(self,dt):
		self.render_ascii_player()
		

	def input(self):
		keys = pygame.key.get_pressed()

		# 处理日志面板输入（优先级高，即使在其他状态下也能操作）
		self.handle_log_panel_input(keys)
		
		# 如果聊天面板的输入框是激活状态，禁用所有玩家输入
		if self.chat_panel and self.chat_panel.is_input_focused():
			return

		# 钓鱼功能 - 在任何状态下都能处理空格键
		if keys[pygame.K_SPACE] and not self.space_key_pressed:
			self.space_key_pressed = True
			self.handle_fishing_input()
		elif not keys[pygame.K_SPACE]:
			self.space_key_pressed = False

		if not self.timers['tool use'].active and not self.sleep and not self.is_fishing:
			# directions 
			if keys[pygame.K_UP]:
				self.direction.y = -1
				self.status = 'up'
			elif keys[pygame.K_DOWN]:
				self.direction.y = 1
				self.status = 'down'
			else:
				self.direction.y = 0

			if keys[pygame.K_RIGHT]:
				self.direction.x = 1
				self.status = 'right'
			elif keys[pygame.K_LEFT]:
				self.direction.x = -1
				self.status = 'left'
			else:
				self.direction.x = 0

			# tool use (改为使用其他键，比如F键)
			if keys[pygame.K_f]:
				self.timers['tool use'].activate()
				self.direction = pygame.math.Vector2()
				self.frame_index = 0

			

			# seed use
			if keys[pygame.K_LCTRL]:
				self.timers['seed use'].activate()
				self.direction = pygame.math.Vector2()
				self.frame_index = 0

			# change seed 
			if keys[pygame.K_e] and not self.timers['seed switch'].active:
				self.timers['seed switch'].activate()
				old_seed = self.selected_seed
				self.seed_index += 1
				self.seed_index = self.seed_index if self.seed_index < len(self.seeds) else 0
				self.selected_seed = self.seeds[self.seed_index]
				
				# 记录种子切换行为
				self.record_behavior("seed_switch", f"从{old_seed}种子切换到{self.selected_seed}种子", {
					"old_seed": old_seed,
					"new_seed": self.selected_seed,
					"seed_index": self.seed_index,
					"seed_inventory": self.seed_inventory.copy()
				})

			# 日志面板切换
			if keys[pygame.K_l] and not self.timers['log_panel'].active:
				self.timers['log_panel'].activate()
				self.log_panel.toggle()

			# 任务面板切换
			if keys[pygame.K_q] and not self.timers['quest_panel'].active and self.quest_panel:
				self.timers['quest_panel'].activate()
				self.quest_panel.toggle()

			if keys[pygame.K_RETURN]:
				collided_interaction_sprite = pygame.sprite.spritecollide(self,self.interaction,False)
				if collided_interaction_sprite:
					if collided_interaction_sprite[0].name == 'Trader':
						self.toggle_shop()
						# 记录进入商店行为
						self.record_dialogue_behavior("商人", "欢迎来到我的商店！", "选择进入商店")
					else:
						self.status = 'left_idle'
						self.sleep = True
						# 记录睡觉行为
						self.record_behavior("sleep", "进入睡眠状态", {"sleep_position": (self.rect.centerx, self.rect.centery)})

	def get_status(self):
		
		# 钓鱼状态优先
		if self.is_fishing:
			self.status = self.status.split('_')[0] + '_fishing'
		
		# idle
		elif self.direction.magnitude() == 0:
			self.status = self.status.split('_')[0] + '_idle'

		# tool use
		elif self.timers['tool use'].active:
			self.status = self.status.split('_')[0] + '_' + self.selected_tool

	def update_timers(self):
		for timer in self.timers.values():
			timer.update()

	def collision(self, direction):
		for sprite in self.collision_sprites.sprites():
			if hasattr(sprite, 'hitbox'):
				if sprite.hitbox.colliderect(self.hitbox):
					if direction == 'horizontal':
						if self.direction.x > 0: # moving right
							self.hitbox.right = sprite.hitbox.left
						if self.direction.x < 0: # moving left
							self.hitbox.left = sprite.hitbox.right
						self.rect.centerx = self.hitbox.centerx
						self.pos.x = self.hitbox.centerx

					if direction == 'vertical':
						if self.direction.y > 0: # moving down
							self.hitbox.bottom = sprite.hitbox.top
						if self.direction.y < 0: # moving up
							self.hitbox.top = sprite.hitbox.bottom
						self.rect.centery = self.hitbox.centery
						self.pos.y = self.hitbox.centery

	def move(self,dt):

		# normalizing a vector 
		if self.direction.magnitude() > 0:
			self.direction = self.direction.normalize()

		# horizontal movement
		self.pos.x += self.direction.x * self.speed * dt
		self.hitbox.centerx = round(self.pos.x)
		self.rect.centerx = self.hitbox.centerx
		self.collision('horizontal')

		# vertical movement
		self.pos.y += self.direction.y * self.speed * dt
		self.hitbox.centery = round(self.pos.y)
		self.rect.centery = self.hitbox.centery
		self.collision('vertical')

	def update(self, dt):
		self.input()
		self.get_status()
		self.update_timers()
		
		# 更新钓鱼状态机
		self.update_fishing_state(dt)
		
		# 检查钓鱼小游戏状态
		if self.is_fishing and hasattr(self, 'level') and self.level:
			# 如果小游戏结束了，触发finish_fishing
			if not self.level.fishing_minigame.is_active and self.level.fishing_minigame.get_result():
				self.finish_fishing()
		
		self.get_target_pos()

		self.move(dt)
		self.animate(dt)

	def update_fisherman_talked(self):
		"""标记已与渔夫对话"""
		if not self.fishing_contest_stats["fisherman_talked"]:
			self.fishing_contest_stats["fisherman_talked"] = True
			print("[钓鱼大赛] 已与渔夫对话，学习了钓鱼技巧！")
			
			# 记录与渔夫对话行为
			self.record_dialogue_behavior("渔夫", "教授钓鱼技巧，分享钓鱼经验", "学习钓鱼知识")
			
			self.check_quest_progress()
	
	def update_trader_sold(self):
		"""标记已向商人出售鱼类"""
		if not self.fishing_contest_stats["trader_sold"]:
			self.fishing_contest_stats["trader_sold"] = True
			print("[钓鱼大赛] 已向商人出售鱼类，体验了完整的钓鱼产业链！")
			
			# 记录与商人交易行为
			self.record_dialogue_behavior("商人", "感谢您的鱼类，这些品质很好！", "完成鱼类交易")
			
			self.check_quest_progress()
	
	def get_fishing_contest_status(self):
		"""获取钓鱼大赛状态信息"""
		stats = self.fishing_contest_stats
		return f"钓鱼大赛状态 - 次数: {stats['total_attempts']}/10, 最长: {stats['max_fish_length']}cm, 稀有鱼: {stats['rare_fish_count']}"

	def print_behavior_history(self, behavior_type=None, limit=20):
		"""
		打印玩家行为历史
		
		Args:
			behavior_type (str): 筛选特定类型的行为，None表示所有类型
			limit (int): 显示最近的记录数量
		"""
		history = self.get_behavior_summary(behavior_type, limit)
		
		print(f"\n=== 玩家行为历史 ===")
		if behavior_type:
			print(f"类型筛选: {behavior_type}")
		print(f"显示最近 {len(history)} 条记录:")
		print("-" * 60)
		
		for i, record in enumerate(history, 1):
			print(f"{i:2d}. [{record['timestamp']}] {record['type']}: {record['action']}")
			if record['details']:
				# 显示一些关键细节
				key_details = []
				details = record['details']
				
				if 'fish_caught' in details:
					key_details.append(f"鱼类: {details['fish_caught']}({details.get('fish_length', 0)}cm)")
				if 'npc_name' in details:
					key_details.append(f"NPC: {details['npc_name']}")
				if 'total_price' in details:
					key_details.append(f"金额: {details['total_price']}")
				if 'quest_title' in details:
					key_details.append(f"任务: {details['quest_title']}")
				
				if key_details:
					print(f"     详情: {', '.join(key_details)}")
		
		print("-" * 60)
		print(f"总行为数: {len(self.behavior_history)}")
		
		# 显示统计信息
		stats = self.get_behavior_statistics()
		print(f"游戏时长: {stats['session_duration']}")
		print("行为分布:", end=" ")
		for behavior_type, count in stats['by_type'].items():
			print(f"{behavior_type}({count})", end=" ")
		print()
		print("=" * 60)

	def export_behavior_history(self):
		"""
		导出行为历史为字典格式，便于保存或分析
		"""
		return {
			"player_name": "Player",
			"export_time": self.get_current_timestamp(),
			"total_behaviors": len(self.behavior_history),
			"session_stats": self.get_behavior_statistics(),
			"behavior_history": self.behavior_history.copy(),
			"player_status": {
				"money": self.money,
				"position": (self.rect.centerx, self.rect.centery),
				"fish_inventory_count": len(self.fish_inventory),
				"active_quests_count": len(self.active_quests),
				"completed_quests_count": len(self.completed_quests),
				"fishing_stats": self.fishing_contest_stats.copy(),
			}
		}

	def handle_log_panel_input(self, keys):
		"""处理日志面板输入"""
		self.log_panel.handle_input(keys)

	def render_log_panel(self, surface):
		"""渲染日志面板"""
		self.log_panel.render(surface, self)
