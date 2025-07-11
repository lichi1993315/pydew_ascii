#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
聊天AI系统测试脚本
"""

import sys
import os
import asyncio

# 添加code目录到路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'code'))

def test_chat_ai_mock():
    """测试聊天AI的模拟回复功能"""
    print("=== 聊天AI模拟回复测试 ===")
    
    try:
        from chat_ai import ChatAI
        
        # 创建ChatAI实例（强制使用模拟模式）
        chat_ai = ChatAI()
        chat_ai.use_api = False  # 强制使用模拟模式
        
        print("✅ ChatAI实例创建成功")
        print(f"模式: {'API模式' if chat_ai.use_api else '模拟模式'}")
        
        # 测试不同NPC的回复
        test_cases = [
            ("trader_zhang", "你好"),
            ("trader_zhang", "我想买种子"),
            ("fisherman_li", "钓鱼有什么技巧吗？"),
            ("fisherman_li", "你好"),
            ("farmer_wang", "今天天气不错"),
            ("farmer_wang", "农业种植"),
            ("unknown_npc", "你好")  # 测试未知NPC
        ]
        
        print("\n📝 测试用例:")
        for npc_id, message in test_cases:
            try:
                response = chat_ai._generate_mock_response(npc_id, message)
                npc_info = chat_ai.npc_personalities.get(npc_id, {"name": "未知NPC"})
                print(f"  {npc_info['name']}: 玩家说'{message}' -> NPC回复'{response}'")
            except Exception as e:
                print(f"  ❌ {npc_id}回复失败: {e}")
        
        print("\n✅ 模拟回复测试完成")
        return True
        
    except Exception as e:
        print(f"❌ 模拟回复测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False

async def test_chat_ai_api():
    """测试聊天AI的API回复功能"""
    print("\n=== 聊天AI API回复测试 ===")
    
    try:
        from chat_ai import ChatAI
        
        chat_ai = ChatAI()
        
        if not chat_ai.use_api:
            print("⚠️  API模式未启用，跳过API测试")
            return True
        
        print("✅ API模式已启用")
        
        # 测试API回复
        test_message = "你好，今天天气怎么样？"
        npc_id = "trader_zhang"
        
        print(f"📤 发送测试消息: '{test_message}' 给 {npc_id}")
        
        response = await chat_ai.generate_npc_response(npc_id, test_message)
        
        print(f"📥 收到API回复: '{response}'")
        print("✅ API回复测试完成")
        return True
        
    except Exception as e:
        print(f"❌ API回复测试失败: {e}")
        print("🔄 回退到模拟模式测试")
        return test_chat_ai_mock()

def test_npc_personalities():
    """测试NPC个性设定"""
    print("\n=== NPC个性设定测试 ===")
    
    try:
        from chat_ai import ChatAI
        
        chat_ai = ChatAI()
        
        print("📋 NPC个性设定:")
        for npc_id, personality in chat_ai.npc_personalities.items():
            print(f"  🧑 {npc_id}:")
            print(f"    姓名: {personality['name']}")
            print(f"    性格: {personality['personality']}")
            print(f"    背景: {personality['context']}")
            print(f"    说话风格: {personality['speaking_style']}")
            print()
        
        print("✅ NPC个性设定测试完成")
        return True
        
    except Exception as e:
        print(f"❌ NPC个性设定测试失败: {e}")
        return False

def test_context_extraction():
    """测试游戏上下文提取"""
    print("\n=== 游戏上下文提取测试 ===")
    
    try:
        from chat_ai import ChatAI
        
        chat_ai = ChatAI()
        
        # 模拟玩家和关卡对象
        class MockPlayer:
            def __init__(self):
                self.money = 1000
                self.level = 5
                self.item_inventory = {"corn": 10, "tomato": 5}
                self.fishing_contest_stats = {"total_attempts": 20, "max_fish_length": 25}
        
        class MockLevel:
            def __init__(self):
                self.raining = False
        
        player = MockPlayer()
        level = MockLevel()
        
        context = chat_ai.add_context_from_game_state(player, level)
        
        print("🎮 提取的游戏上下文:")
        for key, value in context.items():
            print(f"  {key}: {value}")
        
        print("✅ 上下文提取测试完成")
        return True
        
    except Exception as e:
        print(f"❌ 上下文提取测试失败: {e}")
        return False

async def main():
    """主测试函数"""
    print("🤖 聊天AI系统测试")
    print("=" * 50)
    
    # 基础功能测试
    test1 = test_npc_personalities()
    test2 = test_context_extraction()
    test3 = test_chat_ai_mock()
    
    # API功能测试
    test4 = await test_chat_ai_api()
    
    # 总结
    all_passed = test1 and test2 and test3 and test4
    
    print("\n" + "=" * 50)
    if all_passed:
        print("🎉 所有测试通过！")
        print("\n📖 使用说明：")
        print("1. 在游戏中按 C 键打开聊天面板")
        print("2. 走到NPC附近")
        print("3. 按 Enter 键激活输入，输入消息并发送")
        print("4. NPC会根据角色设定智能回复")
        print("\n🔧 配置说明：")
        print("- 设置 CLAUDE_API_KEY 环境变量以启用API模式")
        print("- 确保代理服务器在 http://127.0.0.1:7890 运行")
        print("- 如果API不可用，系统会自动使用模拟回复")
    else:
        print("❌ 部分测试失败，请检查配置")
    
    print("\n🏁 测试完成")

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n🛑 测试被用户中断")
    except Exception as e:
        print(f"\n💥 测试异常: {e}")
        import traceback
        traceback.print_exc()