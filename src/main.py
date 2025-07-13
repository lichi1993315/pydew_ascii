import pygame
import sys
import os
from src.settings import *
from src.core.level import Level
from src.utils.font_manager import FontManager

class Game:
	"""
	主游戏类 - 纯ASCII模式农场模拟游戏
	"""
	def __init__(self):
		pygame.init()
		
		# 显式初始化音频混合器
		try:
			pygame.mixer.pre_init(frequency=22050, size=-16, channels=2, buffer=512)
			pygame.mixer.init()
		except pygame.error as e:
			print(f"⚠️ 音频初始化失败: {e}")
			print("游戏将在无音频模式下运行")
		
		self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
		pygame.display.set_caption('萌爪钓鱼 AI Demo ')
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
		title = self.font.render('Pawfishing AI Demo', True, (255, 255, 255))
		title_rect = title.get_rect(center=(SCREEN_WIDTH//2, SCREEN_HEIGHT//3))
		self.screen.blit(title, title_rect)
		
		# 副标题
		subtitle = self.small_font.render('ASCII Style Fishing Game', True, (200, 200, 200))
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
			'使用ASCII字符渲染的钓鱼游戏',
			'@ = 玩家  T = 树木  * = 花朵  ~ = 水',
			'C键打开聊天面板  靠近NPC聊天',
			'支持连续对话和滚动查看历史  ESC键返回主菜单'
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
			
			# 优先处理猫咪详情UI输入
			if self.level and self.level.cat_info_ui.handle_input(event):
				continue  # 如果猫咪详情UI处理了输入，跳过其他处理
			
			# 处理聊天面板输入
			if self.level and self.level.chat_panel.handle_input(event):
				continue  # 如果聊天系统处理了输入，跳过其他处理
			
			if event.type == pygame.KEYDOWN:
				if event.key == pygame.K_ESCAPE:
					self.show_menu = True
					self.level = None
				elif event.key == pygame.K_c:
					# C键切换聊天面板
					if self.level:
						self.level.chat_panel.toggle()
				elif self.level:
					# 处理NPC对话输入
					if self.level.handle_dialogue_input(event.key):
						continue  # 如果对话系统处理了输入，跳过其他处理
					
					# 处理T键交互
					if event.key == pygame.K_t:
						# 优先检查猫咪交互
						nearby_cat = self.level.check_cat_interaction()
						if nearby_cat:
							self.level.cat_info_ui.show_cat_info(nearby_cat, self.level.chat_ai)
						else:
							# 检查其他NPC交互
							nearby_npc = self.level.check_npc_interaction()
							if nearby_npc:
								self.level.start_npc_dialogue(nearby_npc)
					
					# 时间控制键
					if event.key == pygame.K_EQUALS or event.key == pygame.K_PLUS:
						# 增加时间速度
						current_speed = self.level.sky.time_speed
						if current_speed < 60.0:
							self.level.sky.set_time_speed(60.0)
						elif current_speed < 3600.0:
							self.level.sky.set_time_speed(3600.0)
						else:
							self.level.sky.set_time_speed(min(current_speed * 2, 10000.0))
					
					if event.key == pygame.K_MINUS:
						# 减少时间速度
						current_speed = self.level.sky.time_speed
						if current_speed > 3600.0:
							self.level.sky.set_time_speed(3600.0)
						elif current_speed > 60.0:
							self.level.sky.set_time_speed(60.0)
						elif current_speed > 1.0:
							self.level.sky.set_time_speed(1.0)
						else:
							self.level.sky.set_time_speed(max(current_speed * 0.5, 0.1))
					
					if event.key == pygame.K_0:
						# 重置时间速度为默认值
						self.level.sky.set_time_speed(60.0)
					
					if event.key == pygame.K_9:
						# 切换时间速度（循环）
						current_speed = self.level.sky.time_speed
						if current_speed <= 1.0:
							self.level.sky.set_time_speed(60.0)
						elif current_speed <= 60.0:
							self.level.sky.set_time_speed(3600.0)
						else:
							self.level.sky.set_time_speed(1.0)
		
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

def main():
	"""主函数入口"""
	game = Game()
	game.run()

if __name__ == '__main__':
	main()