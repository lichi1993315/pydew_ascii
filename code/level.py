import pygame 
from settings import *
from player import Player
from overlay import Overlay
from ascii_sprites import ASCIIGeneric, ASCIIWater, ASCIIWildFlower, ASCIITree, ASCIIInteraction, ASCIIParticle, ASCIINPC
from pytmx.util_pygame import load_pygame
from support import *
from transition import Transition
from ascii_soil import ASCIISoilLayer
from sky import Rain, Sky
from random import randint
from menu import Menu
from npc_system import NPCManager
from dialogue_ui import DialogueUI
from quest_panel import QuestPanel  # 添加任务面板导入

class Level:
	"""
	游戏关卡类 - 管理整个游戏世界的主要逻辑
	包括地图加载、精灵管理、天气系统、商店系统等
	完全使用ASCII模式渲染
	"""
	def __init__(self):
		# 获取显示表面
		self.display_surface = pygame.display.get_surface()

		# 精灵组管理
		self.all_sprites = CameraGroup()
		self.collision_sprites = pygame.sprite.Group()
		self.tree_sprites = pygame.sprite.Group()
		self.interaction_sprites = pygame.sprite.Group()
		self.water_sprites = pygame.sprite.Group()  # 水精灵组，用于钓鱼功能
		self.npc_sprites = pygame.sprite.Group()  # NPC精灵组

		# 土壤层系统 - 使用ASCII版本
		self.soil_layer = ASCIISoilLayer(self.all_sprites, self.collision_sprites)
		
		# NPC系统 - 需要在setup之前初始化，因为setup中会用到
		self.npc_manager = NPCManager()  # NPC管理器
		self.dialogue_ui = DialogueUI((SCREEN_WIDTH, SCREEN_HEIGHT))
		self.current_interacting_npc = None
		
		# 任务面板
		self.quest_panel = QuestPanel()
		
		self.setup()
		self.overlay = Overlay(self.player)
		self.transition = Transition(self.reset, self.player)

		# 天气系统
		self.rain = Rain(self.all_sprites)
		self.raining = randint(0,10) > 7  # 随机决定是否下雨
		self.soil_layer.raining = self.raining
		self.sky = Sky()  # 天空效果

		# 商店系统
		self.menu = Menu(self.player, self.toggle_shop)  # 商店菜单
		self.shop_active = False  # 商店是否激活

		# 音频系统
		self.success = pygame.mixer.Sound('../audio/success.wav')  # 成功音效
		self.success.set_volume(0.3)
		self.music = pygame.mixer.Sound('../audio/music.mp3')  # 背景音乐
		self.music.play(loops = -1)  # 循环播放

	def setup(self):
		"""
		设置游戏地图和所有精灵
		从TMX文件加载地图数据并创建相应的游戏对象
		全部使用ASCII模式渲染
		"""
		tmx_data = load_pygame('../data/map.tmx')  # 加载TMX地图文件

		# 房屋地板和家具（底层）
		for layer in ['HouseFloor', 'HouseFurnitureBottom']:
			for x, y, surf in tmx_data.get_layer_by_name(layer).tiles():
				ASCIIGeneric((x * TILE_SIZE,y * TILE_SIZE), 'floor', self.all_sprites, LAYERS['house bottom'])

		# 房屋墙壁和家具（顶层） - 添加到碰撞精灵组
		for layer in ['HouseWalls', 'HouseFurnitureTop']:
			for x, y, surf in tmx_data.get_layer_by_name(layer).tiles():
				ASCIIGeneric((x * TILE_SIZE,y * TILE_SIZE), 'wall', [self.all_sprites, self.collision_sprites])

		# 栅栏
		for x, y, surf in tmx_data.get_layer_by_name('Fence').tiles():
			ASCIIGeneric((x * TILE_SIZE,y * TILE_SIZE), 'fence', [self.all_sprites, self.collision_sprites])

		# 水效果
		for x, y, surf in tmx_data.get_layer_by_name('Water').tiles():
			ASCIIWater((x * TILE_SIZE,y * TILE_SIZE), [self.all_sprites, self.water_sprites])

		# 树木
		for obj in tmx_data.get_layer_by_name('Trees'):
			ASCIITree(
				pos = (obj.x, obj.y), 
				groups = [self.all_sprites, self.collision_sprites, self.tree_sprites], 
				name = obj.name,
				player_add = self.player_add)

		# 野花装饰
		for obj in tmx_data.get_layer_by_name('Decoration'):
			ASCIIWildFlower((obj.x, obj.y), [self.all_sprites, self.collision_sprites])

		# 碰撞瓦片
		for x, y, surf in tmx_data.get_layer_by_name('Collision').tiles():
			ASCIIGeneric((x * TILE_SIZE, y * TILE_SIZE), 'stone', self.collision_sprites)

		# 玩家和交互对象
		for obj in tmx_data.get_layer_by_name('Player'):
			if obj.name == 'Start':  # 玩家起始位置
				self.player = Player(
					pos = (obj.x,obj.y), 
					group = self.all_sprites, 
					collision_sprites = self.collision_sprites,
					tree_sprites = self.tree_sprites,
					interaction = self.interaction_sprites,
					soil_layer = self.soil_layer,
					toggle_shop = self.toggle_shop,
					ascii_mode = True)
				
				# 设置水精灵组，用于钓鱼功能
				self.player.water_sprites = self.water_sprites
			
			if obj.name == 'Bed':  # 床（睡觉交互）
				ASCIIInteraction((obj.x,obj.y), (obj.width,obj.height), self.interaction_sprites, obj.name)

			if obj.name == 'Trader':  # 商人（商店交互）
				ASCIIInteraction((obj.x,obj.y), (obj.width,obj.height), self.interaction_sprites, obj.name)

		# 地面背景
		ASCIIGeneric(
			pos = (0,0),
			tile_type = 'grass',
			groups = self.all_sprites,
			z = LAYERS['ground'])
		
		# 创建NPC精灵
		self.create_npcs()

	def create_npcs(self):
		"""创建NPC精灵"""
		# 商人NPC（在商店区域附近）
		trader_npc = ASCIINPC(
			pos=(1344, 1088),  # 商人位置 - 在房子外面
			npc_id="trader_zhang",
			npc_manager=self.npc_manager,
			groups=[self.all_sprites, self.npc_sprites, self.collision_sprites]
		)
		
		# 渔夫NPC（在水边）
		fisherman_npc = ASCIINPC(
			pos=(768, 448),  # 渔夫位置 - 靠近池塘
			npc_id="fisherman_li",
			npc_manager=self.npc_manager,
			groups=[self.all_sprites, self.npc_sprites, self.collision_sprites]
		)
		
		# 农夫NPC（在田地区域）
		farmer_npc = ASCIINPC(
			pos=(704, 1216),  # 农夫位置 - 在农田附近
			npc_id="farmer_wang",
			npc_manager=self.npc_manager,
			groups=[self.all_sprites, self.npc_sprites, self.collision_sprites]
		)

	def player_add(self,item):
		"""
		玩家获得物品的回调函数
		"""
		self.player.item_inventory[item] += 1  # 增加物品数量
		self.success.play()  # 播放成功音效

	def toggle_shop(self):
		"""
		切换商店状态
		"""
		self.shop_active = not self.shop_active

	def reset(self):
		"""
		重置游戏状态（通常在睡觉后调用）
		"""
		# 更新植物生长
		self.soil_layer.update_plants()

		# 土壤系统重置
		self.soil_layer.remove_water()  # 移除所有水分
		self.raining = randint(0,10) > 7  # 重新随机天气
		self.soil_layer.raining = self.raining
		if self.raining:
			self.soil_layer.water_all()  # 如果下雨，给所有土壤浇水

		# 重置树上的苹果（ASCII模式）
		for tree in self.tree_sprites.sprites():
			tree.create_fruit()

		# 重置天空颜色
		self.sky.start_color = [255,255,255]

	def plant_collision(self):
		"""
		检测玩家与植物的碰撞，实现收获功能
		"""
		if self.soil_layer.plant_sprites:
			for plant in self.soil_layer.plant_sprites.sprites():
				if plant.harvestable and plant.rect.colliderect(self.player.hitbox):
					self.player_add(plant.plant_type)  # 添加收获的物品
					plant.kill()  # 移除植物
					
					# 创建粒子效果（ASCII模式）
					ASCIIParticle(plant.rect.topleft, 'crop', self.all_sprites, z = LAYERS['main'])
					
					self.soil_layer.grid[plant.rect.centery // TILE_SIZE][plant.rect.centerx // TILE_SIZE].remove('P')  # 从网格中移除
	
	def check_npc_interaction(self):
		"""检查NPC交互"""
		# 检查玩家是否靠近NPC（允许一定交互距离）
		interaction_distance = TILE_SIZE * 1.5  # 交互距离
		
		for npc in self.npc_sprites:
			# 计算玩家与NPC的距离
			player_center = self.player.rect.center
			npc_center = npc.rect.center
			distance = ((player_center[0] - npc_center[0]) ** 2 + 
					   (player_center[1] - npc_center[1]) ** 2) ** 0.5
			
			if distance <= interaction_distance:
				# print(f"[NPC交互] 玩家靠近NPC: {npc.npc_id}, 距离: {distance:.1f}")
				return npc
		return None
	
	def start_npc_dialogue(self, npc):
		"""开始NPC对话"""
		if npc and not self.dialogue_ui.is_active():
			print(f"[NPC对话] 开始与 {npc.npc_id} 对话")
			self.current_interacting_npc = npc
			# 获取NPCManager中的NPC实例
			npc_instance = self.npc_manager.get_npc(npc.npc_id)
			if npc_instance:
				# 使用NPCManager的start_dialogue方法，这会触发任务检查
				dialogues = self.npc_manager.start_dialogue(npc_instance, self.player)
				if dialogues:
					print(f"[NPC对话] 对话内容: {dialogues[0].text[:50]}...")
					self.dialogue_ui.start_dialogue(dialogues)
				else:
					print(f"[NPC对话] 无法开始对话或已在对话中")
					self.current_interacting_npc = None
	
	def handle_dialogue_input(self, key):
		"""处理对话输入"""
		if self.dialogue_ui.is_active():
			choice_index = self.dialogue_ui.handle_input(key)
			
			if choice_index is not None and choice_index >= 0:
				# 处理选择
				if self.current_interacting_npc:
					print(f"[NPC对话] 玩家选择选项 {choice_index}")
					response = self.npc_manager.handle_dialogue_choice(
						self.current_interacting_npc.npc_id, 
						choice_index, 
						self.player
					)
					if response:
						print(f"[NPC对话] NPC回复: {response[0].text[:50]}...")
						self.dialogue_ui.start_dialogue(response)
					else:
						print(f"[NPC对话] 对话结束")
						self.dialogue_ui.end_dialogue()
						self.npc_manager.end_dialogue()
						self.current_interacting_npc = None
			elif choice_index == -1:
				# 对话结束
				print(f"[NPC对话] 玩家结束对话")
				self.dialogue_ui.end_dialogue()
				self.npc_manager.end_dialogue()
				self.current_interacting_npc = None
			
			return True  # 表示输入被对话系统处理了
		return False  # 表示输入没有被处理
	
	def show_npc_interaction_hint(self):
		"""显示NPC交互提示"""
		nearby_npc = self.check_npc_interaction()
		if nearby_npc and not self.dialogue_ui.is_active():
			# 获取NPC信息
			npc_data = self.npc_manager.get_npc(nearby_npc.npc_id)
			if npc_data:
				# 在屏幕中心显示交互提示
				from font_manager import FontManager
				font_manager = FontManager.get_instance()
				font = font_manager.load_chinese_font(32, "npc_hint_font")
				hint_text = f"按 T 键与 {npc_data.name} 对话"
				text_surface = font.render(hint_text, True, (255, 255, 100))
				text_rect = text_surface.get_rect(center=(SCREEN_WIDTH//2, SCREEN_HEIGHT//2 - 100))
				
				# 绘制半透明背景
				bg_rect = text_rect.inflate(20, 10)
				bg_surface = pygame.Surface((bg_rect.width, bg_rect.height))
				bg_surface.set_alpha(128)
				bg_surface.fill((0, 0, 0))
				self.display_surface.blit(bg_surface, bg_rect)
				
				# 绘制文本
				self.display_surface.blit(text_surface, text_rect)

	def run(self,dt):
		"""
		主游戏循环
		"""
		# 绘制逻辑
		self.display_surface.fill('black')  # 填充黑色背景
		self.all_sprites.custom_draw(self.player)  # 绘制所有精灵
		
		# 更新逻辑
		if self.shop_active:
			self.menu.update()  # 如果商店激活，更新菜单
		else:
			self.all_sprites.update(dt)  # 更新所有精灵
			self.plant_collision()  # 检测植物碰撞
			
			# 检查NPC交互提示
			self.show_npc_interaction_hint()

		# 天气系统
		self.overlay.display()  # 显示界面覆盖层
		if self.raining and not self.shop_active:
			self.rain.update()  # 更新雨效果
		self.sky.display(dt)  # 显示天空效果
		
		# 对话系统渲染
		self.dialogue_ui.render(self.display_surface)
		
		# 任务面板渲染
		self.quest_panel.render(self.display_surface, self.player)

		# 过渡动画
		if self.player.sleep:
			self.transition.play()  # 如果玩家睡觉，播放过渡动画

class CameraGroup(pygame.sprite.Group):
	"""
	相机精灵组 - 实现跟随玩家的相机效果
	"""
	def __init__(self):
		super().__init__()
		self.display_surface = pygame.display.get_surface()
		self.offset = pygame.math.Vector2()  # 相机偏移量

	def custom_draw(self, player):
		"""
		自定义绘制方法，实现相机跟随效果
		"""
		# 计算相机偏移量，使玩家始终在屏幕中心
		self.offset.x = player.rect.centerx - SCREEN_WIDTH / 2
		self.offset.y = player.rect.centery - SCREEN_HEIGHT / 2

		# 按层级绘制精灵
		for layer in LAYERS.values():
			for sprite in sorted(self.sprites(), key = lambda sprite: sprite.rect.centery):
				if sprite.z == layer:
					offset_rect = sprite.rect.copy()
					offset_rect.center -= self.offset  # 应用相机偏移
					self.display_surface.blit(sprite.image, offset_rect)  # 绘制精灵

					# # 调试分析代码（已注释）
					# if sprite == player:
					# 	pygame.draw.rect(self.display_surface,'red',offset_rect,5)
					# 	hitbox_rect = player.hitbox.copy()
					# 	hitbox_rect.center = offset_rect.center
					# 	pygame.draw.rect(self.display_surface,'green',hitbox_rect,5)
					# 	target_pos = offset_rect.center + PLAYER_TOOL_OFFSET[player.status.split('_')[0]]
					# 	pygame.draw.circle(self.display_surface,'blue',target_pos,5)