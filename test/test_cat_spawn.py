#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
猫咪spawn位置测试
验证猫咪NPC的生成位置是否合理
"""

import sys
sys.path.append('../code')

import pygame
import math
from cat_npc import CatManager
from ascii_sprites import ASCIIGeneric
from settings import *

def test_cat_spawn_positions():
    """测试猫咪spawn位置"""
    print("🧪 测试猫咪spawn位置系统")
    
    # 初始化pygame
    pygame.init()
    
    # 创建精灵组
    all_sprites = pygame.sprite.Group()
    collision_sprites = pygame.sprite.Group()
    npc_sprites = pygame.sprite.Group()
    
    # 创建测试环境 - 模拟真实的障碍物布局
    print("🏗️  创建测试环境...")
    
    # 创建房屋障碍物（模拟地图中的建筑）
    house_obstacles = [
        # 主房屋
        (1300, 1000), (1350, 1000), (1400, 1000), (1450, 1000),
        (1300, 1050), (1450, 1050),
        (1300, 1100), (1450, 1100),
        (1300, 1150), (1350, 1150), (1400, 1150), (1450, 1150),
        
        # 商店建筑
        (1200, 800), (1250, 800), (1300, 800),
        (1200, 850), (1300, 850),
        (1200, 900), (1250, 900), (1300, 900),
    ]
    
    # 创建边界障碍物
    boundary_obstacles = []
    map_size = 1600
    for i in range(0, map_size, 64):
        # 顶部和底部边界
        boundary_obstacles.extend([(i, 0), (i, map_size - 64)])
        # 左侧和右侧边界
        boundary_obstacles.extend([(0, i), (map_size - 64, i)])
    
    # 创建障碍物精灵
    all_obstacles = house_obstacles + boundary_obstacles[:100]  # 限制数量避免过多
    for x, y in all_obstacles:
        obstacle = ASCIIGeneric((x, y), "wall", [all_sprites, collision_sprites])
    
    print(f"✅ 创建了 {len(collision_sprites)} 个障碍物")
    
    # 测试不同的玩家位置
    test_player_positions = [
        (800, 800),    # 地图中心
        (400, 400),    # 左上区域
        (1200, 1200),  # 右下区域
        (400, 1200),   # 左下区域
        (1200, 400),   # 右上区域
        (600, 800),    # 中左
        (1000, 800),   # 中右
    ]
    
    for i, player_pos in enumerate(test_player_positions):
        print(f"\n🎮 测试玩家位置 {i+1}: {player_pos}")
        
        # 创建猫咪管理器
        cat_manager = CatManager()
        
        # 尝试创建猫咪
        cat_manager.create_cats(
            all_sprites, 
            collision_sprites, 
            npc_sprites, 
            None,  # npc_manager不重要
            player_pos=player_pos
        )
        
        # 分析spawn结果
        created_cats = len(cat_manager.cats)
        print(f"   📊 成功创建: {created_cats}/10 只猫咪")
        
        if created_cats > 0:
            # 检查spawn位置质量
            distances_to_player = []
            collision_count = 0
            boundary_violations = 0
            
            for cat in cat_manager.cats:
                cat_pos = cat.rect.center
                
                # 计算与玩家的距离
                distance = math.sqrt((cat_pos[0] - player_pos[0])**2 + 
                                   (cat_pos[1] - player_pos[1])**2)
                distances_to_player.append(distance)
                
                # 检查是否在边界内
                if (cat_pos[0] < 100 or cat_pos[0] > 1500 or 
                    cat_pos[1] < 100 or cat_pos[1] > 1500):
                    boundary_violations += 1
                
                # 检查是否与障碍物重叠
                cat_hitbox = pygame.Rect(cat_pos[0] - 16, cat_pos[1] - 16, 32, 32)
                for obstacle in collision_sprites:
                    if hasattr(obstacle, 'rect') and obstacle.rect.colliderect(cat_hitbox):
                        collision_count += 1
                        break
            
            # 统计结果
            avg_distance = sum(distances_to_player) / len(distances_to_player)
            min_distance = min(distances_to_player)
            max_distance = max(distances_to_player)
            
            print(f"   📏 距离玩家: 平均 {avg_distance:.1f}, 最近 {min_distance:.1f}, 最远 {max_distance:.1f}")
            print(f"   ⚠️  边界违规: {boundary_violations} 只")
            print(f"   💥 碰撞错误: {collision_count} 只")
            
            # 评价spawn质量
            quality_score = 100
            if collision_count > 0:
                quality_score -= collision_count * 20
            if boundary_violations > 0:
                quality_score -= boundary_violations * 15
            if avg_distance < 100:
                quality_score -= 10
            if avg_distance > 600:
                quality_score -= 10
            
            quality_score = max(0, quality_score)
            
            if quality_score >= 80:
                status = "✅ 优秀"
            elif quality_score >= 60:
                status = "⚠️  良好"
            else:
                status = "❌ 需改进"
            
            print(f"   🏆 spawn质量: {quality_score}分 {status}")
        
        # 清空猫咪列表准备下一轮测试
        for cat in cat_manager.cats:
            cat.kill()
        cat_manager.cats.clear()

def test_spawn_edge_cases():
    """测试边缘情况"""
    print("\n🔍 测试spawn边缘情况")
    
    pygame.init()
    
    # 创建精灵组
    all_sprites = pygame.sprite.Group()
    collision_sprites = pygame.sprite.Group()
    npc_sprites = pygame.sprite.Group()
    
    # 创建极端测试环境
    
    # 情况1: 玩家被障碍物包围
    print("\n📦 测试1: 玩家被障碍物包围")
    player_pos = (800, 800)
    
    # 在玩家周围创建密集障碍物
    for x in range(700, 900, 32):
        for y in range(700, 900, 32):
            if abs(x - player_pos[0]) > 64 or abs(y - player_pos[1]) > 64:  # 不在玩家正下方
                obstacle = ASCIIGeneric((x, y), "wall", [all_sprites, collision_sprites])
    
    cat_manager = CatManager()
    cat_manager.create_cats(all_sprites, collision_sprites, npc_sprites, None, player_pos)
    
    print(f"   结果: 创建了 {len(cat_manager.cats)} 只猫咪")
    
    # 清理
    for cat in cat_manager.cats:
        cat.kill()
    cat_manager.cats.clear()
    collision_sprites.empty()
    
    # 情况2: 玩家在地图边缘
    print("\n🗺️  测试2: 玩家在地图边缘")
    edge_positions = [
        (150, 150),    # 左上角
        (1450, 150),   # 右上角
        (150, 1450),   # 左下角
        (1450, 1450),  # 右下角
    ]
    
    for edge_pos in edge_positions:
        cat_manager = CatManager()
        cat_manager.create_cats(all_sprites, collision_sprites, npc_sprites, None, edge_pos)
        created = len(cat_manager.cats)
        print(f"   位置 {edge_pos}: 创建了 {created} 只猫咪")
        
        # 清理
        for cat in cat_manager.cats:
            cat.kill()
        cat_manager.cats.clear()
    
    # 情况3: 无玩家位置
    print("\n❓ 测试3: 无玩家位置（None）")
    cat_manager = CatManager()
    cat_manager.create_cats(all_sprites, collision_sprites, npc_sprites, None, None)
    print(f"   结果: 创建了 {len(cat_manager.cats)} 只猫咪")

def test_spawn_distribution():
    """测试spawn分布"""
    print("\n📊 测试spawn分布")
    
    pygame.init()
    
    all_sprites = pygame.sprite.Group()
    collision_sprites = pygame.sprite.Group()
    npc_sprites = pygame.sprite.Group()
    
    player_pos = (800, 800)
    
    # 多次运行spawn测试，分析分布
    all_positions = []
    
    for run in range(5):  # 运行5次
        cat_manager = CatManager()
        cat_manager.create_cats(all_sprites, collision_sprites, npc_sprites, None, player_pos)
        
        for cat in cat_manager.cats:
            all_positions.append(cat.rect.center)
            cat.kill()
        
        cat_manager.cats.clear()
    
    if all_positions:
        # 分析分布
        x_positions = [pos[0] for pos in all_positions]
        y_positions = [pos[1] for pos in all_positions]
        
        x_center = sum(x_positions) / len(x_positions)
        y_center = sum(y_positions) / len(y_positions)
        
        print(f"   📍 spawn中心: ({x_center:.1f}, {y_center:.1f})")
        print(f"   🎯 玩家位置: {player_pos}")
        print(f"   📏 中心偏移: ({x_center - player_pos[0]:.1f}, {y_center - player_pos[1]:.1f})")
        
        # 计算分布范围
        x_range = max(x_positions) - min(x_positions)
        y_range = max(y_positions) - min(y_positions)
        
        print(f"   📐 分布范围: X轴 {x_range:.1f}, Y轴 {y_range:.1f}")
        
        # 检查是否均匀分布在玩家周围
        center_offset = math.sqrt((x_center - player_pos[0])**2 + (y_center - player_pos[1])**2)
        if center_offset < 50:
            print("   ✅ 分布均匀，以玩家为中心")
        else:
            print(f"   ⚠️  分布偏移较大: {center_offset:.1f}")

if __name__ == "__main__":
    test_cat_spawn_positions()
    test_spawn_edge_cases()
    test_spawn_distribution()
    print("\n🎉 所有spawn测试完成！")