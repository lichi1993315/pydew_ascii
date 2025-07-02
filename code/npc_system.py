import pygame
from dataclasses import dataclass
from typing import Dict, List, Tuple, Optional
from abc import ABC, abstractmethod
import random
import time

@dataclass
class DialogueLine:
    """对话行数据结构"""
    speaker: str      # 说话者名称
    text: str         # 对话内容
    choices: List[str] = None  # 选择项（如果有）

@dataclass
class Quest:
    """任务数据结构"""
    quest_id: str           # 任务ID
    title: str              # 任务标题
    description: str        # 任务描述（简短说明）
    dialogue: List[str]     # 任务对话（剧情铺垫对话列表）
    objectives: Dict        # 任务目标
    rewards: Dict           # 任务奖励
    is_completed: bool = False
    is_active: bool = False

@dataclass
class DialogueState:
    """对话状态管理"""
    npc_id: str
    quest: Quest
    current_line: int = 0
    is_quest_offer: bool = False

class BaseNPC(ABC):
    """NPC基础类"""
    
    def __init__(self, name: str, npc_type: str, pos: Tuple[int, int], ascii_char: str = '&'):
        self.name = name
        self.npc_type = npc_type
        self.pos = pos
        self.ascii_char = ascii_char
        self.dialogues = []
        self.quests = []
        self.relationship_level = 0  # 好感度
        self.last_interaction_time = 0
        
    @abstractmethod
    def get_greeting(self) -> str:
        """获取问候语"""
        pass
    
    @abstractmethod
    def interact(self, player) -> List[DialogueLine]:
        """与玩家交互"""
        pass

class TraderNPC(BaseNPC):
    """商人NPC"""
    
    def __init__(self, name: str, pos: Tuple[int, int]):
        super().__init__(name, "trader", pos, '§')
        self.shop_items = {
            'corn': {'price': 4, 'stock': 50},
            'tomato': {'price': 5, 'stock': 30},
            'fish_bait': {'price': 2, 'stock': 100}  # 鱼饵
        }
        self.buy_prices = {
            'wood': 4,
            'apple': 2,
            'corn': 10,
            'tomato': 20
        }
    
    def get_greeting(self) -> str:
        greetings = [
            f"欢迎来到{self.name}的商店！",
            "今天想买点什么吗？",
            "我这里有最新鲜的种子！"
        ]
        import random
        return random.choice(greetings)
    
    def interact(self, player) -> List[DialogueLine]:
        greeting = self.get_greeting()
        
        dialogues = [
            DialogueLine(
                speaker=self.name,
                text=greeting,
                choices=[
                    "我想买东西",
                    "我想卖东西", 
                    "查看鱼类收购价格",
                    "再见"
                ]
            )
        ]
        return dialogues
    
    def buy_fish_from_player(self, player):
        """从玩家那里收购鱼类"""
        if not player.fish_inventory:
            return "你没有鱼可以卖给我。"
        total_value = player.sell_all_fish()
        player.update_trader_sold()  # 更新钓鱼大赛统计
        return f"我收购了你所有的鱼，支付了{total_value}金币！"

class FishermanNPC(BaseNPC):
    """渔夫NPC"""
    
    def __init__(self, name: str, pos: Tuple[int, int]):
        super().__init__(name, "fisherman", pos, '¤')
        self.fishing_tips = [
            "在不同的时间钓鱼会有不同的收获。",
            "稀有的鱼通常在深水区更容易钓到。",
            "耐心是钓鱼最重要的品质。",
            "我听说黄金鲤鱼只在特定的天气出现...",
            "清晨和黄昏是钓鱼的最佳时间。",
            "不同的鱼饵会吸引不同的鱼类。",
            "观察水面的波纹，能帮你找到鱼群。"
        ]
        # 不再在这里定义quests，改为通过NPCManager获取
    
    def get_greeting(self) -> str:
        greetings = [
            f"你好，年轻的钓鱼者！我是{self.name}。",
            "今天的鱼情看起来不错！",
            "想听听钓鱼的秘诀吗？",
            "水边总是充满惊喜的地方。",
            "钓鱼不仅仅是技术，更是一种艺术。"
        ]
        import random
        return random.choice(greetings)
    
    def interact(self, player) -> List[DialogueLine]:
        # 通过NPCManager获取可用任务，而不是使用硬编码任务
        # 这个方法会在NPCManager的start_dialogue中被调用
        # 此时NPCManager会检查是否有可用任务并初始化对话状态
        return [DialogueLine(self.name, self.get_greeting())]
    
    def give_fishing_tip(self) -> str:
        import random
        return random.choice(self.fishing_tips)
    
    def evaluate_fish_collection(self, player) -> str:
        """评价玩家的鱼类收藏"""
        fish_count = player.get_total_fish_count()
        
        if fish_count == 0:
            return "你还没有钓到任何鱼呢，去试试吧！"
        elif fish_count < 5:
            return f"不错的开始！你已经钓到了{fish_count}条鱼。"
        elif fish_count < 10:
            return f"相当不错！{fish_count}条鱼已经是个小成就了。"
        elif fish_count < 20:
            return f"哇！{fish_count}条鱼！你真是个钓鱼高手！"
        else:
            return f"不可思议！{fish_count}条鱼！你已经是传说级的钓鱼大师了！"

class FarmerNPC(BaseNPC):
    """钓鱼大赛组织者NPC"""
    
    def __init__(self, name: str, pos: Tuple[int, int]):
        super().__init__(name, "contest_organizer", pos, '♦')
        self.contest_tips = [
            "钓鱼大赛的规则很简单：看谁能钓到最长的鱼！",
            "记住，钓鱼技巧比运气更重要。",
            "不同的鱼类有不同的长度范围，选择合适的地点很关键。",
            "参与大赛不仅能获得奖励，还能提升你的钓鱼技能！"
        ]
        # 不再在这里定义quests，改为通过NPCManager获取
    
    def get_greeting(self) -> str:
        greetings = [
            f"欢迎参加钓鱼大赛！我是组织者{self.name}。",
            "今天的鱼情看起来很不错，适合比赛！",
            "想了解钓鱼大赛的规则吗？"
        ]
        import random
        return random.choice(greetings)
    
    def interact(self, player) -> List[DialogueLine]:
        # 返回问候语，任务通过NPCManager的对话状态系统来处理
        return [DialogueLine(self.name, self.get_greeting())]
    
    def give_contest_tip(self) -> str:
        import random
        return random.choice(self.contest_tips)

class NPCManager:
    """NPC管理器"""
    
    def __init__(self):
        self.npcs = {}
        self.active_dialogue = None
        self.dialogue_state = {}
        self.current_dialogue_state = None  # 当前任务对话状态
        
        # 任务库系统
        self.quest_library = QuestLibrary()
        self.npc_quest_pools = {}  # 每个NPC的任务池
        self.max_quests_per_npc = 3  # 每个NPC最多同时提供3个任务
        
        # 创建默认NPC
        self.create_default_npcs()
        
        # 为每个NPC生成初始任务池
        self.refresh_all_quest_pools()
    
    def create_default_npcs(self):
        """创建默认的NPC"""
        # 商人
        trader = TraderNPC("张商人", (800, 600))
        self.add_npc("trader_zhang", trader)
        
        # 渔夫
        fisherman = FishermanNPC("李渔夫", (400, 300))
        self.add_npc("fisherman_li", fisherman)
        
        # 钓鱼大赛组织者
        farmer = FarmerNPC("王大赛", (600, 500))
        self.add_npc("farmer_wang", farmer)
    
    def refresh_all_quest_pools(self, player=None):
        """刷新所有NPC的任务池"""
        for npc_id, npc in self.npcs.items():
            if isinstance(npc, (FishermanNPC, FarmerNPC)):
                self.refresh_npc_quest_pool(npc_id, player)
    
    def refresh_npc_quest_pool(self, npc_id: str, player=None):
        """刷新指定NPC的任务池"""
        npc = self.get_npc(npc_id)
        if not npc:
            return
        
        quest_preferences = self.get_npc_quest_preferences(npc)
        quests = []
        
        # 为NPC生成多样化的任务
        for _ in range(self.max_quests_per_npc):
            if quest_preferences:
                quest_type = random.choice(quest_preferences)
                difficulty = random.choice(["easy", "medium", "hard"])
                quest = self.quest_library.generate_random_quest(quest_type, difficulty, player)
                quests.append(quest)
        
        self.npc_quest_pools[npc_id] = quests
        print(f"[任务库] 为{npc.name}刷新了{len(quests)}个任务")
    
    def get_npc_quest_preferences(self, npc) -> List[str]:
        """获取NPC的任务偏好"""
        if isinstance(npc, FishermanNPC):
            return ["fishing_attempts", "catch_big_fish", "catch_rare_fish"]
        elif isinstance(npc, FarmerNPC):
            return ["talk_to_npc", "sell_fish", "catch_big_fish", "fishing_attempts"]
        else:
            return list(self.quest_library.quest_templates.keys())
    
    def get_available_quest_for_npc(self, npc_id: str, player) -> Optional[Quest]:
        """获取NPC的可用任务"""
        if npc_id not in self.npc_quest_pools:
            self.refresh_npc_quest_pool(npc_id, player)
        
        available_quests = self.npc_quest_pools.get(npc_id, [])
        active_quest_ids = [q.quest_id for q in player.active_quests] if hasattr(player, 'active_quests') else []
        
        # 筛选出玩家尚未接受的任务
        for quest in available_quests:
            if quest.quest_id not in active_quest_ids and not quest.is_active and not quest.is_completed:
                return quest
        
        # 如果没有可用任务，生成新的任务
        npc = self.get_npc(npc_id)
        if npc:
            quest_preferences = self.get_npc_quest_preferences(npc)
            if quest_preferences:
                quest_type = random.choice(quest_preferences)
                difficulty = random.choice(["easy", "medium", "hard"])
                new_quest = self.quest_library.generate_random_quest(quest_type, difficulty, player)
                
                # 添加到任务池
                if npc_id not in self.npc_quest_pools:
                    self.npc_quest_pools[npc_id] = []
                self.npc_quest_pools[npc_id].append(new_quest)
                
                return new_quest
        
        return None
    
    def add_npc(self, npc_id: str, npc: BaseNPC):
        """添加NPC"""
        self.npcs[npc_id] = npc
    
    def get_npc(self, npc_id: str) -> Optional[BaseNPC]:
        """获取NPC"""
        return self.npcs.get(npc_id)
    
    def interact_with_npc(self, npc_id: str, player) -> List[DialogueLine]:
        """与NPC交互"""
        npc = self.get_npc(npc_id)
        if npc:
            self.active_dialogue = npc_id
            
            # 检查是否有可用任务，初始化对话状态
            if isinstance(npc, (FishermanNPC, FarmerNPC)):
                available_quests = [q for q in npc.quests if not q.is_active and not q.is_completed]
                active_quest_ids = [q.quest_id for q in player.active_quests] if hasattr(player, 'active_quests') else []
                available_quests = [q for q in available_quests if q.quest_id not in active_quest_ids]
                
                if available_quests:
                    # 初始化任务对话状态
                    self.current_dialogue_state = DialogueState(
                        npc_id=npc_id,
                        quest=available_quests[0],
                        current_line=0,
                        is_quest_offer=False
                    )
            
            return npc.interact(player)
        return []
    
    def handle_dialogue_choice(self, npc_id: str, choice_index: int, player):
        """处理对话选择"""
        npc = self.get_npc(npc_id)
        if not npc:
            return None
        
        # 优先处理任务对话选择
        if self.current_dialogue_state and self.current_dialogue_state.is_quest_offer:
            state = self.current_dialogue_state
            if choice_index == 0:  # 接受任务
                player.add_quest(state.quest)
                response = [DialogueLine(npc.name, f"太好了！我相信你一定能完成这个任务的。")]
            else:  # 拒绝任务
                response = [DialogueLine(npc.name, "没关系，以后有机会再说吧。")]
            
            # 清除对话状态
            self.current_dialogue_state = None
            return response
        
        # 获取或初始化对话状态（原有逻辑）
        if npc_id not in self.dialogue_state:
            self.dialogue_state[npc_id] = {"stage": "main", "data": {}}
        
        state = self.dialogue_state[npc_id]
        
        # 根据NPC类型和对话阶段处理不同的逻辑
        if isinstance(npc, TraderNPC):
            return self._handle_trader_dialogue(npc, choice_index, player, state)
        elif isinstance(npc, FishermanNPC):
            return self._handle_fisherman_choice(npc, choice_index, player)
        elif isinstance(npc, FarmerNPC):
            return self._handle_farmer_choice(npc, choice_index, player)
        
        # 清除对话状态
        if npc_id in self.dialogue_state:
            del self.dialogue_state[npc_id]
        return None
    
    def _handle_trader_dialogue(self, npc: TraderNPC, choice_index: int, player, state):
        """处理商人对话（支持多层对话）"""
        stage = state.get("stage", "main")
        
        if stage == "main":
            # 主菜单选择
            if choice_index == 0:  # 买东西
                state["stage"] = "shop"
                return self._handle_trader_shop(npc, player)
            elif choice_index == 1:  # 卖东西
                state["stage"] = "sell"
                return self._handle_trader_sell(npc, player)
            elif choice_index == 2:  # 鱼类收购
                result = npc.buy_fish_from_player(player)
                return [DialogueLine(npc.name, result)]
            else:  # 再见
                return [DialogueLine(npc.name, "欢迎下次再来！")]
        
        elif stage == "shop":
            # 商店购买选择
            if choice_index == 0:  # 买玉米种子
                return self._execute_transaction(npc, "buy_corn", player)
            elif choice_index == 1:  # 买番茄种子
                return self._execute_transaction(npc, "buy_tomato", player)
            else:  # 不买了
                return [DialogueLine(npc.name, "下次再来看看吧！")]
        
        elif stage == "sell":
            # 出售选择
            if choice_index == 0:  # 全部卖掉
                return self._execute_transaction(npc, "sell_all", player)
            else:  # 不卖了
                return [DialogueLine(npc.name, "有需要的时候再来找我。")]
        
        return [DialogueLine(npc.name, "再见！")]
    
    def _handle_trader_shop(self, npc: TraderNPC, player):
        """处理商人商店"""
        if player.money >= 4:  # 最便宜的种子价格
            shop_text = f"我的商品：\n玉米种子 - 4金币\n番茄种子 - 5金币\n你有{player.money}金币"
            return [DialogueLine(
                npc.name, 
                shop_text,
                choices=["买玉米种子(4金币)", "买番茄种子(5金币)", "不买了"]
            )]
        else:
            return [DialogueLine(npc.name, f"你只有{player.money}金币，买不起任何种子。")]
    
    def _handle_trader_sell(self, npc: TraderNPC, player):
        """处理玩家卖东西给商人"""
        sellable_items = []
        total_value = 0
        
        for item, price in npc.buy_prices.items():
            if player.item_inventory.get(item, 0) > 0:
                count = player.item_inventory[item]
                value = count * price
                sellable_items.append(f"{item} x{count} - {value}金币")
                total_value += value
        
        if sellable_items:
            sell_text = f"我可以收购你的：" + "\n".join(sellable_items) + f"\n总价值：{total_value}金币"
            return [DialogueLine(
                npc.name,
                sell_text,
                choices=["全部卖掉", "不卖了"]
            )]
        else:
            return [DialogueLine(npc.name, "你没有我需要的商品。")]
    
    def _execute_transaction(self, npc: TraderNPC, transaction_type: str, player):
        """执行交易"""
        if transaction_type == "buy_corn":
            if player.money >= 4:
                player.money -= 4
                player.seed_inventory['corn'] = player.seed_inventory.get('corn', 0) + 1
                return [DialogueLine(npc.name, "你买了玉米种子！还需要其他的吗？", 
                                    choices=["买玉米种子(4金币)", "买番茄种子(5金币)", "不买了"])]
            else:
                return [DialogueLine(npc.name, "你的钱不够。")]
        elif transaction_type == "buy_tomato":
            if player.money >= 5:
                player.money -= 5
                player.seed_inventory['tomato'] = player.seed_inventory.get('tomato', 0) + 1
                return [DialogueLine(npc.name, "你买了番茄种子！还需要其他的吗？",
                                    choices=["买玉米种子(4金币)", "买番茄种子(5金币)", "不买了"])]
            else:
                return [DialogueLine(npc.name, "你的钱不够。")]
        elif transaction_type == "sell_all":
            total_value = 0
            sold_items = []
            
            for item, price in npc.buy_prices.items():
                if player.item_inventory.get(item, 0) > 0:
                    count = player.item_inventory[item]
                    value = count * price
                    total_value += value
                    sold_items.append(f"{item} x{count}")
                    player.item_inventory[item] = 0
            
            if total_value > 0:
                player.money += total_value
                items_text = ", ".join(sold_items)
                return [DialogueLine(npc.name, f"交易完成！我收购了你的{items_text}，支付了{total_value}金币。")]
            else:
                return [DialogueLine(npc.name, "没有可以出售的商品。")]
        
        return [DialogueLine(npc.name, "交易取消。")]
    
    def _handle_fisherman_choice(self, npc: FishermanNPC, choice_index: int, player):
        """处理渔夫选择"""
        if choice_index == 0:  # 钓鱼技巧
            tip = npc.give_fishing_tip()
            return [DialogueLine(npc.name, tip)]
        elif choice_index == 1:  # 查看任务
            # 检查是否有可分配的任务（使用任务库系统）
            npc_id = "fisherman_li"  # 渔夫的ID
            available_quest = self.get_available_quest_for_npc(npc_id, player)
            
            if available_quest and not any(q.quest_id == available_quest.quest_id for q in player.active_quests):
                # 分配任务
                player.add_quest(available_quest)
                return [DialogueLine(npc.name, f"我有个任务给你：{available_quest.title} - {available_quest.description}")]
            else:
                return [DialogueLine(npc.name, "暂时没有新任务给你，继续努力钓鱼吧！")]
        elif choice_index == 2 and player.get_total_fish_count() > 0:  # 显摆鱼类
            evaluation = npc.evaluate_fish_collection(player)
            return [DialogueLine(npc.name, evaluation)]
        else:  # 再见
            return [DialogueLine(npc.name, "祝你钓鱼愉快！")]
    
    def _handle_farmer_choice(self, npc: FarmerNPC, choice_index: int, player):
        """处理农夫选择"""
        if choice_index == 0:  # 种植技巧
            tip = npc.give_contest_tip()
            return [DialogueLine(npc.name, tip)]
        elif choice_index == 1:  # 查看任务
            # 检查是否有可分配的任务（使用任务库系统）
            npc_id = "farmer_wang"  # 大赛组织者的ID
            available_quest = self.get_available_quest_for_npc(npc_id, player)
            
            if available_quest and not any(q.quest_id == available_quest.quest_id for q in player.active_quests):
                # 分配任务
                player.add_quest(available_quest)
                return [DialogueLine(npc.name, f"我有个任务给你：{available_quest.title} - {available_quest.description}")]
            else:
                return [DialogueLine(npc.name, "暂时没有新任务给你，继续努力钓鱼吧！")]
        else:  # 再见
            return [DialogueLine(npc.name, "祝你钓鱼愉快！")]

    def start_dialogue(self, npc, player):
        """开始与NPC的对话"""
        if self.active_dialogue:
            return None  # 已经在对话中
        
        print(f"[NPC对话] 开始与{npc.name}对话")
        
        # 特殊处理：与渔夫对话时更新统计
        if isinstance(npc, FishermanNPC):
            player.update_fisherman_talked()
        
        self.active_dialogue = npc
        self.dialogue_state = {}
        
        # 找到NPC ID
        npc_id = None
        for npc_id_key, npc_instance in self.npcs.items():
            if npc_instance == npc:
                npc_id = npc_id_key
                break
        
        # 检查是否有可用任务（使用任务库系统）
        if isinstance(npc, (FishermanNPC, FarmerNPC)) and npc_id:
            available_quest = self.get_available_quest_for_npc(npc_id, player)
            
            if available_quest:
                # 初始化任务对话状态
                self.current_dialogue_state = DialogueState(
                    npc_id=npc_id,
                    quest=available_quest,
                    current_line=0,
                    is_quest_offer=False
                )
                # 返回任务对话的第一句
                return [DialogueLine(npc.name, available_quest.dialogue[0])]
        
        # 如果没有任务，返回普通对话
        dialogue_lines = npc.interact(player)
        return dialogue_lines
    
    def end_dialogue(self):
        """结束对话"""
        self.active_dialogue = None
        self.dialogue_state = {}
        self.current_dialogue_state = None
    
    def continue_dialogue(self, player) -> List[DialogueLine]:
        """继续任务对话（按Enter时调用）"""
        if not self.current_dialogue_state:
            return []
        
        state = self.current_dialogue_state
        npc = self.get_npc(state.npc_id)
        if not npc:
            return []
        
        # 继续到下一句对话
        state.current_line += 1
        
        # 检查是否还有更多对话
        if state.current_line < len(state.quest.dialogue):
            # 返回下一句对话
            return [DialogueLine(npc.name, state.quest.dialogue[state.current_line])]
        else:
            # 对话结束，显示任务选择
            state.is_quest_offer = True
            reward_text = ""
            if 'money' in state.quest.rewards:
                reward_text += f"{state.quest.rewards['money']}金币"
            if 'items' in state.quest.rewards:
                for item, count in state.quest.rewards['items'].items():
                    if reward_text:
                        reward_text += "、"
                    reward_text += f"{item} x{count}"
            
            quest_offer_text = f"任务：{state.quest.title}\n奖励：{reward_text}\n你愿意接受这个任务吗？"
            return [DialogueLine(
                npc.name, 
                quest_offer_text,
                choices=["接受任务", "拒绝任务"]
            )] 
    
    def refresh_quest_pools_on_schedule(self):
        """定期刷新任务池（可以在游戏中定时调用）"""
        # 可以根据时间或其他条件来刷新
        current_time = int(time.time())
        
        # 每隔一段时间刷新一次
        if not hasattr(self, 'last_refresh_time'):
            self.last_refresh_time = current_time
        
        if current_time - self.last_refresh_time > 300:  # 5分钟刷新一次
            self.quest_library.refresh_random_npc_quests(self)
            self.last_refresh_time = current_time
    
    def get_npc_quest_count(self, npc_id: str) -> int:
        """获取指定NPC的任务数量"""
        return len(self.npc_quest_pools.get(npc_id, []))
    
    def get_all_quest_statistics(self) -> dict:
        """获取所有任务统计信息"""
        stats = self.quest_library.get_quest_statistics()
        stats["npc_quest_pools"] = {
            npc_id: len(quests) for npc_id, quests in self.npc_quest_pools.items()
        }
        return stats
    
    def force_refresh_all_quest_pools(self):
        """强制刷新所有NPC的任务池"""
        self.refresh_all_quest_pools()
        print("[任务库] 已强制刷新所有NPC的任务池")

class QuestLibrary:
    """任务库系统 - 生成丰富多样的任务"""
    
    def __init__(self):
        # 任务模板定义
        self.quest_templates = {
            # 钓鱼次数类任务
            "fishing_attempts": {
                "titles": [
                    "钓鱼练习", "熟能生巧", "勤能补拙", "钓鱼训练", 
                    "水边修行", "垂钓时光", "钓鱼体验", "渔具试用"
                ],
                "descriptions": [
                    "多练习钓鱼技巧，熟能生巧",
                    "通过反复练习提升钓鱼水平", 
                    "在水边花更多时间磨练技艺",
                    "体验钓鱼的乐趣和挑战"
                ],
                "params": {
                    "num": [5, 8, 10, 15, 20, 25, 30]
                },
                "rewards": {
                    "money": [30, 50, 80, 100, 150, 200],
                    "items": [
                        {"fish_bait": 5}, {"fish_bait": 10}, {"fish_bait": 15},
                        {"fish_bait": 20}, {"fish_bait": 25}
                    ]
                }
            },
            
            # 钓大鱼类任务
            "catch_big_fish": {
                "titles": [
                    "大鱼挑战", "长度竞赛", "巨鱼传说", "尺寸之王",
                    "钓鱼高手", "长度证明", "巨鱼猎手", "大鱼专家"
                ],
                "descriptions": [
                    "钓到指定长度以上的大鱼",
                    "证明你的钓鱼技术，挑战大鱼",
                    "追求更大更长的鱼类",
                    "成为钓大鱼的专家"
                ],
                "params": {
                    "minimum_length": [25, 30, 35, 40, 45, 50, 60, 70]
                },
                "rewards": {
                    "money": [100, 150, 200, 300, 500, 800],
                    "items": [
                        {"fish_bait": 10}, {"fish_bait": 20}, {"fish_bait": 30}
                    ]
                }
            },
            
            # 钓稀有鱼类任务
            "catch_rare_fish": {
                "titles": [
                    "稀有猎手", "珍品收集", "传说追寻", "稀世珍鱼",
                    "珍稀探索", "品质追求", "罕见收藏", "稀有专家"
                ],
                "descriptions": [
                    "钓到指定稀有度的珍贵鱼类",
                    "收集稀有品质的鱼类标本",
                    "追寻传说中的稀有鱼类",
                    "成为稀有鱼类收集专家"
                ],
                "params": {
                    "minimum_rarity": ["uncommon", "rare", "epic", "legendary"],
                },
                "rewards": {
                    "money": [150, 250, 400, 600, 1000],
                    "items": [
                        {"fish_bait": 15}, {"fish_bait": 25}, {"fish_bait": 40}
                    ]
                }
            },
            
                         # NPC对话类任务
             "talk_to_npc": {
                 "titles": [
                     "社交达人", "信息收集", "人脉建设", "友好交流",
                     "镇民互动", "关系维护", "社区融入", "交际能手"
                 ],
                 "descriptions": [
                     "与镇上的居民建立良好关系",
                     "通过对话了解更多信息",
                     "加强与社区成员的联系",
                     "扩展你的人际网络"
                 ],
                "params": {
                    "target": ["fisherman", "trader", "farmer"]
                },
                "rewards": {
                    "money": [25, 50, 75, 100],
                    "items": [
                        {"fish_bait": 5}, {"fish_bait": 8}, {"fish_bait": 12}
                    ]
                }
            },
            
            # 售鱼类任务
            "sell_fish": {
                "titles": [
                    "商业头脑", "经济循环", "市场交易", "渔业贸易",
                    "商业伙伴", "经济活动", "贸易往来", "市场参与"
                ],
                "descriptions": [
                    "将钓到的鱼类出售获得收益",
                    "参与镇上的经济循环",
                    "售卖你的鱼，体验渔业贸易的完整流程",
                    "成为活跃的市场参与者"
                ],
                "params": {
                    "fish_type": ["all", "common", "uncommon", "rare"],
                },
                "rewards": {
                    "money": [50, 100, 150, 200, 300],
                    "items": [
                        {"fish_bait": 8}, {"fish_bait": 15}, {"fish_bait": 25}
                    ]
                }
            },
            
        }
        
        # 任务难度和奖励的对应关系
        self.difficulty_multipliers = {
            "easy": {"money": 1.0, "items": 1.0},
            "medium": {"money": 1.5, "items": 1.3}, 
            "hard": {"money": 2.0, "items": 1.8},
            "expert": {"money": 3.0, "items": 2.5}
        }
    
    def generate_random_quest(self, quest_type: str = None, difficulty: str = "medium", player=None) -> Quest:
        """生成随机任务"""
        if quest_type is None:
            quest_type = random.choice(list(self.quest_templates.keys()))
        
        if quest_type not in self.quest_templates:
            quest_type = "fishing_attempts"  # 默认类型
        
        template = self.quest_templates[quest_type]
        
        # 随机选择标题和描述
        title = random.choice(template["titles"])
        description = random.choice(template["descriptions"])
        
        # 生成随机参数
        objectives = {}
        params = {}
        
        if quest_type == "fishing_attempts":
            params["num"] = random.choice(template["params"]["num"])
            objectives["fishing_attempts"] = params
            
        elif quest_type == "catch_big_fish":
            # 根据玩家当前最大鱼长度调整任务难度
            available_lengths = template["params"]["minimum_length"]
            
            if player and hasattr(player, 'fishing_contest_stats'):
                current_max_length = player.fishing_contest_stats.get("max_fish_length", 0)
                # 筛选出比玩家当前最大长度更长的要求
                challenging_lengths = [length for length in available_lengths if length > current_max_length]
                
                if challenging_lengths:
                    # 如果有更高的挑战，随机选择一个
                    params["minimum_length"] = random.choice(challenging_lengths)
                    print(f"[任务生成] 根据玩家当前最大鱼长度 {current_max_length}cm，生成挑战长度 {params['minimum_length']}cm")
                else:
                    # 如果玩家已经超过了所有预设长度，生成比当前最大长度更高的挑战
                    params["minimum_length"] = current_max_length + random.randint(5, 15)
                    print(f"[任务生成] 玩家已达到高水平，生成超越挑战长度 {params['minimum_length']}cm")
            else:
                # 没有玩家信息时使用默认逻辑
                params["minimum_length"] = random.choice(available_lengths)
            
            objectives["catch_fish"] = params
            
        elif quest_type == "catch_rare_fish":
            # 根据玩家当前最高稀有度调整任务难度
            available_rarities = template["params"]["minimum_rarity"]
            rarity_levels = {"common": 1, "uncommon": 2, "rare": 3, "epic": 4, "legendary": 5}
            
            if player and hasattr(player, 'fish_inventory'):
                # 计算玩家当前钓到的最高稀有度
                current_max_rarity_level = 0
                for fish in player.fish_inventory:
                    fish_rarity = fish.get("rarity", "common")
                    fish_level = rarity_levels.get(fish_rarity, 1)
                    current_max_rarity_level = max(current_max_rarity_level, fish_level)
                
                # 筛选出比当前最高稀有度更高的要求
                challenging_rarities = []
                for rarity in available_rarities:
                    if rarity_levels.get(rarity, 1) > current_max_rarity_level:
                        challenging_rarities.append(rarity)
                
                if challenging_rarities:
                    # 如果有更高的挑战，随机选择一个
                    params["minimum_rarity"] = random.choice(challenging_rarities)
                    current_rarity_name = ""
                    for rarity, level in rarity_levels.items():
                        if level == current_max_rarity_level:
                            current_rarity_name = rarity
                            break
                    print(f"[任务生成] 根据玩家当前最高稀有度 {current_rarity_name}，生成挑战稀有度 {params['minimum_rarity']}")
                else:
                    # 如果玩家已经钓到最高稀有度，使用最高稀有度作为挑战
                    params["minimum_rarity"] = "legendary"
                    print(f"[任务生成] 玩家已达到最高稀有度，生成传说级挑战")
            else:
                # 没有玩家信息时使用默认逻辑
                params["minimum_rarity"] = random.choice(available_rarities)
                
            objectives["catch_fish"] = params
            
        elif quest_type == "talk_to_npc":
            params["target"] = random.choice(template["params"]["target"])
            objectives["talk_to_npc"] = params
            
        elif quest_type == "sell_fish":
            params["fish_type"] = random.choice(template["params"]["fish_type"])
            objectives["sell_fish"] = params
            
        
        # 生成奖励
        rewards = self._generate_rewards(template, difficulty, params)
        
        # 生成剧情对话
        dialogue = self._generate_dialogue(quest_type, title, params)
        
        # 生成唯一ID
        quest_id = f"{quest_type}_{random.randint(1000, 9999)}"
        
        return Quest(
            quest_id=quest_id,
            title=title,
            description=description,
            dialogue=dialogue,
            objectives=objectives,
            rewards=rewards
        )
    
    def _generate_rewards(self, template: dict, difficulty: str, params: dict) -> dict:
        """根据难度和参数生成奖励"""
        rewards = {}
        multiplier = self.difficulty_multipliers.get(difficulty, self.difficulty_multipliers["medium"])
        
        # 基础金钱奖励
        base_money = random.choice(template["rewards"]["money"])
        rewards["money"] = int(base_money * multiplier["money"])
        
        # 基础物品奖励
        base_items = random.choice(template["rewards"]["items"])
        rewards["items"] = {}
        for item, count in base_items.items():
            rewards["items"][item] = int(count * multiplier["items"])
        
        # 根据任务参数调整奖励
        param_bonus = self._calculate_param_bonus(params)
        rewards["money"] = int(rewards["money"] * param_bonus)
        
        return rewards
    
    def _calculate_param_bonus(self, params: dict) -> float:
        """根据任务参数计算奖励加成"""
        bonus = 1.0
        
        # 数量加成
        if "num" in params:
            bonus *= (1 + params["num"] * 0.1)
        
        # 长度要求加成
        if "minimum_length" in params:
            bonus *= (1 + params["minimum_length"] * 0.02)
        
        # 稀有度要求加成
        if "minimum_rarity" in params:
            rarity_bonus = {
                "common": 1.0, "uncommon": 1.2, "rare": 1.5, "epic": 2.0, "legendary": 3.0
            }
            bonus *= rarity_bonus.get(params["minimum_rarity"], 1.0)
        
        
        return bonus
    
    def _generate_dialogue(self, quest_type: str, title: str, params: dict) -> List[str]:
        """生成任务对话"""
        dialogue_templates = {
            "fishing_attempts": [
                "我注意到你对钓鱼很有兴趣。",
                "想要提升钓鱼技术需要大量的练习。",
                "在水边多花些时间，你会有意想不到的收获。",
                f"试着钓{params.get('num', 10)}次鱼吧，这会让你的技术更加熟练！"
            ],
            "catch_big_fish": [
                "我听说最近水里有些大家伙游来游去。",
                "真正的钓鱼高手总是能钓到令人印象深刻的大鱼。",
                "长度不仅代表鱼的价值，也象征着钓鱼者的技艺。",
                f"你能钓到一条{params.get('minimum_length', 30)}厘米以上的大鱼吗？"
            ],
            "catch_rare_fish": [
                "这片水域隐藏着许多秘密。",
                "稀有的鱼类通常只有最有经验的钓鱼者才能遇到。",
                "它们聪明、美丽，而且极其难得。",
                f"如果你能钓到{params.get('minimum_rarity', 'rare')}品质的鱼，那就证明了你的实力！"
            ],
            "talk_to_npc": [
                "这个小镇的每个人都有自己的故事。",
                "通过交流，你能了解到很多有用的信息。",
                "建立良好的人际关系对每个人都很重要。",
                f"去和{params.get('target', '其他人')}聊聊吧，你会有收获的！"
            ],
            "sell_fish": [
                "钓鱼不仅仅是爱好，也可以是一门生意。",
                "通过出售鱼类，你能体验到完整的渔业循环。",
                "这个镇上的商人总是需要新鲜的鱼类。",
                f"试着出售一些{params.get('fish_type', '鱼类')}吧，这对大家都有好处！"
            ]
            
        }
        
        return dialogue_templates.get(quest_type, [
            "这是一个有趣的挑战。",
            "我相信你能够完成这个任务。",
            "让我们看看你的能力如何。",
            "祝你好运，年轻的冒险者！"
        ])
    
    def generate_quest_batch(self, count: int = 5, difficulty_mix: bool = True, player=None) -> List[Quest]:
        """生成一批任务"""
        quests = []
        quest_types = list(self.quest_templates.keys())
        difficulties = ["easy", "medium", "hard", "expert"]
        
        for _ in range(count):
            quest_type = random.choice(quest_types)
            difficulty = random.choice(difficulties) if difficulty_mix else "medium"
            quest = self.generate_random_quest(quest_type, difficulty, player)
            quests.append(quest)
        
        return quests

    def refresh_random_npc_quests(self, npc_manager=None, player=None):
        """随机刷新一个NPC的任务池（可以在游戏中定期调用）"""
        if npc_manager:
            npc_ids = list(npc_manager.npcs.keys())
            if npc_ids:
                random_npc_id = random.choice(npc_ids)
                npc_manager.refresh_npc_quest_pool(random_npc_id, player)
                print(f"[任务库] 随机刷新了{random_npc_id}的任务池")
    
    def get_quest_statistics(self) -> dict:
        """获取任务库统计信息"""
        return {
            "total_quest_types": len(self.quest_templates),
            "quest_types": list(self.quest_templates.keys()),
            "difficulty_levels": list(self.difficulty_multipliers.keys())
        } 