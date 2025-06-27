import pygame
from settings import *
from font_manager import FontManager

class Overlay:
	def __init__(self, player):
		# general setup
		self.display_surface = pygame.display.get_surface()
		self.player = player
		
		# 字体设置
		font_manager = FontManager.get_instance()
		self.font = font_manager.load_chinese_font(24, "overlay_font")
		self.small_font = font_manager.load_chinese_font(18, "overlay_small_font")
		
		# 工具和种子的中文名称映射
		self.tool_names = {
			'hoe': '锄头',
			'axe': '斧子', 
			'water': '水壶'
		}
		
		self.seed_names = {
			'corn': '玉米种子',
			'tomato': '番茄种子'
		}
		
		# 颜色设置
		self.text_color = (255, 255, 255)
		self.bg_color = (0, 0, 0, 128)  # 半透明黑色背景
		self.selected_color = (255, 215, 0)  # 金色高亮
		self.border_color = (100, 100, 100)

	def draw_text_box(self, text, pos, font, text_color, bg_color=None, border_color=None):
		"""
		绘制带背景的文本框
		"""
		# 渲染文本
		text_surface = font.render(text, True, text_color)
		text_rect = text_surface.get_rect()
		
		# 设置位置
		text_rect.midbottom = pos
		
		# 如果有背景色，绘制背景
		if bg_color:
			padding = 8
			bg_rect = text_rect.inflate(padding * 2, padding * 2)
			
			# 创建半透明背景
			bg_surface = pygame.Surface((bg_rect.width, bg_rect.height))
			bg_surface.set_alpha(bg_color[3] if len(bg_color) == 4 else 255)
			bg_surface.fill(bg_color[:3])
			
			self.display_surface.blit(bg_surface, bg_rect)
			
			# 绘制边框
			if border_color:
				pygame.draw.rect(self.display_surface, border_color, bg_rect, 2)
		
		# 绘制文本
		self.display_surface.blit(text_surface, text_rect)
		
		return text_rect

	def display(self):
		# 显示当前工具
		tool_name = self.tool_names.get(self.player.selected_tool, self.player.selected_tool)
		tool_text = f"当前工具: {tool_name} [Q键切换]"
		
		self.draw_text_box(
			tool_text, 
			OVERLAY_POSITIONS['tool'], 
			self.font,
			self.selected_color,
			self.bg_color,
			self.border_color
		)
		
		# 显示当前种子
		seed_name = self.seed_names.get(self.player.selected_seed, self.player.selected_seed)
		seed_count = self.player.seed_inventory.get(self.player.selected_seed, 0)
		seed_text = f"当前种子: {seed_name} x{seed_count} [E键切换]"
		
		self.draw_text_box(
			seed_text,
			OVERLAY_POSITIONS['seed'],
			self.font, 
			self.selected_color,
			self.bg_color,
			self.border_color
		)
		
		# 显示操作提示
		control_tips = [
			"【操作说明】",
			"空格键: 使用工具",
			"左Ctrl: 种植种子", 
			"方向键: 移动角色",
			"回车键: 交互/睡觉"
		]
		
		# 在屏幕右上角显示控制提示
		for i, tip in enumerate(control_tips):
			# 渲染文本
			color = (255, 255, 255) if i == 0 else (180, 180, 180)
			font = self.font if i == 0 else self.small_font
			text_surface = font.render(tip, True, color)
			text_rect = text_surface.get_rect()
			text_rect.topright = (SCREEN_WIDTH - 20, 40 + i * 22)
			
			# 如果是标题，添加背景
			if i == 0:
				padding = 6
				bg_rect = text_rect.inflate(padding * 2, padding * 2)
				bg_surface = pygame.Surface((bg_rect.width, bg_rect.height))
				bg_surface.set_alpha(80)
				bg_surface.fill((0, 0, 0))
				self.display_surface.blit(bg_surface, bg_rect)
				pygame.draw.rect(self.display_surface, self.border_color, bg_rect, 1)
			
			# 绘制文本
			self.display_surface.blit(text_surface, text_rect)