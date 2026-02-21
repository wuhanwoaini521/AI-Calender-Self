# Calendar MCP Backend Makefile

.PHONY: help run install clean dev frontend

FRONTEND_DIR = AI-Calender-self-fronted

# 默认显示帮助信息
help:
	@echo "Calendar MCP Backend 快捷命令"
	@echo ""
	@echo "可用命令:"
	@echo "  make run       - 启动后端服务 (http://localhost:8000)"
	@echo "  make frontend  - 启动前端服务 (http://localhost:5173)"
	@echo "  make dev       - 同时启动前后端服务"
	@echo "  make install   - 安装后端依赖"
	@echo "  make install-all - 安装前后端依赖"
	@echo "  make clean     - 清理缓存文件"

# 启动后端服务
run:
	@echo "================================"
	@echo "Calendar MCP Backend"
	@echo "================================"
	@echo "启动服务中..."
	@echo "访问 http://localhost:8000/docs 查看 API 文档"
	@echo ""
	@uv run uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# 启动前端服务
frontend:
	@echo "================================"
	@echo "AI Calendar Frontend"
	@echo "================================"
	@cd $(FRONTEND_DIR) && make run

# 同时启动前后端（后台运行后端，前台运行前端）
dev:
	@echo "================================"
	@echo "启动前后端服务..."
	@echo "后端: http://localhost:8000"
	@echo "前端: http://localhost:5173"
	@echo "================================"
	@make run &
	@sleep 2
	@make frontend

# 安装后端依赖
install:
	@echo "安装后端依赖..."
	@uv sync

# 安装前端依赖
install-frontend:
	@echo "安装前端依赖..."
	@cd $(FRONTEND_DIR) && npm install

# 安装所有依赖
install-all: install install-frontend
	@echo "所有依赖安装完成！"

# 清理缓存文件
clean:
	@echo "清理缓存文件..."
	@find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
	@find . -type f -name "*.pyc" -delete 2>/dev/null || true
	@find . -type f -name ".DS_Store" -delete 2>/dev/null || true
	@echo "清理完成"
