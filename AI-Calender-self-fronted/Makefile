# AI Calendar Frontend Makefile

.PHONY: help run install clean build preview

# 默认显示帮助信息
help:
	@echo "AI Calendar Frontend 快捷命令"
	@echo ""
	@echo "可用命令:"
	@echo "  make run      - 启动开发服务器 (http://localhost:5173)"
	@echo "  make install  - 安装项目依赖"
	@echo "  make build    - 构建生产版本"
	@echo "  make preview  - 预览生产构建"
	@echo "  make clean    - 清理 node_modules 和构建产物"
	@echo "  make lint     - 运行代码检查"

# 启动开发服务器
run:
	@echo "================================"
	@echo "AI Calendar Frontend"
	@echo "================================"
	@echo "启动开发服务器..."
	@echo "访问 http://localhost:5173 查看应用"
	@echo ""
	@npm run dev

# 安装依赖
install:
	@echo "安装项目依赖..."
	@npm install

# 构建生产版本
build:
	@echo "构建生产版本..."
	@npm run build
	@echo "构建完成！产物在 dist/ 目录"

# 预览生产构建
preview: build
	@echo "预览生产构建..."
	@npm run preview

# 运行代码检查
lint:
	@echo "运行代码检查..."
	@npm run lint

# 清理项目
clean:
	@echo "清理项目..."
	@rm -rf node_modules dist
	@echo "清理完成"

# 重新安装依赖
reinstall: clean install
	@echo "重新安装依赖完成"
