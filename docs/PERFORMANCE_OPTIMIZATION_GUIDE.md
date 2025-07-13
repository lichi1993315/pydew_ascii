# 性能优化指南

## 🎯 当前性能分析

### 主要瓶颈识别
1. **渲染系统** - 每帧重新创建文本表面
2. **碰撞检测** - O(n)复杂度的距离计算
3. **AI请求** - 阻塞式API调用
4. **内存管理** - 缺乏对象池和缓存

## 🚀 立即可实施的优化

### 1. 渲染系统缓存优化

创建字符渲染缓存系统：

```python
# code/rendering/char_cache.py
import pygame
from typing import Dict, Tuple
from functools import lru_cache

class CharacterCache:
    """字符渲染缓存系统"""
    
    def __init__(self, max_cache_size: int = 1000):
        self.cache: Dict[Tuple, pygame.Surface] = {}
        self.max_size = max_cache_size
        self.access_count = {}
    
    def get_char_surface(self, char: str, color: Tuple[int, int, int], 
                        font: pygame.font.Font) -> pygame.Surface:
        """获取字符表面，自动缓存"""
        cache_key = (char, color, font)
        
        if cache_key in self.cache:
            self.access_count[cache_key] = self.access_count.get(cache_key, 0) + 1
            return self.cache[cache_key]
        
        # 缓存未命中，创建新表面
        surface = font.render(char, True, color)
        
        # 缓存管理
        if len(self.cache) >= self.max_size:
            self._evict_least_used()
        
        self.cache[cache_key] = surface
        self.access_count[cache_key] = 1
        return surface
    
    def _evict_least_used(self):
        """驱逐最少使用的缓存项"""
        least_used = min(self.access_count.items(), key=lambda x: x[1])
        del self.cache[least_used[0]]
        del self.access_count[least_used[0]]

# 全局缓存实例
char_cache = CharacterCache()
```

### 2. 空间分割优化碰撞检测

```python
# code/physics/spatial_grid.py
from typing import List, Set, Tuple
from collections import defaultdict

class SpatialGrid:
    """空间网格加速碰撞检测"""
    
    def __init__(self, cell_size: int = 128):
        self.cell_size = cell_size
        self.grid: Dict[Tuple[int, int], Set] = defaultdict(set)
        self.entity_cells: Dict = {}  # 实体到网格的映射
    
    def _get_cell_coords(self, x: float, y: float) -> Tuple[int, int]:
        """获取位置对应的网格坐标"""
        return int(x // self.cell_size), int(y // self.cell_size)
    
    def add_entity(self, entity, x: float, y: float):
        """添加实体到空间网格"""
        cell = self._get_cell_coords(x, y)
        self.grid[cell].add(entity)
        self.entity_cells[entity] = cell
    
    def remove_entity(self, entity):
        """从空间网格移除实体"""
        if entity in self.entity_cells:
            cell = self.entity_cells[entity]
            self.grid[cell].discard(entity)
            del self.entity_cells[entity]
    
    def update_entity(self, entity, new_x: float, new_y: float):
        """更新实体位置"""
        new_cell = self._get_cell_coords(new_x, new_y)
        
        if entity in self.entity_cells:
            old_cell = self.entity_cells[entity]
            if old_cell != new_cell:
                self.grid[old_cell].discard(entity)
                self.grid[new_cell].add(entity)
                self.entity_cells[entity] = new_cell
        else:
            self.add_entity(entity, new_x, new_y)
    
    def get_nearby_entities(self, x: float, y: float, radius: float) -> Set:
        """获取指定范围内的实体"""
        center_cell = self._get_cell_coords(x, y)
        cell_radius = int(radius // self.cell_size) + 1
        
        nearby = set()
        for dx in range(-cell_radius, cell_radius + 1):
            for dy in range(-cell_radius, cell_radius + 1):
                cell = (center_cell[0] + dx, center_cell[1] + dy)
                nearby.update(self.grid.get(cell, set()))
        
        return nearby
```

### 3. 异步AI请求池

```python
# code/ai/async_ai_pool.py
import asyncio
from concurrent.futures import ThreadPoolExecutor
from typing import Optional, Callable
import queue
import threading

class AsyncAIPool:
    """异步AI请求池"""
    
    def __init__(self, max_workers: int = 3):
        self.executor = ThreadPoolExecutor(max_workers=max_workers)
        self.pending_requests = queue.Queue()
        self.request_id_counter = 0
        self.callbacks = {}
        
    async def submit_request(self, ai_func: Callable, *args, 
                           callback: Optional[Callable] = None) -> int:
        """提交AI请求"""
        request_id = self.request_id_counter
        self.request_id_counter += 1
        
        if callback:
            self.callbacks[request_id] = callback
        
        # 异步执行AI请求
        loop = asyncio.get_event_loop()
        future = loop.run_in_executor(self.executor, ai_func, *args)
        
        # 设置完成回调
        future.add_done_callback(
            lambda f: self._handle_completion(request_id, f.result())
        )
        
        return request_id
    
    def _handle_completion(self, request_id: int, result):
        """处理请求完成"""
        if request_id in self.callbacks:
            self.callbacks[request_id](result)
            del self.callbacks[request_id]

# 全局AI池
ai_pool = AsyncAIPool()
```

### 4. 脏矩形更新系统

```python
# code/rendering/dirty_rect_manager.py
import pygame
from typing import List, Set

class DirtyRectManager:
    """脏矩形管理器，只更新变化的区域"""
    
    def __init__(self):
        self.dirty_rects: Set[pygame.Rect] = set()
        self.last_frame_rects: Set[pygame.Rect] = set()
    
    def mark_dirty(self, rect: pygame.Rect):
        """标记区域为脏区域"""
        self.dirty_rects.add(rect.copy())
    
    def mark_sprite_dirty(self, sprite):
        """标记精灵为脏区域"""
        if hasattr(sprite, 'rect'):
            self.mark_dirty(sprite.rect)
    
    def get_update_rects(self) -> List[pygame.Rect]:
        """获取需要更新的矩形区域"""
        # 合并重叠的矩形
        merged_rects = self._merge_overlapping_rects(self.dirty_rects)
        
        # 清空脏矩形
        self.last_frame_rects = self.dirty_rects.copy()
        self.dirty_rects.clear()
        
        return merged_rects
    
    def _merge_overlapping_rects(self, rects: Set[pygame.Rect]) -> List[pygame.Rect]:
        """合并重叠的矩形"""
        if not rects:
            return []
        
        rect_list = list(rects)
        merged = []
        
        for rect in rect_list:
            merged_with_existing = False
            for i, existing in enumerate(merged):
                if rect.colliderect(existing):
                    merged[i] = rect.union(existing)
                    merged_with_existing = True
                    break
            
            if not merged_with_existing:
                merged.append(rect)
        
        return merged

# 全局脏矩形管理器
dirty_rect_manager = DirtyRectManager()
```

## 📊 性能监控系统

### 1. 游戏性能监控器

```python
# code/utils/performance_monitor.py
import time
import psutil
import pygame
from collections import deque
from typing import Dict, List

class PerformanceMonitor:
    """游戏性能监控器"""
    
    def __init__(self, history_size: int = 60):
        self.history_size = history_size
        self.fps_history = deque(maxlen=history_size)
        self.frame_time_history = deque(maxlen=history_size)
        self.memory_history = deque(maxlen=history_size)
        
        self.last_frame_time = time.time()
        self.frame_count = 0
        
        # 性能阈值
        self.fps_warning_threshold = 30
        self.memory_warning_threshold = 500  # MB
        
    def update(self):
        """更新性能数据"""
        current_time = time.time()
        frame_time = current_time - self.last_frame_time
        
        self.frame_time_history.append(frame_time)
        
        # 计算FPS
        if frame_time > 0:
            fps = 1.0 / frame_time
            self.fps_history.append(fps)
        
        # 内存使用情况
        process = psutil.Process()
        memory_mb = process.memory_info().rss / 1024 / 1024
        self.memory_history.append(memory_mb)
        
        self.last_frame_time = current_time
        self.frame_count += 1
        
        # 性能警告
        self._check_performance_warnings()
    
    def _check_performance_warnings(self):
        """检查性能警告"""
        if len(self.fps_history) > 10:
            avg_fps = sum(list(self.fps_history)[-10:]) / 10
            if avg_fps < self.fps_warning_threshold:
                print(f"⚠️ 性能警告: FPS过低 ({avg_fps:.1f})")
        
        if len(self.memory_history) > 5:
            current_memory = self.memory_history[-1]
            if current_memory > self.memory_warning_threshold:
                print(f"⚠️ 内存警告: 使用过多 ({current_memory:.1f} MB)")
    
    def get_stats(self) -> Dict:
        """获取性能统计"""
        if not self.fps_history:
            return {}
        
        return {
            "avg_fps": sum(self.fps_history) / len(self.fps_history),
            "min_fps": min(self.fps_history),
            "max_fps": max(self.fps_history),
            "avg_frame_time": sum(self.frame_time_history) / len(self.frame_time_history),
            "current_memory_mb": self.memory_history[-1] if self.memory_history else 0,
            "frame_count": self.frame_count
        }
    
    def render_debug_info(self, surface: pygame.Surface, font: pygame.font.Font):
        """渲染调试信息"""
        stats = self.get_stats()
        if not stats:
            return
        
        debug_lines = [
            f"FPS: {stats['avg_fps']:.1f} (min: {stats['min_fps']:.1f})",
            f"Frame Time: {stats['avg_frame_time']*1000:.1f}ms",
            f"Memory: {stats['current_memory_mb']:.1f}MB",
            f"Frames: {stats['frame_count']}"
        ]
        
        for i, line in enumerate(debug_lines):
            text_surface = font.render(line, True, (255, 255, 0))
            surface.blit(text_surface, (10, 10 + i * 20))

# 全局性能监控器
performance_monitor = PerformanceMonitor()
```

### 2. AI性能分析器

```python
# code/ai/ai_profiler.py
import time
from collections import defaultdict, deque
from typing import Dict, List
import functools

class AIProfiler:
    """AI性能分析器"""
    
    def __init__(self):
        self.request_times = defaultdict(deque)  # 按模型类型记录
        self.error_counts = defaultdict(int)
        self.cache_hits = 0
        self.cache_misses = 0
    
    def profile_ai_request(self, model_type: str):
        """AI请求性能分析装饰器"""
        def decorator(func):
            @functools.wraps(func)
            async def wrapper(*args, **kwargs):
                start_time = time.time()
                try:
                    result = await func(*args, **kwargs)
                    # 记录成功请求时间
                    duration = time.time() - start_time
                    self.request_times[model_type].append(duration)
                    
                    # 保持历史记录在合理范围内
                    if len(self.request_times[model_type]) > 100:
                        self.request_times[model_type].popleft()
                    
                    return result
                except Exception as e:
                    # 记录错误
                    self.error_counts[model_type] += 1
                    raise e
            return wrapper
        return decorator
    
    def record_cache_hit(self):
        """记录缓存命中"""
        self.cache_hits += 1
    
    def record_cache_miss(self):
        """记录缓存未命中"""
        self.cache_misses += 1
    
    def get_ai_stats(self) -> Dict:
        """获取AI性能统计"""
        stats = {}
        
        for model_type, times in self.request_times.items():
            if times:
                stats[model_type] = {
                    "avg_time": sum(times) / len(times),
                    "min_time": min(times),
                    "max_time": max(times),
                    "request_count": len(times),
                    "error_count": self.error_counts[model_type]
                }
        
        # 缓存统计
        total_requests = self.cache_hits + self.cache_misses
        cache_hit_rate = self.cache_hits / total_requests if total_requests > 0 else 0
        
        stats["cache"] = {
            "hit_rate": cache_hit_rate,
            "hits": self.cache_hits,
            "misses": self.cache_misses
        }
        
        return stats

# 全局AI分析器
ai_profiler = AIProfiler()
```

## 🎮 游戏循环优化

### 固定时间步长游戏循环

```python
# code/core/optimized_game_loop.py
import time
import pygame

class OptimizedGameLoop:
    """优化的游戏循环"""
    
    def __init__(self, target_fps: int = 60):
        self.target_fps = target_fps
        self.target_frame_time = 1.0 / target_fps
        self.accumulator = 0.0
        self.current_time = time.time()
        
        # 性能监控
        self.performance_monitor = performance_monitor
        
    def run(self, game_instance):
        """运行优化的游戏循环"""
        clock = pygame.time.Clock()
        
        while game_instance.running:
            new_time = time.time()
            frame_time = new_time - self.current_time
            self.current_time = new_time
            
            # 防止螺旋死亡
            frame_time = min(frame_time, 0.25)
            
            self.accumulator += frame_time
            
            # 固定时间步长更新
            while self.accumulator >= self.target_frame_time:
                game_instance.update(self.target_frame_time)
                self.accumulator -= self.target_frame_time
            
            # 渲染（可变时间步长）
            interpolation = self.accumulator / self.target_frame_time
            game_instance.render(interpolation)
            
            # 性能监控
            self.performance_monitor.update()
            
            # 帧率控制
            clock.tick(self.target_fps)
```

## 📈 性能基准测试

### 创建性能测试套件

```python
# test/performance/test_rendering_performance.py
import pytest
import pygame
import time
from code.rendering.char_cache import CharacterCache

class TestRenderingPerformance:
    
    @pytest.fixture
    def setup_pygame(self):
        pygame.init()
        surface = pygame.Surface((800, 600))
        font = pygame.font.Font(None, 24)
        return surface, font
    
    def test_char_cache_performance(self, setup_pygame):
        """测试字符缓存性能"""
        surface, font = setup_pygame
        cache = CharacterCache()
        
        # 测试缓存性能
        chars = "abcdefghijklmnopqrstuvwxyz0123456789"
        colors = [(255, 255, 255), (255, 0, 0), (0, 255, 0), (0, 0, 255)]
        
        # 预热缓存
        for char in chars:
            for color in colors:
                cache.get_char_surface(char, color, font)
        
        # 测量缓存命中性能
        start_time = time.time()
        for _ in range(1000):
            for char in chars:
                for color in colors:
                    cache.get_char_surface(char, color, font)
        
        cached_time = time.time() - start_time
        
        # 测量直接渲染性能
        start_time = time.time()
        for _ in range(1000):
            for char in chars:
                for color in colors:
                    font.render(char, True, color)
        
        direct_time = time.time() - start_time
        
        # 缓存应该更快
        assert cached_time < direct_time
        print(f"缓存性能提升: {direct_time/cached_time:.2f}x")

# test/performance/test_collision_performance.py
class TestCollisionPerformance:
    
    def test_spatial_grid_performance(self):
        """测试空间网格性能"""
        from code.physics.spatial_grid import SpatialGrid
        
        grid = SpatialGrid(cell_size=64)
        
        # 添加大量实体
        entities = []
        for i in range(1000):
            entity = f"entity_{i}"
            x, y = i % 100 * 10, i // 100 * 10
            grid.add_entity(entity, x, y)
            entities.append((entity, x, y))
        
        # 测试查询性能
        start_time = time.time()
        for _ in range(100):
            nearby = grid.get_nearby_entities(500, 500, 100)
        
        grid_time = time.time() - start_time
        
        # 对比暴力搜索
        start_time = time.time()
        for _ in range(100):
            nearby = []
            for entity, x, y in entities:
                distance = ((500 - x) ** 2 + (500 - y) ** 2) ** 0.5
                if distance <= 100:
                    nearby.append(entity)
        
        brute_time = time.time() - start_time
        
        print(f"空间网格性能提升: {brute_time/grid_time:.2f}x")
```

## 📋 性能优化检查清单

### 立即实施 ✅
- [ ] 实现字符渲染缓存
- [ ] 添加空间网格碰撞检测
- [ ] 创建异步AI请求池
- [ ] 实现脏矩形更新
- [ ] 添加性能监控

### 中期优化 📈
- [ ] 优化游戏循环
- [ ] 实现对象池
- [ ] 添加LOD系统
- [ ] 优化内存分配
- [ ] 实现多线程渲染

### 长期优化 🚀
- [ ] GPU加速渲染
- [ ] 流式资源加载
- [ ] 预测性缓存
- [ ] 自适应质量设置
- [ ] 实时性能调优

通过系统性的性能优化，PyDew可以在保持功能完整性的同时，提供流畅的游戏体验！