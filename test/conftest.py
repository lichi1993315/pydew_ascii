#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
pytest配置文件
"""

import pytest
import sys
import os
from pathlib import Path

# 添加项目根目录到路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root / "code"))

@pytest.fixture(scope="session")
def project_root_path():
    """返回项目根目录路径"""
    return project_root

@pytest.fixture(scope="session")
def config_path():
    """返回配置文件目录路径"""
    return project_root / "config"

@pytest.fixture(scope="function")
def mock_env_vars(monkeypatch):
    """模拟环境变量"""
    monkeypatch.setenv("CLAUDE_API_KEY", "test_claude_key")
    monkeypatch.setenv("ARK_API_KEY", "test_ark_key")
    monkeypatch.setenv("AI_MODEL_TYPE", "mock")
    return {
        "CLAUDE_API_KEY": "test_claude_key",
        "ARK_API_KEY": "test_ark_key",
        "AI_MODEL_TYPE": "mock"
    }

@pytest.fixture(scope="function")
def temp_config_file(tmp_path):
    """创建临时配置文件"""
    config_content = {
        "ai_models": {
            "default_model": "claude",
            "fallback_model": "mock",
            "models": {
                "claude": {
                    "name": "Claude Sonnet 4",
                    "api_key_env": "CLAUDE_API_KEY"
                },
                "doubao": {
                    "name": "豆包模型",
                    "api_key_env": "ARK_API_KEY"
                },
                "mock": {
                    "name": "模拟模式",
                    "enabled": True
                }
            }
        }
    }
    
    import json
    config_file = tmp_path / "ai_model_config.json"
    config_file.write_text(json.dumps(config_content, ensure_ascii=False, indent=2))
    return str(config_file)

# 标记慢速测试
def pytest_configure(config):
    config.addinivalue_line("markers", "slow: marks tests as slow (deselect with '-m \"not slow\"')")
    config.addinivalue_line("markers", "integration: marks tests as integration tests")
    config.addinivalue_line("markers", "unit: marks tests as unit tests")
    config.addinivalue_line("markers", "ai: marks tests that require AI API")

# 跳过需要API密钥的测试
def pytest_collection_modifyitems(config, items):
    """自动跳过需要真实API密钥的测试"""
    skip_ai = pytest.mark.skip(reason="需要真实的API密钥")
    
    for item in items:
        if "ai" in item.keywords and not (
            os.getenv("CLAUDE_API_KEY") or os.getenv("ARK_API_KEY")
        ):
            item.add_marker(skip_ai)