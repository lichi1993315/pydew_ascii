import pygame
import sys
import os
from settings import *
from level import Level
from font_manager import FontManager

class Game:
	"""
	主游戏类 - 纯ASCII模式农场模拟游戏
	"""
	def __init__(self):
		pygame.init()
		self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
		pygame.display.set_caption('农场模拟游戏 - ASCII模式')
		self.clock = pygame.time.Clock()
		
		# 游戏状态
		self.level = None
		self.show_menu = True
		
		# 初始化字体管理器并加载字体
		self.font_manager = FontManager.get_instance()
		self.font = self.font_manager.load_chinese_font(36, "menu_large")
		self.small_font = self.font_manager.load_chinese_font(24, "menu_small")
		
		# 开始游戏按钮
		self.start_button = pygame.Rect(SCREEN_WIDTH//2 - 100, SCREEN_HEIGHT//2 - 25, 200, 50)
		self.quit_button = pygame.Rect(SCREEN_WIDTH//2 - 100, SCREEN_HEIGHT//2 + 50, 200, 50)
	
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
		subtitle = self.small_font.render('ASCII矮人要塞风格', True, (200, 200, 200))
		subtitle_rect = subtitle.get_rect(center=(SCREEN_WIDTH//2, SCREEN_HEIGHT//3 + 40))
		self.screen.blit(subtitle, subtitle_rect)
		
		# 开始游戏按钮
		pygame.draw.rect(self.screen, (100, 100, 100), self.start_button)
		pygame.draw.rect(self.screen, (255, 255, 255), self.start_button, 2)
		start_text = self.font.render('开始游戏', True, (255, 255, 255))
		start_rect = start_text.get_rect(center=self.start_button.center)
		self.screen.blit(start_text, start_rect)
		
		# 退出游戏按钮
		pygame.draw.rect(self.screen, (100, 100, 100), self.quit_button)
		pygame.draw.rect(self.screen, (255, 255, 255), self.quit_button, 2)
		quit_text = self.font.render('退出游戏', True, (255, 255, 255))
		quit_rect = quit_text.get_rect(center=self.quit_button.center)
		self.screen.blit(quit_text, quit_rect)
		
		# 说明文字
		desc_lines = [
			'使用ASCII字符渲染的农场模拟游戏',
			'@ = 玩家  T = 树木  * = 花朵  ~ = 水',
			'ESC键返回主菜单'
		]
		
		for i, line in enumerate(desc_lines):
			desc = self.small_font.render(line, True, (150, 150, 150))
			desc_rect = desc.get_rect(center=(SCREEN_WIDTH//2, SCREEN_HEIGHT//2 + 120 + i*25))
			self.screen.blit(desc, desc_rect)
	
	def handle_menu_events(self):
		"""
		处理菜单事件
		"""
		for event in pygame.event.get():
			if event.type == pygame.QUIT:
				return False
			
			if event.type == pygame.MOUSEBUTTONDOWN:
				if self.start_button.collidepoint(event.pos):
					self.start_game()
				elif self.quit_button.collidepoint(event.pos):
					return False
			
			if event.type == pygame.KEYDOWN:
				if event.key == pygame.K_RETURN:
					self.start_game()
				elif event.key == pygame.K_ESCAPE:
					return False
		
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
		
		return True
	
	def start_game(self):
		"""
		开始游戏（ASCII模式）
		"""
		self.show_menu = False
		self.level = Level()
	
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
			
			pygame.display.flip()
		
		pygame.quit()
		sys.exit()

if __name__ == '__main__':
	game = Game()
	game.run()