import random
from dataclasses import dataclass
from typing import Dict, List, Tuple

@dataclass
class Fish:
    """
    鱼类数据结构
    """
    name: str           # 鱼的名称
    rarity: str         # 稀有度 (common, uncommon, rare, epic, legendary)
    min_length: int     # 最小长度(厘米)
    max_length: int     # 最大长度(厘米)
    base_price: int     # 基础价格
    color: Tuple[int, int, int]  # RGB颜色
    ascii_char: str     # ASCII字符表示
    catch_rate: float   # 捕获概率(0-1)

class FishSystem:
    """
    鱼类系统管理器
    """
    
    def __init__(self):
        # 定义所有鱼类
        self.fish_types = {
            # 普通鱼类 - 白色
            'minnow': Fish(
                name='小鱼',
                rarity='common',
                min_length=5,
                max_length=12,
                base_price=3,
                color=(255, 255, 255),
                ascii_char='><>',
                catch_rate=0.4
            ),
            'carp': Fish(
                name='鲤鱼',
                rarity='common',
                min_length=15,
                max_length=30,
                base_price=8,
                color=(255, 255, 255),
                ascii_char='><)))',
                catch_rate=0.25
            ),
            
            # 不常见鱼类 - 绿色
            'bass': Fish(
                name='鲈鱼',
                rarity='uncommon',
                min_length=20,
                max_length=45,
                base_price=15,
                color=(0, 255, 0),
                ascii_char='><))))',
                catch_rate=0.15
            ),
            'trout': Fish(
                name='鳟鱼',
                rarity='uncommon',
                min_length=18,
                max_length=40,
                base_price=18,
                color=(0, 255, 0),
                ascii_char='><(((',
                catch_rate=0.12
            ),
            
            # 稀有鱼类 - 蓝色
            'salmon': Fish(
                name='三文鱼',
                rarity='rare',
                min_length=30,
                max_length=60,
                base_price=35,
                color=(0, 150, 255),
                ascii_char='><))))*',
                catch_rate=0.06
            ),
            'pike': Fish(
                name='梭鱼',
                rarity='rare',
                min_length=35,
                max_length=70,
                base_price=40,
                color=(0, 150, 255),
                ascii_char='><---)',
                catch_rate=0.05
            ),
            
            # 史诗鱼类 - 紫色
            'swordfish': Fish(
                name='剑鱼',
                rarity='epic',
                min_length=50,
                max_length=100,
                base_price=80,
                color=(160, 0, 255),
                ascii_char='><=====>',
                catch_rate=0.02
            ),
            
            # 传说鱼类 - 金色
            'golden_carp': Fish(
                name='金鲤鱼',
                rarity='legendary',
                min_length=40,
                max_length=80,
                base_price=200,
                color=(255, 215, 0),
                ascii_char='><$$$>',
                catch_rate=0.01
            )
        }
        
        # 稀有度颜色映射
        self.rarity_colors = {
            'common': (255, 255, 255),      # 白色
            'uncommon': (0, 255, 0),        # 绿色
            'rare': (0, 150, 255),          # 蓝色
            'epic': (160, 0, 255),          # 紫色
            'legendary': (255, 215, 0)      # 金色
        }
        
        # 稀有度中文名称
        self.rarity_names = {
            'common': '普通',
            'uncommon': '不常见',
            'rare': '稀有',
            'epic': '史诗',
            'legendary': '传说'
        }
    
    def catch_fish(self) -> Dict or None:
        """
        尝试捕获一条鱼
        返回鱼的信息字典，如果没钓到返回None
        """
        # 计算总概率
        total_rate = sum(fish.catch_rate for fish in self.fish_types.values())
        
        # 随机选择
        rand = random.random() * total_rate
        current_rate = 0
        
        for fish_id, fish in self.fish_types.items():
            current_rate += fish.catch_rate
            if rand <= current_rate:
                # 钓到这种鱼，生成具体信息
                length = random.randint(fish.min_length, fish.max_length)
                
                # 根据长度调整价格
                length_ratio = (length - fish.min_length) / (fish.max_length - fish.min_length)
                price = int(fish.base_price * (1 + length_ratio * 0.5))
                
                return {
                    'id': fish_id,
                    'name': fish.name,
                    'rarity': fish.rarity,
                    'rarity_name': self.rarity_names[fish.rarity],
                    'length': length,
                    'price': price,
                    'color': fish.color,
                    'ascii_char': fish.ascii_char
                }
        
        # 没钓到鱼
        return None
    
    def get_fish_display_name(self, fish_info: Dict) -> str:
        """
        获取鱼的显示名称
        """
        return f"{fish_info['name']} ({fish_info['length']}cm, {fish_info['rarity_name']})"
    
    def get_fish_by_id(self, fish_id: str) -> Fish:
        """
        根据ID获取鱼类信息
        """
        return self.fish_types.get(fish_id) 