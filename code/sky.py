import pygame 
from settings import *
from random import randint, choice

class Sky:
	def __init__(self):
		self.display_surface = pygame.display.get_surface()
		self.full_surf = pygame.Surface((SCREEN_WIDTH,SCREEN_HEIGHT))
		self.start_color = [255,255,255]
		self.end_color = (38,101,189)

	def display(self, dt):
		for index, value in enumerate(self.end_color):
			if self.start_color[index] > value:
				self.start_color[index] -= 2 * dt

		self.full_surf.fill(self.start_color)
		self.display_surface.blit(self.full_surf, (0,0), special_flags = pygame.BLEND_RGBA_MULT)

# Drop类已移除 - ASCII模式下直接使用ASCIIGeneric

class Rain:
	def __init__(self, all_sprites):
		self.all_sprites = all_sprites
		# ASCII模式下不需要加载图片，使用预设尺寸
		self.floor_w, self.floor_h = 1280, 768  # 使用固定地图尺寸

	def create_floor(self):
		# ASCII模式下创建ASCII雨滴精灵
		from ascii_sprites import ASCIIGeneric
		ASCIIGeneric(
			pos = (randint(0,self.floor_w),randint(0,self.floor_h)), 
			tile_type = 'water',
			groups = [self.all_sprites], 
			z = LAYERS['rain floor'])

	def create_drops(self):
		# ASCII模式下创建ASCII雨滴精灵
		from ascii_sprites import ASCIIGeneric
		ASCIIGeneric(
			pos = (randint(0,self.floor_w),randint(0,self.floor_h)), 
			tile_type = 'water',
			groups = [self.all_sprites], 
			z = LAYERS['rain drops'])

	def update(self):
		self.create_floor()
		self.create_drops()