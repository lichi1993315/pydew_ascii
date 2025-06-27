import pygame
from settings import *
from support import *
from timer import Timer
from fish_system import FishSystem

class Player(pygame.sprite.Sprite):
	def __init__(self, pos, group, collision_sprites, tree_sprites, interaction, soil_layer, toggle_shop, ascii_mode=False):
		super().__init__(group)

		# ASCII模式设置
		
		from ascii_renderer import ASCIIRenderer
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
			"trader_sold": False,         # 是否向商人出售过
		}

		# interaction
		self.tree_sprites = tree_sprites
		self.interaction = interaction
		self.sleep = False
		self.soil_layer = soil_layer
		self.toggle_shop = toggle_shop
		
		

		# sound
		self.watering = pygame.mixer.Sound('../audio/water.mp3')
		self.watering.set_volume(0.2)

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
		
		if self.selected_tool == 'axe':
			for tree in self.tree_sprites.sprites():
				if tree.rect.collidepoint(self.target_pos):
					tree.damage()
		
		if self.selected_tool == 'water':
			self.soil_layer.water(self.target_pos)
			self.watering.play()

	def get_target_pos(self):

		self.target_pos = self.rect.center + PLAYER_TOOL_OFFSET[self.status.split('_')[0]]

	def use_seed(self):
		if self.seed_inventory[self.selected_seed] > 0:
			self.soil_layer.plant_seed(self.target_pos, self.selected_seed)
			self.seed_inventory[self.selected_seed] -= 1
	
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
	
	def start_fishing(self):
		"""
		开始钓鱼
		"""
		if self.check_near_water() and not self.is_fishing:
			self.is_fishing = True
			self.timers['fishing'].activate()
			self.direction = pygame.math.Vector2()  # 停止移动
			print("开始钓鱼...")
	
	def finish_fishing(self):
		"""
		钓鱼结束
		"""
		if self.is_fishing:
			# 更新钓鱼次数
			self.fishing_contest_stats["total_attempts"] += 1
			
			# 尝试钓鱼
			caught_fish = self.fish_system.catch_fish()
			
			if caught_fish:
				# 钓到鱼了
				self.fish_inventory.append(caught_fish)
				display_name = self.fish_system.get_fish_display_name(caught_fish)
				
				# 随机生成鱼的长度（基于鱼的类型和品质）
				base_length = {
					'carp': 25, 'salmon': 35, 'trout': 20, 'bass': 30,
					'minnow': 10, 'pike': 45, 'swordfish': 75, 'golden_carp': 60
				}.get(caught_fish['id'], 25)
				
				# 根据品质调整长度
				quality_modifier = {
					'common': 1.0, 'uncommon': 1.2, 'rare': 1.5, 'epic': 2.0, 'legendary': 3.0
				}.get(caught_fish['rarity'], 1.0)
				
				import random
				fish_length = int(base_length * quality_modifier * random.uniform(0.8, 1.3))
				caught_fish['length'] = fish_length
				
				# 更新钓鱼大赛统计
				if fish_length > self.fishing_contest_stats["max_fish_length"]:
					self.fishing_contest_stats["max_fish_length"] = fish_length
					print(f"[钓鱼大赛] 新纪录！钓到了{fish_length}cm长的鱼！")
				
				if caught_fish['rarity'] in ['rare', 'epic', 'legendary']:
					self.fishing_contest_stats["rare_fish_count"] += 1
				
				print(f"钓到了 {display_name}（{fish_length}cm）！售价: {caught_fish['price']}金币")
				
				# 显示ASCII鱼类图案
				print(f"   {caught_fish['ascii_char']}")
				
				# 检查任务进度
				self.check_quest_progress()
			else:
				print("没有钓到鱼...")
			
			self.is_fishing = False
	
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
	
	def complete_quest(self, quest_id):
		"""完成任务"""
		for quest in self.active_quests:
			if quest.quest_id == quest_id:
				quest.is_completed = True
				quest.is_active = False
				self.active_quests.remove(quest)
				self.completed_quests.append(quest)
				
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
				for objective, target in quest.objectives.items():
					if objective == "fishing_attempts":
						# 钓鱼次数
						if self.fishing_contest_stats["total_attempts"] < target:
							all_completed = False
					elif objective == "catch_big_fish":
						# 钓到大鱼（指定长度以上）
						if self.fishing_contest_stats["max_fish_length"] < target:
							all_completed = False
					elif objective == "catch_champion_fish":
						# 钓到冠军级别的鱼
						if self.fishing_contest_stats["max_fish_length"] < target:
							all_completed = False
					elif objective == "catch_rare_fish":
						# 钓到稀有鱼
						if self.fishing_contest_stats["rare_fish_count"] < target:
							all_completed = False
					elif objective == "talk_to_fisherman":
						# 与渔夫对话
						if not self.fishing_contest_stats["fisherman_talked"]:
							all_completed = False
					elif objective == "sell_fish":
						# 向商人出售鱼类
						if not self.fishing_contest_stats["trader_sold"]:
							all_completed = False
				
				if all_completed:
					self.complete_quest(quest.quest_id)
	
	def get_current_quest_info(self):
		"""获取当前任务信息用于显示"""
		if not self.active_quests:
			return None
		
		quest = self.active_quests[0]  # 显示第一个活跃任务
		progress_info = []
		
		for objective, target in quest.objectives.items():
			if objective == "fishing_attempts":
				current = self.fishing_contest_stats["total_attempts"]
				progress_info.append(f"钓鱼次数: {current}/{target}")
			elif objective == "catch_big_fish":
				current = self.fishing_contest_stats["max_fish_length"]
				progress_info.append(f"最大鱼长度: {current}cm/{target}cm")
			elif objective == "catch_champion_fish":
				current = self.fishing_contest_stats["max_fish_length"]
				progress_info.append(f"冠军鱼长度: {current}cm/{target}cm")
			elif objective == "catch_rare_fish":
				current = self.fishing_contest_stats["rare_fish_count"]
				progress_info.append(f"稀有鱼: {current}/{target}")
			elif objective == "talk_to_fisherman":
				status = "已完成" if self.fishing_contest_stats["fisherman_talked"] else "未完成"
				progress_info.append(f"与渔夫对话: {status}")
			elif objective == "sell_fish":
				status = "已完成" if self.fishing_contest_stats["trader_sold"] else "未完成"
				progress_info.append(f"向商人出售鱼类: {status}")
		
		return {
			'title': quest.title,
			'description': quest.description,
			'progress': progress_info
		}

	def animate(self,dt):
		self.render_ascii_player()
		

	def input(self):
		keys = pygame.key.get_pressed()

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

			# 钓鱼功能 (替换原来的工具使用)
			if keys[pygame.K_SPACE]:
				self.start_fishing()

			# tool use (改为使用其他键，比如F键)
			if keys[pygame.K_f]:
				self.timers['tool use'].activate()
				self.direction = pygame.math.Vector2()
				self.frame_index = 0

			# change tool
			if keys[pygame.K_q] and not self.timers['tool switch'].active:
				self.timers['tool switch'].activate()
				self.tool_index += 1
				self.tool_index = self.tool_index if self.tool_index < len(self.tools) else 0
				self.selected_tool = self.tools[self.tool_index]

			# seed use
			if keys[pygame.K_LCTRL]:
				self.timers['seed use'].activate()
				self.direction = pygame.math.Vector2()
				self.frame_index = 0

			# change seed 
			if keys[pygame.K_e] and not self.timers['seed switch'].active:
				self.timers['seed switch'].activate()
				self.seed_index += 1
				self.seed_index = self.seed_index if self.seed_index < len(self.seeds) else 0
				self.selected_seed = self.seeds[self.seed_index]

			if keys[pygame.K_RETURN]:
				collided_interaction_sprite = pygame.sprite.spritecollide(self,self.interaction,False)
				if collided_interaction_sprite:
					if collided_interaction_sprite[0].name == 'Trader':
						self.toggle_shop()
					else:
						self.status = 'left_idle'
						self.sleep = True

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
		self.get_target_pos()

		self.move(dt)
		self.animate(dt)

	def update_fisherman_talked(self):
		"""标记已与渔夫对话"""
		if not self.fishing_contest_stats["fisherman_talked"]:
			self.fishing_contest_stats["fisherman_talked"] = True
			print("[钓鱼大赛] 已与渔夫对话，学习了钓鱼技巧！")
			self.check_quest_progress()
	
	def update_trader_sold(self):
		"""标记已向商人出售鱼类"""
		if not self.fishing_contest_stats["trader_sold"]:
			self.fishing_contest_stats["trader_sold"] = True
			print("[钓鱼大赛] 已向商人出售鱼类，体验了完整的钓鱼产业链！")
			self.check_quest_progress()
	
	def get_fishing_contest_status(self):
		"""获取钓鱼大赛状态信息"""
		stats = self.fishing_contest_stats
		return f"钓鱼大赛状态 - 次数: {stats['total_attempts']}/10, 最长: {stats['max_fish_length']}cm, 稀有鱼: {stats['rare_fish_count']}"
