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
from ..data.cat_data import get_cat_data_manager

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
    print("WARNING: anthropic library not installed, using mock reply mode")

try:
    import openai
    OPENAI_AVAILABLE = True
except ImportError:
    OPENAI_AVAILABLE = False
    print("WARNING: openai library not installed, Doubao model unavailable")

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
        
        # 加载统一的猫咪数据管理器
        self.cat_data_manager = get_cat_data_manager()
        
        # NPC角色设定 - 基础NPC + 动态加载的猫咪
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
            }
        }
        
        # 动态加载猫咪角色设定
        self._load_cat_personalities()
        
        # 模拟回复模板 - 基础NPC + 动态加载的猫咪
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
            ]
        }
        
        # 动态加载猫咪回复
        self._load_cat_mock_responses()
        
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
                print("CHATAI: Claude API client initialized successfully")
                
            except Exception as e:
                print(f"CHATAI: Claude API client initialization failed: {e}")
        
        # 初始化Doubao客户端
        if OPENAI_AVAILABLE and self.doubao_api_key:
            try:
                self.doubao_client = openai.OpenAI(
                    api_key=self.doubao_api_key,
                    base_url="https://ark.cn-beijing.volces.com/api/v3",
                    timeout=30.0
                )
                print("CHATAI: Doubao API client initialized successfully")
                
            except Exception as e:
                print(f"CHATAI: Doubao API client initialization failed: {e}")
        
        if not self.claude_client and not self.doubao_client:
            print("CHATAI: No available API clients, using mock reply mode")
    
    def _set_active_model(self, model_type: str):
        """设置当前活跃的模型"""
        self.model_type = model_type.lower()
        
        if self.model_type == "claude" and self.claude_client:
            self.current_client = self.claude_client
            self.use_api = True
            print(f"CHATAI: Switched to Claude model")
        elif self.model_type == "doubao" and self.doubao_client:
            self.current_client = self.doubao_client
            self.use_api = True
            print(f"CHATAI: Switched to Doubao model")
        else:
            self.current_client = None
            self.use_api = False
            print(f"CHATAI: Model {model_type} unavailable, using mock reply mode")
    
    def switch_model(self, model_type: str):
        """动态切换AI模型"""
        print(f"CHATAI: Attempting to switch to {model_type} model")
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
                print(f"CHATAI: {self.model_type} API call failed, fallback to mock mode: {e}")
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
            print(f"CHATAI: Claude API call exception: {e}")
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
            print(f"CHATAI: Doubao API call exception: {e}")
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
    
    def _load_cat_personalities(self):
        """动态加载猫咪角色设定"""
        all_cats = self.cat_data_manager.get_all_cats()
        
        for cat_info in all_cats:
            # 根据性格生成说话风格
            speaking_style = self._generate_speaking_style(cat_info.personality)
            
            # 生成角色ID（简化版，用于匹配）
            cat_id = self._get_cat_id_from_name(cat_info.name)
            
            self.npc_personalities[cat_id] = {
                "name": cat_info.name,
                "personality": cat_info.personality,
                "context": f"在小镇自由漫步的{cat_info.name}，{cat_info.personality}",
                "speaking_style": speaking_style
            }
        
        print(f"[ChatAI] 加载了 {len(all_cats)} 只猫咪的角色设定")
    
    def _load_cat_mock_responses(self):
        """动态加载猫咪模拟回复"""
        all_cats = self.cat_data_manager.get_all_cats()
        
        for cat_info in all_cats:
            cat_id = self._get_cat_id_from_name(cat_info.name)
            responses = self._generate_cat_responses(cat_info)
            self.mock_responses[cat_id] = responses
        
        print(f"[ChatAI] 加载了 {len(all_cats)} 只猫咪的模拟回复")
    
    def _generate_speaking_style(self, personality: str) -> str:
        """根据性格生成说话风格"""
        if "优雅" in personality or "高贵" in personality:
            return "优雅的猫语，语气高贵"
        elif "活泼" in personality or "活力" in personality:
            return "活泼的猫语，充满活力"
        elif "天真" in personality or "可爱" in personality:
            return "天真可爱的猫语，声音软糯"
        elif "神秘" in personality or "黑暗" in personality:
            return "神秘的猫语，深沉低调"
        elif "聪明" in personality or "狡猾" in personality:
            return "聪明的猫语，话中有话"
        elif "懒" in personality or "睡" in personality:
            return "慵懒的猫语，经常打哈欠"
        elif "温顺" in personality or "善良" in personality:
            return "温顺的猫语，语气轻柔"
        elif "勇敢" in personality or "威武" in personality:
            return "威武的猫语，气势十足"
        else:
            return "可爱的猫语，经常用'喵'结尾"
    
    def _generate_cat_responses(self, cat_info) -> List[str]:
        """根据猫咪信息生成回复"""
        name = cat_info.name
        personality = cat_info.personality
        
        # 基础回复模板
        base_responses = [
            f"喵！你好呀，我是{name}！",
            f"喵～想了解{name}吗？",
            f"今天天气真好呢，喵～",
            f"{name}很高兴见到你，喵！"
        ]
        
        # 根据性格添加特定回复
        personality_responses = []
        
        if "优雅" in personality or "高贵" in personality:
            personality_responses.extend([
                f"请保持优雅的姿态，喵～",
                f"我是高贵的{name}，喵。",
                f"举止要得体哦，喵～"
            ])
        elif "活泼" in personality or "活力" in personality:
            personality_responses.extend([
                f"一起来玩吧，喵！",
                f"跑跑跳跳真开心，喵～",
                f"今天也很有活力呢，喵！"
            ])
        elif "天真" in personality or "可爱" in personality:
            personality_responses.extend([
                f"用大眼睛看着你，喵～",
                f"好可爱的人类呀，喵！",
                f"天真无邪地看着你，喵～"
            ])
        elif "神秘" in personality or "黑暗" in personality:
            personality_responses.extend([
                f"在黑暗中注视着你...喵",
                f"我有神秘的能力，喵...",
                f"不可思议的事情即将发生，喵..."
            ])
        elif "聪明" in personality or "机智" in personality:
            personality_responses.extend([
                f"我很聪明的，什么都知道，喵～",
                f"智慧的光芒在眼中闪烁，喵！",
                f"要不要看看我的聪明才智，喵？"
            ])
        elif "懒" in personality or "睡" in personality:
            personality_responses.extend([
                f"喵...好困啊...哈欠～",
                f"让我再睡一会儿嘛，喵...",
                f"懒懒的最舒服了，喵～"
            ])
        elif "温顺" in personality or "善良" in personality:
            personality_responses.extend([
                f"轻轻地靠近你，喵～",
                f"温顺地看着你，喵...",
                f"善良的心在温暖着大家，喵～"
            ])
        elif "勇敢" in personality or "威武" in personality:
            personality_responses.extend([
                f"勇敢地保护大家，喵！",
                f"威武霸气的{name}，喵！",
                f"勇气是我的力量，喵～"
            ])
        else:
            # 默认可爱回复
            personality_responses.extend([
                f"做个可爱的表情，喵～",
                f"平凡也是一种美好，喵！",
                f"每天都很开心呢，喵～"
            ])
        
        # 合并所有回复
        all_responses = base_responses + personality_responses
        return all_responses
    
    def _get_cat_id_from_name(self, cat_name: str) -> str:
        """根据猫咪名字生成ID"""
        # 使用猫咪的名字作为ID，确保与其他系统一致
        return f"cat_{cat_name}"
    
    def register_dynamic_cat(self, cat_name: str, cat_personality: str):
        """动态注册新的猫咪（当从钓鱼获得新猫咪时调用）"""
        cat_id = self._get_cat_id_from_name(cat_name)
        speaking_style = self._generate_speaking_style(cat_personality)
        
        # 添加到角色设定
        self.npc_personalities[cat_id] = {
            "name": cat_name,
            "personality": cat_personality,
            "context": f"在小镇自由漫步的{cat_name}，{cat_personality}",
            "speaking_style": speaking_style
        }
        
        # 生成模拟回复
        from ..data.cat_data import CatInfo
        cat_info = CatInfo(
            id=cat_id,
            name=cat_name,
            personality=cat_personality,
            rarity='common',
            color=(255, 255, 255),
            ascii_char='🐱',
            catch_rate=0.03,
            category='classic'
        )
        responses = self._generate_cat_responses(cat_info)
        self.mock_responses[cat_id] = responses
        
        print(f"[ChatAI] 动态注册新猫咪: {cat_name} ({cat_id})")

# 全局聊天AI实例
_chat_ai_instance = None

def get_chat_ai():
    """获取聊天AI单例"""
    global _chat_ai_instance
    if _chat_ai_instance is None:
        _chat_ai_instance = ChatAI()
    return _chat_ai_instance