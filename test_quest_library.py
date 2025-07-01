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
    
    print("\n2. 生成随机任务示例:")
    
    # 测试各种任务类型
    quest_types = ["fishing_attempts", "catch_big_fish", "catch_rare_fish", "talk_to_npc", "sell_fish", "consecutive_fishing"]
    
    for quest_type in quest_types:
        print(f"\n--- {quest_type} 任务示例 ---")
        for difficulty in ["easy", "medium", "hard"]:
            quest = quest_lib.generate_random_quest(quest_type, difficulty)
            print(f"[{difficulty.upper()}] {quest.title}")
            print(f"  描述: {quest.description}")
            print(f"  目标: {quest.objectives}")
            print(f"  奖励: {quest.rewards}")
            print(f"  对话: {quest.dialogue[0]}...")
    
    print("\n3. 批量生成任务测试:")
    batch = quest_lib.generate_quest_batch(10, True)
    for i, quest in enumerate(batch, 1):
        print(f"{i}. {quest.title} ({list(quest.objectives.keys())[0]})")

def test_npc_manager():
    """测试NPC管理器"""
    print("\n=== NPC管理器测试 ===")
    
    # 创建模拟的玩家对象
    class MockPlayer:
        def __init__(self):
            self.active_quests = []
            
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
    
    print("\n2. 为各个NPC获取任务:")
    for npc_id in ["fisherman_li", "farmer_wang"]:
        print(f"\n--- {npc_id} ---")
        for i in range(3):
            quest = npc_manager.get_available_quest_for_npc(npc_id, player)
            if quest:
                print(f"任务 {i+1}: {quest.title}")
                print(f"  类型: {list(quest.objectives.keys())[0]}")
                print(f"  参数: {list(quest.objectives.values())[0]}")
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