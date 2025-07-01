#!/usr/bin/env python3
"""
Claude API 测试脚本
用于测试API连接和调用功能
"""

import os
import json
import asyncio
import httpx
from datetime import datetime

# 导入dotenv来加载.env文件
try:
    from dotenv import load_dotenv
    load_dotenv()
    print("✅ .env文件加载成功")
except ImportError:
    print("⚠️  python-dotenv未安装，如果使用.env文件请安装: pip install python-dotenv")

# 尝试导入anthropic库
try:
    import anthropic
    print("✅ anthropic库导入成功")
except ImportError:
    print("❌ anthropic库未安装")
    print("   安装方法: pip install anthropic")
    exit(1)

async def test_claude_api():
    """测试Claude API调用"""
    print("🤖 开始测试Claude API...")
    print("=" * 50)
    
    # 获取API密钥
    api_key = os.environ.get("CLAUDE_API_KEY")
    if not api_key:
        print("❌ 未找到CLAUDE_API_KEY环境变量")
        print("   请设置环境变量或直接输入API密钥")
        api_key = input("请输入API密钥: ").strip()
        if not api_key:
            print("❌ 未提供API密钥，退出测试")
            return
    
    print(f"✅ 检测到API密钥: {api_key[:10]}...")
    
    try:
        # 创建客户端

        custom_httpx_client = httpx.Client(
            transport=httpx.HTTPTransport(
                proxy=httpx.Proxy(
                    url="http://127.0.0.1:7890"
                )
            ),
            timeout=30.0
        )
        client = anthropic.Anthropic(
            api_key=api_key,
            http_client=custom_httpx_client
        )
        print("✅ Claude客户端创建成功")
        
        # 准备测试提示词
        test_prompt = """你好！这是一个API连接测试。请简单回复以下问题：

1. 你是什么AI助手？
2. 今天天气怎么样？（可以说你不知道具体天气）
3. 请用一句话介绍一下钓鱼游戏的乐趣

请用JSON格式回复，格式如下：
{"ai_name": "你的名字", "weather": "关于天气的回复", "fishing_fun": "关于钓鱼乐趣的描述"}"""
        
        print("\n🔄 正在发送测试请求...")
        print(f"📝 测试提示词: {test_prompt[:100]}...")
        
        # 使用用户提供的代码格式进行API调用
        
        
        
        
        
        # 发送请求
        response = client.messages.create(
            model="claude-3-7-sonnet-20250219",
            max_tokens=1024,
            messages=[
                {
                    "role": "user",
                    "content": "hello?"
                }
            ]
        )
        
        print(response.content)

        message = client.messages.create(
            model="claude-opus-4-20250514",
            max_tokens=1024,
            messages=[
                {"role": "user", "content": "Hello, Claude"}
            ]
        )
        print(message.content)

        
        print("✅ API调用成功！")
        
        # 解析响应
        response_text = response.content[0].text
        print(f"\n📨 API响应:")
        print(f"📄 响应长度: {len(response_text)} 字符")
        print(f"📝 响应内容:")
        print("-" * 40)
        print(response_text)
        print("-" * 40)
        
        # 尝试解析JSON
        try:
            json_response = json.loads(response_text)
            print("\n✅ JSON解析成功:")
            for key, value in json_response.items():
                print(f"   {key}: {value}")
        except json.JSONDecodeError:
            print("\n⚠️  响应不是有效的JSON格式")
        
        # 显示使用统计
        print(f"\n📊 API调用统计:")
        print(f"   模型: claude-3-5-sonnet-20241022")
        print(f"   请求时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"   Token限制: 2048")
        print(f"   温度参数: 0.7")
        
        print("\n🎉 API测试完成！")
        
    except anthropic.APIError as e:
        print(f"❌ API错误: {e}")
        if "403" in str(e):
            print("💡 可能的解决方案:")
            print("   1. 检查API密钥是否正确")
            print("   2. 检查账户是否有足够的额度")
            print("   3. 检查API密钥是否有相应权限")
    except Exception as e:
        print(f"❌ 未知错误: {e}")
        import traceback
        traceback.print_exc()

async def test_game_dialogue():
    """测试游戏对话生成"""
    print("\n🎮 测试游戏对话生成...")
    print("=" * 50)
    
    # 获取API密钥
    api_key = os.environ.get("CLAUDE_API_KEY")
    if not api_key:
        print("⚠️  跳过对话测试（无API密钥）")
        return
    
    try:
        client = anthropic.Anthropic(api_key=api_key)
        
        # 游戏角色对话测试
        character_prompt = """你是《萌爪派对：小镇时光》中的钓鱼店老板老墨。

**核心性格特征：**
- 粗犷暴躁的外表，但内心善良
- 说话风格：短句、带方言味、爱用"老子"自称
- 对钓鱼技巧极其执着，是隐退的"镇钓王"
- 表面毒舌但会偷偷帮助新手

**当前情况：**
玩家第一次来到你的钓鱼店，带着一只橘猫。

请以老墨的身份回应，并提供2-3个对话选项。

**回复格式：**
{"text": "老墨的话", "options": ["选项1", "选项2", "选项3"]}

玩家行动：向你打招呼"""
        
        print("🗣️  测试角色对话生成...")
        
        response = client.messages.create(
            model="claude-3-7-sonnet-20250219",
            max_tokens=2048,
            temperature=0.7,
            messages=[
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": character_prompt}
                    ]
                }
            ]
        )
        
        print("✅ 对话生成成功！")
        
        response_text = response.content[0].text
        print(f"\n💬 老墨的回复:")
        print("-" * 40)
        print(response_text)
        print("-" * 40)
        
        # 尝试解析对话JSON
        try:
            dialogue = json.loads(response_text)
            print("\n✅ 对话JSON解析成功:")
            print(f"   对话内容: {dialogue.get('text', 'N/A')}")
            print(f"   选项数量: {len(dialogue.get('options', []))}")
            for i, option in enumerate(dialogue.get('options', []), 1):
                print(f"   选项{i}: {option}")
        except json.JSONDecodeError:
            print("\n⚠️  对话响应不是有效的JSON格式")
        
    except Exception as e:
        print(f"❌ 对话测试失败: {e}")

def test_without_api():
    """无API的模拟测试"""
    print("\n🎭 模拟模式测试...")
    print("=" * 50)
    
    # 模拟API响应
    mock_responses = {
        "basic_test": {
            "ai_name": "Claude (模拟模式)",
            "weather": "我无法获取实时天气信息，但希望今天是个好天气！",
            "fishing_fun": "钓鱼游戏让玩家体验宁静致远的乐趣，在等待鱼儿上钩的过程中享受平静时光。"
        },
        "game_dialogue": {
            "text": "啧！又来了个嫩头青！看你那小猫挺有意思的...想学钓鱼？先证明你不是来浪费老子时间的！",
            "options": [
                "我想学钓鱼技巧",
                "这猫咪有什么特别的吗？",
                "给我推荐个钓竿"
            ]
        }
    }
    
    print("✅ 基础测试模拟响应:")
    basic_response = mock_responses["basic_test"]
    for key, value in basic_response.items():
        print(f"   {key}: {value}")
    
    print("\n✅ 游戏对话模拟响应:")
    game_response = mock_responses["game_dialogue"]
    print(f"   老墨说: {game_response['text']}")
    print(f"   选项数量: {len(game_response['options'])}")
    for i, option in enumerate(game_response['options'], 1):
        print(f"   选项{i}: {option}")
    
    print("\n🎉 模拟测试完成！")

async def main():
    """主测试函数"""
    print("🧪 Claude API 测试工具")
    print("🎮 萌爪派对：小镇时光")
    print("=" * 60)
    
    # 基础API测试
    await test_claude_api()
    
    # 游戏对话测试
    await test_game_dialogue()
    
    # 模拟模式测试
    test_without_api()
    
    print("\n🏁 所有测试完成！")
    print("💡 如果API测试失败，游戏会自动切换到模拟模式继续运行。")

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n🛑 测试被用户中断")
    except Exception as e:
        print(f"\n💥 测试异常: {e}") 