#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
统一的猫咪数据管理系统
负责管理所有猫咪的基础信息，供各个系统使用
"""

import csv
import random
from dataclasses import dataclass
from typing import Dict, List, Tuple, Optional
from src.core.support import get_resource_path, safe_print

@dataclass
class CatInfo:
    """统一的猫咪信息数据结构"""
    id: str                    # 猫咪ID（唯一标识）
    name: str                  # 猫咪名称
    personality: str           # 性格描述
    rarity: str               # 稀有度 (common, uncommon, rare, epic, legendary)
    color: Tuple[int, int, int]  # RGB颜色
    ascii_char: str           # ASCII字符表示
    catch_rate: float         # 钓鱼捕获概率
    category: str             # 类别 (classic, wild, pet, legend, farm)

class CatDataManager:
    """猫咪数据管理器"""
    
    def __init__(self):
        self.cats: Dict[str, CatInfo] = {}  # id -> CatInfo
        self.cats_by_name: Dict[str, CatInfo] = {}  # name -> CatInfo
        self.cats_by_rarity: Dict[str, List[CatInfo]] = {
            'common': [],
            'uncommon': [],
            'rare': [],
            'epic': [],
            'legendary': []
        }
        self.cats_by_category: Dict[str, List[CatInfo]] = {}
        
        self.load_cat_data()
    
    def load_cat_data(self):
        """从CSV文件加载猫咪数据"""
        try:
            csv_path = get_resource_path('config/cat_info.csv')
            with open(csv_path, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                
                for row in reader:
                    cat_info = CatInfo(
                        id=row['id'],
                        name=row['name'],
                        personality=row['personality'],
                        rarity=row['rarity'],
                        color=(int(row['color_r']), int(row['color_g']), int(row['color_b'])),
                        ascii_char=row['ascii_char'],
                        catch_rate=float(row['catch_rate']),
                        category=row['category']
                    )
                    
                    # 添加到各个索引
                    self.cats[cat_info.id] = cat_info
                    self.cats_by_name[cat_info.name] = cat_info
                    
                    if cat_info.rarity in self.cats_by_rarity:
                        self.cats_by_rarity[cat_info.rarity].append(cat_info)
                    
                    if cat_info.category not in self.cats_by_category:
                        self.cats_by_category[cat_info.category] = []
                    self.cats_by_category[cat_info.category].append(cat_info)
            
            safe_print(f"SUCCESS: 加载了 {len(self.cats)} 只猫咪的数据")
            
        except Exception as e:
            safe_print(f"ERROR: 无法加载猫咪数据: {e}")
            self.create_fallback_data()
    
    def create_fallback_data(self):
        """创建备用数据（如果CSV加载失败）"""
        fallback_cats = [
            {
                'id': 'fallback_cat_1',
                'name': '小橘',
                'personality': '活泼好动，喜欢到处跑跳',
                'rarity': 'common',
                'color': (255, 165, 0),
                'ascii_char': '🐱',
                'catch_rate': 0.03,
                'category': 'classic'
            },
            {
                'id': 'fallback_cat_2',
                'name': '小白',
                'personality': '温顺安静，喜欢晒太阳',
                'rarity': 'common',
                'color': (255, 255, 255),
                'ascii_char': '🐈',
                'catch_rate': 0.03,
                'category': 'classic'
            }
        ]
        
        for cat_data in fallback_cats:
            cat_info = CatInfo(**cat_data)
            self.cats[cat_info.id] = cat_info
            self.cats_by_name[cat_info.name] = cat_info
            self.cats_by_rarity[cat_info.rarity].append(cat_info)
            
            if cat_info.category not in self.cats_by_category:
                self.cats_by_category[cat_info.category] = []
            self.cats_by_category[cat_info.category].append(cat_info)
    
    def get_cat_by_id(self, cat_id: str) -> Optional[CatInfo]:
        """根据ID获取猫咪信息"""
        return self.cats.get(cat_id)
    
    def get_cat_by_name(self, name: str) -> Optional[CatInfo]:
        """根据名字获取猫咪信息"""
        return self.cats_by_name.get(name)
    
    def get_cats_by_rarity(self, rarity: str) -> List[CatInfo]:
        """获取指定稀有度的所有猫咪"""
        return self.cats_by_rarity.get(rarity, [])
    
    def get_cats_by_category(self, category: str) -> List[CatInfo]:
        """获取指定类别的所有猫咪"""
        return self.cats_by_category.get(category, [])
    
    def get_random_cat(self, rarity_weights: Optional[Dict[str, float]] = None) -> CatInfo:
        """根据稀有度权重随机获取一只猫咪"""
        if rarity_weights is None:
            # 默认权重（普通猫咪更容易出现）
            rarity_weights = {
                'common': 0.5,
                'uncommon': 0.3,
                'rare': 0.15,
                'epic': 0.04,
                'legendary': 0.01
            }
        
        # 根据权重选择稀有度
        rarities = list(rarity_weights.keys())
        weights = list(rarity_weights.values())
        
        chosen_rarity = random.choices(rarities, weights=weights)[0]
        cats_of_rarity = self.get_cats_by_rarity(chosen_rarity)
        
        if cats_of_rarity:
            return random.choice(cats_of_rarity)
        else:
            # 如果该稀有度没有猫咪，随机返回一只
            return random.choice(list(self.cats.values()))
    
    def get_random_fishing_cat(self) -> CatInfo:
        """获取一只用于钓鱼的随机猫咪（基于catch_rate）"""
        # 创建基于catch_rate的权重列表
        cats = list(self.cats.values())
        weights = [cat.catch_rate for cat in cats]
        
        if not cats:
            # 如果没有猫咪数据，创建一个默认的
            return CatInfo(
                id='default_cat',
                name='神秘猫咪',
                personality='这是一只可爱的猫咪，有着独特的性格。',
                rarity='common',
                color=(255, 255, 255),
                ascii_char='🐱',
                catch_rate=0.03,
                category='classic'
            )
        
        return random.choices(cats, weights=weights)[0]
    
    def get_all_cats(self) -> List[CatInfo]:
        """获取所有猫咪信息"""
        return list(self.cats.values())
    
    def get_cat_count(self) -> int:
        """获取猫咪总数"""
        return len(self.cats)
    
    def get_rarity_distribution(self) -> Dict[str, int]:
        """获取稀有度分布"""
        return {rarity: len(cats) for rarity, cats in self.cats_by_rarity.items()}
    
    def get_category_distribution(self) -> Dict[str, int]:
        """获取类别分布"""
        return {category: len(cats) for category, cats in self.cats_by_category.items()}
    
    def debug_print_all_cats(self):
        """调试用：打印所有猫咪信息"""
        safe_print(f"[CatDataManager] 总计 {len(self.cats)} 只猫咪:")
        
        for category, cats in self.cats_by_category.items():
            safe_print(f"  {category} 类别: {len(cats)} 只")
            for cat in cats:
                safe_print(f"    {cat.name} ({cat.rarity}) - {cat.personality[:20]}...")
        
        safe_print(f"稀有度分布: {self.get_rarity_distribution()}")

# 全局单例
_cat_data_manager = None

def get_cat_data_manager() -> CatDataManager:
    """获取猫咪数据管理器单例"""
    global _cat_data_manager
    if _cat_data_manager is None:
        _cat_data_manager = CatDataManager()
    return _cat_data_manager

# 便捷函数
def get_cat_by_name(name: str) -> Optional[CatInfo]:
    """便捷函数：根据名字获取猫咪信息"""
    return get_cat_data_manager().get_cat_by_name(name)

def get_random_cat() -> CatInfo:
    """便捷函数：获取随机猫咪"""
    return get_cat_data_manager().get_random_cat()

def get_random_fishing_cat() -> CatInfo:
    """便捷函数：获取钓鱼随机猫咪"""
    return get_cat_data_manager().get_random_fishing_cat()