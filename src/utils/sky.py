import pygame 
from ..settings import *
from random import randint, choice

class Sky:
	def __init__(self):
		self.display_surface = pygame.display.get_surface()
		self.full_surf = pygame.Surface((SCREEN_WIDTH,SCREEN_HEIGHT))
		
		# 时间系统设置
		self.game_hour = 6    # 游戏开始时间：早上6点
		self.game_minute = 0  # 游戏开始分钟：0分
		self.time_speed = 60.0 # 时间流逝速度（60.0 = 1游戏分钟 = 1现实秒）
		self.time_accumulator = 0.0  # 时间累积器
		
		# 昼夜循环颜色管理
		self.current_color = [255, 255, 255]  # 当前颜色
		self.day_color = [255, 255, 255]      # 白天颜色（中午12点）
		self.night_color = [38, 101, 189]     # 夜晚颜色（午夜0点）
		
		# 日出日落时间定义
		self.sunrise_hour = 6   # 日出时间：6点
		self.sunset_hour = 18   # 日落时间：18点
		
		# 初始化颜色
		self.update_color_based_on_time()

	def display(self, dt):
		# 更新游戏时间
		self.update_time(dt)
		
		# 根据当前时间更新颜色
		self.update_color_based_on_time()
		
		# 渲染天空
		self.full_surf.fill(self.current_color)
		self.display_surface.blit(self.full_surf, (0,0), special_flags = pygame.BLEND_RGBA_MULT)
	
	def update_time(self, dt):
		"""
		更新游戏时间
		dt: 现实时间增量（秒）
		time_speed: 时间流逝倍数（60.0 = 1现实秒 = 1游戏分钟）
		"""
		# 累积时间，基于时间速度
		self.time_accumulator += dt * self.time_speed
		
		# 当累积器达到1.0时，增加1分钟
		if self.time_accumulator >= 1.0:
			# 增加分钟数
			minutes_to_add = int(self.time_accumulator)
			self.time_accumulator -= minutes_to_add
			
			old_time = f"{self.game_hour:02d}:{self.game_minute:02d}"
			
			self.game_minute += minutes_to_add
			
			# 处理分钟溢出
			if self.game_minute >= 60:
				self.game_hour += self.game_minute // 60
				self.game_minute = self.game_minute % 60
				
				# 处理小时溢出（24小时制）
				if self.game_hour >= 24:
					self.game_hour = self.game_hour % 24
			
			# 调试输出（可以注释掉）
			# new_time = f"{self.game_hour:02d}:{self.game_minute:02d}"
			# if minutes_to_add > 0:
			# 	print(f"[时间系统] 时间更新: {old_time} -> {new_time} ({self.get_time_period()})")
	
	def update_color_based_on_time(self):
		"""
		根据当前时间计算天空颜色
		"""
		# 计算当前时间在一天中的位置（0-1）
		current_time_minutes = self.game_hour * 60 + self.game_minute
		
		# 定义关键时间点（分钟）
		dawn_start = 5 * 60      # 5:00 黎明开始
		sunrise = 6 * 60         # 6:00 日出
		noon = 12 * 60          # 12:00 中午
		sunset = 18 * 60        # 18:00 日落
		dusk_end = 19 * 60      # 19:00 黄昏结束
		
		# 根据时间段计算颜色
		if dawn_start <= current_time_minutes < sunrise:
			# 黎明时段（5:00-6:00）：从夜晚颜色渐变到白天颜色
			progress = (current_time_minutes - dawn_start) / (sunrise - dawn_start)
			self.current_color = self.interpolate_color(self.night_color, self.day_color, progress)
			
		elif sunrise <= current_time_minutes < sunset:
			# 白天时段（6:00-18:00）：保持白天颜色
			self.current_color = self.day_color.copy()
			
		elif sunset <= current_time_minutes < dusk_end:
			# 黄昏时段（18:00-19:00）：从白天颜色渐变到夜晚颜色
			progress = (current_time_minutes - sunset) / (dusk_end - sunset)
			self.current_color = self.interpolate_color(self.day_color, self.night_color, progress)
			
		else:
			# 夜晚时段（19:00-5:00）：保持夜晚颜色
			self.current_color = self.night_color.copy()
	
	def interpolate_color(self, color1, color2, progress):
		"""
		在两个颜色之间进行线性插值
		"""
		progress = max(0, min(1, progress))  # 确保progress在0-1之间
		result = []
		for i in range(3):  # RGB三个通道
			value = color1[i] + (color2[i] - color1[i]) * progress
			result.append(int(value))
		return result
	
	def get_time_of_day(self):
		"""
		获取当前时间（HH:MM格式）
		"""
		return f"{self.game_hour:02d}:{self.game_minute:02d}"
	
	def get_time_period(self):
		"""
		获取当前时间段状态
		返回值：'day', 'night', 'dawn', 'dusk'
		"""
		current_time_minutes = self.game_hour * 60 + self.game_minute
		
		# 定义时间段
		dawn_start = 5 * 60      # 5:00 黎明开始
		sunrise = 6 * 60         # 6:00 日出
		sunset = 18 * 60        # 18:00 日落
		dusk_end = 19 * 60      # 19:00 黄昏结束
		
		if dawn_start <= current_time_minutes < sunrise:
			return 'dawn'      # 黎明
		elif sunrise <= current_time_minutes < sunset:
			return 'day'       # 白天
		elif sunset <= current_time_minutes < dusk_end:
			return 'dusk'      # 黄昏
		else:
			return 'night'     # 夜晚
	
	def is_day_time(self):
		"""
		判断当前是否为白天
		"""
		return self.sunrise_hour <= self.game_hour < self.sunset_hour
	
	def get_brightness_factor(self):
		"""
		获取当前亮度因子（0.0 - 1.0）
		0.0 = 完全夜晚, 1.0 = 完全白天
		"""
		# 基于当前颜色的平均值计算亮度
		current_brightness = sum(self.current_color) / 3
		day_brightness = sum(self.day_color) / 3
		night_brightness = sum(self.night_color) / 3
		
		# 归一化到0-1范围
		brightness_range = day_brightness - night_brightness
		if brightness_range == 0:
			return 1.0
		
		return (current_brightness - night_brightness) / brightness_range
	
	def set_time_speed(self, speed):
		"""
		设置时间流逝速度
		speed: 时间速度倍数（1.0 = 正常速度, 60.0 = 1现实秒=1游戏分钟）
		"""
		self.time_speed = max(0.1, speed)
		print(f"[时间系统] 时间速度设置为: {self.get_time_speed_description()}")
	
	def get_time_speed_description(self):
		"""
		获取时间速度的描述
		"""
		if self.time_speed == 1.0:
			return "正常速度 (1现实秒 = 1游戏秒)"
		elif self.time_speed == 60.0:
			return "快速 (1现实秒 = 1游戏分钟)"
		elif self.time_speed == 3600.0:
			return "极快 (1现实秒 = 1游戏小时)"
		else:
			return f"自定义速度 ({self.time_speed}x)"
	
	def force_time(self, hour, minute=0):
		"""
		强制设置游戏时间
		hour: 小时（0-23）
		minute: 分钟（0-59）
		"""
		self.game_hour = hour % 24
		self.game_minute = minute % 60
		self.update_color_based_on_time()
	
	def get_time_until_sunrise(self):
		"""
		获取距离日出还有多长时间（分钟）
		"""
		current_minutes = self.game_hour * 60 + self.game_minute
		sunrise_minutes = self.sunrise_hour * 60
		
		if current_minutes < sunrise_minutes:
			return sunrise_minutes - current_minutes
		else:
			return (24 * 60 - current_minutes) + sunrise_minutes
	
	def get_time_until_sunset(self):
		"""
		获取距离日落还有多长时间（分钟）
		"""
		current_minutes = self.game_hour * 60 + self.game_minute
		sunset_minutes = self.sunset_hour * 60
		
		if current_minutes < sunset_minutes:
			return sunset_minutes - current_minutes
		else:
			return (24 * 60 - current_minutes) + sunset_minutes

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