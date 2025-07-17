import pygame
from ..settings import *
from ..systems.timer import Timer
from src.utils.font_manager import FontManager

class Menu:
	def __init__(self, player, toggle_menu):

		# general setup
		self.player = player
		self.toggle_menu = toggle_menu
		self.display_surface = pygame.display.get_surface()
		# font - 使用统一的阿里妈妈字体
		font_manager = FontManager.get_instance()
		self.font = font_manager.load_chinese_font(30, "menu_font")

		# options
		self.width = 400
		self.space = 10
		self.padding = 8

		# entries - 只显示物品出售和猫窝购买
		self.options = list(self.player.item_inventory.keys())
		self.sell_border = len(self.player.item_inventory) - 1
		
		# 添加猫窝商品（替换种子购买）
		from ..settings import CAT_BED_TYPES
		self.cat_bed_options = list(CAT_BED_TYPES.keys())
		self.options.extend(self.cat_bed_options)
		
		self.setup()

		# movement
		self.index = 0
		self.timer = Timer(200)

	def display_money(self):
		text_surf = self.font.render(f'${self.player.money}', False, 'Black')
		text_rect = text_surf.get_rect(midbottom = (SCREEN_WIDTH / 2,SCREEN_HEIGHT - 20))

		pygame.draw.rect(self.display_surface,'White',text_rect.inflate(10,10),0,4)
		self.display_surface.blit(text_surf,text_rect)

	def setup(self):

		# create the text surfaces
		self.text_surfs = []
		self.total_height = 0

		for item in self.options:
			# 获取显示名称
			if item in self.cat_bed_options:
				from ..settings import CAT_BED_TYPES
				display_name = CAT_BED_TYPES[item]['name']
			else:
				display_name = item
			
			text_surf = self.font.render(display_name, False, 'Black')
			self.text_surfs.append(text_surf)
			self.total_height += text_surf.get_height() + (self.padding * 2)

		self.total_height += (len(self.text_surfs) - 1) * self.space
		self.menu_top = SCREEN_HEIGHT / 2 - self.total_height / 2
		self.main_rect = pygame.Rect(SCREEN_WIDTH / 2 - self.width / 2,self.menu_top,self.width,self.total_height)

		# buy / sell text surface
		self.buy_text = self.font.render('buy',False,'Black')
		self.sell_text =  self.font.render('sell',False,'Black')

	def input(self):
		keys = pygame.key.get_pressed()
		self.timer.update()

		if keys[pygame.K_ESCAPE]:
			self.toggle_menu()

		if not self.timer.active:
			if keys[pygame.K_UP]:
				self.index -= 1
				self.timer.activate()

			if keys[pygame.K_DOWN]:
				self.index += 1
				self.timer.activate()

			if keys[pygame.K_SPACE]:
				self.timer.activate()

				# get item
				current_item = self.options[self.index]

				# sell
				if self.index <= self.sell_border:
					if self.player.item_inventory[current_item] > 0:
						self.player.item_inventory[current_item] -= 1
						self.player.money += SALE_PRICES[current_item]

				# buy
				else:
					if current_item in self.cat_bed_options:
						# 猫窝购买逻辑
						self._handle_cat_bed_purchase(current_item)
					# 移除种子购买逻辑，现在只支持猫窝购买

		# clamo the values
		if self.index < 0:
			self.index = len(self.options) - 1
		if self.index > len(self.options) - 1:
			self.index = 0
	
	def _handle_cat_bed_purchase(self, bed_type):
		"""处理猫窝购买"""
		from ..settings import PURCHASE_PRICES
		
		bed_price = PURCHASE_PRICES[bed_type]
		
		if self.player.money >= bed_price:
			# 检查是否有猫咪可以绑定
			available_cats = self._get_available_cats_for_bed()
			
			if available_cats:
				# 简单起见，自动绑定第一只没有猫窝的猫咪
				selected_cat = available_cats[0]
				
				# 扣除金币
				self.player.money -= bed_price
				
				# 添加猫窝到玩家背包
				if not hasattr(self.player, 'cat_bed_inventory'):
					self.player.cat_bed_inventory = {}
				
				if bed_type not in self.player.cat_bed_inventory:
					self.player.cat_bed_inventory[bed_type] = []
				
				bed_data = {
					'bed_id': f"bed_{len(self.player.cat_bed_inventory[bed_type]) + 1}",
					'owner_cat': selected_cat['name'],
					'owner_id': selected_cat['id']
				}
				
				self.player.cat_bed_inventory[bed_type].append(bed_data)
				
				from ..settings import CAT_BED_TYPES
				bed_name = CAT_BED_TYPES[bed_type]['name']
				print(f"[商店] 购买了 {bed_name} 给 {selected_cat['name']} (花费 {bed_price} 金币)")
			else:
				print("[商店] 没有可以绑定猫窝的猫咪")
		else:
			print(f"[商店] 金币不足，需要 {bed_price} 金币")
	
	def _get_available_cats_for_bed(self):
		"""获取可以绑定猫窝的猫咪列表"""
		available_cats = []
		
		# 从level获取猫咪管理器
		try:
			import pygame
			from ..core.level import Level
			
			# 通过游戏中的level实例获取猫咪信息
			# 这里需要一个更好的方法来获取猫咪列表
			# 暂时使用简单的方法
			
			# 获取当前游戏实例中的猫咪
			level = getattr(self.player, 'level', None)
			if level and hasattr(level, 'cat_manager'):
				cats = level.cat_manager.cats
				
				# 检查已有猫窝的猫咪
				from ..systems.cat_bed import get_cat_bed_manager
				cat_bed_manager = get_cat_bed_manager()
				
				for cat in cats:
					# 检查这只猫是否已经有猫窝
					existing_bed = cat_bed_manager.get_cat_bed_by_owner(cat.npc_id)
					if not existing_bed:
						available_cats.append({
							'name': cat.cat_name,
							'id': cat.npc_id
						})
		except Exception as e:
			print(f"[商店] 获取猫咪列表失败: {e}")
		
		return available_cats

	def show_entry(self, text_surf, amount, top, selected):

		# background
		bg_rect = pygame.Rect(self.main_rect.left,top,self.width,text_surf.get_height() + (self.padding * 2))
		pygame.draw.rect(self.display_surface, 'White',bg_rect, 0, 4)

		# text
		text_rect = text_surf.get_rect(midleft = (self.main_rect.left + 20,bg_rect.centery))
		self.display_surface.blit(text_surf, text_rect)

		# amount or price
		current_item = self.options[self.index] if selected else None
		
		if selected and current_item in self.cat_bed_options:
			# 显示猫窝价格
			from ..settings import PURCHASE_PRICES
			price = PURCHASE_PRICES[current_item]
			amount_surf = self.font.render(f"${price}", False, 'Black')
		else:
			amount_surf = self.font.render(str(amount), False, 'Black')
		
		amount_rect = amount_surf.get_rect(midright = (self.main_rect.right - 20,bg_rect.centery))
		self.display_surface.blit(amount_surf, amount_rect)

		# selected
		if selected:
			pygame.draw.rect(self.display_surface,'black',bg_rect,4,4)
			if self.index <= self.sell_border: # sell
				pos_rect = self.sell_text.get_rect(midleft = (self.main_rect.left + 150,bg_rect.centery))
				self.display_surface.blit(self.sell_text,pos_rect)
			else: # buy
				pos_rect = self.buy_text.get_rect(midleft = (self.main_rect.left + 150,bg_rect.centery))
				self.display_surface.blit(self.buy_text,pos_rect)

	def update(self):
		self.input()
		self.display_money()

		for text_index, text_surf in enumerate(self.text_surfs):
			top = self.main_rect.top + text_index * (text_surf.get_height() + (self.padding * 2) + self.space)
			
			# 获取数量或价格
			item_name = self.options[text_index]
			
			if item_name in self.cat_bed_options:
				# 猫窝显示价格
				from ..settings import PURCHASE_PRICES
				amount = PURCHASE_PRICES[item_name]
			else:
				# 普通物品显示数量
				amount_list = list(self.player.item_inventory.values())
				amount = amount_list[text_index]
			
			self.show_entry(text_surf, amount, top, self.index == text_index)