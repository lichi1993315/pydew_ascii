import pygame 
from settings import *
from player import Player
from overlay import Overlay
from sprites import Generic, Water, WildFlower, Tree, Interaction, Particle
from ascii_sprites import ASCIIGeneric, ASCIIWater, ASCIIWildFlower, ASCIITree, ASCIIInteraction, ASCIIParticle
from pytmx.util_pygame import load_pygame
from support import *
from transition import Transition
from soil import SoilLayer
from ascii_soil import ASCIISoilLayer
from sky import Rain, Sky
from random import randint
from menu import Menu

class Level:
	"""
	游戏关卡类 - 管理整个游戏世界的主要逻辑
	包括地图加载、精灵管理、天气系统、商店系统等
	支持ASCII模式和图片模式
	"""
	def __init__(self, ascii_mode=False):
		# ASCII模式开关
		self.ascii_mode = ascii_mode
		
		# 获取显示表面
		self.display_surface = pygame.display.get_surface()

		# 精灵组管理
		self.all_sprites = CameraGroup()
		self.collision_sprites = pygame.sprite.Group()
		self.tree_sprites = pygame.sprite.Group()
		self.interaction_sprites = pygame.sprite.Group()

		# 土壤层系统 - 根据模式选择
		if self.ascii_mode:
			self.soil_layer = ASCIISoilLayer(self.all_sprites, self.collision_sprites, ascii_mode=True)
		else:
			self.soil_layer = SoilLayer(self.all_sprites, self.collision_sprites)
		
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
		"""
		tmx_data = load_pygame('../data/map.tmx')  # 加载TMX地图文件

		# 房屋地板和家具（底层）
		for layer in ['HouseFloor', 'HouseFurnitureBottom']:
			for x, y, surf in tmx_data.get_layer_by_name(layer).tiles():
				if self.ascii_mode:
					ASCIIGeneric((x * TILE_SIZE,y * TILE_SIZE), 'floor', self.all_sprites, LAYERS['house bottom'])
				else:
					Generic((x * TILE_SIZE,y * TILE_SIZE), surf, self.all_sprites, LAYERS['house bottom'])

		# 房屋墙壁和家具（顶层）
		for layer in ['HouseWalls', 'HouseFurnitureTop']:
			for x, y, surf in tmx_data.get_layer_by_name(layer).tiles():
				if self.ascii_mode:
					ASCIIGeneric((x * TILE_SIZE,y * TILE_SIZE), 'wall', self.all_sprites)
				else:
					Generic((x * TILE_SIZE,y * TILE_SIZE), surf, self.all_sprites)

		# 栅栏
		for x, y, surf in tmx_data.get_layer_by_name('Fence').tiles():
			if self.ascii_mode:
				ASCIIGeneric((x * TILE_SIZE,y * TILE_SIZE), 'fence', [self.all_sprites, self.collision_sprites])
			else:
				Generic((x * TILE_SIZE,y * TILE_SIZE), surf, [self.all_sprites, self.collision_sprites])

		# 水效果
		if self.ascii_mode:
			for x, y, surf in tmx_data.get_layer_by_name('Water').tiles():
				ASCIIWater((x * TILE_SIZE,y * TILE_SIZE), self.all_sprites)
		else:
			water_frames = import_folder('../graphics/water')
			for x, y, surf in tmx_data.get_layer_by_name('Water').tiles():
				Water((x * TILE_SIZE,y * TILE_SIZE), water_frames, self.all_sprites)

		# 树木
		for obj in tmx_data.get_layer_by_name('Trees'):
			if self.ascii_mode:
				ASCIITree(
					pos = (obj.x, obj.y), 
					groups = [self.all_sprites, self.collision_sprites, self.tree_sprites], 
					name = obj.name,
					player_add = self.player_add)
			else:
				Tree(
					pos = (obj.x, obj.y), 
					surf = obj.image, 
					groups = [self.all_sprites, self.collision_sprites, self.tree_sprites], 
					name = obj.name,
					player_add = self.player_add)

		# 野花装饰
		for obj in tmx_data.get_layer_by_name('Decoration'):
			if self.ascii_mode:
				ASCIIWildFlower((obj.x, obj.y), [self.all_sprites, self.collision_sprites])
			else:
				WildFlower((obj.x, obj.y), obj.image, [self.all_sprites, self.collision_sprites])

		# 碰撞瓦片
		for x, y, surf in tmx_data.get_layer_by_name('Collision').tiles():
			if self.ascii_mode:
				ASCIIGeneric((x * TILE_SIZE, y * TILE_SIZE), 'stone', self.collision_sprites)
			else:
				Generic((x * TILE_SIZE, y * TILE_SIZE), pygame.Surface((TILE_SIZE, TILE_SIZE)), self.collision_sprites)

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
					ascii_mode = self.ascii_mode)
			
			if obj.name == 'Bed':  # 床（睡觉交互）
				if self.ascii_mode:
					ASCIIInteraction((obj.x,obj.y), (obj.width,obj.height), self.interaction_sprites, obj.name)
				else:
					Interaction((obj.x,obj.y), (obj.width,obj.height), self.interaction_sprites, obj.name)

			if obj.name == 'Trader':  # 商人（商店交互）
				if self.ascii_mode:
					ASCIIInteraction((obj.x,obj.y), (obj.width,obj.height), self.interaction_sprites, obj.name)
				else:
					Interaction((obj.x,obj.y), (obj.width,obj.height), self.interaction_sprites, obj.name)

		# 地面背景
		if self.ascii_mode:
			ASCIIGeneric(
				pos = (0,0),
				tile_type = 'grass',
				groups = self.all_sprites,
				z = LAYERS['ground'])
		else:
			Generic(
				pos = (0,0),
				surf = pygame.image.load('../graphics/world/ground.png').convert_alpha(),
				groups = self.all_sprites,
				z = LAYERS['ground'])

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

		# 重置树上的苹果
		for tree in self.tree_sprites.sprites():
			if self.ascii_mode:
				tree.create_fruit()
			else:
				for apple in tree.apple_sprites.sprites():
					apple.kill()  # 移除所有苹果
				tree.create_fruit()  # 重新生成苹果

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
					
					# 创建粒子效果
					if self.ascii_mode:
						ASCIIParticle(plant.rect.topleft, 'crop', self.all_sprites, z = LAYERS['main'])
					else:
						Particle(plant.rect.topleft, plant.image, self.all_sprites, z = LAYERS['main'])
					
					self.soil_layer.grid[plant.rect.centery // TILE_SIZE][plant.rect.centerx // TILE_SIZE].remove('P')  # 从网格中移除

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

		# 天气系统
		self.overlay.display()  # 显示界面覆盖层
		if self.raining and not self.shop_active:
			self.rain.update()  # 更新雨效果
		self.sky.display(dt)  # 显示天空效果

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