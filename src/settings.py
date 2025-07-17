from pygame.math import Vector2
# screen
SCREEN_WIDTH = 1280
SCREEN_HEIGHT = 720
TILE_SIZE = 64

# overlay positions 
OVERLAY_POSITIONS = {
	'tool' : (120, SCREEN_HEIGHT - 50), 
	'seed': (120, SCREEN_HEIGHT - 20)}

PLAYER_TOOL_OFFSET = {
	'left': Vector2(-50,40),
	'right': Vector2(50,40),
	'up': Vector2(0,-10),
	'down': Vector2(0,50)
}

LAYERS = {
	'water': 0,
	'ground': 1,
	'soil': 2,
	'soil water': 3,
	'rain floor': 4,
	'house bottom': 5,
	'ground plant': 6,
	'main': 7,
	'house top': 8,
	'fruit': 9,
	'rain drops': 10
}

APPLE_POS = {
	'Small': [(18,17), (30,37), (12,50), (30,45), (20,30), (30,10)],
	'Large': [(30,24), (60,65), (50,50), (16,40),(45,50), (42,70)]
}

GROW_SPEED = {
	'corn': 1,
	'tomato': 0.7
}

SALE_PRICES = {
	'wood': 4,
	'apple': 2,
	'corn': 10,
	'tomato': 20,
	'fish': 15  # 鱼类售价
}
PURCHASE_PRICES = {
	'corn': 4,
	'tomato': 5,
	'simple_cat_bed': 100,    # 简易猫窝
	'comfort_cat_bed': 200,   # 舒适猫窝
	'luxury_cat_bed': 400,    # 豪华猫窝
}

# 猫窝类型配置
CAT_BED_TYPES = {
	'simple_cat_bed': {
		'name': '简易猫窝',
		'energy_restoration': 15,
		'mood_bonus': 1,
		'ascii_char': '🛏️',
		'description': '基础的猫窝，提供基本的睡眠恢复'
	},
	'comfort_cat_bed': {
		'name': '舒适猫窝',
		'energy_restoration': 20,
		'mood_bonus': 2,
		'ascii_char': '🏠',
		'description': '舒适的猫窝，提供更好的睡眠体验'
	},
	'luxury_cat_bed': {
		'name': '豪华猫窝',
		'energy_restoration': 25,
		'mood_bonus': 3,
		'ascii_char': '🏰',
		'description': '豪华的猫窝，提供最佳的睡眠体验'
	}
}