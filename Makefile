# PyDew 游戏开发工具
.PHONY: help install dev-install test test-unit test-integration test-ai clean format lint run run-test build docs

# 默认目标
help:
	@echo "PyDew 游戏开发工具"
	@echo ""
	@echo "可用命令:"
	@echo "  install        安装游戏依赖"
	@echo "  dev-install    安装开发依赖"
	@echo "  test           运行所有测试"
	@echo "  test-unit      运行单元测试"
	@echo "  test-integration  运行集成测试"
	@echo "  test-ai        运行AI功能测试"
	@echo "  clean          清理临时文件"
	@echo "  format         格式化代码"
	@echo "  lint           代码质量检查"
	@echo "  run            运行游戏"
	@echo "  run-test       运行测试版本"
	@echo "  build          构建发布版本"
	@echo "  docs           生成文档"

# 安装依赖
install:
	pip install -r requirements.txt

dev-install: install
	pip install -e .[dev,ai,performance]

# 测试相关
test:
	pytest test/ -v

test-unit:
	pytest test/ -m "unit" -v

test-integration:
	pytest test/ -m "integration" -v

test-ai:
	pytest test/ -m "ai" -v

test-coverage:
	pytest test/ --cov=code --cov-report=html --cov-report=term

# 代码质量
clean:
	find . -type f -name "*.pyc" -delete
	find . -type d -name "__pycache__" -delete
	find . -type d -name "*.egg-info" -exec rm -rf {} +
	find . -type f -name "*.log" -delete
	rm -rf build/ dist/ htmlcov/ .coverage .pytest_cache/

format:
	black code/ test/
	isort code/ test/

lint:
	flake8 code/ test/
	mypy code/ --ignore-missing-imports

# 运行游戏
run:
	python run.py

run-test:
	cd test && python test_doubao_basic.py

# 构建和发布
build: clean
	python setup.py sdist bdist_wheel

# 文档生成
docs:
	@echo "生成项目文档..."
	@echo "项目结构已优化，请查看 PROJECT_STRUCTURE_GUIDE.md"

# 快速开发环境设置
setup-dev: dev-install
	@echo "复制环境变量模板..."
	@if [ ! -f .env ]; then cp .env.example .env; fi
	@echo "开发环境设置完成！"
	@echo "请编辑 .env 文件添加您的API密钥"

# AI模型测试
test-models:
	cd test && python test_model_comparison.py

# 性能测试
profile:
	cd code && python -m cProfile -o game.prof main.py
	@echo "性能分析文件已生成: code/game.prof"

# 内存使用分析
memory-profile:
	cd code && python -m memory_profiler main.py

# 检查项目健康状况
health-check:
	@echo "🔍 检查项目健康状况..."
	@echo "1. 检查依赖..."
	@pip check
	@echo "2. 运行代码质量检查..."
	@make lint
	@echo "3. 运行单元测试..."
	@make test-unit
	@echo "✅ 项目健康检查完成"