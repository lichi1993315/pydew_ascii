#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
PyDew 游戏安装配置
"""

from setuptools import setup, find_packages
import os

# 读取README文件
def read_readme():
    readme_path = os.path.join(os.path.dirname(__file__), 'README_ASCII.md')
    if os.path.exists(readme_path):
        with open(readme_path, 'r', encoding='utf-8') as f:
            return f.read()
    return "一个基于pygame的农场模拟游戏，支持ASCII和像素图形双重渲染模式。"

# 读取requirements.txt
def read_requirements():
    requirements = []
    req_path = os.path.join(os.path.dirname(__file__), 'requirements.txt')
    if os.path.exists(req_path):
        with open(req_path, 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#'):
                    # 移除注释
                    if '#' in line:
                        line = line[:line.index('#')].strip()
                    requirements.append(line)
    return requirements

setup(
    name="pydew",
    version="0.2.0",
    description="一个支持AI对话的农场模拟游戏",
    long_description=read_readme(),
    long_description_content_type="text/markdown",
    author="PyDew Team",
    author_email="dev@pydew.com",
    url="https://github.com/pydew/pydew",
    license="MIT",
    
    # 包配置
    packages=find_packages(include=['code', 'code.*']),
    package_dir={'': '.'},
    
    # 依赖配置
    install_requires=read_requirements(),
    
    # Python版本要求
    python_requires=">=3.8",
    
    # 分类信息
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: End Users/Desktop",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Topic :: Games/Entertainment :: Simulation",
        "Topic :: Multimedia :: Graphics",
        "Natural Language :: Chinese (Simplified)",
    ],
    
    # 关键词
    keywords="game pygame farming simulation ascii ai chat npc",
    
    # 入口点
    entry_points={
        'console_scripts': [
            'pydew=code.main:main',
        ],
    },
    
    # 包含的数据文件
    package_data={
        '': ['*.json', '*.md', '*.txt'],
    },
    include_package_data=True,
    
    # 额外的数据文件
    data_files=[
        ('config', ['config/ai_model_config.json']),
    ],
    
    # 可选依赖
    extras_require={
        'ai': ['anthropic>=0.30.0', 'openai>=1.30.0'],
        'dev': [
            'pytest>=7.4.0',
            'pytest-asyncio>=0.21.0',
            'pytest-cov>=4.1.0',
            'black>=23.0.0',
            'flake8>=6.0.0',
            'mypy>=1.5.0',
        ],
        'performance': [
            'psutil>=5.9.0',
            'memory-profiler>=0.61.0',
        ],
    },
    
    # 项目URLs
    project_urls={
        "Bug Reports": "https://github.com/pydew/pydew/issues",
        "Source": "https://github.com/pydew/pydew",
        "Documentation": "https://github.com/pydew/pydew/wiki",
    },
)