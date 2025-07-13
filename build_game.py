#!/usr/bin/env python3
"""
游戏打包脚本
自动化创建可执行文件的过程
"""

import os
import sys
import shutil
import subprocess
from pathlib import Path

def print_banner():
    """打印横幅"""
    print("=" * 60)
    print("🎣 Pawfishing Game 打包工具")
    print("=" * 60)

def check_requirements():
    """检查必要的工具和文件"""
    print("📋 检查打包要求...")
    
    # 检查是否安装了PyInstaller
    try:
        import PyInstaller
        print("✅ PyInstaller 已安装")
    except ImportError:
        print("❌ PyInstaller 未安装，正在安装...")
        subprocess.run([sys.executable, "-m", "pip", "install", "pyinstaller"])
        print("✅ PyInstaller 安装完成")
    
    # 检查必要文件
    required_files = [
        "run.py",
        "pawfishing_game.spec",
        "src/main.py",
        "assets/",
    ]
    
    for file_path in required_files:
        if os.path.exists(file_path):
            print(f"✅ {file_path} 存在")
        else:
            print(f"❌ {file_path} 不存在")
            return False
    
    return True

def clean_build_dirs():
    """清理之前的构建目录"""
    print("🧹 清理之前的构建文件...")
    
    dirs_to_clean = ["build", "dist", "__pycache__"]
    
    for dir_name in dirs_to_clean:
        if os.path.exists(dir_name):
            shutil.rmtree(dir_name)
            print(f"✅ 已删除 {dir_name}")
    
    # 清理.pyc文件
    for root, dirs, files in os.walk("."):
        for file in files:
            if file.endswith(".pyc"):
                os.remove(os.path.join(root, file))

def install_minimal_requirements():
    """安装最小依赖"""
    print("📦 安装最小依赖...")
    
    if os.path.exists("requirements_minimal.txt"):
        subprocess.run([
            sys.executable, "-m", "pip", "install", 
            "-r", "requirements_minimal.txt"
        ])
        print("✅ 最小依赖安装完成")
    else:
        print("⚠️ requirements_minimal.txt 不存在，跳过依赖安装")

def build_executable():
    """构建可执行文件"""
    print("🔨 开始构建可执行文件...")
    
    # 执行PyInstaller
    cmd = [
        sys.executable, "-m", "PyInstaller",
        "--clean",  # 清理临时文件
        "pawfishing_game.spec"
    ]
    
    print(f"执行命令: {' '.join(cmd)}")
    result = subprocess.run(cmd, capture_output=True, text=True)
    
    if result.returncode == 0:
        print("✅ 构建成功!")
        return True
    else:
        print("❌ 构建失败!")
        print("错误输出:")
        print(result.stderr)
        return False

def create_release_package():
    """创建发布包"""
    print("📦 创建发布包...")
    
    # 检查多文件模式的游戏目录
    game_dir = Path("dist/PawfishingGame")
    if not game_dir.exists():
        print("❌ 没有找到游戏目录 dist/PawfishingGame")
        return False
    
    # 检查exe文件
    exe_file = game_dir / "PawfishingGame.exe"
    if not exe_file.exists():
        print("❌ 没有找到可执行文件")
        return False
    
    print(f"✅ 找到可执行文件: {exe_file}")
    
    # 创建发布目录
    release_dir = Path("release")
    if release_dir.exists():
        shutil.rmtree(release_dir)
    release_dir.mkdir()
    
    # 复制整个游戏目录
    shutil.copytree(game_dir, release_dir / "PawfishingGame")
    print("✅ 已复制游戏目录到发布包")
    
    # 创建说明文件
    readme_content = """# Pawfishing Game 🎣

欢迎试玩萌爪钓鱼游戏！

## 游戏启动

1. 进入 `PawfishingGame` 目录
2. 双击运行 `PawfishingGame.exe`

## 游戏说明

这是一个 ASCII 风格的钓鱼模拟游戏，你可以：
- 🎣 钓鱼获得各种鱼类
- 🐱 通过钓鱼获得可爱的猫咪NPC
- 💬 与猫咪和NPC对话
- 🌱 种植农作物
- 🏪 买卖物品

## 操作说明

- **移动**: 方向键 ↑↓←→
- **钓鱼**: 空格键 (在水边使用)
- **工具使用**: F键
- **种植**: Ctrl键
- **切换种子**: E键
- **对话/交互**: T键
- **聊天面板**: C键
- **任务面板**: Q键
- **日志面板**: L键
- **返回菜单**: ESC键

## 钓鱼玩法

1. 走到水边，按空格键投掷鱼饵
2. 等待3-10秒，鱼饵会开始晃动
3. 看到"鱼上钩了"提示时，再按空格键
4. 进入钓鱼小游戏，按住空格键收线
5. 注意鱼的状态：挣扎时不要按键，力竭时才收线
6. 成功将鱼拉到顶部就能钓到鱼或猫咪！

## 文件结构

- `PawfishingGame.exe` - 游戏主程序
- `assets/` - 游戏资源文件夹（包含图像、音效等）
- `config/` - 配置文件夹
- 其他依赖文件 - 游戏运行所需的库文件

## 技术信息

- 游戏引擎: Pygame
- 支持中文字体和emoji显示
- 包含AI对话功能（需要配置API密钥）

## 故障排除

如果游戏无法启动，请检查：
1. 确保所有文件完整，不要移动或删除任何文件
2. 确保在PawfishingGame目录内运行exe文件
3. 检查系统是否支持
4. 尝试以管理员身份运行

享受游戏！
"""
    
    with open(release_dir / "README.txt", "w", encoding="utf-8") as f:
        f.write(readme_content)
    
    # 复制配置文件
    if Path("config").exists():
        shutil.copytree("config", release_dir / "config")
    
    # 创建环境变量示例文件
    env_example = """# 可选的AI功能配置
# 如果要启用AI对话功能，请取消注释并填入你的API密钥

# ANTHROPIC_API_KEY=your_anthropic_api_key_here
# OPENAI_API_KEY=your_openai_api_key_here
"""
    
    with open(release_dir / ".env.example", "w", encoding="utf-8") as f:
        f.write(env_example)
    
    print(f"✅ 发布包已创建: {release_dir}")
    return True

def get_file_size(file_path):
    """获取文件大小并格式化"""
    size = os.path.getsize(file_path)
    for unit in ['B', 'KB', 'MB', 'GB']:
        if size < 1024.0:
            return f"{size:.1f} {unit}"
        size /= 1024.0
    return f"{size:.1f} TB"

def show_results():
    """显示构建结果"""
    print("📊 构建结果:")
    
    # 显示多文件模式的构建结果
    game_dir = Path("dist/PawfishingGame")
    if game_dir.exists():
        # 显示主要文件
        exe_file = game_dir / "PawfishingGame.exe"
        if exe_file.exists():
            size = get_file_size(exe_file)
            print(f"  🎮 PawfishingGame.exe: {size}")
        
        # 显示assets目录
        assets_dir = game_dir / "assets"
        if assets_dir.exists():
            assets_size = sum(f.stat().st_size for f in assets_dir.rglob('*') if f.is_file())
            print(f"  📁 assets/: {get_file_size_from_bytes(assets_size)}")
        
        # 显示总大小
        total_size = sum(f.stat().st_size for f in game_dir.rglob('*') if f.is_file())
        print(f"  📦 游戏目录总大小: {get_file_size_from_bytes(total_size)}")
    
    release_dir = Path("release")
    if release_dir.exists():
        total_size = sum(f.stat().st_size for f in release_dir.rglob('*') if f.is_file())
        print(f"  📦 发布包大小: {get_file_size_from_bytes(total_size)}")

def get_file_size_from_bytes(size_bytes):
    """从字节数获取格式化的文件大小"""
    for unit in ['B', 'KB', 'MB', 'GB']:
        if size_bytes < 1024.0:
            return f"{size_bytes:.1f} {unit}"
        size_bytes /= 1024.0
    return f"{size_bytes:.1f} TB"

def test_executable():
    """测试生成的可执行文件"""
    print("🧪 测试可执行文件...")
    
    # 查找exe文件（多文件模式）
    exe_file = Path("dist/PawfishingGame/PawfishingGame.exe")
    
    if not exe_file.exists():
        print("❌ 没有找到exe文件进行测试")
        return False
    
    print(f"🔍 测试文件: {exe_file}")
    
    try:
        # 运行exe文件5秒钟，检查是否有traceback错误
        cmd = [str(exe_file)]
        print("启动游戏进行测试...")
        
        process = subprocess.Popen(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            cwd=str(exe_file.parent)
        )
        
        # 等待5秒钟
        try:
            stdout, stderr = process.communicate(timeout=5)
            
            # 检查是否有错误输出
            if stderr and ("Traceback" in stderr or "Error" in stderr):
                print("❌ 检测到运行时错误:")
                print(stderr)
                return False
            else:
                print("✅ 程序正常启动，未检测到明显错误")
                return True
                
        except subprocess.TimeoutExpired:
            # 超时说明程序正在正常运行
            process.terminate()
            try:
                process.wait(timeout=2)
            except subprocess.TimeoutExpired:
                process.kill()
                process.wait()
            
            print("✅ 程序运行超过5秒，测试通过")
            return True
            
    except Exception as e:
        print(f"❌ 测试过程中发生错误: {e}")
        return False

def main():
    """主函数"""
    print_banner()
    
    try:
        # 检查要求
        if not check_requirements():
            print("❌ 前置条件检查失败")
            return 1
        
        # 清理构建目录
        clean_build_dirs()
        
        # 安装最小依赖
        install_minimal_requirements()
        
        # 构建可执行文件
        if not build_executable():
            return 1
        
        # 创建发布包
        if not create_release_package():
            return 1
        
        # 显示结果
        show_results()
        
        # 自动测试exe文件
        test_executable()
        
        print("=" * 60)
        print("🎉 游戏打包完成!")
        print("📂 可执行文件位于: dist/PawfishingGame/")
        print("📦 发布包位于: release/PawfishingGame/")
        print("🎮 运行游戏: 进入对应目录，双击 PawfishingGame.exe")
        print("=" * 60)
        
        return 0
        
    except Exception as e:
        print(f"❌ 打包过程中发生错误: {e}")
        import traceback
        traceback.print_exc()
        return 1

if __name__ == "__main__":
    sys.exit(main())