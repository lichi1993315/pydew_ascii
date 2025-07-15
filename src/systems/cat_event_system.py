#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
猫猫事件系统
负责管理猫猫之间的随机互动事件
"""

import json
import random
import time
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass, field
from src.core.support import get_resource_path, safe_print

@dataclass
class CatRelationship:
    """猫猫关系数据"""
    friendship: float = 0.0      # 友好度 (-100 到 100)
    romance: float = 0.0         # 恋爱度 (-100 到 100) 
    rivalry: float = 0.0         # 竞争度 (0 到 100)
    cooperation: float = 0.0     # 合作度 (0 到 100)
    last_interaction: float = 0.0  # 上次互动时间戳
    interaction_count: int = 0   # 互动次数
    relationship_history: List[str] = field(default_factory=list)  # 关系历史事件

@dataclass
class CatEventResult:
    """事件结果数据"""
    success: bool = True
    message: str = ""
    participants: List[str] = field(default_factory=list)
    relationship_changes: Dict[str, Dict[str, float]] = field(default_factory=dict)
    follow_up_events: List[str] = field(default_factory=list)
    
class CatEventSystem:
    """猫猫事件系统主控制器"""
    
    def __init__(self):
        self.events_config = {}
        self.cat_relationships = {}  # {(cat1_id, cat2_id): CatRelationship}
        self.event_cooldowns = {}    # {event_id: last_trigger_time}
        self.global_cooldown = 5.0   # 全局事件冷却时间（秒）
        self.last_event_time = 0.0
        
        # 事件触发参数
        self.base_event_chance = 0.02  # 基础事件概率 (每次检查2%概率)
        self.proximity_threshold = 128  # 猫猫接近距离阈值（像素）
        
        self.load_events_config()
        
    def load_events_config(self):
        """加载事件配置文件"""
        try:
            config_path = get_resource_path('config/cat_events.json')
            with open(config_path, 'r', encoding='utf-8') as f:
                self.events_config = json.load(f)
            safe_print(f"SUCCESS: 加载猫猫事件配置: {len(self.events_config.get('events', []))} 个事件")
        except Exception as e:
            safe_print(f"WARNING: 无法加载猫猫事件配置: {e}")
            self.events_config = {"events": []}
    
    def get_relationship(self, cat1_id: str, cat2_id: str) -> CatRelationship:
        """获取两只猫之间的关系，如果不存在则创建新关系"""
        # 确保关系键的一致性（总是较小的ID在前）
        key = tuple(sorted([cat1_id, cat2_id]))
        
        if key not in self.cat_relationships:
            self.cat_relationships[key] = CatRelationship()
        
        return self.cat_relationships[key]
    
    def update_relationship(self, cat1_id: str, cat2_id: str, 
                          friendship_change: float = 0, romance_change: float = 0,
                          rivalry_change: float = 0, cooperation_change: float = 0):
        """更新猫猫关系值"""
        rel = self.get_relationship(cat1_id, cat2_id)
        
        # 更新关系值，确保在合理范围内
        rel.friendship = max(-100, min(100, rel.friendship + friendship_change))
        rel.romance = max(-100, min(100, rel.romance + romance_change))
        rel.rivalry = max(0, min(100, rel.rivalry + rivalry_change))
        rel.cooperation = max(0, min(100, rel.cooperation + cooperation_change))
        
        rel.last_interaction = time.time()
        rel.interaction_count += 1
        
        safe_print(f"[事件系统] 更新关系 {cat1_id} <-> {cat2_id}: "
                  f"友好度{rel.friendship:.1f} 恋爱度{rel.romance:.1f}")
    
    def check_event_trigger(self, nearby_cats: List[Dict]) -> Optional[CatEventResult]:
        """检查是否应该触发事件"""
        current_time = time.time()
        
        # 检查全局冷却
        if current_time - self.last_event_time < self.global_cooldown:
            return None
        
        # 需要至少2只猫
        if len(nearby_cats) < 2:
            return None
        
        # 基础概率检查
        if random.random() > self.base_event_chance:
            return None
        
        # 选择可能的事件
        possible_events = self._find_possible_events(nearby_cats)
        if not possible_events:
            return None
        
        # 根据权重随机选择事件
        event = self._weighted_random_choice(possible_events)
        if not event:
            return None
        
        # 执行事件
        result = self._execute_event(event, nearby_cats)
        if result.success:
            self.last_event_time = current_time
            safe_print(f"[事件系统] 触发事件: {event.get('name', '未知事件')}")
        
        return result
    
    def _find_possible_events(self, nearby_cats: List[Dict]) -> List[Dict]:
        """找到所有可能触发的事件"""
        possible_events = []
        
        for event in self.events_config.get('events', []):
            if self._check_event_conditions(event, nearby_cats):
                possible_events.append(event)
        
        return possible_events
    
    def _check_event_conditions(self, event: Dict, nearby_cats: List[Dict]) -> bool:
        """检查事件是否满足触发条件"""
        # 检查参与者数量
        min_participants = event.get('min_participants', 2)
        max_participants = event.get('max_participants', 10)
        
        if not (min_participants <= len(nearby_cats) <= max_participants):
            return False
        
        # 检查事件冷却
        event_id = event.get('id', '')
        if event_id in self.event_cooldowns:
            cooldown = event.get('cooldown', 30.0)
            if time.time() - self.event_cooldowns[event_id] < cooldown:
                return False
        
        # 检查关系条件
        conditions = event.get('conditions', {})
        if conditions:
            if not self._check_relationship_conditions(conditions, nearby_cats):
                return False
        
        return True
    
    def _check_relationship_conditions(self, conditions: Dict, nearby_cats: List[Dict]) -> bool:
        """检查关系条件是否满足"""
        # 这里可以根据需要实现更复杂的条件检查
        # 目前简单返回True，后续可以扩展
        return True
    
    def _weighted_random_choice(self, events: List[Dict]) -> Optional[Dict]:
        """根据权重随机选择事件"""
        if not events:
            return None
        
        weights = [event.get('weight', 1.0) for event in events]
        total_weight = sum(weights)
        
        if total_weight <= 0:
            return random.choice(events)
        
        rand_val = random.random() * total_weight
        current_weight = 0
        
        for event, weight in zip(events, weights):
            current_weight += weight
            if rand_val <= current_weight:
                return event
        
        return events[-1]  # 备选方案
    
    def _execute_event(self, event: Dict, participants: List[Dict]) -> CatEventResult:
        """执行事件"""
        event_id = event.get('id', '')
        event_name = event.get('name', '未知事件')
        
        # 随机选择参与者（如果需要限制数量）
        max_participants = event.get('max_participants', len(participants))
        selected_participants = random.sample(participants, 
                                            min(max_participants, len(participants)))
        
        # 随机选择一个结果
        outcomes = event.get('outcomes', [])
        if not outcomes:
            return CatEventResult(success=False, message="事件没有定义结果")
        
        outcome = random.choice(outcomes)
        
        # 生成事件描述
        message = self._generate_event_message(event, outcome, selected_participants)
        
        # 应用关系变化
        relationship_changes = self._apply_relationship_changes(
            outcome.get('relationship_changes', {}), selected_participants)
        
        # 设置事件冷却
        self.event_cooldowns[event_id] = time.time()
        
        return CatEventResult(
            success=True,
            message=message,
            participants=[cat.get('id', '') for cat in selected_participants],
            relationship_changes=relationship_changes,
            follow_up_events=outcome.get('follow_up_events', [])
        )
    
    def _generate_event_message(self, event: Dict, outcome: Dict, 
                               participants: List[Dict]) -> str:
        """生成事件描述文本"""
        template = outcome.get('message', event.get('name', '发生了一个事件'))
        
        # 替换占位符
        cat_names = [cat.get('name', f"猫咪{i+1}") for i, cat in enumerate(participants)]
        
        try:
            if len(cat_names) >= 1:
                template = template.replace('{cat1}', cat_names[0])
            if len(cat_names) >= 2:
                template = template.replace('{cat2}', cat_names[1])
            if len(cat_names) >= 3:
                template = template.replace('{cat3}', cat_names[2])
            
            # 替换其他可能的占位符
            template = template.replace('{cats}', '、'.join(cat_names))
            
        except Exception as e:
            safe_print(f"[事件系统] 生成消息时出错: {e}")
            template = f"{cat_names[0] if cat_names else '猫咪们'}发生了一个有趣的事件"
        
        return template
    
    def _apply_relationship_changes(self, changes: Dict, participants: List[Dict]) -> Dict:
        """应用关系变化"""
        result_changes = {}
        
        if len(participants) < 2:
            return result_changes
        
        # 应用两两之间的关系变化
        for i in range(len(participants)):
            for j in range(i + 1, len(participants)):
                cat1 = participants[i]
                cat2 = participants[j]
                cat1_id = cat1.get('id', '')
                cat2_id = cat2.get('id', '')
                
                if not cat1_id or not cat2_id:
                    continue
                
                # 应用关系变化
                friendship_change = changes.get('friendship', 0)
                romance_change = changes.get('romance', 0)
                rivalry_change = changes.get('rivalry', 0)
                cooperation_change = changes.get('cooperation', 0)
                
                self.update_relationship(
                    cat1_id, cat2_id,
                    friendship_change=friendship_change,
                    romance_change=romance_change,
                    rivalry_change=rivalry_change,
                    cooperation_change=cooperation_change
                )
                
                # 记录变化用于UI显示
                relationship_key = f"{cat1_id}-{cat2_id}"
                result_changes[relationship_key] = {
                    'friendship': friendship_change,
                    'romance': romance_change,
                    'rivalry': rivalry_change,
                    'cooperation': cooperation_change
                }
        
        return result_changes
    
    def get_cat_compatibility(self, cat1_id: str, cat2_id: str) -> float:
        """获取两只猫的兼容性分数 (0-100)"""
        rel = self.get_relationship(cat1_id, cat2_id)
        
        # 基于各种关系值计算兼容性
        compatibility = 50  # 基础分数
        compatibility += rel.friendship * 0.3
        compatibility += rel.romance * 0.2
        compatibility += rel.cooperation * 0.2
        compatibility -= rel.rivalry * 0.3
        
        return max(0, min(100, compatibility))
    
    def get_relationship_summary(self, cat1_id: str, cat2_id: str) -> str:
        """获取关系摘要描述"""
        rel = self.get_relationship(cat1_id, cat2_id)
        
        if rel.romance > 50:
            return "恋人"
        elif rel.friendship > 60:
            return "好朋友"
        elif rel.rivalry > 60:
            return "竞争对手"
        elif rel.cooperation > 60:
            return "合作伙伴"
        elif rel.friendship < -30:
            return "敌人"
        else:
            return "普通关系"
    
    def debug_print_relationships(self):
        """调试用：打印所有关系"""
        safe_print("[事件系统] 当前关系状态:")
        for (cat1, cat2), rel in self.cat_relationships.items():
            summary = self.get_relationship_summary(cat1, cat2)
            safe_print(f"  {cat1} <-> {cat2}: {summary} "
                      f"(友好{rel.friendship:.1f} 恋爱{rel.romance:.1f})")