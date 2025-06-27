import pygame
import sys
import os
from settings import *
from level import Level
from font_manager import FontManager

class Game:
	"""
	主游戏类
	"""
	def __init__(self):
		pygame.init()
		self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
		pygame.display.set_caption('农场模拟游戏 - ASCII/图片模式')
		self.clock = pygame.time.Clock()
		
		# 游戏状态
		self.ascii_mode = False
		self.level = None
		self.show_menu = True
		
		# 初始化字体管理器并加载字体
		self.font_manager = FontManager.get_instance()
		self.font = self.font_manager.load_chinese_font(36, "menu_large")
		self.small_font = self.font_manager.load_chinese_font(24, "menu_small")
		
		# 按钮
		self.ascii_button = pygame.Rect(SCREEN_WIDTH//2 - 100, SCREEN_HEIGHT//2 - 50, 200, 50)
		self.image_button = pygame.Rect(SCREEN_WIDTH//2 - 100, SCREEN_HEIGHT//2 + 20, 200, 50)
		self.toggle_button = pygame.Rect(SCREEN_WIDTH - 150, 10, 140, 30)
	
	def draw_menu(self):
		"""
		绘制主菜单
		"""
		self.screen.fill((0, 0, 0))
		
		# 标题
		title = self.font.render('农场模拟游戏', True, (255, 255, 255))
		title_rect = title.get_rect(center=(SCREEN_WIDTH//2, SCREEN_HEIGHT//3))
		self.screen.blit(title, title_rect)
		
		# 副标题
		subtitle = self.small_font.render('选择游戏模式', True, (200, 200, 200))
		subtitle_rect = subtitle.get_rect(center=(SCREEN_WIDTH//2, SCREEN_HEIGHT//3 + 40))
		self.screen.blit(subtitle, subtitle_rect)
		
		# ASCII模式按钮
		pygame.draw.rect(self.screen, (100, 100, 100), self.ascii_button)
		pygame.draw.rect(self.screen, (255, 255, 255), self.ascii_button, 2)
		ascii_text = self.font.render('ASCII模式', True, (255, 255, 255))
		ascii_rect = ascii_text.get_rect(center=self.ascii_button.center)
		self.screen.blit(ascii_text, ascii_rect)
		
		# 图片模式按钮
		pygame.draw.rect(self.screen, (100, 100, 100), self.image_button)
		pygame.draw.rect(self.screen, (255, 255, 255), self.image_button, 2)
		image_text = self.font.render('图片模式', True, (255, 255, 255))
		image_rect = image_text.get_rect(center=self.image_button.center)
		self.screen.blit(image_text, image_rect)
		
		# 说明文字
		ascii_desc = self.small_font.render('矮人要塞风格，使用ASCII字符', True, (150, 150, 150))
		ascii_desc_rect = ascii_desc.get_rect(center=(SCREEN_WIDTH//2, SCREEN_HEIGHT//2 + 80))
		self.screen.blit(ascii_desc, ascii_desc_rect)
		
		image_desc = self.small_font.render('传统像素风格，使用精美图片', True, (150, 150, 150))
		image_desc_rect = image_desc.get_rect(center=(SCREEN_WIDTH//2, SCREEN_HEIGHT//2 + 110))
		self.screen.blit(image_desc, image_desc_rect)
	
	def draw_toggle_button(self):
		"""
		绘制模式切换按钮
		"""
		pygame.draw.rect(self.screen, (50, 50, 50), self.toggle_button)
		pygame.draw.rect(self.screen, (255, 255, 255), self.toggle_button, 2)
		
		mode_text = 'ASCII' if self.ascii_mode else '图片'
		toggle_text = self.small_font.render(f'切换: {mode_text}', True, (255, 255, 255))
		toggle_rect = toggle_text.get_rect(center=self.toggle_button.center)
		self.screen.blit(toggle_text, toggle_rect)
	
	def handle_menu_events(self):
		"""
		处理菜单事件
		"""
		for event in pygame.event.get():
			if event.type == pygame.QUIT:
				return False
			
			if event.type == pygame.MOUSEBUTTONDOWN:
				if self.ascii_button.collidepoint(event.pos):
					self.ascii_mode = True
					self.start_game()
				elif self.image_button.collidepoint(event.pos):
					self.ascii_mode = False
					self.start_game()
		
		return True
	
	def handle_game_events(self):
		"""
		处理游戏事件
		"""
		for event in pygame.event.get():
			if event.type == pygame.QUIT:
				return False
			
			if event.type == pygame.KEYDOWN:
				if event.key == pygame.K_ESCAPE:
					self.show_menu = True
					self.level = None
			
			if event.type == pygame.MOUSEBUTTONDOWN:
				if self.toggle_button.collidepoint(event.pos):
					self.toggle_mode()
		
		return True
	
	def start_game(self):
		"""
		开始游戏
		"""
		self.show_menu = False
		self.level = Level(ascii_mode=self.ascii_mode)
	
	def toggle_mode(self):
		"""
		切换游戏模式
		"""
		self.ascii_mode = not self.ascii_mode
		self.level = Level(ascii_mode=self.ascii_mode)
	
	def run(self):
		"""
		主游戏循环
		"""
		running = True
		
		while running:
			dt = self.clock.tick(60) / 1000
			
			if self.show_menu:
				running = self.handle_menu_events()
				self.draw_menu()
			else:
				running = self.handle_game_events()
				if self.level:
					self.level.run(dt)
					self.draw_toggle_button()
			
			pygame.display.flip()
		
		pygame.quit()
		sys.exit()

if __name__ == '__main__':
	game = Game()
	game.run()