#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
鱼饵系统 - 管理鱼饵的获取、制作和使用
"""

import random
from dataclasses import dataclass
from typing import Dict, List, Optional, Tuple
from src.core.support import safe_print

@dataclass
class BaitType:
    """鱼饵类型数据结构"""
    id: str                    # 鱼饵ID
    name: str                  # 鱼饵名称
    description: str           # 描述
    rarity: str               # 稀有度 (common, uncommon, rare, epic, legendary)
    max_stack: int            # 最大持有数量
    price: int                # 商店购买价格
    ascii_char: str           # ASCII字符表示
    color: Tuple[int, int, int]  # RGB颜色
    # 钓鱼概率修正 (对不同稀有度鱼类的概率加成)
    fish_probability_modifiers: Dict[str, float]

@dataclass
class Insect:
    """昆虫数据结构（用于制作鱼饵）"""
    id: str                    # 昆虫ID
    name: str                  # 昆虫名称
    description: str           # 描述
    ascii_char: str           # ASCII字符表示
    color: Tuple[int, int, int]  # RGB颜色
    catch_probability: float   # 猫咪抓到的概率

class BaitSystem:
    """鱼饵系统管理器"""
    
    def __init__(self):
        # 玩家鱼饵库存 {bait_id: count}
        self.bait_inventory = {}
        
        # 昆虫箱库存 {insect_id: count}
        self.insect_box = {}
        
        # 初始化鱼饵类型
        self.bait_types = self._initialize_bait_types()
        
        # 初始化昆虫类型
        self.insect_types = self._initialize_insect_types()
        
        # 鱼饵制作配方 {bait_id: {insect_id: count, ...}}
        self.bait_recipes = self._initialize_bait_recipes()
        
        # 给玩家一些初始鱼饵
        self._give_initial_bait()
        
        safe_print("[鱼饵系统] 初始化完成")
    
    def _initialize_bait_types(self) -> Dict[str, BaitType]:
        """初始化鱼饵类型"""
        return {
            # 基础鱼饵
            'earthworm': BaitType(
                id='earthworm',
                name='蚯蚓饵',
                description='最基础的鱼饵，适合钓取普通鱼类',
                rarity='common',
                max_stack=5,
                price=10,
                ascii_char='🪱',
                color=(139, 69, 19),
                fish_probability_modifiers={
                    'common': 1.2,
                    'uncommon': 1.0,
                    'rare': 0.8,
                    'epic': 0.5,
                    'legendary': 0.3
                }
            ),
            'butterfly': BaitType(
                id='butterfly',
                name='蝴蝶饵',
                description='美丽的蝴蝶制作的鱼饵，能吸引色彩鲜艳的鱼类',
                rarity='common',
                max_stack=5,
                price=15,
                ascii_char='🦋',
                color=(255, 105, 180),
                fish_probability_modifiers={
                    'common': 1.1,
                    'uncommon': 1.3,
                    'rare': 1.0,
                    'epic': 0.7,
                    'legendary': 0.4
                }
            ),
            'cricket': BaitType(
                id='cricket',
                name='蟋蟀饵',
                description='活跃的蟋蟀制作的鱼饵，能吸引敏捷的鱼类',
                rarity='uncommon',
                max_stack=5,
                price=25,
                ascii_char='🦗',
                color=(34, 139, 34),
                fish_probability_modifiers={
                    'common': 0.9,
                    'uncommon': 1.2,
                    'rare': 1.4,
                    'epic': 1.0,
                    'legendary': 0.6
                }
            ),
            'grasshopper': BaitType(
                id='grasshopper',
                name='蚂蚱饵',
                description='强壮的蚂蚱制作的高级鱼饵，深受大型鱼类喜爱',
                rarity='rare',
                max_stack=5,
                price=50,
                ascii_char='🦟',
                color=(154, 205, 50),
                fish_probability_modifiers={
                    'common': 0.8,
                    'uncommon': 1.0,
                    'rare': 1.3,
                    'epic': 1.5,
                    'legendary': 1.0
                }
            ),
            'firefly': BaitType(
                id='firefly',
                name='萤火虫饵',
                description='神秘的萤火虫制作的稀有鱼饵，能吸引传说中的鱼类',
                rarity='epic',
                max_stack=5,
                price=100,
                ascii_char='✨',
                color=(255, 255, 0),
                fish_probability_modifiers={
                    'common': 0.7,
                    'uncommon': 0.9,
                    'rare': 1.1,
                    'epic': 1.4,
                    'legendary': 1.8
                }
            ),
            'golden_beetle': BaitType(
                id='golden_beetle',
                name='黄金甲虫饵',
                description='传说中的黄金甲虫制作的终极鱼饵，只有最稀有的鱼类才会被吸引',
                rarity='legendary',
                max_stack=5,
                price=200,
                ascii_char='🪲',
                color=(255, 215, 0),
                fish_probability_modifiers={
                    'common': 0.5,
                    'uncommon': 0.7,
                    'rare': 0.9,
                    'epic': 1.2,
                    'legendary': 2.5
                }
            )
        }
    
    def _initialize_insect_types(self) -> Dict[str, Insect]:
        """初始化昆虫类型"""
        return {
            'earthworm_bug': Insect(
                id='earthworm_bug',
                name='蚯蚓',
                description='常见的土壤生物，是制作基础鱼饵的好材料',
                ascii_char='🪱',
                color=(139, 69, 19),
                catch_probability=0.8
            ),
            'butterfly_bug': Insect(
                id='butterfly_bug',
                name='蝴蝶',
                description='美丽的昆虫，翅膀色彩斑斓',
                ascii_char='🦋',
                color=(255, 105, 180),
                catch_probability=0.6
            ),
            'cricket_bug': Insect(
                id='cricket_bug',
                name='蟋蟀',
                description='会鸣叫的昆虫，在夜晚特别活跃',
                ascii_char='🦗',
                color=(34, 139, 34),
                catch_probability=0.4
            ),
            'grasshopper_bug': Insect(
                id='grasshopper_bug',
                name='蚂蚱',
                description='善于跳跃的昆虫，腿部非常强壮',
                ascii_char='🦟',
                color=(154, 205, 50),
                catch_probability=0.3
            ),
            'firefly_bug': Insect(
                id='firefly_bug',
                name='萤火虫',
                description='会发光的神秘昆虫，只在夜晚出现',
                ascii_char='✨',
                color=(255, 255, 0),
                catch_probability=0.15
            ),
            'golden_beetle_bug': Insect(
                id='golden_beetle_bug',
                name='黄金甲虫',
                description='传说中的昆虫，全身闪闪发光',
                ascii_char='🪲',
                color=(255, 215, 0),
                catch_probability=0.05
            )
        }
    
    def _initialize_bait_recipes(self) -> Dict[str, Dict[str, int]]:
        """初始化鱼饵制作配方"""
        return {
            'earthworm': {
                'earthworm_bug': 1
            },
            'butterfly': {
                'butterfly_bug': 1
            },
            'cricket': {
                'cricket_bug': 1
            },
            'grasshopper': {
                'grasshopper_bug': 1
            },
            'firefly': {
                'firefly_bug': 2,
                'cricket_bug': 1
            },
            'golden_beetle': {
                'golden_beetle_bug': 1,
                'firefly_bug': 3,
                'grasshopper_bug': 2
            }
        }
    
    def _give_initial_bait(self):
        """给玩家一些初始鱼饵"""
        self.bait_inventory['earthworm'] = 3
        self.bait_inventory['butterfly'] = 2
        safe_print("[鱼饵系统] 获得初始鱼饵：蚯蚓饵x3，蝴蝶饵x2")
    
    def get_bait_count(self, bait_id: str) -> int:
        """获取指定鱼饵的数量"""
        return self.bait_inventory.get(bait_id, 0)
    
    def get_insect_count(self, insect_id: str) -> int:
        """获取指定昆虫的数量"""
        return self.insect_box.get(insect_id, 0)
    
    def has_bait(self, bait_id: str) -> bool:
        """检查是否有指定鱼饵"""
        return self.get_bait_count(bait_id) > 0
    
    def use_bait(self, bait_id: str) -> bool:
        """使用鱼饵"""
        if self.has_bait(bait_id):
            self.bait_inventory[bait_id] -= 1
            if self.bait_inventory[bait_id] <= 0:
                del self.bait_inventory[bait_id]
            safe_print(f"[鱼饵系统] 使用了 {self.bait_types[bait_id].name}")
            return True
        return False
    
    def add_bait(self, bait_id: str, count: int = 1) -> bool:
        """添加鱼饵"""
        if bait_id not in self.bait_types:
            return False
        
        bait_type = self.bait_types[bait_id]
        current_count = self.get_bait_count(bait_id)
        
        if current_count + count > bait_type.max_stack:
            # 计算实际能添加的数量
            can_add = bait_type.max_stack - current_count
            if can_add <= 0:
                safe_print(f"[鱼饵系统] {bait_type.name} 已达到上限({bait_type.max_stack})")
                return False
            count = can_add
            safe_print(f"[鱼饵系统] {bait_type.name} 接近上限，只能添加{can_add}个")
        
        self.bait_inventory[bait_id] = current_count + count
        safe_print(f"[鱼饵系统] 获得 {bait_type.name} x{count}")
        return True
    
    def add_insect(self, insect_id: str, count: int = 1):
        """添加昆虫到鱼饵箱"""
        if insect_id not in self.insect_types:
            return False
        
        current_count = self.get_insect_count(insect_id)
        self.insect_box[insect_id] = current_count + count
        
        insect = self.insect_types[insect_id]
        safe_print(f"[鱼饵箱] 猫咪抓到了 {insect.name} x{count}")
        return True
    
    def can_craft_bait(self, bait_id: str) -> bool:
        """检查是否可以制作指定鱼饵"""
        if bait_id not in self.bait_recipes:
            return False
        
        recipe = self.bait_recipes[bait_id]
        
        # 从工作台检查材料是否足够
        from .bait_workbench import get_bait_workbench
        workbench = get_bait_workbench()
        
        if not workbench:
            return False
        
        for insect_id, required_count in recipe.items():
            if workbench.get_insect_count(insect_id) < required_count:
                return False
        
        # 检查鱼饵是否已达上限
        bait_type = self.bait_types[bait_id]
        if self.get_bait_count(bait_id) >= bait_type.max_stack:
            return False
        
        return True
    
    def craft_bait(self, bait_id: str) -> bool:
        """制作鱼饵"""
        if not self.can_craft_bait(bait_id):
            return False
        
        recipe = self.bait_recipes[bait_id]
        
        # 从工作台消耗材料
        from .bait_workbench import get_bait_workbench
        workbench = get_bait_workbench()
        
        if not workbench:
            return False
        
        # 消耗材料
        for insect_id, required_count in recipe.items():
            workbench.consume_insect(insect_id, required_count)
        
        # 添加鱼饵
        self.add_bait(bait_id, 1)
        
        bait_name = self.bait_types[bait_id].name
        safe_print(f"[鱼饵制作] 成功制作了 {bait_name}")
        return True
    
    def get_fishing_probability_modifier(self, bait_id: str, fish_rarity: str) -> float:
        """获取鱼饵对指定稀有度鱼类的概率修正"""
        if bait_id not in self.bait_types:
            return 1.0
        
        bait_type = self.bait_types[bait_id]
        return bait_type.fish_probability_modifiers.get(fish_rarity, 1.0)
    
    def get_available_baits(self) -> List[str]:
        """获取当前可用的鱼饵列表"""
        return [bait_id for bait_id in self.bait_inventory.keys() if self.bait_inventory[bait_id] > 0]
    
    def get_craftable_baits(self) -> List[str]:
        """获取当前可制作的鱼饵列表"""
        return [bait_id for bait_id in self.bait_recipes.keys() if self.can_craft_bait(bait_id)]
    
    def get_bait_inventory_summary(self) -> str:
        """获取鱼饵库存摘要"""
        if not self.bait_inventory:
            return "鱼饵库存：空"
        
        summary = "鱼饵库存：\n"
        for bait_id, count in self.bait_inventory.items():
            bait_name = self.bait_types[bait_id].name
            max_stack = self.bait_types[bait_id].max_stack
            summary += f"  {bait_name}: {count}/{max_stack}\n"
        
        return summary.strip()
    
    def get_insect_box_summary(self) -> str:
        """获取昆虫箱摘要"""
        if not self.insect_box:
            return "昆虫箱：空"
        
        summary = "昆虫箱：\n"
        for insect_id, count in self.insect_box.items():
            insect_name = self.insect_types[insect_id].name
            summary += f"  {insect_name}: {count}\n"
        
        return summary.strip()
    
    def buy_bait_from_shop(self, bait_id: str, count: int = 1) -> Tuple[bool, int]:
        """从商店购买鱼饵
        
        Returns:
            (success, total_cost): 是否成功，总费用
        """
        if bait_id not in self.bait_types:
            return False, 0
        
        bait_type = self.bait_types[bait_id]
        current_count = self.get_bait_count(bait_id)
        
        # 检查容量限制
        max_can_buy = bait_type.max_stack - current_count
        if max_can_buy <= 0:
            safe_print(f"[商店] {bait_type.name} 已达到上限，无法购买")
            return False, 0
        
        # 调整购买数量
        actual_count = min(count, max_can_buy)
        total_cost = actual_count * bait_type.price
        
        return True, total_cost
    
    def complete_bait_purchase(self, bait_id: str, count: int):
        """完成鱼饵购买（在扣费后调用）"""
        self.add_bait(bait_id, count)
    
    def get_bait_shop_info(self) -> List[Dict]:
        """获取商店鱼饵信息"""
        shop_info = []
        for bait_id, bait_type in self.bait_types.items():
            current_count = self.get_bait_count(bait_id)
            can_buy = current_count < bait_type.max_stack
            
            shop_info.append({
                'id': bait_id,
                'name': bait_type.name,
                'price': bait_type.price,
                'current_count': current_count,
                'max_stack': bait_type.max_stack,
                'can_buy': can_buy,
                'description': bait_type.description
            })
        
        return shop_info

# 全局鱼饵系统实例
_bait_system = None

def get_bait_system():
    """获取鱼饵系统单例"""
    global _bait_system
    if _bait_system is None:
        _bait_system = BaitSystem()
    return _bait_system