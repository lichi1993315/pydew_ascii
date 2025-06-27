import pygame
from dataclasses import dataclass
from typing import Dict, List, Tuple, Optional
from abc import ABC, abstractmethod

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
    description: str        # 任务描述
    objectives: Dict        # 任务目标
    rewards: Dict           # 任务奖励
    is_completed: bool = False
    is_active: bool = False

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
            "我听说黄金鲤鱼只在特定的天气出现..."
        ]
        
        # 渔夫的任务
        self.quests = [
            Quest(
                quest_id="fishing_contest_entry",
                title="参与钓鱼大赛",
                description="镇上正在举办钓鱼大赛！钓10次鱼来参与比赛",
                objectives={"fishing_attempts": 10},
                rewards={"money": 100, "items": {"fish_bait": 10}}
            ),
            Quest(
                quest_id="catch_big_fish",
                title="钓大鱼挑战",
                description="在钓鱼大赛中钓到一条30cm以上的大鱼",
                objectives={"catch_big_fish": 30},
                rewards={"money": 200, "relationship": 1}
            ),
            Quest(
                quest_id="rare_fish_hunter",
                title="稀有鱼类猎手",
                description="钓到一条稀有品质以上的鱼来证明你的技术",
                objectives={"catch_rare_fish": 1},
                rewards={"money": 300, "items": {"fish_bait": 20}}
            )
        ]
    
    def get_greeting(self) -> str:
        greetings = [
            f"你好，年轻的钓鱼者！我是{self.name}。",
            "今天的鱼情看起来不错！",
            "想听听钓鱼的秘诀吗？"
        ]
        import random
        return random.choice(greetings)
    
    def interact(self, player) -> List[DialogueLine]:
        greeting = self.get_greeting()
        
        choices = [
            "听听钓鱼技巧",
            "查看任务",
            "再见"
        ]
        
        # 如果玩家有鱼，添加显示选项
        if player.get_total_fish_count() > 0:
            choices.insert(-1, "显摆我的鱼")
        
        dialogues = [
            DialogueLine(
                speaker=self.name,
                text=greeting,
                choices=choices
            )
        ]
        return dialogues
    
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
        else:
            return f"哇！{fish_count}条鱼！你真是个钓鱼高手！"

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
        
        # 钓鱼大赛组织者的任务
        self.quests = [
            Quest(
                quest_id="talk_to_fisherman",
                title="拜访钓鱼专家",
                description="去找渔夫李先生学习钓鱼技巧，为大赛做准备",
                objectives={"talk_to_fisherman": 1},
                rewards={"money": 50, "items": {"fish_bait": 5}}
            ),
            Quest(
                quest_id="sell_fish_to_trader",
                title="鱼类交易",
                description="将你钓到的鱼卖给商人，体验完整的钓鱼产业链",
                objectives={"sell_fish": 1},
                rewards={"money": 150}
            ),
            Quest(
                quest_id="contest_champion",
                title="钓鱼大赛冠军",
                description="在钓鱼大赛中钓到一条50cm以上的超大鱼，成为冠军！",
                objectives={"catch_champion_fish": 50},
                rewards={"money": 1000, "items": {"fish_bait": 50}}
            )
        ]
    
    def get_greeting(self) -> str:
        greetings = [
            f"欢迎参加钓鱼大赛！我是组织者{self.name}。",
            "今天的鱼情看起来很不错，适合比赛！",
            "想了解钓鱼大赛的规则吗？"
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
                    "了解大赛规则",
                    "查看任务",
                    "再见"
                ]
            )
        ]
        return dialogues
    
    def give_contest_tip(self) -> str:
        import random
        return random.choice(self.contest_tips)

class NPCManager:
    """NPC管理器"""
    
    def __init__(self):
        self.npcs = {}
        self.active_dialogue = None
        self.dialogue_state = {}
        
        # 创建默认NPC
        self.create_default_npcs()
    
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
            return npc.interact(player)
        return []
    
    def handle_dialogue_choice(self, npc_id: str, choice_index: int, player):
        """处理对话选择"""
        npc = self.get_npc(npc_id)
        if not npc:
            return None
        
        # 获取或初始化对话状态
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
            # 检查是否有可分配的任务
            available_quests = [q for q in npc.quests if not q.is_active and not q.is_completed]
            if available_quests and not any(q.quest_id == available_quests[0].quest_id for q in player.active_quests):
                # 分配第一个可用任务
                quest = available_quests[0]
                player.add_quest(quest)
                return [DialogueLine(npc.name, f"我有个任务给你：{quest.title} - {quest.description}")]
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
            # 检查是否有可分配的任务
            available_quests = [q for q in npc.quests if not q.is_active and not q.is_completed]
            if available_quests and not any(q.quest_id == available_quests[0].quest_id for q in player.active_quests):
                # 分配第一个可用任务
                quest = available_quests[0]
                player.add_quest(quest)
                return [DialogueLine(npc.name, f"我有个任务给你：{quest.title} - {quest.description}")]
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
        dialogue_lines = npc.interact(player)
        return dialogue_lines
    
    def end_dialogue(self):
        """结束对话"""
        self.active_dialogue = None
        self.dialogue_state = {} 