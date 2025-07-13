"""
Simple map loader to replace pytmx dependency
Loads map configuration from JSON file instead of TMX
"""
import json
import os
from .support import get_resource_path

class MapData:
    """Simple map data class to replace pytmx functionality"""
    
    def __init__(self, config_path):
        """Load map configuration from JSON file"""
        try:
            map_config_path = get_resource_path(config_path)
            with open(map_config_path, 'r', encoding='utf-8') as f:
                self.config = json.load(f)
            
            self.width = self.config['map_info']['width']
            self.height = self.config['map_info']['height']
            self.tile_size = self.config['map_info']['tile_size']
            
            print(f"Map loaded: {self.width}x{self.height} tiles")
            
        except Exception as e:
            print(f"ERROR: Failed to load map config: {e}")
            # 设置默认值
            self.width = 50
            self.height = 50
            self.tile_size = 64
            self.config = {
                'farmable_tiles': [],
                'water_tiles': [],
                'tree_positions': [],
                'decoration_positions': [],
                'collision_tiles': [],
                'player_spawn': {'x': 640, 'y': 360}
            }
    
    def get_layer_by_name(self, layer_name):
        """Get layer data by name (compatible with pytmx interface)"""
        return MapLayer(self.config, layer_name)


class MapLayer:
    """Map layer class to provide pytmx-compatible interface"""
    
    def __init__(self, config, layer_name):
        self.config = config
        self.layer_name = layer_name
    
    def tiles(self):
        """Return tile positions for the layer"""
        if self.layer_name == 'Farmable':
            # 返回可耕种的瓦片位置
            for x, y in self.config.get('farmable_tiles', []):
                yield x, y, None  # None 代替原来的surf参数
        
        elif self.layer_name == 'Water':
            # 返回水域瓦片位置
            for x, y in self.config.get('water_tiles', []):
                yield x, y, None
        
        elif self.layer_name == 'Collision':
            # 返回碰撞瓦片位置
            for x, y in self.config.get('collision_tiles', []):
                yield x, y, None
        
        elif self.layer_name == 'Path':
            # 返回小径瓦片位置
            for x, y in self.config.get('path_tiles', []):
                yield x, y, None
        
        elif self.layer_name == 'Beach':
            # 返回海滩瓦片位置
            for x, y in self.config.get('beach_tiles', []):
                yield x, y, None
        
        elif self.layer_name in ['HouseFloor', 'HouseFurnitureBottom', 'HouseFurnitureTop', 'Fence']:
            # 这些层暂时为空，可以后续添加
            return
            yield  # 确保这是一个生成器


class MapObjectLayer:
    """Map object layer for trees, decorations, etc."""
    
    def __init__(self, config, layer_name):
        self.config = config
        self.layer_name = layer_name
    
    def __iter__(self):
        """Return objects for the layer"""
        if self.layer_name == 'Trees':
            for tree in self.config.get('tree_positions', []):
                yield MapObject(tree['x'], tree['y'], tree['name'])
        
        elif self.layer_name == 'Decoration':
            for deco in self.config.get('decoration_positions', []):
                yield MapObject(deco['x'], deco['y'], deco['name'])
        
        elif self.layer_name == 'Player':
            spawn = self.config.get('player_spawn', {'x': 640, 'y': 360})
            yield MapObject(spawn['x'], spawn['y'], 'start')


class MapObject:
    """Simple map object class"""
    
    def __init__(self, x, y, name):
        self.x = x
        self.y = y
        self.name = name


def load_pygame(config_path='config/map_config.json'):
    """
    Load map data from JSON config (replacement for pytmx.load_pygame)
    """
    return MapData(config_path)