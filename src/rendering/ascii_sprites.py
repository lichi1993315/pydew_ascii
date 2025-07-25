import pygame
from .sprites import Generic
from .ascii_renderer import ASCIIRenderer
from ..settings import TILE_SIZE, LAYERS

class ASCIIGeneric(Generic):
	"""
	ASCII版本的通用精灵类
	"""
	
	def __init__(self, pos, tile_type, groups, z=0, variant=0):
		super().__init__(pos, pygame.Surface((TILE_SIZE, TILE_SIZE)), groups, z)
		self.tile_type = tile_type
		self.variant = variant
		self.ascii_renderer = ASCIIRenderer()
		
		# 创建ASCII表面
		self.image = pygame.Surface((TILE_SIZE, TILE_SIZE), pygame.SRCALPHA)
		self.ascii_renderer.render_tile(self.image, tile_type, (0, 0), variant)
		
		# 根据瓦片类型设置合适的碰撞盒
		self.setup_hitbox()
	
	def setup_hitbox(self):
		"""
		根据瓦片类型设置合适的碰撞盒
		"""
		# 实体障碍物使用完整的碰撞盒
		solid_tiles = ['wall', 'fence', 'stone', 'tree']
		# 装饰物使用较小的碰撞盒
		decorative_tiles = ['flower', 'grass', 'crop']
		# 交互物品使用中等碰撞盒
		interactive_tiles = ['bed', 'npc']
		
		if self.tile_type in solid_tiles:
			# 实体障碍物：使用完整尺寸的碰撞盒
			self.hitbox = self.rect.copy()
		elif self.tile_type in decorative_tiles:
			# 装饰物：使用较小的碰撞盒（可以被踩踏）
			self.hitbox = self.rect.copy().inflate(-self.rect.width * 0.4, -self.rect.height * 0.8)
		elif self.tile_type in interactive_tiles:
			# 交互物品：使用稍小的碰撞盒
			self.hitbox = self.rect.copy().inflate(-self.rect.width * 0.1, -self.rect.height * 0.1)
		else:
			# 默认：使用原来的设置
			self.hitbox = self.rect.copy().inflate(-self.rect.width * 0.2, -self.rect.height * 0.75)
	
	def update_ascii(self, new_tile_type=None, new_variant=None):
		"""
		更新ASCII显示
		"""
		if new_tile_type:
			self.tile_type = new_tile_type
		if new_variant is not None:
			self.variant = new_variant
		
		# 重新渲染
		self.image.fill((0, 0, 0, 0))
		self.ascii_renderer.render_tile(self.image, self.tile_type, (0, 0), self.variant)

class ASCIIWater(ASCIIGeneric):
	"""
	ASCII版本的水精灵
	"""
	
	def __init__(self, pos, groups):
		super().__init__(pos, 'water', groups)
		self.animation_frame = 0
		self.animation_speed = 0.1
		self.animation_timer = 0
	
	def update(self, dt):
		"""
		更新水动画
		"""
		self.animation_timer += dt
		if self.animation_timer >= self.animation_speed:
			self.animation_timer = 0
			self.animation_frame += 1
			
			# 重新渲染水动画
			self.image.fill((0, 0, 0, 0))
			self.ascii_renderer.render_water_animation(self.image, (0, 0), self.animation_frame)

class ASCIIWildFlower(ASCIIGeneric):
	"""
	ASCII版本的野花精灵
	"""
	
	def __init__(self, pos, groups):
		# 随机选择花的变体
		import random
		variant = random.randint(0, 3)
		super().__init__(pos, 'flower', groups, variant=variant)
		
		# 动画相关属性
		self.animation_frame = 0
		self.animation_speed = 0.3  # 比水的动画稍慢一些
		self.animation_timer = 0
		
		# 随机化初始动画帧，让不同花朵的动画不同步
		self.animation_frame = random.randint(0, 3)
	
	def update(self, dt):
		"""
		更新花朵动画
		"""
		self.animation_timer += dt
		if self.animation_timer >= self.animation_speed:
			self.animation_timer = 0
			self.animation_frame += 1
			
			# 重新渲染花朵动画
			self.image.fill((0, 0, 0, 0))
			self.ascii_renderer.render_flower_animation(self.image, (0, 0), self.animation_frame, self.variant)

class ASCIITree(ASCIIGeneric):
	"""
	ASCII版本的树木精灵
	"""
	
	def __init__(self, pos, groups, name, player_add):
		super().__init__(pos, 'tree', groups)
		self.name = name
		self.player_add = player_add
		self.has_fruit = True
		self.fruit_count = 3
		
		# 重新渲染树木（包含果实）
		self.render_tree()
	
	def render_tree(self):
		"""
		渲染树木和果实
		"""
		self.image.fill((0, 0, 0, 0))
		
		# 渲染树干
		self.ascii_renderer.render_ascii(self.image, 'T', self.ascii_renderer.color_map['tree'], (0, 0))
		
		# 渲染果实
		if self.has_fruit and self.fruit_count > 0:
			# 在树干上方渲染果实
			self.ascii_renderer.render_ascii(self.image, 'o', self.ascii_renderer.color_map['apple'], (0, -8))
	
	def create_fruit(self):
		"""
		创建果实
		"""
		self.has_fruit = True
		self.fruit_count = 3
		self.render_tree()
	
	def harvest_fruit(self):
		"""
		收获果实
		"""
		if self.has_fruit and self.fruit_count > 0:
			self.fruit_count -= 1
			self.player_add('apple')
			
			if self.fruit_count <= 0:
				self.has_fruit = False
			
			self.render_tree()
	
	def damage(self):
		"""
		砍伐树木（使用斧头）
		"""
		# 在ASCII模式下，砍伐会掉落木材
		self.player_add('wood')
		self.kill()

class ASCIIInteraction(ASCIIGeneric):
	"""
	ASCII版本的交互精灵
	"""
	
	def __init__(self, pos, size, groups, name):
		super().__init__(pos, self.get_interaction_type(name), groups)
		self.name = name
		self.size = size
	
	def get_interaction_type(self, name):
		"""
		根据交互对象名称获取ASCII类型
		"""
		interaction_map = {
			'Bed': 'bed',
			'Trader': 'npc',
		}
		return interaction_map.get(name, '?')

class ASCIIParticle(ASCIIGeneric):
	"""
	ASCII版本的粒子效果精灵
	"""
	
	def __init__(self, pos, original_type, groups, z=0):
		super().__init__(pos, original_type, groups, z)
		self.lifetime = 1.0  # 1秒生命周期
		self.timer = 0
	
	def update(self, dt):
		"""
		更新粒子效果
		"""
		self.timer += dt
		if self.timer >= self.lifetime:
			self.kill()
		else:
			# 根据生命周期调整透明度
			alpha = int(255 * (1 - self.timer / self.lifetime))
			self.image.set_alpha(alpha)

class ASCIIPlayer(pygame.sprite.Sprite):
	"""
	ASCII版本的玩家精灵
	使用@字符显示玩家，支持不同状态和方向的显示
	"""
	
	def __init__(self, pos, groups):
		super().__init__(groups)
		self.ascii_renderer = ASCIIRenderer()
		
		# 创建ASCII表面
		self.image = pygame.Surface((64, 64), pygame.SRCALPHA)  # 玩家尺寸较大
		self.rect = self.image.get_rect(center=pos)
		self.z = LAYERS['main']
		
		# 玩家状态
		self.status = 'down_idle'
		self.frame_index = 0
		
		# ASCII字符映射 - 根据状态显示不同字符
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
		}
		
		# 渲染初始状态
		self.render_player()
	
	def render_player(self):
		"""
		渲染玩家ASCII字符
		"""
		self.image.fill((0, 0, 0, 0))
		
		# 获取当前状态对应的字符
		char = self.ascii_chars.get(self.status, '@')
		color = self.ascii_renderer.color_map['player']
		
		# 渲染到图像中心
		self.ascii_renderer.render_ascii(self.image, char, color, (16, 16), 32)
	
	def update_status(self, status):
		"""
		更新玩家状态并重新渲染
		"""
		if self.status != status:
			self.status = status
			self.render_player()
	
	def update(self, dt):
		"""
		更新玩家ASCII显示
		"""
		# 这里可以添加闪烁或其他动画效果
		pass 

class ASCIINPC(ASCIIGeneric):
	"""ASCII NPC精灵类"""
	def __init__(self, pos, npc_id, npc_manager, groups, z = LAYERS['main']):
		# 从NPC管理器获取NPC数据
		npc = npc_manager.get_npc(npc_id)
		if npc:
			ascii_char = npc.ascii_char
		else:
			ascii_char = '&'  # 默认字符
		
		# 调用父类构造函数
		super().__init__(pos, ascii_char, groups, z)
		
		# NPC相关属性
		self.npc_id = npc_id
		self.npc_manager = npc_manager
		
		# 设置碰撞盒
		self.hitbox = self.rect.copy().inflate(-self.rect.width * 0.2, -self.rect.height * 0.75)
		
	def interact(self, player):
		"""与NPC交互"""
		if self.npc_manager:
			return self.npc_manager.interact_with_npc(self.npc_id, player)
		return []


class ASCIIHouse(pygame.sprite.Sprite):
	"""
	ASCII版本的房屋精灵类
	"""
	
	def __init__(self, pos, house_type, groups, z=LAYERS['main']):
		super().__init__(groups)
		
		# 基本设置
		self.image = pygame.Surface((TILE_SIZE, TILE_SIZE), pygame.SRCALPHA)
		self.rect = self.image.get_rect(topleft=pos)
		self.z = z
		self.house_type = house_type
		
		# ASCII渲染器
		self.ascii_renderer = ASCIIRenderer()
		
		# 渲染房屋部件
		self.ascii_renderer.render_house(self.image, (0, 0), house_type)
		
		# 根据房屋类型设置碰撞盒
		self.setup_hitbox()
	
	def setup_hitbox(self):
		"""
		根据房屋类型设置碰撞盒
		"""
		if self.house_type in ['wall', 'door']:
			# 墙和门有碰撞
			self.hitbox = self.rect.copy()
		elif self.house_type in ['window']:
			# 窗户也有碰撞（不能穿越）
			self.hitbox = self.rect.copy()
		else:
			# 地板、屋顶等没有碰撞
			self.hitbox = pygame.Rect(0, 0, 0, 0) 