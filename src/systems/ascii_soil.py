import pygame
from ..settings import *
from ..rendering.ascii_renderer import ASCIIRenderer
from random import choice
from ..core.map_loader import load_pygame
from ..core.support import get_resource_path

class ASCIISoilTile(pygame.sprite.Sprite):
	"""
	ASCII版本的土壤瓦片
	"""
	def __init__(self, pos, groups, tile_type='o'):
		super().__init__(groups)
		self.tile_type = tile_type
		self.ascii_renderer = ASCIIRenderer()
		
		# 创建ASCII表面
		self.image = pygame.Surface((TILE_SIZE, TILE_SIZE), pygame.SRCALPHA)
		self.rect = self.image.get_rect(topleft=pos)
		self.z = LAYERS['soil']
		
		# 渲染土壤
		self.render_soil()
	
	def render_soil(self):
		"""
		渲染土壤瓦片
		"""
		self.image.fill((0, 0, 0, 0))
		
		# 根据瓦片类型选择字符
		soil_chars = {
			'o': ',',    # 单个土壤
			'x': '#',    # 中心土壤
			'r': '[',    # 右边土壤
			'l': ']',    # 左边土壤
			'lr': '=',   # 水平土壤
			't': '^',    # 上边土壤
			'b': 'v',    # 下边土壤
			'tb': '|',   # 垂直土壤
			'tr': '/',   # 右上角
			'tl': '\\',  # 左上角
			'br': '\\',  # 右下角
			'bl': '/',   # 左下角
			'tbr': 'T',  # T形（上右下）
			'tbl': 'T',  # T形（上左下）
			'lrb': 'H',  # H形（左右下）
			'lrt': 'H',  # H形（左右上）
		}
		
		char = soil_chars.get(self.tile_type, ',')
		color = self.ascii_renderer.color_map['dirt']
		
		# 渲染到瓦片中心
		self.ascii_renderer.render_ascii(self.image, char, color, (0, 0), TILE_SIZE)

class ASCIIWaterTile(pygame.sprite.Sprite):
	"""
	ASCII版本的水分瓦片
	"""
	def __init__(self, pos, groups):
		super().__init__(groups)
		self.ascii_renderer = ASCIIRenderer()
		
		# 创建ASCII表面
		self.image = pygame.Surface((TILE_SIZE, TILE_SIZE), pygame.SRCALPHA)
		self.rect = self.image.get_rect(topleft=pos)
		self.z = LAYERS['soil water']
		
		# 动画相关
		self.animation_frame = 0
		self.animation_speed = 0.2
		self.animation_timer = 0
		
		# 渲染水分
		self.render_water()
	
	def render_water(self):
		"""
		渲染水分瓦片
		"""
		self.image.fill((0, 0, 0, 0))
		
		# 水分字符
		water_chars = ['~', '≈', '≈', '~']
		char = water_chars[self.animation_frame % len(water_chars)]
		color = self.ascii_renderer.color_map['water']
		
		# 渲染到瓦片中心
		self.ascii_renderer.render_ascii(self.image, char, color, (0, 0), TILE_SIZE)
	
	def update(self, dt):
		"""
		更新水分动画
		"""
		self.animation_timer += dt
		if self.animation_timer >= self.animation_speed:
			self.animation_timer = 0
			self.animation_frame += 1
			self.render_water()

class ASCIIPlant(pygame.sprite.Sprite):
	"""
	ASCII版本的植物
	"""
	def __init__(self, plant_type, groups, soil, check_watered):
		super().__init__(groups)
		
		# 设置
		self.plant_type = plant_type
		self.soil = soil
		self.check_watered = check_watered
		self.ascii_renderer = ASCIIRenderer()

		# 植物生长
		self.age = 0
		self.max_age = 3  # 简化生长阶段
		self.grow_speed = 0.1  # 简化生长速度
		self.harvestable = False

		# 精灵设置
		self.image = pygame.Surface((TILE_SIZE, TILE_SIZE), pygame.SRCALPHA)
		self.y_offset = -8
		self.rect = self.image.get_rect(midbottom=soil.rect.midbottom + pygame.math.Vector2(0, self.y_offset))
		self.z = LAYERS['ground plant']
		
		# 渲染植物
		self.render_plant()

	def render_plant(self):
		"""
		渲染植物
		"""
		self.image.fill((0, 0, 0, 0))
		
		# 根据生长阶段选择字符
		growth_stages = ['s', 'c', 'C', '*']  # 种子 -> 幼苗 -> 成熟 -> 开花
		stage_index = min(int(self.age), len(growth_stages) - 1)
		char = growth_stages[stage_index]
		
		# 根据植物类型选择颜色
		plant_colors = {
			'corn': (255, 215, 0),    # 金色
			'tomato': (255, 0, 0),    # 红色
			'apple': (255, 0, 0),     # 红色
			'default': (34, 139, 34)  # 绿色
		}
		color = plant_colors.get(self.plant_type, plant_colors['default'])
		
		# 渲染植物
		self.ascii_renderer.render_ascii(self.image, char, color, (0, 0), TILE_SIZE)

	def grow(self):
		"""
		植物生长
		"""
		if self.check_watered(self.rect.center):
			self.age += self.grow_speed

			if int(self.age) > 0:
				self.z = LAYERS['main']
				self.hitbox = self.rect.copy().inflate(-26, -self.rect.height * 0.4)

			if self.age >= self.max_age:
				self.age = self.max_age
				self.harvestable = True

			self.render_plant()
			self.rect = self.image.get_rect(midbottom=self.soil.rect.midbottom + pygame.math.Vector2(0, self.y_offset))

class ASCIISoilLayer:
	"""
	ASCII版本的土壤层
	"""
	def __init__(self, all_sprites, collision_sprites):
		
		# 精灵组
		self.all_sprites = all_sprites
		self.collision_sprites = collision_sprites
		self.soil_sprites = pygame.sprite.Group()
		self.water_sprites = pygame.sprite.Group()
		self.plant_sprites = pygame.sprite.Group()

		# 创建土壤网格
		self.create_soil_grid()
		self.create_hit_rects()

		# 音效
		self.hoe_sound = None
		self.plant_sound = None
		
		# 尝试加载音效文件
		try:
			if pygame.mixer.get_init():
				hoe_path = get_resource_path('assets/audio/hoe.wav')
				plant_path = get_resource_path('assets/audio/plant.wav')
				self.hoe_sound = pygame.mixer.Sound(hoe_path)
				self.hoe_sound.set_volume(0.1)
				self.plant_sound = pygame.mixer.Sound(plant_path) 
				self.plant_sound.set_volume(0.2)
		except (pygame.error, FileNotFoundError) as e:
			print(f"WARNING: Audio loading failed: {e}")
			print("Game will run without sound effects")

	def create_soil_grid(self):
		"""
		创建土壤网格
		"""
		# 使用JSON地图数据获取尺寸，而不是加载TMX文件
		tmx_data = load_pygame('config/map_config.json')
		h_tiles, v_tiles = tmx_data.width, tmx_data.height
		
		self.grid = [[[] for col in range(h_tiles)] for row in range(v_tiles)]
		for x, y, _ in tmx_data.get_layer_by_name('Farmable').tiles():
			self.grid[y][x].append('F')

	def create_hit_rects(self):
		"""
		创建碰撞矩形
		"""
		self.hit_rects = []
		for index_row, row in enumerate(self.grid):
			for index_col, cell in enumerate(row):
				if 'F' in cell:
					x = index_col * TILE_SIZE
					y = index_row * TILE_SIZE
					rect = pygame.Rect(x, y, TILE_SIZE, TILE_SIZE)
					self.hit_rects.append(rect)

	def get_hit(self, point):
		"""
		锄地
		"""
		for rect in self.hit_rects:
			if rect.collidepoint(point):
				if self.hoe_sound:
					self.hoe_sound.play()

				x = rect.x // TILE_SIZE
				y = rect.y // TILE_SIZE

				if 'F' in self.grid[y][x]:
					self.grid[y][x].append('X')
					self.create_soil_tiles()
					if hasattr(self, 'raining') and self.raining:
						self.water_all()

	def water(self, target_pos):
		"""
		浇水
		"""
		for soil_sprite in self.soil_sprites.sprites():
			if soil_sprite.rect.collidepoint(target_pos):
				x = soil_sprite.rect.x // TILE_SIZE
				y = soil_sprite.rect.y // TILE_SIZE
				self.grid[y][x].append('W')

				pos = soil_sprite.rect.topleft
				ASCIIWaterTile(pos, [self.all_sprites, self.water_sprites])

	def water_all(self):
		"""
		给所有土壤浇水
		"""
		for index_row, row in enumerate(self.grid):
			for index_col, cell in enumerate(row):
				if 'X' in cell and 'W' not in cell:
					cell.append('W')
					x = index_col * TILE_SIZE
					y = index_row * TILE_SIZE
					ASCIIWaterTile((x, y), [self.all_sprites, self.water_sprites])

	def remove_water(self):
		"""
		移除所有水分
		"""
		# 销毁所有水分精灵
		for sprite in self.water_sprites.sprites():
			sprite.kill()

		# 清理网格
		for row in self.grid:
			for cell in row:
				if 'W' in cell:
					cell.remove('W')

	def check_watered(self, pos):
		"""
		检查是否浇水
		"""
		x = pos[0] // TILE_SIZE
		y = pos[1] // TILE_SIZE
		cell = self.grid[y][x]
		is_watered = 'W' in cell
		return is_watered

	def plant_seed(self, target_pos, seed):
		"""
		种植种子
		"""
		for soil_sprite in self.soil_sprites.sprites():
			if soil_sprite.rect.collidepoint(target_pos):
				if self.plant_sound:
					self.plant_sound.play()

				x = soil_sprite.rect.x // TILE_SIZE
				y = soil_sprite.rect.y // TILE_SIZE

				if 'P' not in self.grid[y][x]:
					self.grid[y][x].append('P')
					ASCIIPlant(seed, [self.all_sprites, self.plant_sprites, self.collision_sprites], soil_sprite, self.check_watered)

	def update_plants(self):
		"""
		更新植物生长
		"""
		for plant in self.plant_sprites.sprites():
			plant.grow()

	def create_soil_tiles(self):
		"""
		创建土壤瓦片
		"""
		self.soil_sprites.empty()
		for index_row, row in enumerate(self.grid):
			for index_col, cell in enumerate(row):
				if 'X' in cell:
					# 瓦片选项
					t = 'X' in self.grid[index_row - 1][index_col]
					b = 'X' in self.grid[index_row + 1][index_col]
					r = 'X' in row[index_col + 1]
					l = 'X' in row[index_col - 1]

					tile_type = 'o'

					# 所有边
					if all((t, r, b, l)): tile_type = 'x'

					# 只有水平瓦片
					if l and not any((t, r, b)): tile_type = 'r'
					if r and not any((t, l, b)): tile_type = 'l'
					if r and l and not any((t, b)): tile_type = 'lr'

					# 只有垂直瓦片
					if t and not any((r, l, b)): tile_type = 'b'
					if b and not any((r, l, t)): tile_type = 't'
					if b and t and not any((r, l)): tile_type = 'tb'

					# 角落
					if l and b and not any((t, r)): tile_type = 'tr'
					if r and b and not any((t, l)): tile_type = 'tl'
					if l and t and not any((b, r)): tile_type = 'br'
					if r and t and not any((b, l)): tile_type = 'bl'

					# T形
					if all((t, b, r)) and not l: tile_type = 'tbr'
					if all((t, b, l)) and not r: tile_type = 'tbl'
					if all((l, r, t)) and not b: tile_type = 'lrb'
					if all((l, r, b)) and not t: tile_type = 'lrt'

					ASCIISoilTile(
						pos=(index_col * TILE_SIZE, index_row * TILE_SIZE),
						groups=[self.all_sprites, self.soil_sprites],
						tile_type=tile_type) 