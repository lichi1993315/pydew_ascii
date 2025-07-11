import os
import pygame
from settings import *
from font_manager import FontManager

class ASCIIRenderer:
	"""
	ASCII渲染器 - 将游戏对象渲染为ASCII字符
	参考矮人要塞的视觉风格
	"""
	
	def __init__(self):
		# 使用字体管理器获取字体
		font_manager = FontManager.get_instance()
		self.font = font_manager.load_chinese_font(16, "ascii_renderer")
		self.emoji_font = font_manager.load_emoji_font(16, "ascii_emoji_renderer")
		self.tile_size = 16  # ASCII字符大小
		
		# ASCII字符映射表 - 参考矮人要塞风格
		self.ascii_map = {
			# 地形
			'grass': '.',      # 草地
			'water': '~',      # 水
			'stone': '#',      # 石头
			'dirt': ',',       # 泥土
			'sand': ':',       # 沙子
			
			# 植物
			'tree': 'T',       # 大树
			'sapling': 't',    # 小树
			'bush': 'b',       # 灌木
			'flower': '*',     # 花
			'mushroom': 'm',   # 蘑菇
			'crop': 'c',       # 农作物
			
			# 建筑
			'wall': '#',       # 墙
			'floor': '.',      # 地板
			'door': '+',       # 门
			'window': '=',     # 窗户
			'fence': '|',      # 栅栏
			
			# 角色
			'player': '@',     # 玩家
			'npc': '&',        # NPC
			'animal': 'a',     # 动物
			
			# 物品
			'apple': 'o',      # 苹果
			'fruit': 'f',      # 水果
			'seed': 's',       # 种子
			'tool': 'w',       # 工具
			
			# 特殊
			'bed': '=',        # 床
			'chest': 'C',      # 箱子
			'stump': 'S',      # 树桩
			'rock': 'r',       # 岩石
		}
		
		# 颜色映射表
		self.color_map = {
			# 地形颜色
			'grass': (34, 139, 34),      # 绿色
			'water': (0, 191, 255),      # 蓝色
			'stone': (105, 105, 105),    # 灰色
			'dirt': (139, 69, 19),       # 棕色
			'sand': (238, 203, 173),     # 沙色
			
			# 植物颜色
			'tree': (0, 100, 0),         # 深绿色
			'sapling': (34, 139, 34),    # 绿色
			'bush': (85, 107, 47),       # 橄榄绿
			'flower': (255, 20, 147),    # 粉色
			'mushroom': (255, 0, 0),     # 红色
			'crop': (255, 215, 0),       # 金色
			
			# 建筑颜色
			'wall': (139, 69, 19),       # 棕色
			'floor': (160, 82, 45),      # 棕色
			'door': (139, 69, 19),       # 棕色
			'window': (135, 206, 235),   # 天蓝色
			'fence': (139, 69, 19),      # 棕色
			
			# 角色颜色
			'player': (255, 255, 255),   # 白色
			'npc': (255, 255, 0),        # 黄色
			'animal': (255, 140, 0),     # 橙色
			
			# 物品颜色
			'apple': (255, 0, 0),        # 红色
			'fruit': (255, 165, 0),      # 橙色
			'seed': (139, 69, 19),       # 棕色
			'tool': (192, 192, 192),     # 银色
			
			# 特殊颜色
			'bed': (255, 228, 196),      # 米色
			'chest': (139, 69, 19),      # 棕色
			'stump': (101, 67, 33),      # 深棕色
			'rock': (105, 105, 105),     # 灰色
		}
	
	def _is_emoji(self, char):
		"""检查字符是否为emoji"""
		# 简单的emoji检测 - 检查Unicode范围
		if len(char) == 0:
			return False
		
		code_point = ord(char[0]) if len(char) == 1 else ord(char)
		
		# 常见emoji Unicode范围
		emoji_ranges = [
			(0x1F600, 0x1F64F),  # Emoticons
			(0x1F300, 0x1F5FF),  # Misc Symbols and Pictographs
			(0x1F680, 0x1F6FF),  # Transport and Map
			(0x1F1E0, 0x1F1FF),  # Regional indicator symbols
			(0x2600, 0x26FF),    # Misc symbols
			(0x2700, 0x27BF),    # Dingbats
			(0xFE00, 0xFE0F),    # Variation selectors
			(0x1F900, 0x1F9FF),  # Supplemental Symbols and Pictographs
		]
		
		return any(start <= code_point <= end for start, end in emoji_ranges)
	
	def render_ascii(self, surface, char, color, pos, size=None):
		"""
		渲染ASCII字符到指定位置
		智能选择emoji字体或普通字体
		"""
		if size is None:
			size = self.tile_size
		
		# 选择合适的字体
		if self._is_emoji(char):
			selected_font = self.emoji_font
		else:
			selected_font = self.font
		
		try:
			# 创建文本表面
			text_surface = selected_font.render(char, True, color)
			
			# 检查渲染结果
			if text_surface.get_width() == 0:
				# 如果emoji字体渲染失败，回退到普通字体
				if self._is_emoji(char):
					text_surface = self.font.render(char, True, color)
			
			# 计算居中位置
			text_rect = text_surface.get_rect()
			text_rect.center = (pos[0] + size // 2, pos[1] + size // 2)
			
			# 绘制到目标表面
			surface.blit(text_surface, text_rect)
			
		except Exception as e:
			print(f"字符渲染失败 '{char}': {e}")
			# 尝试用备用字符渲染
			try:
				fallback_char = "?" if not self._is_emoji(char) else "🐱"
				text_surface = self.font.render(fallback_char, True, color)
				text_rect = text_surface.get_rect()
				text_rect.center = (pos[0] + size // 2, pos[1] + size // 2)
				surface.blit(text_surface, text_rect)
			except:
				pass  # 完全失败时什么都不做
	
	def get_ascii_char(self, tile_type, variant=0):
		"""
		根据瓦片类型获取ASCII字符
		"""
		base_char = self.ascii_map.get(tile_type, '?')
		
		# 根据变体调整字符
		if variant > 0:
			variants = {
				'grass': ['.', ',', '`', "'"],
				'water': ['~', '≈', '≈', '≈'],
				'tree': ['T', 't', 'Y', 'y'],
				'flower': ['*', '✿', '✾', '✽'],
				'mushroom': ['m', 'M', 'n', 'N'],
			}
			
			if tile_type in variants:
				variant_chars = variants[tile_type]
				return variant_chars[variant % len(variant_chars)]
		
		return base_char
	
	def get_color(self, tile_type, variant=0):
		"""
		根据瓦片类型获取颜色
		"""
		base_color = self.color_map.get(tile_type, (255, 255, 255))
		
		# 根据变体调整颜色亮度
		if variant > 0:
			r, g, b = base_color
			# 稍微调整亮度
			factor = 0.9 + (variant * 0.1)
			r = min(255, int(r * factor))
			g = min(255, int(g * factor))
			b = min(255, int(b * factor))
			return (r, g, b)
		
		return base_color
	
	def render_tile(self, surface, tile_type, pos, variant=0):
		"""
		渲染单个瓦片
		"""
		char = self.get_ascii_char(tile_type, variant)
		color = self.get_color(tile_type, variant)
		self.render_ascii(surface, char, color, pos)
	
	def render_water_animation(self, surface, pos, frame):
		"""
		渲染水动画效果
		"""
		water_chars = ['~', '≈', '≈', '~']
		char = water_chars[frame % len(water_chars)]
		color = self.color_map['water']
		self.render_ascii(surface, char, color, pos)
	
	def render_tree(self, surface, pos, tree_type='tree', has_fruit=False):
		"""
		渲染树木
		"""
		# 渲染树干
		self.render_ascii(surface, 'T', self.color_map['tree'], pos)
		
		# 如果有果实，在树干上方渲染果实
		if has_fruit:
			fruit_pos = (pos[0], pos[1] - self.tile_size)
			self.render_ascii(surface, 'o', self.color_map['apple'], fruit_pos)
	
	def render_plant(self, surface, pos, growth_stage):
		"""
		渲染植物（根据生长阶段）
		"""
		stages = ['s', 'c', 'C', '*']  # 种子 -> 幼苗 -> 成熟 -> 开花
		if growth_stage < len(stages):
			char = stages[growth_stage]
			color = self.color_map['crop']
			self.render_ascii(surface, char, color, pos)
	
	def render_house(self, surface, pos, part_type):
		"""
		渲染房屋部件
		"""
		house_parts = {
			'wall': ('#', 'wall'),
			'floor': ('.', 'floor'),
			'door': ('+', 'door'),
			'window': ('=', 'window'),
			'roof': ('^', 'wall'),
		}
		
		if part_type in house_parts:
			char, color_key = house_parts[part_type]
			color = self.color_map[color_key]
			self.render_ascii(surface, char, color, pos) 