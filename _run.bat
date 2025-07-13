@echo off
setlocal enabledelayedexpansion

if "%1"=="test" (
    echo 运行所有测试...
    pytest test/ -v
) else if "%1"=="test-unit" (
    echo 运行单元测试...
    pytest test/ -m "unit" -v
) else if "%1"=="test-integration" (
    echo 运行集成测试...
    pytest test/ -m "integration" -v  
) else if "%1"=="test-ai" (
    echo 运行AI测试...
    pytest test/ -m "ai" -v
) else if "%1"=="run" (
    echo 启动游戏...
    cd code
    python main.py
) else if "%1"=="install" (
    echo 安装依赖...
    pip install -r requirements.txt
) else if "%1"=="dev-install" (
    echo 安装开发依赖...
    pip install -r requirements.txt
    pip install -e .[dev,ai,performance]
) else if "%1"=="format" (
    echo 格式化代码...
    black code/ test/
    isort code/ test/
) else if "%1"=="lint" (
    echo 代码检查...
    flake8 code/ test/
    mypy code/ --ignore-missing-imports
) else if "%1"=="clean" (
    echo 清理临时文件...
    for /r %%i in (*.pyc) do del "%%i"
    for /f "delims=" %%i in ('dir /s /b /a:d __pycache__') do rd /s /q "%%i"
) else if "%1"=="help" (
    echo PyDew 游戏开发工具
    echo.
    echo 可用命令:
    echo   install        安装游戏依赖
    echo   dev-install    安装开发依赖  
    echo   test           运行所有测试
    echo   test-unit      运行单元测试
    echo   test-integration  运行集成测试
    echo   test-ai        运行AI功能测试
    echo   clean          清理临时文件
    echo   format         格式化代码
    echo   lint           代码质量检查
    echo   run            运行游戏
    echo.
    echo 使用方法: run.bat [命令]
) else (
    echo 未知命令: %1
    echo 使用 'run.bat help' 查看可用命令
) 