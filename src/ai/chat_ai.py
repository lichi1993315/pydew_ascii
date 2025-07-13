#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
聊天AI系统 - 使用Claude API为NPC生成智能回复
"""

import os
import json
import asyncio
import httpx
from typing import Dict, Optional, List
from datetime import datetime
from .ai_config_manager import get_config_manager

# 尝试导入相关库
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

try:
    import anthropic
    ANTHROPIC_AVAILABLE = True
except ImportError:
    ANTHROPIC_AVAILABLE = False
    print("⚠️  anthropic库未安装，将使用模拟回复模式")

try:
    import openai
    OPENAI_AVAILABLE = True
except ImportError:
    OPENAI_AVAILABLE = False
    print("⚠️  openai库未安装，无法使用Doubao模型")

class ChatAI:
    """
    聊天AI系统 - 管理NPC的智能回复
    支持多种AI模型：Claude、Doubao
    """
    
    def __init__(self, model_type: str = None):
        # 加载配置管理器
        self.config_manager = get_config_manager()
        
        # 模型配置
        self.model_type = model_type or os.environ.get("AI_MODEL_TYPE") or self.config_manager.get_default_model()
        
        # API配置
        self.claude_api_key = os.environ.get("CLAUDE_API_KEY")
        self.doubao_api_key = os.environ.get("ARK_API_KEY")
        
        # 客户端初始化
        self.claude_client = None
        self.doubao_client = None
        self.current_client = None
        self.use_api = False
        
        # 响应缓存
        self.response_cache = {}  # 缓存回复以减少API调用
        
        # 对话历史管理
        self.conversation_history = {}  # 按NPC ID存储对话历史
        chat_settings = self.config_manager.get_chat_settings()
        self.max_history_length = chat_settings.get("conversation_history_length", 10)   # 最大保存的对话轮数
        
        # NPC角色设定
        self.npc_personalities = {
            "trader_zhang": {
                "name": "商人张三",
                "personality": "精明的商人，说话直接，喜欢讨论生意和交易",
                "context": "经营着小镇的杂货店，出售种子和购买农产品",
                "speaking_style": "商人口吻，爱谈钱和生意"
            },
            "fisherman_li": {
                "name": "渔夫老李",
                "personality": "经验丰富的老渔夫，话不多但很实在，对钓鱼很有心得",
                "context": "在小镇池塘边钓鱼的老人，知道所有钓鱼技巧",
                "speaking_style": "简朴的话语，经常分享钓鱼经验"
            },
            "farmer_wang": {
                "name": "农夫老王",
                "personality": "勤劳朴实的农夫，热爱土地，对农业很有经验",
                "context": "小镇的农业专家，种植各种作物",
                "speaking_style": "朴实的农民话语，喜欢谈论农作物和天气"
            },
            # 猫咪NPC设定
            "cat_01": {
                "name": "小橘",
                "personality": "活泼好动的橘猫，喜欢到处跑跳，充满活力",
                "context": "在小镇自由漫步的可爱橘猫",
                "speaking_style": "活泼可爱的猫语，经常用'喵'开头"
            },
            "cat_02": {
                "name": "小白",
                "personality": "温顺安静的白猫，喜欢晒太阳，性格温和",
                "context": "优雅的白猫，喜欢安静的地方",
                "speaking_style": "温柔优雅的猫语，语气轻柔"
            },
            "cat_03": {
                "name": "小黑",
                "personality": "好奇心强的黑猫，喜欢探索新事物",
                "context": "神秘的黑猫，总是在探索新的地方",
                "speaking_style": "好奇的猫语，经常问问题"
            },
            "cat_04": {
                "name": "小灰",
                "personality": "慵懒可爱的灰猫，总是想睡觉",
                "context": "懒洋洋的灰猫，大部分时间在休息",
                "speaking_style": "慵懒的猫语，经常打哈欠"
            },
            "cat_05": {
                "name": "小花",
                "personality": "聪明机灵的花猫，会各种小把戏",
                "context": "聪明的花猫，喜欢展示自己的技能",
                "speaking_style": "聪明的猫语，喜欢炫耀自己"
            },
            "cat_06": {
                "name": "咪咪",
                "personality": "粘人撒娇的猫咪，喜欢被摸摸",
                "context": "非常亲人的猫咪，喜欢与人类互动",
                "speaking_style": "撒娇的猫语，经常求抚摸"
            },
            "cat_07": {
                "name": "喵喵",
                "personality": "独立自主的猫，有自己的想法",
                "context": "独立的猫咪，有自己的生活方式",
                "speaking_style": "独立的猫语，不太依赖他人"
            },
            "cat_08": {
                "name": "球球",
                "personality": "贪吃的小猫，对食物很敏感",
                "context": "总是在寻找食物的圆滚滚猫咪",
                "speaking_style": "贪吃的猫语，经常提到食物"
            },
            "cat_09": {
                "name": "毛毛",
                "personality": "胆小害羞的猫，容易受到惊吓",
                "context": "害羞的长毛猫，不太敢接近陌生人",
                "speaking_style": "胆怯的猫语，说话小心翼翼"
            },
            "cat_10": {
                "name": "糖糖",
                "personality": "淘气捣蛋的猫，喜欢恶作剧",
                "context": "调皮的猫咪，总是制造小麻烦",
                "speaking_style": "调皮的猫语，充满恶作剧精神"
            }
        }
        
        # 模拟回复模板
        self.mock_responses = {
            "trader_zhang": [
                "你好！需要买点什么吗？我这里有最新鲜的种子！",
                "生意兴隆！你带了什么好货来卖吗？",
                "哎呀，这位朋友看起来就像个成功的农夫！",
                "价格公道，童叟无欺！想要什么尽管说！"
            ],
            "fisherman_li": [
                "小伙子，钓鱼要有耐心啊...",
                "今天的鱼儿特别活跃，是个钓鱼的好日子。",
                "我钓了一辈子鱼，有什么不懂的可以问我。",
                "静下心来，鱼儿自然会上钩的。"
            ],
            "farmer_wang": [
                "种地不容易啊，要用心照料每一株作物。",
                "看这天气，明天应该会下雨，对庄稼有好处。",
                "土地是我们的根本，要好好爱护她。",
                "年轻人，农业可是门大学问！"
            ],
            # 猫咪回复
            "cat_01": [
                "喵！你好呀，我是小橘！",
                "喵喵～想和我一起玩吗？",
                "橘猫最可爱了，喵！",
                "跑跑跳跳真开心，喵～"
            ],
            "cat_02": [
                "喵...你好，我是小白...",
                "今天的阳光真温暖呢，喵...",
                "安安静静最舒服了，喵～",
                "轻轻的摸摸头就好，喵..."
            ],
            "cat_03": [
                "喵？你是谁？好奇怪的人类...",
                "这里有什么好玩的吗，喵？",
                "我要去探索新地方了，喵！",
                "黑猫也很可爱的，喵～"
            ],
            "cat_04": [
                "喵...好困啊...哈欠～",
                "让我再睡一会儿嘛，喵...",
                "懒懒的最舒服了，喵～",
                "不想动...只想睡觉，喵..."
            ],
            "cat_05": [
                "喵！看我的新把戏！",
                "我很聪明的，什么都会，喵～",
                "花猫就是比别的猫厉害，喵！",
                "要不要看我翻跟头，喵？"
            ],
            "cat_06": [
                "喵～摸摸我嘛～",
                "我最喜欢人类了，喵！",
                "抱抱我好不好，喵～",
                "咪咪要被宠爱，喵！"
            ],
            "cat_07": [
                "喵...我有自己的事要做...",
                "独立的猫不需要别人照顾，喵。",
                "我按自己的方式生活，喵～",
                "别太粘人，保持距离比较好，喵。"
            ],
            "cat_08": [
                "喵！你有食物吗？",
                "肚子好饿啊，有小鱼干吗，喵？",
                "球球要吃好吃的，喵～",
                "闻到香味了，在哪里呢，喵？"
            ],
            "cat_09": [
                "喵...不要靠太近...",
                "我有点害怕陌生人，喵...",
                "请温柔一点好吗，喵...",
                "毛毛很胆小的，喵..."
            ],
            "cat_10": [
                "喵嘿嘿！要不要看我恶作剧？",
                "糖糖最会捣蛋了，喵！",
                "今天又搞了什么坏事呢，喵～",
                "调皮才有趣，你说对吧，喵？"
            ]
        }
        
        self._initialize_clients()
        self._set_active_model(self.model_type)
    
    def _initialize_clients(self):
        """初始化所有可用的AI客户端"""
        # 初始化Claude客户端
        if ANTHROPIC_AVAILABLE and self.claude_api_key:
            try:
                # 使用与test_claude_api.py相同的proxy设置
                custom_httpx_client = httpx.Client(
                    transport=httpx.HTTPTransport(
                        proxy=httpx.Proxy(
                            url="http://127.0.0.1:7890"
                        )
                    ),
                    timeout=30.0
                )
                
                self.claude_client = anthropic.Anthropic(
                    api_key=self.claude_api_key,
                    http_client=custom_httpx_client
                )
                print("🤖 ChatAI: Claude API客户端初始化成功")
                
            except Exception as e:
                print(f"🤖 ChatAI: Claude API客户端初始化失败: {e}")
        
        # 初始化Doubao客户端
        if OPENAI_AVAILABLE and self.doubao_api_key:
            try:
                self.doubao_client = openai.OpenAI(
                    api_key=self.doubao_api_key,
                    base_url="https://ark.cn-beijing.volces.com/api/v3",
                    timeout=30.0
                )
                print("🤖 ChatAI: Doubao API客户端初始化成功")
                
            except Exception as e:
                print(f"🤖 ChatAI: Doubao API客户端初始化失败: {e}")
        
        if not self.claude_client and not self.doubao_client:
            print("🤖 ChatAI: 没有可用的API客户端，使用模拟回复模式")
    
    def _set_active_model(self, model_type: str):
        """设置当前活跃的模型"""
        self.model_type = model_type.lower()
        
        if self.model_type == "claude" and self.claude_client:
            self.current_client = self.claude_client
            self.use_api = True
            print(f"🤖 ChatAI: 切换到Claude模型")
        elif self.model_type == "doubao" and self.doubao_client:
            self.current_client = self.doubao_client
            self.use_api = True
            print(f"🤖 ChatAI: 切换到Doubao模型")
        else:
            self.current_client = None
            self.use_api = False
            print(f"🤖 ChatAI: 模型 {model_type} 不可用，使用模拟回复模式")
    
    def switch_model(self, model_type: str):
        """动态切换AI模型"""
        print(f"🤖 ChatAI: 尝试切换到 {model_type} 模型")
        self._set_active_model(model_type)
        # 清除缓存以确保使用新模型
        self.response_cache.clear()
    
    def get_available_models(self) -> List[str]:
        """获取可用的模型列表"""
        available = []
        if self.claude_client:
            available.append("claude")
        if self.doubao_client:
            available.append("doubao")
        available.append("mock")  # 模拟模式总是可用
        return available
    
    def get_current_model_info(self) -> Dict:
        """获取当前模型信息"""
        return {
            "model_type": self.model_type,
            "use_api": self.use_api,
            "available_models": self.get_available_models(),
            "client_status": {
                "claude": self.claude_client is not None,
                "doubao": self.doubao_client is not None
            }
        }
    
    def get_best_model_for_npc(self, npc_id: str) -> str:
        """根据NPC获取最佳模型"""
        return self.config_manager.get_preferred_model_for_npc(npc_id)
    
    def auto_switch_model_for_npc(self, npc_id: str):
        """为NPC自动切换到最佳模型"""
        best_model = self.get_best_model_for_npc(npc_id)
        if best_model != self.model_type:
            print(f"🔄 为NPC {npc_id} 自动切换到 {best_model} 模型")
            self.switch_model(best_model)
    
    async def generate_npc_response(self, npc_id: str, player_message: str, context: Dict = None) -> str:
        """
        为NPC生成回复
        
        Args:
            npc_id: NPC的ID
            player_message: 玩家的消息
            context: 额外的上下文信息（如玩家状态、游戏进度等）
            
        Returns:
            NPC的回复文本
        """
        
        # 自动为NPC选择最佳模型
        self.auto_switch_model_for_npc(npc_id)
        
        # 添加玩家消息到对话历史
        self._add_to_conversation_history(npc_id, "玩家", player_message)
        
        # 生成包含历史的缓存键（考虑最近3轮对话和模型类型）
        recent_history = self._get_recent_conversation_context(npc_id, 3)
        cache_key = f"{npc_id}:{self.model_type}:{hash(str(recent_history) + player_message)}"
        
        if cache_key in self.response_cache:
            response = self.response_cache[cache_key]
        elif self.use_api and self.current_client:
            try:
                response = await self._generate_api_response(npc_id, player_message, context)
                # 缓存回复
                self.response_cache[cache_key] = response
            except Exception as e:
                print(f"🤖 ChatAI: {self.model_type} API调用失败，回退到模拟模式: {e}")
                # 回退到模拟回复
                response = self._generate_mock_response(npc_id, player_message)
        else:
            response = self._generate_mock_response(npc_id, player_message)
        
        # 添加NPC回复到对话历史
        self._add_to_conversation_history(npc_id, self.npc_personalities.get(npc_id, {}).get("name", "NPC"), response)
        
        return response
    
    async def _generate_api_response(self, npc_id: str, player_message: str, context: Dict = None) -> str:
        """使用当前选定的API生成回复"""
        if self.model_type == "claude":
            return await self._generate_claude_response(npc_id, player_message, context)
        elif self.model_type == "doubao":
            return await self._generate_doubao_response(npc_id, player_message, context)
        else:
            raise ValueError(f"不支持的模型类型: {self.model_type}")
    
    async def _generate_claude_response(self, npc_id: str, player_message: str, context: Dict = None) -> str:
        """使用Claude API生成回复"""
        
        npc_info = self.npc_personalities.get(npc_id, {
            "name": "NPC",
            "personality": "友好的村民",
            "context": "小镇居民",
            "speaking_style": "友好随和"
        })
        
        # 获取对话历史
        conversation_history = self._format_conversation_history(npc_id, 5)
        
        # 构建提示词
        system_prompt = f"""你是游戏《萌爪钓鱼》中的NPC：{npc_info['name']}

**角色设定：**
- 性格：{npc_info['personality']}
- 背景：{npc_info['context']}
- 说话风格：{npc_info['speaking_style']}

**重要指示：**
1. 请始终以{npc_info['name']}的身份回复
2. 保持角色的性格和说话风格
3. 回复要简洁自然，像真正的对话
4. 不要提及你是AI或游戏角色
5. 回复长度控制在1-2句话
6. 使用中文回复
7. 基于对话历史保持连贯性，记住之前聊过的内容
8. 如果玩家提到之前的话题，要能够回应

**对话上下文：**
{conversation_history}

**当前情况：**
玩家对你说："{player_message}"

请以{npc_info['name']}的身份，基于对话历史自然回复："""

        try:
            response = self.claude_client.messages.create(
                model="claude-sonnet-4-20250514",
                max_tokens=150,
                temperature=0.7,
                messages=[
                    {
                        "role": "user", 
                        "content": system_prompt
                    }
                ]
            )
            
            response_text = response.content[0].text.strip()
            
            # 清理回复（移除可能的引号或格式符号）
            response_text = response_text.strip('"\'`')
            
            return response_text
            
        except Exception as e:
            print(f"🤖 ChatAI: Claude API调用异常: {e}")
            raise e
    
    async def _generate_doubao_response(self, npc_id: str, player_message: str, context: Dict = None) -> str:
        """使用Doubao API生成回复"""
        
        npc_info = self.npc_personalities.get(npc_id, {
            "name": "NPC",
            "personality": "友好的村民",
            "context": "小镇居民",
            "speaking_style": "友好随和"
        })
        
        # 获取对话历史
        conversation_history = self._format_conversation_history(npc_id, 5)
        
        # 构建提示词
        system_prompt = f"""你是游戏《萌爪钓鱼》中的NPC：{npc_info['name']}

**角色设定：**
- 性格：{npc_info['personality']}
- 背景：{npc_info['context']}
- 说话风格：{npc_info['speaking_style']}

**重要指示：**
1. 请始终以{npc_info['name']}的身份回复
2. 保持角色的性格和说话风格
3. 回复要简洁自然，像真正的对话
4. 不要提及你是AI或游戏角色
5. 回复长度控制在1-2句话
6. 使用中文回复
7. 基于对话历史保持连贯性，记住之前聊过的内容
8. 如果玩家提到之前的话题，要能够回应

**对话上下文：**
{conversation_history}

**当前情况：**
玩家对你说："{player_message}"

请以{npc_info['name']}的身份，基于对话历史自然回复："""

        try:
            response = self.doubao_client.chat.completions.create(
                model="doubao-seed-1-6-250615",
                messages=[
                    {
                        "role": "system",
                        "content": "你是一个游戏中的NPC角色，需要根据角色设定进行对话。"
                    },
                    {
                        "role": "user", 
                        "content": system_prompt
                    }
                ],
                max_tokens=150,
                temperature=0.7
            )
            
            response_text = response.choices[0].message.content.strip()
            
            # 清理回复（移除可能的引号或格式符号）
            response_text = response_text.strip('"\'`')
            
            return response_text
            
        except Exception as e:
            print(f"🤖 ChatAI: Doubao API调用异常: {e}")
            raise e
    
    def _generate_mock_response(self, npc_id: str, player_message: str) -> str:
        """生成模拟回复"""
        
        # 获取对话历史
        recent_history = self._get_recent_conversation_context(npc_id, 3)
        
        # 获取该NPC的模拟回复列表
        npc_responses = self.mock_responses.get(npc_id, [
            "你好！很高兴见到你。",
            "有什么我可以帮助你的吗？",
            "今天天气不错呢！",
            "小镇生活很平静。"
        ])
        
        # 扩展模拟回复，包含上下文相关的回复
        contextual_responses = {
            "trader_zhang": {
                "follow_up": [
                    "刚才你问的那个，我想想...",
                    "说到这个，我记得你之前提过...",
                    "对了，关于你刚才说的事情...",
                    "继续聊聊刚才的话题吧。"
                ],
                "topic_responses": {
                    "种子": ["那个种子确实不错，要不要再看看其他的？", "我这里还有更好的种子呢！"],
                    "价格": ["价格都是公道的，你放心！", "这个价格在市场上算便宜的了。"],
                    "生意": ["生意还行，多亏了你们这些顾客！", "做生意就是要诚信为本。"]
                }
            },
            "fisherman_li": {
                "follow_up": [
                    "你刚才说的对...",
                    "钓鱼这事儿，得慢慢来...",
                    "我想起你之前问过的...",
                    "继续说说钓鱼的事吧。"
                ],
                "topic_responses": {
                    "钓鱼": ["钓鱼确实需要耐心，你试过了吗？", "今天的鱼比昨天活跃多了。"],
                    "技巧": ["技巧这东西，得多练习。", "我可以教你一些窍门。"],
                    "耐心": ["耐心是钓鱼最重要的品质。", "急躁的人钓不到好鱼。"]
                }
            },
            "farmer_wang": {
                "follow_up": [
                    "你说得有道理...",
                    "种地的事儿，我最有发言权...",
                    "刚才聊到的那个...",
                    "农业这行当不容易啊。"
                ],
                "topic_responses": {
                    "种植": ["种植要看天时地利。", "这季节种什么都不错。"],
                    "天气": ["天气确实很重要，影响收成。", "看这天色，应该要下雨了。"],
                    "作物": ["作物长得怎么样？", "今年的收成应该不错。"]
                }
            }
        }
        
        # 检查是否有对话历史，如果有则考虑上下文
        message_lower = player_message.lower()
        
        # 如果有对话历史，优先使用上下文相关回复
        if recent_history and len(recent_history) > 0:
            last_messages = [entry["message"].lower() for entry in recent_history[-3:]]
            
            # 检查是否有相关话题的延续
            if npc_id in contextual_responses:
                npc_context = contextual_responses[npc_id]
                
                # 检查话题连续性
                for topic, responses in npc_context.get("topic_responses", {}).items():
                    if any(topic in msg for msg in last_messages) or topic in message_lower:
                        import random
                        return random.choice(responses)
                
                # 使用跟进回复
                if len(recent_history) >= 2:  # 如果已经有一些对话
                    import random
                    follow_up_chance = random.random()
                    if follow_up_chance < 0.3:  # 30%的概率使用跟进回复
                        return random.choice(npc_context["follow_up"])
        
        # 原有的关键词匹配逻辑
        if any(word in message_lower for word in ['你好', 'hello', '嗨', '早上好', '晚上好']):
            # 如果之前已经打过招呼，用不同的回复
            if recent_history and any("你好" in entry["message"] for entry in recent_history):
                return "我们不是刚聊过吗？哈哈。"
            greetings = [resp for resp in npc_responses if any(greet in resp for greet in ['你好', '见到你', '朋友'])]
            if greetings:
                return greetings[0]
        
        elif any(word in message_lower for word in ['钓鱼', '鱼', 'fishing']) and npc_id == "fisherman_li":
            fishing_responses = [resp for resp in npc_responses if any(word in resp for word in ['钓鱼', '鱼儿', '耐心'])]
            if fishing_responses:
                return fishing_responses[0]
        
        elif any(word in message_lower for word in ['种子', '买', '卖', '生意']) and npc_id == "trader_zhang":
            trade_responses = [resp for resp in npc_responses if any(word in resp for word in ['种子', '生意', '货', '价格'])]
            if trade_responses:
                return trade_responses[0]
        
        elif any(word in message_lower for word in ['农业', '种植', '作物', '土地']) and npc_id == "farmer_wang":
            farm_responses = [resp for resp in npc_responses if any(word in resp for word in ['作物', '土地', '农业', '庄稼'])]
            if farm_responses:
                return farm_responses[0]
        
        # 默认返回随机回复
        import random
        return random.choice(npc_responses)
    
    def get_nearby_npc(self, player_pos: tuple, npc_sprites) -> Optional[str]:
        """
        获取玩家附近的NPC
        
        Args:
            player_pos: 玩家位置 (x, y)
            npc_sprites: NPC精灵组
            
        Returns:
            附近NPC的ID，如果没有则返回None
        """
        interaction_distance = 150  # 增大聊天交互距离
        
        print(f"[ChatAI] 检查附近NPC，玩家位置: {player_pos}")
        
        for npc in npc_sprites:
            npc_pos = npc.rect.center
            distance = ((player_pos[0] - npc_pos[0]) ** 2 + 
                       (player_pos[1] - npc_pos[1]) ** 2) ** 0.5
            
            print(f"[ChatAI] NPC {npc.npc_id} 位置: {npc_pos}, 距离: {distance:.1f}")
            
            if distance <= interaction_distance:
                print(f"[ChatAI] 找到附近的NPC: {npc.npc_id}")
                return npc.npc_id
        
        print("[ChatAI] 没有找到附近的NPC")
        return None
    
    def add_context_from_game_state(self, player, level) -> Dict:
        """
        从游戏状态中提取上下文信息
        
        Args:
            player: 玩家对象
            level: 关卡对象
            
        Returns:
            上下文字典
        """
        context = {
            "player_money": getattr(player, 'money', 0),
            "player_level": getattr(player, 'level', 1),
            "current_time": datetime.now().strftime("%H:%M"),
            "weather": "晴朗" if not getattr(level, 'raining', False) else "下雨"
        }
        
        # 添加玩家库存信息
        if hasattr(player, 'item_inventory'):
            context["player_items"] = dict(player.item_inventory)
        
        # 添加钓鱼统计
        if hasattr(player, 'fishing_contest_stats'):
            context["fishing_stats"] = dict(player.fishing_contest_stats)
        
        return context
    
    def _add_to_conversation_history(self, npc_id: str, speaker: str, message: str):
        """添加消息到对话历史"""
        if npc_id not in self.conversation_history:
            self.conversation_history[npc_id] = []
        
        self.conversation_history[npc_id].append({
            "speaker": speaker,
            "message": message,
            "timestamp": datetime.now().isoformat()
        })
        
        # 限制历史长度
        if len(self.conversation_history[npc_id]) > self.max_history_length * 2:  # *2因为包含玩家和NPC的消息
            self.conversation_history[npc_id] = self.conversation_history[npc_id][-self.max_history_length * 2:]
        
        print(f"[ChatAI] 添加对话历史 {npc_id}: {speaker}: {message}")
    
    def _get_recent_conversation_context(self, npc_id: str, num_turns: int = 3) -> List[Dict]:
        """获取最近的对话上下文"""
        if npc_id not in self.conversation_history:
            return []
        
        # 获取最近的对话记录
        recent_messages = self.conversation_history[npc_id][-num_turns * 2:]  # *2因为包含玩家和NPC
        return recent_messages
    
    def _format_conversation_history(self, npc_id: str, num_turns: int = 5) -> str:
        """格式化对话历史为文本"""
        recent_history = self._get_recent_conversation_context(npc_id, num_turns)
        
        if not recent_history:
            return "这是你们的第一次对话。"
        
        formatted_history = "最近的对话历史:\n"
        for entry in recent_history:
            formatted_history += f"{entry['speaker']}: {entry['message']}\n"
        
        return formatted_history
    
    def clear_conversation_history(self, npc_id: str = None):
        """清除对话历史"""
        if npc_id:
            if npc_id in self.conversation_history:
                del self.conversation_history[npc_id]
                print(f"[ChatAI] 清除{npc_id}的对话历史")
        else:
            self.conversation_history.clear()
            print("[ChatAI] 清除所有对话历史")
    
    def get_conversation_summary(self, npc_id: str) -> Dict:
        """获取对话摘要"""
        if npc_id not in self.conversation_history:
            return {"total_messages": 0, "last_interaction": None}
        
        history = self.conversation_history[npc_id]
        return {
            "total_messages": len(history),
            "last_interaction": history[-1]["timestamp"] if history else None,
            "recent_topics": [msg["message"][:50] + "..." if len(msg["message"]) > 50 else msg["message"] 
                            for msg in history[-3:]]
        }

# 全局聊天AI实例
_chat_ai_instance = None

def get_chat_ai():
    """获取聊天AI单例"""
    global _chat_ai_instance
    if _chat_ai_instance is None:
        _chat_ai_instance = ChatAI()
    return _chat_ai_instance