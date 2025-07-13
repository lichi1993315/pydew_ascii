#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
猫咪碰撞检测测试
验证猫咪NPC的碰撞检测是否正常工作
"""

import sys
sys.path.append('../code')

import pygame
import random
from cat_npc import CatNPC, CatManager
from ascii_sprites import ASCIIGeneric
from settings import *

def test_cat_collision():
    """测试猫咪碰撞检测"""
    print("🧪 测试猫咪碰撞检测系统")
    
    # 初始化pygame
    pygame.init()
    screen = pygame.Surface((800, 600))
    
    # 创建精灵组
    all_sprites = pygame.sprite.Group()
    collision_sprites = pygame.sprite.Group()
    npc_sprites = pygame.sprite.Group()
    
    # 创建一些障碍物
    obstacles = [
        (400, 300, "wall"),  # 中央障碍物
        (200, 200, "wall"),  # 左上障碍物
        (600, 400, "wall"),  # 右下障碍物
    ]
    
    for x, y, obj_type in obstacles:
        obstacle = ASCIIGeneric((x, y), obj_type, [all_sprites, collision_sprites])
        print(f"创建障碍物: {obj_type} 位置: ({x}, {y})")
    
    # 创建猫咪管理器和猫咪
    cat_manager = CatManager()
    
    # 手动创建一只测试猫咪
    test_cat = CatNPC(
        pos=(300, 250),  # 接近障碍物的位置
        npc_id="test_cat",
        npc_manager=None,
        groups=[all_sprites, npc_sprites],
        cat_name="测试猫",
        cat_personality="测试猫咪",
        collision_sprites=collision_sprites
    )
    
    print(f"✅ 创建测试猫咪: {test_cat.cat_name}")
    print(f"   初始位置: {test_cat.rect.center}")
    print(f"   碰撞精灵数量: {len(collision_sprites)}")
    
    # 测试位置有效性检查
    print("\n🔍 测试位置有效性检查:")
    test_positions = [
        (350, 280),  # 接近障碍物
        (400, 300),  # 障碍物位置
        (450, 350),  # 远离障碍物
        (100, 100),  # 空旷区域
    ]
    
    for x, y in test_positions:
        is_valid = test_cat._is_position_valid(x, y)
        status = "✅ 有效" if is_valid else "❌ 无效"
        print(f"   位置 ({x}, {y}): {status}")
    
    # 模拟移动测试
    print("\n🎮 模拟移动测试:")
    for i in range(5):
        print(f"\n--- 移动测试 {i+1} ---")
        initial_pos = test_cat.rect.center
        print(f"移动前位置: {initial_pos}")
        
        # 设置新目标
        test_cat._set_random_target()
        print(f"目标位置: {test_cat.target_pos}")
        
        # 模拟几帧移动
        dt = 1/60  # 60 FPS
        for frame in range(30):  # 半秒移动
            test_cat._update_movement(dt)
            
            # 检查是否卡在障碍物中
            for obstacle in collision_sprites:
                if hasattr(obstacle, 'hitbox'):
                    if obstacle.hitbox.colliderect(test_cat.hitbox):
                        print(f"⚠️  警告: 猫咪与障碍物重叠! 帧: {frame}")
                        break
                elif obstacle.rect.colliderect(test_cat.hitbox):
                    print(f"⚠️  警告: 猫咪与障碍物重叠! 帧: {frame}")
                    break
        
        final_pos = test_cat.rect.center
        print(f"移动后位置: {final_pos}")
        
        # 计算移动距离
        distance = ((final_pos[0] - initial_pos[0]) ** 2 + 
                   (final_pos[1] - initial_pos[1]) ** 2) ** 0.5
        print(f"移动距离: {distance:.1f} 像素")
    
    # 测试边界检查
    print("\n🚧 测试边界检查:")
    
    # 尝试移动到边界外
    test_cat.rect.center = (50, 50)  # 接近边界
    test_cat.pos = pygame.math.Vector2(test_cat.rect.center)
    test_cat.hitbox.center = test_cat.rect.center
    
    print(f"设置到边界位置: {test_cat.rect.center}")
    
    # 设置目标到边界外
    test_cat.target_pos = pygame.math.Vector2(10, 10)  # 边界外
    test_cat.direction = pygame.math.Vector2(-1, -1).normalize()
    
    # 尝试移动
    for _ in range(60):  # 1秒移动
        test_cat._update_movement(1/60)
        
        # 检查是否超出边界
        if not test_cat.world_bounds.contains(test_cat.rect):
            print(f"❌ 错误: 猫咪超出世界边界! 位置: {test_cat.rect.center}")
            break
    else:
        print(f"✅ 边界检查正常，最终位置: {test_cat.rect.center}")
    
    print("\n🎉 碰撞检测测试完成!")

def test_cat_pathfinding():
    """测试猫咪寻路能力"""
    print("\n🗺️  测试猫咪寻路能力")
    
    pygame.init()
    
    # 创建精灵组
    all_sprites = pygame.sprite.Group()
    collision_sprites = pygame.sprite.Group()
    npc_sprites = pygame.sprite.Group()
    
    # 创建复杂障碍物布局
    obstacle_layout = [
        # 创建一个"房间"，只有一个出口
        (300, 200), (350, 200), (400, 200), (450, 200),
        (300, 250), (450, 250),
        (300, 300), (450, 300),
        (300, 350), (350, 350), (400, 350),  # 缺少 (450, 350) 形成出口
    ]
    
    for x, y in obstacle_layout:
        obstacle = ASCIIGeneric((x, y), "wall", [all_sprites, collision_sprites])
    
    # 在"房间"内创建猫咪
    test_cat = CatNPC(
        pos=(375, 275),  # 房间中央
        npc_id="pathfind_cat",
        npc_manager=None,
        groups=[all_sprites, npc_sprites],
        cat_name="寻路猫",
        cat_personality="聪明的猫咪",
        collision_sprites=collision_sprites
    )
    
    print(f"在复杂环境中创建猫咪: {test_cat.rect.center}")
    
    # 统计成功找到有效目标的次数
    valid_targets = 0
    total_attempts = 20
    
    for i in range(total_attempts):
        test_cat._set_random_target()
        if test_cat.target_pos:
            # 检查目标是否在房间外（表示找到了出路）
            if (test_cat.target_pos.x < 300 or test_cat.target_pos.x > 450 or
                test_cat.target_pos.y < 200 or test_cat.target_pos.y > 350):
                valid_targets += 1
                print(f"✅ 找到房间外目标: {test_cat.target_pos}")
    
    success_rate = valid_targets / total_attempts * 100
    print(f"\n寻路成功率: {success_rate:.1f}% ({valid_targets}/{total_attempts})")
    
    if success_rate > 50:
        print("✅ 寻路能力良好")
    else:
        print("⚠️  寻路能力需要改进")

if __name__ == "__main__":
    test_cat_collision()
    test_cat_pathfinding()
    print("\n🎯 所有测试完成!")