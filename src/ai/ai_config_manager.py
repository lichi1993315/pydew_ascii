#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
AI模型配置管理器
负责加载和管理AI模型配置
"""

import json
import os
from typing import Dict, Optional, List
from src.core.support import safe_print,get_resource_path

class AIConfigManager:
    """AI配置管理器"""
    
    def __init__(self):
        self.config_path = get_resource_path('config/ai_model_config.json')
        self.config = {}
        self.load_config()
    
    def load_config(self):
        """加载配置文件"""
        try:
            if os.path.exists(self.config_path):
                with open(self.config_path, 'r', encoding='utf-8') as f:
                    self.config = json.load(f)
                safe_print(f"SUCCESS: Loaded AI config file: {self.config_path}")
            else:
                safe_print(f"WARNING: Config file not found: {self.config_path}, using default config")
                self.config = self._get_default_config()
        except Exception as e:
            safe_print(f"ERROR: Failed to load config file: {e}, using default config")
            self.config = self._get_default_config()
    
    def _get_default_config(self) -> Dict:
        """获取默认配置"""
        return {
            "ai_models": {
                "default_model": "claude",
                "fallback_model": "mock",
                "models": {
                    "claude": {
                        "name": "Claude Sonnet 4",
                        "api_key_env": "CLAUDE_API_KEY",
                        "model_id": "claude-sonnet-4-20250514"
                    },
                    "doubao": {
                        "name": "豆包模型",
                        "api_key_env": "ARK_API_KEY", 
                        "model_id": "doubao-seed-1-6-250615"
                    }
                }
            },
            "chat_settings": {
                "conversation_history_length": 10,
                "cache_responses": True
            }
        }
    
    def get_default_model(self) -> str:
        """获取默认模型"""
        return self.config.get("ai_models", {}).get("default_model", "claude")
    
    def get_fallback_model(self) -> str:
        """获取回退模型"""
        return self.config.get("ai_models", {}).get("fallback_model", "mock")
    
    def get_model_config(self, model_name: str) -> Optional[Dict]:
        """获取指定模型的配置"""
        models = self.config.get("ai_models", {}).get("models", {})
        return models.get(model_name)
    
    def get_available_models(self) -> List[str]:
        """获取所有可用模型列表"""
        models = self.config.get("ai_models", {}).get("models", {})
        return list(models.keys())
    
    def get_model_api_key(self, model_name: str) -> Optional[str]:
        """获取模型的API密钥"""
        model_config = self.get_model_config(model_name)
        if model_config and "api_key_env" in model_config:
            env_var = model_config["api_key_env"]
            return os.environ.get(env_var)
        return None
    
    def is_model_available(self, model_name: str) -> bool:
        """检查模型是否可用（有API密钥或是mock模式）"""
        if model_name == "mock":
            return True
        
        api_key = self.get_model_api_key(model_name)
        return api_key is not None and api_key.strip() != ""
    
    def get_preferred_model_for_npc(self, npc_id: str) -> str:
        """根据NPC类型获取推荐模型"""
        preferences = self.config.get("npc_model_preferences", {})
        
        # 检查是否是猫咪NPC
        if npc_id.startswith("cat_"):
            cat_pref = preferences.get("cat_npcs", {})
            preferred = cat_pref.get("preferred_model", self.get_default_model())
            if self.is_model_available(preferred):
                return preferred
        
        # 检查是否是人类NPC
        elif npc_id in ["trader_zhang", "fisherman_li", "farmer_wang"]:
            human_pref = preferences.get("human_npcs", {})
            preferred = human_pref.get("preferred_model", self.get_default_model())
            if self.is_model_available(preferred):
                return preferred
        
        # 回退到默认模型
        default = self.get_default_model()
        if self.is_model_available(default):
            return default
        
        # 最后回退到fallback模型
        return self.get_fallback_model()
    
    def get_chat_settings(self) -> Dict:
        """获取聊天设置"""
        return self.config.get("chat_settings", {})
    
    def update_model_preference(self, npc_type: str, model_name: str):
        """更新NPC类型的模型偏好"""
        if "npc_model_preferences" not in self.config:
            self.config["npc_model_preferences"] = {}
        
        self.config["npc_model_preferences"][npc_type] = {
            "preferred_model": model_name
        }
        
        self.save_config()
    
    def save_config(self):
        """保存配置到文件"""
        try:
            with open(self.config_path, 'w', encoding='utf-8') as f:
                json.dump(self.config, f, ensure_ascii=False, indent=2)
            safe_print(f"SUCCESS: Config saved to: {self.config_path}")
        except Exception as e:
            safe_print(f"ERROR: Failed to save config: {e}")
    
    def print_status(self):
        """打印配置状态"""
        safe_print("\nAI Model Configuration Status:")
        safe_print(f"默认模型: {self.get_default_model()}")
        safe_print(f"回退模型: {self.get_fallback_model()}")
        
        safe_print("\n可用模型:")
        for model_name in self.get_available_models():
            available = self.is_model_available(model_name)
            status = "OK" if available else "FAIL"
            model_config = self.get_model_config(model_name)
            display_name = model_config.get("name", model_name) if model_config else model_name
            safe_print(f"  {status} {display_name} ({model_name})")
        
        safe_print("\nNPC模型偏好:")
        preferences = self.config.get("npc_model_preferences", {})
        for npc_type, pref in preferences.items():
            preferred_model = pref.get("preferred_model", "未设置")
            safe_print(f"  {npc_type}: {preferred_model}")

# 全局配置管理器实例
_config_manager = None

def get_config_manager() -> AIConfigManager:
    """获取配置管理器单例"""
    global _config_manager
    if _config_manager is None:
        _config_manager = AIConfigManager()
    return _config_manager

# 便捷函数
def get_preferred_model_for_npc(npc_id: str) -> str:
    """便捷函数：获取NPC的推荐模型"""
    return get_config_manager().get_preferred_model_for_npc(npc_id)

def is_model_available(model_name: str) -> bool:
    """便捷函数：检查模型是否可用"""
    return get_config_manager().is_model_available(model_name)