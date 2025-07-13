#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
AI模型对比测试 - Claude vs Doubao
测试两种模型在猫咪对话场景下的表现差异
"""

import asyncio
import os
import json
import time
from typing import Dict, List, Tuple
from datetime import datetime

# 设置环境变量路径
import sys
sys.path.append('../code')

from chat_ai import ChatAI

class ModelComparison:
    """AI模型对比测试类"""
    
    def __init__(self):
        self.claude_ai = None
        self.doubao_ai = None
        self.test_results = []
        
    def setup_models(self):
        """初始化两个模型的AI实例"""
        print("🔧 初始化AI模型...")
        
        # 初始化Claude模型
        try:
            self.claude_ai = ChatAI(model_type="claude")
            claude_available = "claude" in self.claude_ai.get_available_models()
            print(f"Claude模型: {'✅ 可用' if claude_available else '❌ 不可用'}")
        except Exception as e:
            print(f"Claude模型初始化失败: {e}")
            
        # 初始化Doubao模型
        try:
            self.doubao_ai = ChatAI(model_type="doubao")
            doubao_available = "doubao" in self.doubao_ai.get_available_models()
            print(f"Doubao模型: {'✅ 可用' if doubao_available else '❌ 不可用'}")
        except Exception as e:
            print(f"Doubao模型初始化失败: {e}")
    
    async def test_single_conversation(self, npc_id: str, player_message: str) -> Dict:
        """测试单次对话，比较两个模型的回复"""
        print(f"\n🧪 测试对话 - NPC: {npc_id}, 消息: {player_message}")
        
        results = {
            "npc_id": npc_id,
            "player_message": player_message,
            "timestamp": datetime.now().isoformat(),
            "claude_response": None,
            "doubao_response": None,
            "claude_time": 0,
            "doubao_time": 0,
            "claude_error": None,
            "doubao_error": None
        }
        
        # 测试Claude模型
        if self.claude_ai and self.claude_ai.use_api:
            try:
                start_time = time.time()
                claude_response = await self.claude_ai.generate_npc_response(npc_id, player_message)
                results["claude_time"] = time.time() - start_time
                results["claude_response"] = claude_response
                print(f"Claude回复: {claude_response}")
            except Exception as e:
                results["claude_error"] = str(e)
                print(f"Claude错误: {e}")
        else:
            results["claude_error"] = "Claude模型不可用"
            print("Claude模型不可用")
        
        # 测试Doubao模型
        if self.doubao_ai and self.doubao_ai.use_api:
            try:
                start_time = time.time()
                doubao_response = await self.doubao_ai.generate_npc_response(npc_id, player_message)
                results["doubao_time"] = time.time() - start_time
                results["doubao_response"] = doubao_response
                print(f"Doubao回复: {doubao_response}")
            except Exception as e:
                results["doubao_error"] = str(e)
                print(f"Doubao错误: {e}")
        else:
            results["doubao_error"] = "Doubao模型不可用"
            print("Doubao模型不可用")
        
        return results
    
    async def run_comprehensive_test(self):
        """运行综合对比测试"""
        print("🚀 开始综合模型对比测试")
        
        # 测试场景定义
        test_scenarios = [
            # 猫咪对话测试
            ("cat_01", "你好小橘！"),
            ("cat_01", "你今天在做什么呢？"),
            ("cat_02", "小白，你看起来很悠闲呢"),
            ("cat_03", "小黑，你在探索什么新地方吗？"),
            ("cat_04", "小灰，你又想睡觉了吗？"),
            ("cat_05", "小花，能给我表演个把戏吗？"),
            
            # NPC对话测试
            ("trader_zhang", "你好，我想买点种子"),
            ("fisherman_li", "今天适合钓鱼吗？"),
            ("farmer_wang", "这个季节种什么比较好？"),
            
            # 复杂对话测试
            ("cat_06", "咪咪，你想被摸摸吗？我很温柔的"),
            ("cat_07", "喵喵，虽然你很独立，但我们还是可以做朋友的对吧？"),
            ("cat_08", "球球，我这里有小鱼干，你要吗？"),
            ("cat_09", "毛毛，不要怕，我不会伤害你的"),
            ("cat_10", "糖糖，你又在计划什么恶作剧吗？")
        ]
        
        # 执行测试
        for npc_id, message in test_scenarios:
            result = await self.test_single_conversation(npc_id, message)
            self.test_results.append(result)
            
            # 等待一秒避免API限流
            await asyncio.sleep(1)
        
        # 生成测试报告
        self.generate_test_report()
    
    def generate_test_report(self):
        """生成测试报告"""
        print("\n📊 生成测试报告...")
        
        # 统计数据
        claude_successes = sum(1 for r in self.test_results if r["claude_response"] is not None)
        doubao_successes = sum(1 for r in self.test_results if r["doubao_response"] is not None)
        total_tests = len(self.test_results)
        
        claude_avg_time = sum(r["claude_time"] for r in self.test_results if r["claude_time"] > 0) / max(claude_successes, 1)
        doubao_avg_time = sum(r["doubao_time"] for r in self.test_results if r["doubao_time"] > 0) / max(doubao_successes, 1)
        
        # 创建报告
        report = {
            "test_summary": {
                "total_tests": total_tests,
                "claude_success_rate": claude_successes / total_tests * 100,
                "doubao_success_rate": doubao_successes / total_tests * 100,
                "claude_avg_response_time": round(claude_avg_time, 2),
                "doubao_avg_response_time": round(doubao_avg_time, 2),
                "test_timestamp": datetime.now().isoformat()
            },
            "detailed_results": self.test_results
        }
        
        # 保存报告到文件
        report_filename = f"model_comparison_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(report_filename, 'w', encoding='utf-8') as f:
            json.dump(report, f, ensure_ascii=False, indent=2)
        
        # 打印概要报告
        print("\n" + "="*60)
        print("                   模型对比测试报告")
        print("="*60)
        print(f"总测试数: {total_tests}")
        print(f"Claude成功率: {claude_successes}/{total_tests} ({report['test_summary']['claude_success_rate']:.1f}%)")
        print(f"Doubao成功率: {doubao_successes}/{total_tests} ({report['test_summary']['doubao_success_rate']:.1f}%)")
        print(f"Claude平均响应时间: {claude_avg_time:.2f}秒")
        print(f"Doubao平均响应时间: {doubao_avg_time:.2f}秒")
        print(f"\n详细报告已保存到: {report_filename}")
        
        # 分析回复质量
        self.analyze_response_quality()
    
    def analyze_response_quality(self):
        """分析回复质量"""
        print("\n🔍 回复质量分析:")
        
        for result in self.test_results:
            if result["claude_response"] and result["doubao_response"]:
                print(f"\n--- {result['npc_id']} 对话分析 ---")
                print(f"玩家消息: {result['player_message']}")
                print(f"Claude回复: {result['claude_response']}")
                print(f"Doubao回复: {result['doubao_response']}")
                
                # 简单的质量指标
                claude_len = len(result['claude_response'])
                doubao_len = len(result['doubao_response'])
                
                print(f"回复长度 - Claude: {claude_len}字, Doubao: {doubao_len}字")
                
                # 检查是否包含角色特色
                npc_name = self.claude_ai.npc_personalities.get(result['npc_id'], {}).get('name', '')
                claude_has_character = any(word in result['claude_response'] for word in ['喵', '嗯', '呵呵', '哈哈'])
                doubao_has_character = any(word in result['doubao_response'] for word in ['喵', '嗯', '呵呵', '哈哈'])
                
                print(f"角色特色表现 - Claude: {'✅' if claude_has_character else '❌'}, Doubao: {'✅' if doubao_has_character else '❌'}")

async def main():
    """主测试函数"""
    print("🎯 AI模型对比测试开始")
    
    # 创建测试实例
    comparison = ModelComparison()
    
    # 设置模型
    comparison.setup_models()
    
    # 运行测试
    await comparison.run_comprehensive_test()
    
    print("\n✅ 测试完成！")

if __name__ == "__main__":
    # 运行测试
    asyncio.run(main())