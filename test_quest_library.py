#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
任务库系统测试脚本
"""

import sys
import os

# 添加code目录到路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'code'))

from npc_system import QuestLibrary, NPCManager

def test_quest_library():
    """测试任务库系统"""
    print("=== 任务库系统测试 ===")
    
    # 创建任务库
    quest_lib = QuestLibrary()
    
    print("\n1. 任务库统计信息:")
    stats = quest_lib.get_quest_statistics()
    print(f"任务类型总数: {stats['total_quest_types']}")
    print(f"可用任务类型: {', '.join(stats['quest_types'])}")
    print(f"难度等级: {', '.join(stats['difficulty_levels'])}")
    
    print("\n2. 无玩家进度时的任务生成:")
    # 测试各种任务类型（无玩家信息）
    quest_types = ["fishing_attempts", "catch_big_fish", "catch_rare_fish", "talk_to_npc", "sell_fish"]
    
    for quest_type in quest_types:
        quest = quest_lib.generate_random_quest(quest_type, "medium")
        print(f"- {quest.title}: {quest.objectives}")
    
    print("\n3. 根据玩家进度生成适应性任务:")
    
    # 创建模拟的玩家对象 - 新手玩家
    class MockPlayer:
        def __init__(self, name, max_fish_length=0, fish_inventory=None):
            self.name = name
            self.fishing_contest_stats = {"max_fish_length": max_fish_length}
            self.fish_inventory = fish_inventory or []
    
    # 测试不同玩家进度
    players = [
        MockPlayer("新手玩家", 0, []),
        MockPlayer("初级玩家", 28, [{"rarity": "common"}, {"rarity": "uncommon"}]),
        MockPlayer("中级玩家", 45, [{"rarity": "common"}, {"rarity": "uncommon"}, {"rarity": "rare"}]),
        MockPlayer("高级玩家", 65, [{"rarity": "rare"}, {"rarity": "epic"}]),
        MockPlayer("专家玩家", 85, [{"rarity": "epic"}, {"rarity": "legendary"}]),
    ]
    
    for player in players:
        print(f"\n--- {player.name} (最大鱼长度: {player.fishing_contest_stats['max_fish_length']}cm) ---")
        
        # 测试钓大鱼任务
        big_fish_quest = quest_lib.generate_random_quest("catch_big_fish", "medium", player)
        print(f"钓大鱼任务: {big_fish_quest.title}")
        print(f"  要求长度: {big_fish_quest.objectives['catch_fish']['minimum_length']}cm")
        
        # 测试稀有鱼任务
        rare_fish_quest = quest_lib.generate_random_quest("catch_rare_fish", "medium", player)
        print(f"稀有鱼任务: {rare_fish_quest.title}")
        print(f"  要求稀有度: {rare_fish_quest.objectives['catch_fish']['minimum_rarity']}")
    
    print("\n4. 批量生成任务测试:")
    batch = quest_lib.generate_quest_batch(5, True, players[2])  # 使用中级玩家
    for i, quest in enumerate(batch, 1):
        obj_type = list(quest.objectives.keys())[0]
        obj_params = list(quest.objectives.values())[0]
        print(f"{i}. {quest.title} ({obj_type}: {obj_params})")

def test_npc_manager():
    """测试NPC管理器"""
    print("\n=== NPC管理器测试 ===")
    
    # 创建模拟的玩家对象（带钓鱼进度）
    class MockPlayer:
        def __init__(self):
            self.active_quests = []
            self.fishing_contest_stats = {"max_fish_length": 35}  # 模拟中等水平
            self.fish_inventory = [
                {"rarity": "common"}, 
                {"rarity": "uncommon"}, 
                {"rarity": "rare"}
            ]
            
        def add_quest(self, quest):
            self.active_quests.append(quest)
            print(f"添加任务: {quest.title}")
    
    # 创建NPC管理器
    npc_manager = NPCManager()
    player = MockPlayer()
    
    print("\n1. NPC管理器统计:")
    stats = npc_manager.get_all_quest_statistics()
    print(f"总任务类型: {stats['total_quest_types']}")
    print(f"NPC任务池: {stats['npc_quest_pools']}")
    
    print(f"\n2. 测试玩家进度适应性 (最大鱼长度: {player.fishing_contest_stats['max_fish_length']}cm):")
    for npc_id in ["fisherman_li", "farmer_wang"]:
        print(f"\n--- {npc_id} ---")
        for i in range(3):
            quest = npc_manager.get_available_quest_for_npc(npc_id, player)
            if quest:
                obj_type = list(quest.objectives.keys())[0]
                obj_params = list(quest.objectives.values())[0]
                print(f"任务 {i+1}: {quest.title}")
                print(f"  类型: {obj_type}")
                print(f"  参数: {obj_params}")
                # 模拟接受任务
                player.add_quest(quest)
            else:
                print(f"任务 {i+1}: 无可用任务")

def main():
    """主函数"""
    print("🎮 PyDew任务库系统测试\n")
    
    try:
        test_quest_library()
        test_npc_manager()
        
        print("\n✅ 测试完成！任务库系统运行正常。")
        
    except Exception as e:
        print(f"\n❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main() 