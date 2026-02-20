# Calendar MCP Backend Makefile

.PHONY: help run install clean

# 默认显示帮助信息
help:
	@echo "Calendar MCP Backend 快捷命令"
	@echo ""
	@echo "可用命令:"
	@echo "  make run      - 启动后端服务 (http://localhost:8000)"
	@echo "  make install  - 安装项目依赖"
	@echo "  make clean    - 清理缓存文件"

# 启动后端服务
run:
	@echo "================================"
	@echo "Calendar MCP Backend"
	@echo "================================"
	@echo "启动服务中..."
	@echo "访问 http://localhost:8000/docs 查看 API 文档"
	@echo ""
	@uv run uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# 安装依赖
install:
	@echo "安装项目依赖..."
	@uv sync

# 清理缓存文件
clean:
	@echo "清理缓存文件..."
	@find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
	@find . -type f -name "*.pyc" -delete 2>/dev/null || true
	@find . -type f -name ".DS_Store" -delete 2>/dev/null || true
	@echo "清理完成"
