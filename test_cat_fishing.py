#!/usr/bin/env python3
"""
测试钓鱼获得猫咪功能
"""

import sys
import os
sys.path.append('src')

from systems.fish_system import FishSystem

def test_cat_fishing():
    """测试钓鱼获得猫咪的概率"""
    fish_system = FishSystem()
    
    # 统计结果
    total_attempts = 1000
    cat_catches = 0
    fish_catches = 0
    nothing_catches = 0
    cat_types = {}
    
    print(f"🎣 开始测试钓鱼系统，总共尝试 {total_attempts} 次...")
    print("=" * 50)
    
    for i in range(total_attempts):
        result = fish_system.catch_fish()
        
        if result:
            if result.get('type') == 'cat':
                cat_catches += 1
                cat_name = result['name']
                cat_types[cat_name] = cat_types.get(cat_name, 0) + 1
                if cat_catches <= 10:  # 只显示前10只猫
                    print(f"🐱 第{cat_catches}只: {cat_name} ({result['rarity_name']})")
            else:
                fish_catches += 1
        else:
            nothing_catches += 1
    
    print("=" * 50)
    print("📊 测试结果统计:")
    print(f"总尝试次数: {total_attempts}")
    print(f"钓到猫咪: {cat_catches} 只 ({cat_catches/total_attempts*100:.2f}%)")
    print(f"钓到鱼类: {fish_catches} 条 ({fish_catches/total_attempts*100:.2f}%)")
    print(f"什么都没钓到: {nothing_catches} 次 ({nothing_catches/total_attempts*100:.2f}%)")
    
    print("\n🐱 猫咪类型统计:")
    for cat_name, count in cat_types.items():
        print(f"  {cat_name}: {count} 只 ({count/cat_catches*100:.1f}%)")

def test_single_cat_catch():
    """测试单次钓到猫咪的详细信息"""
    fish_system = FishSystem()
    
    print("🎯 尝试钓到一只猫咪...")
    
    attempts = 0
    while attempts < 500:  # 最多尝试500次
        attempts += 1
        result = fish_system.catch_fish()
        
        if result and result.get('type') == 'cat':
            print(f"🎉 在第 {attempts} 次尝试后钓到了猫咪！")
            print(f"🐱 猫咪信息:")
            print(f"  名称: {result['name']}")
            print(f"  性格: {result['personality']}")
            print(f"  稀有度: {result['rarity_name']}")
            print(f"  颜色: {result['color']}")
            print(f"  ASCII: {result['ascii_char']}")
            break
    else:
        print(f"😿 尝试了 {attempts} 次都没有钓到猫咪")

if __name__ == "__main__":
    print("🐱 猫咪钓鱼系统测试")
    print("选择测试模式:")
    print("1. 概率统计测试 (1000次)")
    print("2. 单次猫咪捕获测试")
    
    choice = input("请输入选择 (1/2): ").strip()
    
    if choice == "1":
        test_cat_fishing()
    elif choice == "2":
        test_single_cat_catch()
    else:
        print("无效选择，运行概率测试...")
        test_cat_fishing()