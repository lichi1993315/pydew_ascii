#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Doubao模型基础功能测试
验证Doubao模型集成是否正常工作
"""

import asyncio
import os
import sys

# 设置环境变量路径
sys.path.append('../code')

from chat_ai import ChatAI

async def test_doubao_basic():
    """测试Doubao模型基础功能"""
    print("🧪 测试Doubao模型基础功能")
    
    # 创建Doubao AI实例
    print("\n1. 初始化Doubao模型...")
    doubao_ai = ChatAI(model_type="doubao")
    
    # 检查模型状态
    model_info = doubao_ai.get_current_model_info()
    print(f"当前模型: {model_info['model_type']}")
    print(f"API状态: {'✅ 激活' if model_info['use_api'] else '❌ 未激活'}")
    print(f"可用模型: {model_info['available_models']}")
    print(f"客户端状态: {model_info['client_status']}")
    
    if not doubao_ai.use_api:
        print("❌ Doubao模型不可用，可能的原因:")
        print("   - ARK_API_KEY环境变量未设置")
        print("   - openai库未安装")
        print("   - 网络连接问题")
        return
    
    # 测试基础对话
    print("\n2. 测试基础对话...")
    test_cases = [
        ("cat_01", "你好小橘！"),
        ("trader_zhang", "你好，有什么好货吗？"),
        ("cat_06", "咪咪，想被摸摸吗？")
    ]
    
    for npc_id, message in test_cases:
        try:
            print(f"\n测试 {npc_id}: {message}")
            response = await doubao_ai.generate_npc_response(npc_id, message)
            print(f"回复: {response}")
        except Exception as e:
            print(f"错误: {e}")
    
    # 测试模型切换
    print("\n3. 测试模型切换...")
    available_models = doubao_ai.get_available_models()
    print(f"可用模型: {available_models}")
    
    if "claude" in available_models:
        print("切换到Claude模型...")
        doubao_ai.switch_model("claude")
        new_info = doubao_ai.get_current_model_info()
        print(f"切换后模型: {new_info['model_type']}")
        
        # 测试Claude回复
        try:
            response = await doubao_ai.generate_npc_response("cat_01", "测试Claude模型")
            print(f"Claude回复: {response}")
        except Exception as e:
            print(f"Claude测试错误: {e}")
        
        # 切换回Doubao
        print("切换回Doubao模型...")
        doubao_ai.switch_model("doubao")
    
    print("\n✅ 基础功能测试完成")

async def test_model_comparison():
    """快速对比两个模型"""
    print("\n🔄 快速模型对比测试")
    
    claude_ai = ChatAI(model_type="claude")
    doubao_ai = ChatAI(model_type="doubao")
    
    test_message = "你好，我是新来的农夫！"
    test_npc = "trader_zhang"
    
    print(f"\n测试场景: {test_npc} - {test_message}")
    
    # Claude回复
    if claude_ai.use_api:
        try:
            claude_response = await claude_ai.generate_npc_response(test_npc, test_message)
            print(f"Claude: {claude_response}")
        except Exception as e:
            print(f"Claude错误: {e}")
    else:
        print("Claude: 模型不可用")
    
    # Doubao回复
    if doubao_ai.use_api:
        try:
            doubao_response = await doubao_ai.generate_npc_response(test_npc, test_message)
            print(f"Doubao: {doubao_response}")
        except Exception as e:
            print(f"Doubao错误: {e}")
    else:
        print("Doubao: 模型不可用")

if __name__ == "__main__":
    print("🎯 Doubao模型测试开始")
    
    # 检查环境变量
    claude_key = os.environ.get("CLAUDE_API_KEY")
    doubao_key = os.environ.get("ARK_API_KEY")
    
    print(f"CLAUDE_API_KEY: {'✅ 已设置' if claude_key else '❌ 未设置'}")
    print(f"ARK_API_KEY: {'✅ 已设置' if doubao_key else '❌ 未设置'}")
    
    # 运行测试
    asyncio.run(test_doubao_basic())
    asyncio.run(test_model_comparison())
    
    print("\n🎉 所有测试完成！")