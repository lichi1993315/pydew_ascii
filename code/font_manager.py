import os
import pygame

class FontManager:
	"""
	字体管理器 - 统一管理所有字体的加载
	确保每个字体只加载一次，避免重复加载
	"""
	_instance = None
	_fonts = {}
	
	def __new__(cls):
		if cls._instance is None:
			cls._instance = super(FontManager, cls).__new__(cls)
		return cls._instance
	
	def __init__(self):
		if not hasattr(self, 'initialized'):
			self.initialized = True
			self._fonts = {}
			print("字体管理器初始化")
	
	def load_chinese_font(self, size, font_key=None):
		"""
		加载支持中文的字体
		"""
		if font_key is None:
			font_key = f"chinese_{size}"
		
		# 如果已经加载过，直接返回
		if font_key in self._fonts:
			return self._fonts[font_key]
		
		font_path = '../font/AlimamaShuHeiTi-Bold.ttf'
		font_loaded = False
		font = None
		
		try:
			if os.path.exists(font_path):
				font = pygame.font.Font(font_path, size)
				print(f"字体加载成功: {font_path} (大小: {size})")
				font_loaded = True
			else:
				print(f"字体文件不存在: {font_path}")
		except Exception as e:
			print(f"字体加载失败: {e}")
		
		if not font_loaded:
			try:
				font = pygame.font.SysFont('microsoftyahei', size)
				print(f"使用系统微软雅黑字体 (大小: {size})")
				font_loaded = True
			except Exception as e:
				print(f"系统字体加载失败: {e}")
		
		if not font_loaded:
			try:
				font = pygame.font.Font(None, size)
				print(f"使用系统默认字体 (大小: {size})")
			except Exception as e:
				print(f"默认字体加载失败: {e}")
		
		# 测试中文渲染
		try:
			test_surface = font.render("测试中文", True, (255,255,255))
			print(f"中文渲染测试成功 (大小: {size})")
		except Exception as e:
			print(f"中文渲染测试失败: {e}")
		
		# 缓存字体
		self._fonts[font_key] = font
		return font
	
	def load_emoji_font(self, size, font_key=None):
		"""
		加载支持emoji的字体
		优先使用系统emoji字体
		"""
		if font_key is None:
			font_key = f"emoji_{size}"
		
		# 如果已经加载过，直接返回
		if font_key in self._fonts:
			return self._fonts[font_key]
		
		font = None
		font_loaded = False
		
		# 尝试系统emoji字体
		emoji_fonts = [
			'segoe-ui-emoji',  # Windows
			'apple-color-emoji',  # macOS
			'noto-color-emoji',  # Linux
		]
		
		for font_name in emoji_fonts:
			try:
				font = pygame.font.SysFont(font_name, size)
				# 测试emoji渲染
				test_surface = font.render("🐈", True, (255, 255, 255))
				if test_surface.get_width() > 0:
					print(f"Emoji字体加载成功: {font_name} (大小: {size})")
					font_loaded = True
					break
			except Exception as e:
				continue
		
		# 如果系统emoji字体都失败，使用默认字体
		if not font_loaded:
			try:
				font = pygame.font.Font(None, size)
				print(f"使用默认字体作为emoji字体 (大小: {size})")
			except Exception as e:
				print(f"Emoji字体加载完全失败: {e}")
				# 回退到中文字体
				return self.load_chinese_font(size)
		
		# 缓存字体
		self._fonts[font_key] = font
		return font
	
	def get_font(self, font_key):
		"""
		获取已加载的字体
		"""
		return self._fonts.get(font_key)
	
	@classmethod
	def get_instance(cls):
		"""
		获取字体管理器实例
		"""
		if cls._instance is None:
			cls._instance = cls()
		return cls._instance 