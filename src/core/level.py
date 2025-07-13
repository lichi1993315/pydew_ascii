import pygame 
from src.settings import *
from .player import Player
from src.ui.overlay import Overlay
from src.rendering.ascii_sprites import ASCIIGeneric, ASCIIWater, ASCIIWildFlower, ASCIITree, ASCIIInteraction, ASCIIParticle, ASCIINPC
from .map_loader import load_pygame, MapObjectLayer
from src.core.support import *
from src.utils.transition import Transition
from src.systems.ascii_soil import ASCIISoilLayer
from src.utils.sky import Rain, Sky
from random import randint
from src.ui.menu import Menu
from src.systems.npc_system import NPCManager
from src.ui.dialogue_ui import DialogueUI
from src.ui.quest_panel import QuestPanel  # 添加任务面板导入
from src.ui.chat_panel import ChatPanel  # 添加聊天面板导入
from src.ai.chat_ai import get_chat_ai  # 添加聊天AI导入
from src.ai.cat_npc import CatManager  # 添加猫咪管理器导入
from src.ui.cat_info_ui import CatInfoUI  # 添加猫咪详情UI导入
from src.ui.fishing_minigame import FishingMinigame  # 添加钓鱼小游戏导入
from src.ui.catch_result_panel import CatchResultPanel  # 添加鱼获面板导入
from src.utils.font_manager import FontManager

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
		
		# 聊天面板
		self.chat_panel = ChatPanel(SCREEN_WIDTH, SCREEN_HEIGHT)
		
		# 聊天AI系统
		self.chat_ai = get_chat_ai()
		self.chat_panel.set_message_callback(self.handle_player_chat_message)
		self.chat_panel.set_chat_ai_instance(self.chat_ai)  # 设置AI实例引用
		self.chat_panel.set_spawn_cat_callback(self.spawn_cat_from_chat)  # 设置猫咪生成回调
		self.pending_npc_response = None  # 待处理的NPC回复
		
		# 猫咪管理器
		self.cat_manager = CatManager()
		
		# 猫咪详情UI
		self.cat_info_ui = CatInfoUI(SCREEN_WIDTH, SCREEN_HEIGHT)
		
		# 钓鱼小游戏
		self.fishing_minigame = FishingMinigame(SCREEN_WIDTH, SCREEN_HEIGHT)
		
		# 鱼获结果面板
		self.catch_result_panel = CatchResultPanel(SCREEN_WIDTH, SCREEN_HEIGHT)
		
		self.setup()
		
		# 设置玩家对聊天面板的引用
		if self.player:
			self.player.chat_panel = self.chat_panel
		
		self.overlay = Overlay(self.player)
		self.transition = Transition(self.reset, self.player)

		# 天气系统
		self.rain = Rain(self.all_sprites)
		self.raining = False  # 不下雨
		self.soil_layer.raining = self.raining
		self.sky = Sky()  # 天空效果
		
		# 设置覆盖层的天空系统引用
		self.overlay.sky_system = self.sky

		# 商店系统
		self.menu = Menu(self.player, self.toggle_shop)  # 商店菜单
		self.shop_active = False  # 商店是否激活

		# 音频系统
		self.success = None
		self.music = None
		
		# 尝试加载音效文件
		try:
			if pygame.mixer.get_init():
				success_path = get_resource_path('assets/audio/success.wav')
				music_path = get_resource_path('assets/audio/music.mp3')
				self.success = pygame.mixer.Sound(success_path)  # 成功音效
				self.success.set_volume(0.3)
				self.music = pygame.mixer.Sound(music_path)  # 背景音乐
				self.music.play(loops = -1)  # 循环播放
		except (pygame.error, FileNotFoundError) as e:
			print(f"⚠️ 关卡音效加载失败: {e}")
			print("游戏将在无音效模式下运行")

	def setup(self):
		"""
		设置游戏地图和所有精灵
		从TMX文件加载地图数据并创建相应的游戏对象
		全部使用ASCII模式渲染
		"""
		tmx_data = load_pygame('config/map_config.json')  # 加载JSON地图文件

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
			ASCIIGeneric((x * TILE_SIZE,y * TILE_SIZE), 'fence', [self.all_sprites])

		# 水效果 (水有碰撞)
		for x, y, surf in tmx_data.get_layer_by_name('Water').tiles():
			ASCIIWater((x * TILE_SIZE,y * TILE_SIZE), [self.all_sprites, self.water_sprites])
			# 给水添加碰撞
			ASCIIGeneric((x * TILE_SIZE, y * TILE_SIZE), 'water', [self.collision_sprites])
		
		# 小径
		for x, y, surf in tmx_data.get_layer_by_name('Path').tiles():
			ASCIIGeneric((x * TILE_SIZE, y * TILE_SIZE), 'dirt', [self.all_sprites], z=LAYERS['ground'])
		
		# 海滩
		for x, y, surf in tmx_data.get_layer_by_name('Beach').tiles():
			ASCIIGeneric((x * TILE_SIZE, y * TILE_SIZE), 'sand', [self.all_sprites], z=LAYERS['ground'])

		# 树木
		tree_layer = MapObjectLayer(tmx_data.config, 'Trees')
		for obj in tree_layer:
			ASCIITree(
				pos = (obj.x, obj.y), 
				groups = [self.all_sprites, self.tree_sprites], 
				name = obj.name,
				player_add = self.player_add)

		# 装饰物
		decoration_layer = MapObjectLayer(tmx_data.config, 'Decoration')
		for obj in decoration_layer:
			decoration_type = obj.name.lower()
			if decoration_type == 'flower':
				ASCIIWildFlower((obj.x, obj.y), [self.all_sprites])
			elif decoration_type == 'grass':
				ASCIIGeneric((obj.x, obj.y), 'grass', [self.all_sprites], z=LAYERS['main'])
			elif decoration_type == 'bush':
				ASCIIGeneric((obj.x, obj.y), 'bush', [self.all_sprites], z=LAYERS['main'])
			elif decoration_type == 'rock':
				ASCIIGeneric((obj.x, obj.y), 'rock', [self.all_sprites], z=LAYERS['main'])
			elif decoration_type == 'mushroom':
				ASCIIGeneric((obj.x, obj.y), 'mushroom', [self.all_sprites], z=LAYERS['main'])
			else:
				# 默认草地装饰
				ASCIIGeneric((obj.x, obj.y), 'grass', [self.all_sprites], z=LAYERS['main'])

		# 碰撞瓦片
		for x, y, surf in tmx_data.get_layer_by_name('Collision').tiles():
			ASCIIGeneric((x * TILE_SIZE, y * TILE_SIZE), 'stone', self.collision_sprites)

		# 玩家和交互对象
		player_layer = MapObjectLayer(tmx_data.config, 'Player')
		for obj in player_layer:
			if obj.name == 'start':  # 玩家起始位置
				self.player = Player(
					pos = (obj.x,obj.y), 
					group = self.all_sprites, 
					collision_sprites = self.collision_sprites,
					tree_sprites = self.tree_sprites,
					interaction = self.interaction_sprites,
					soil_layer = self.soil_layer,
					toggle_shop = self.toggle_shop,
					quest_panel = self.quest_panel,
					ascii_mode = True)
				
				# 设置水精灵组，用于钓鱼功能
				self.player.water_sprites = self.water_sprites
				
				# 设置level引用，用于猫咪管理
				self.player.level = self
			
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
		
		# 创建猫咪NPCs（传递玩家位置）
		player_pos = None
		if self.player:
			player_pos = self.player.rect.center
		
		self.cat_manager.create_cats(
			self.all_sprites, 
			self.collision_sprites, 
			self.npc_sprites, 
			self.npc_manager,
			player_pos=player_pos,
			initial_cats=0  # 初始无猫咪，需要通过钓鱼获得
		)
		print(f"[Level] 初始化猫咪管理器，初始猫咪数量: {len(self.cat_manager.cats)}")
		
		# 注册猫咪NPCs到NPC管理器
		self.npc_manager.register_cat_npcs(self.cat_manager)

	def player_add(self,item):
		"""
		玩家获得物品的回调函数
		"""
		self.player.item_inventory[item] += 1  # 增加物品数量
		if self.success:
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

		# 睡觉后跳到第二天早上6点（传统农场游戏的睡觉机制）
		self.sky.force_time(6, 0)  # 设置为早上6:00
		
		print(f"[游戏重置] 睡觉后，时间重置为早上6:00")
		print(f"[游戏重置] 当前时间: {self.sky.get_time_of_day()}")
		print(f"[游戏重置] 当前时段: {self.sky.get_time_period()}")

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
	
	def check_cat_interaction(self):
		"""检查猫咪NPC交互"""
		interaction_distance = TILE_SIZE * 1.5  # 交互距离
		
		for cat in self.cat_manager.cats:
			# 计算玩家与猫咪的距离
			player_center = self.player.rect.center
			cat_center = cat.rect.center
			distance = ((player_center[0] - cat_center[0]) ** 2 + 
					   (player_center[1] - cat_center[1]) ** 2) ** 0.5
			
			if distance <= interaction_distance:
				# print(f"[猫咪交互] 玩家靠近猫咪: {cat.cat_name}, 距离: {distance:.1f}")
				return cat
		return None
	
	def start_npc_dialogue(self, npc):
		"""开始NPC对话"""
		if npc and not self.dialogue_ui.is_active():
			print(f"[NPC对话] 开始与 {npc.npc_id} 对话")
			self.current_interacting_npc = npc
			
			# 获取NPCManager中的NPC实例
			npc_instance = self.npc_manager.get_npc(npc.npc_id)
			if npc_instance:
				# 添加对话开始消息到聊天面板
				self.chat_panel.add_system_message(f"开始与 {npc_instance.name} 对话")
				
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
					
					# 记录玩家的选择到聊天面板
					if hasattr(self.dialogue_ui.current_dialogue, 'choices') and self.dialogue_ui.current_dialogue.choices:
						choice_text = self.dialogue_ui.current_dialogue.choices[choice_index]
						self.chat_panel.add_message(choice_text, "玩家")
					
					response = self.npc_manager.handle_dialogue_choice(
						self.current_interacting_npc.npc_id, 
						choice_index, 
						self.player
					)
					if response:
						print(f"[NPC对话] NPC回复: {response[0].text[:50]}...")
						
						# 记录NPC回复到聊天面板
						npc_instance = self.npc_manager.get_npc(self.current_interacting_npc.npc_id)
						if npc_instance:
							self.chat_panel.add_message(response[0].text, npc_instance.name)
						
						self.dialogue_ui.start_dialogue(response)
					else:
						print(f"[NPC对话] 对话结束")
						self.chat_panel.add_system_message("对话结束")
						self.dialogue_ui.end_dialogue()
						self.npc_manager.end_dialogue()
						self.current_interacting_npc = None
			elif choice_index == -1:
				# 检查是否有任务对话状态，如果有则继续对话
				if (self.npc_manager.current_dialogue_state and 
					not self.npc_manager.current_dialogue_state.is_quest_offer):
					# 继续任务对话
					continued_dialogue = self.npc_manager.continue_dialogue(self.player)
					if continued_dialogue:
						print(f"[NPC对话] 继续任务对话: {continued_dialogue[0].text[:50]}...")
						
						# 记录继续的对话到聊天面板
						npc_instance = self.npc_manager.get_npc(self.current_interacting_npc.npc_id)
						if npc_instance:
							self.chat_panel.add_message(continued_dialogue[0].text, npc_instance.name)
						
						self.dialogue_ui.start_dialogue(continued_dialogue)
					else:
						# 对话结束
						print(f"[NPC对话] 任务对话结束")
						self.chat_panel.add_system_message("对话结束")
						self.dialogue_ui.end_dialogue()
						self.npc_manager.end_dialogue()
						self.current_interacting_npc = None
				else:
					# 普通对话结束
					print(f"[NPC对话] 玩家结束对话")
					self.chat_panel.add_system_message("对话结束")
					self.dialogue_ui.end_dialogue()
					self.npc_manager.end_dialogue()
					self.current_interacting_npc = None
			
			return True  # 表示输入被对话系统处理了
		return False  # 表示输入没有被处理
	
	def handle_player_chat_message(self, message: str):
		"""处理玩家聊天消息并生成NPC回复"""
		import asyncio
		import threading
		
		# 检测附近的NPC
		nearby_npc_id = self.chat_ai.get_nearby_npc(
			self.player.rect.center, 
			self.npc_sprites
		)
		
		if nearby_npc_id:
			# 获取NPC数据并显示思考指示器
			npc_data = self.npc_manager.get_npc(nearby_npc_id)
			if npc_data:
				print(f"[Level] 找到附近NPC: {npc_data.name} ({nearby_npc_id})")
				
				# 立即显示"正在思考"消息
				self.chat_panel.add_thinking_message(npc_data.name)
				
				# 在新线程中处理AI回复，避免阻塞游戏循环
				def generate_response():
					try:
						# 创建新的事件循环
						loop = asyncio.new_event_loop()
						asyncio.set_event_loop(loop)
						
						# 获取游戏上下文
						context = self.chat_ai.add_context_from_game_state(self.player, self)
						
						# 生成AI回复
						response = loop.run_until_complete(
							self.chat_ai.generate_npc_response(nearby_npc_id, message, context)
						)
						
						# 在主线程中处理回复（替换思考消息）
						self.pending_npc_response = (npc_data.name, response, True)  # 第三个参数表示替换思考消息
						
						loop.close()
						
					except Exception as e:
						print(f"[聊天AI] 生成回复失败: {e}")
						# 添加错误回复
						self.pending_npc_response = (npc_data.name, "抱歉，我没听清楚你在说什么...", True)
				
				# 启动线程
				response_thread = threading.Thread(target=generate_response)
				response_thread.daemon = True
				response_thread.start()
			else:
				print(f"[Level] 找到NPC ID但无法获取NPC数据: {nearby_npc_id}")
		else:
			# 没有附近的NPC，添加系统消息
			print("[Level] 没有找到附近的NPC")
			self.chat_panel.add_system_message("附近没有人能听到你的话...")
	
	def show_npc_interaction_hint(self):
		"""显示NPC交互提示"""
		# 如果猫咪详情UI正在显示，不显示提示
		if self.cat_info_ui.is_active:
			return
		
		# 优先检查猫咪交互
		nearby_cat = self.check_cat_interaction()
		if nearby_cat:
			# 显示猫咪交互提示
			font_manager = FontManager.get_instance()
			font = font_manager.load_chinese_font(32, "npc_hint_font")
			hint_text = f"按 T 键查看 {nearby_cat.cat_name} 的详细信息"
			text_surface = font.render(hint_text, True, (255, 182, 193))  # 粉色
			text_rect = text_surface.get_rect(center=(SCREEN_WIDTH//2, SCREEN_HEIGHT//2 - 100))
			
			# 绘制半透明背景
			bg_rect = text_rect.inflate(20, 10)
			bg_surface = pygame.Surface((bg_rect.width, bg_rect.height))
			bg_surface.set_alpha(128)
			bg_surface.fill((0, 0, 0))
			self.display_surface.blit(bg_surface, bg_rect)
			
			# 绘制文本
			self.display_surface.blit(text_surface, text_rect)
			return
		
		# 检查其他NPC交互
		nearby_npc = self.check_npc_interaction()
		if nearby_npc and not self.dialogue_ui.is_active():
			# 获取NPC信息
			npc_data = self.npc_manager.get_npc(nearby_npc.npc_id)
			if npc_data:
				# 在屏幕中心显示交互提示
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
		
		# 日志面板渲染
		self.player.render_log_panel(self.display_surface)
		
		# 处理待处理的NPC回复
		if self.pending_npc_response:
			if len(self.pending_npc_response) == 3:
				npc_name, response_text, replace_thinking = self.pending_npc_response
				if replace_thinking:
					self.chat_panel.replace_thinking_with_response(npc_name, response_text)
				else:
					self.chat_panel.add_ai_response(response_text, npc_name)
			else:
				# 兼容旧格式
				npc_name, response_text = self.pending_npc_response
				self.chat_panel.add_ai_response(response_text, npc_name)
			
			self.pending_npc_response = None
		
		# 聊天面板更新和渲染
		self.chat_panel.update(dt)
		self.chat_panel.render(self.display_surface)
		
		# 猫咪详情UI渲染
		self.cat_info_ui.render(self.display_surface)

		# 钓鱼小游戏更新和渲染
		self.fishing_minigame.update(dt)
		self.fishing_minigame.render(self.display_surface)
		
		# 钓鱼状态UI显示
		self.render_fishing_state_ui()
		
		# 渲染鱼饵
		self.render_bait()
		
		# 鱼获结果面板更新和渲染
		self.catch_result_panel.update(dt)
		self.catch_result_panel.render(self.display_surface)

		# 过渡动画
		if self.player.sleep:
			self.transition.play()  # 如果玩家睡觉，播放过渡动画
	
	def render_fishing_state_ui(self):
		"""渲染钓鱼状态UI"""
		if not self.player.is_fishing or self.fishing_minigame.is_active:
			return
		
		# 获取钓鱼状态信息
		state = self.player.fishing_state
		
		# 定义状态文本和颜色
		state_texts = {
			"casting": ("🎣 正在出杆...", (255, 255, 100)),
			"waiting": ("🎣 等待鱼上钩...", (100, 255, 100)),  
			"fish_hooked": ("🎣 鱼上钩了！快按空格键！", (255, 100, 100))
		}
		
		if state not in state_texts:
			return
			
		text, color = state_texts[state]
		
		# 添加额外信息
		if state == "waiting" and hasattr(self.player, 'fishing_timer'):
			remaining_time = max(0, self.player.fishing_timer)
			text += f" ({remaining_time:.1f}s)"
		elif state == "fish_hooked" and hasattr(self.player, 'bait_shake_timer'):
			shake_time = self.player.bait_shake_timer
			text += f" (已晃动 {shake_time:.1f}s)"
		
		# 渲染文本
		font_manager = FontManager.get_instance()
		font = font_manager.load_chinese_font(32, "fishing_state_font")
		text_surface = font.render(text, True, color)
		text_rect = text_surface.get_rect(center=(SCREEN_WIDTH//2, 100))
		
		# 绘制半透明背景
		bg_rect = text_rect.inflate(20, 10)
		bg_surface = pygame.Surface((bg_rect.width, bg_rect.height))
		bg_surface.set_alpha(128)
		bg_surface.fill((0, 0, 0))
		self.display_surface.blit(bg_surface, bg_rect)
		
		# 绘制文本
		self.display_surface.blit(text_surface, text_rect)
		
		# 添加操作提示
		hint_text = ""
		if state == "waiting":
			hint_text = "按空格键可以提前收杆"
		elif state == "fish_hooked":
			hint_text = "快按空格键收杆，否则鱼会跑掉！"
		
		if hint_text:
			hint_font = font_manager.load_chinese_font(24, "fishing_hint_font")
			hint_surface = hint_font.render(hint_text, True, (200, 200, 200))
			hint_rect = hint_surface.get_rect(center=(SCREEN_WIDTH//2, 140))
			self.display_surface.blit(hint_surface, hint_rect)
	
	def render_bait(self):
		"""渲染鱼饵emoji"""
		if not self.player.is_fishing or not self.player.bait_position:
			return
		
		# 只在casting、waiting、fish_hooked状态时显示鱼饵
		if self.player.fishing_state not in ["casting", "waiting", "fish_hooked"]:
			return
		
		# 获取鱼饵位置
		bait_x, bait_y = self.player.bait_position
		
		# 获取摄像机偏移量（与精灵渲染保持一致）
		camera_offset = self.all_sprites.offset
		screen_x = bait_x - camera_offset.x
		screen_y = bait_y - camera_offset.y
		
		# 检查是否在屏幕范围内
		if (screen_x < -50 or screen_x > SCREEN_WIDTH + 50 or 
			screen_y < -50 or screen_y > SCREEN_HEIGHT + 50):
			return
		
		# 获取字体
		font_manager = FontManager.get_instance()
		font = font_manager.load_emoji_font(12, "bait_font")
		
		# 根据状态选择不同的显示效果
		if self.player.fishing_state == "casting":
			# 出杆阶段，鱼饵稍微透明
			bait_text = "🌰"
			alpha = 150
		elif self.player.fishing_state == "waiting":
			# 等待阶段，鱼饵正常显示
			bait_text = "🌰"
			alpha = 255
		elif self.player.fishing_state == "fish_hooked":
			# 鱼上钩阶段，鱼饵晃动效果
			import math
			shake_offset = int(math.sin(self.player.bait_shake_timer * 10) * 3)
			screen_x += shake_offset
			screen_y += shake_offset
			bait_text = "🌰"
			alpha = 255
		
		# 渲染鱼饵 - 如果emoji渲染失败，使用简单字符
		try:
			bait_surface = font.render(bait_text, True, (255, 255, 255))
		except:
			# 如果emoji渲染失败，使用简单字符
			bait_text = "B"  # B代表Bait
			bait_surface = font.render(bait_text, True, (255, 255, 0))  # 黄色
		
		if alpha < 255:
			bait_surface.set_alpha(alpha)
		
		# 居中显示
		bait_rect = bait_surface.get_rect(center=(screen_x, screen_y))
		self.display_surface.blit(bait_surface, bait_rect)

	def spawn_cat_from_chat(self):
		"""
		从聊天面板生成猫咪的回调函数
		"""
		print("[Level] 从聊天面板生成猫咪")
		# 获取玩家位置
		player_pos = self.player.rect.center
		
		# 使用cat_manager的add_new_cat_from_fishing方法来生成猫咪
		new_cat = self.cat_manager.add_new_cat_from_fishing(player_pos)
		
		if new_cat:
			# 注册猫咪NPCs到NPC管理器
			self.npc_manager.register_cat_npcs(self.cat_manager)
			print(f"[Level] 成功从聊天面板生成猫咪: {new_cat.cat_name}")
			return new_cat
		else:
			print("[Level] 从聊天面板生成猫咪失败")
			return None

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