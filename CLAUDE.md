# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Running the Game

```bash
# Run the main game
python code/main.py

# Or use the Makefile
make run
```

The game supports both ASCII mode (Dwarf Fortress style) and traditional pixel graphics mode, selectable from the main menu.

## Project Structure

The project follows a modular structure:
- `code/` - Core game code
- `config/` - Configuration files (AI models, game settings)
- `test/` - Test scripts and unit tests
- `assets/` - Game resources (audio, graphics, fonts, data)
- `docs/` - Documentation

## Testing

```bash
# Run all tests
make test

# Run specific types of tests
make test-unit          # Unit tests
make test-integration   # Integration tests
make test-ai           # AI functionality tests

# Run test coverage
make test-coverage

# Manual test scripts
cd test && python test_doubao_basic.py
cd test && python test_model_comparison.py
```

if not permitted, do not make any attempt to create test script.

## Dependencies

Install dependencies using:
```bash
# Basic installation
pip install -r requirements.txt

# Development installation with all optional features
make dev-install
```

Core dependencies:
- pygame (main game engine)
- pytmx (TMX map loading)

Optional dependencies for AI features:
- anthropic (Claude API integration)
- openai (Doubao/OpenAI API integration)
- httpx (HTTP requests)
- python-dotenv (environment variables)

## Configuration

Copy the environment template and configure your API keys:
```bash
cp .env.example .env
# Edit .env file with your API keys
```

AI model configuration is in `config/ai_model_config.json`.

## Architecture Overview

This is a farming simulation game with dual rendering modes (ASCII and pixel graphics). The architecture follows a component-based design:

### Core Systems

**Main Game Loop** (`code/main.py`): Entry point with menu system and game state management

**Level System** (`code/level.py`): Central game world manager that coordinates all game systems including:
- Sprite management with CameraGroup
- Collision detection
- NPC system integration
- Quest system integration
- Weather system (rain/sky)
- Soil/farming system

**Rendering Systems**: 
- ASCII rendering (`code/ascii_renderer.py`, `code/ascii_sprites.py`) - Dwarf Fortress style
- Traditional pixel graphics (various sprite classes in `code/sprites.py`)

### Key Game Systems

**Player System** (`code/player.py`): Character movement, tool usage, inventory management

**NPC System** (`code/npc_system.py`): NPC behavior, dialogue system, quest generation
- Integrates with Claude API for dynamic dialogue generation
- Quest library system for procedural quest generation

**Farming System** (`code/soil.py`, `code/ascii_soil.py`): Soil tilling, planting, watering, harvesting

**UI Systems**:
- Dialogue UI (`code/dialogue_ui.py`)
- Quest Panel (`code/quest_panel.py`) 
- Log Panel (`code/log_panel.py`)
- Menu System (`code/menu.py`)

**Map System**: Uses TMX maps (`data/map.tmx`) with tilesets for world layout

### Asset Structure

- `graphics/`: Pixel art assets organized by category (character, environment, objects, etc.)
- `audio/`: Sound effects and background music
- `font/`: Custom fonts including Chinese character support
- `data/`: TMX map files and tilesets

### Special Features

**Dual Rendering**: The game can switch between ASCII and pixel graphics modes at runtime. ASCII mode uses character mapping for all game elements with color coding.

**AI Integration**: Optional Claude API integration for dynamic NPC dialogue generation, configured via environment variables.

**Internationalization**: Supports Chinese text rendering with custom font loading and fallback mechanisms.

## Development Notes

The codebase uses pygame as the main framework with a custom sprite system. When working with rendering, be aware that there are parallel ASCII and pixel graphics implementations for most visual elements.

The game uses a tile-based coordinate system (64px tiles) for world positioning and collision detection.

Font management is handled through a singleton FontManager class that supports Chinese character rendering with fallback mechanisms.

## 重要开发规范

### 文本渲染规范

**动态换行要求**: 
- 所有在UI中显示的文本（对话、旁白、描述等）都必须实现动态换行
- 不能让文本超出容器边界导致看不见
- 必须使用统一的`TextRenderer`类处理所有文本渲染
- 禁止直接使用pygame的`font.render()`进行多行文本渲染
- 在计算UI元素高度时要考虑换行后的实际高度

**TextRenderer使用规范**:
- 使用`text_renderer.render_multiline_text()`渲染普通多行文本
- 使用`text_renderer.render_text_with_background()`渲染带背景的文本
- 使用`text_renderer.calculate_text_size()`计算文本尺寸
- 使用`text_renderer.wrap_text_advanced()`进行高级文本换行

**emoji和中文字符处理**:
- TextRenderer已优化中文字符和emoji的宽度计算
- 支持全角/半角字符的正确换行
- 自动处理emoji字符的特殊宽度
- 优先使用emoji_font渲染emoji字符
- 提供字体回退机制：emoji_font → normal_font → fallback字符

## SuperCompact 记录

最后执行时间: 2025-07-13
执行内容: 会话压缩 + 自动提交 + 项目文件更新 + 猫咪emoji功能实现
Git提交: 待生成

上次执行: 2025-07-13
上次Git提交: b3c3c9e

## 最新功能更新

### 猫咪NPC头顶emoji系统 (2025-07-13)
- 实现了猫咪NPC头顶显示emoji功能，表达当前行为状态
- 包含多种行为emoji：😴💤🤔😌🥱🚶🏃👀🎯🔍🧘😊☀️🌸💭等
- 特殊功能：猫咪对话时显示💬气泡emoji
- 随机显示机制：1%概率每帧触发，持续2-5秒
- 智能行为映射：根据移动状态、社交状态等自动选择对应emoji
- 文件修改：`src/ai/cat_npc.py`，`src/rendering/ascii_renderer.py`