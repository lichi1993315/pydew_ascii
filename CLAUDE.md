# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Running the Game

```bash
# Run the main game
python code/main.py
```

The game supports both ASCII mode (Dwarf Fortress style) and traditional pixel graphics mode, selectable from the main menu.

## Testing

if not permitted, do not make any attempt to create test script.

## Dependencies

Core dependencies:
- pygame (main game engine)
- pytmx (TMX map loading)

Optional dependencies for AI features:
- anthropic (Claude API integration)
- httpx (HTTP requests)
- python-dotenv (environment variables)

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

## SuperCompact 记录

最后执行时间: 2025-07-12
执行内容: 会话压缩 + 自动提交 + 项目文件更新
Git提交: 待创建