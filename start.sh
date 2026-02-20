#!/bin/bash

# 快速启动脚本

echo "================================"
echo "Calendar MCP Backend"
echo "================================"

# 检查 Python 版本
python_version=$(python3 --version 2>&1 | awk '{print $2}')
echo "Python 版本: $python_version"

# 检查是否存在虚拟环境
if [ ! -d "venv" ]; then
    echo ""
    echo "创建虚拟环境..."
    python3 -m venv venv
fi

# 激活虚拟环境
echo "激活虚拟环境..."
source venv/bin/activate

# 安装依赖
echo ""
echo "安装依赖..."
pip install -r requirements.txt

# 检查 .env 文件
if [ ! -f ".env" ]; then
    echo ""
    echo "警告: .env 文件不存在"
    echo "请复制 .env.example 到 .env 并填写 API Key"
    echo "cp .env.example .env"
    exit 1
fi

# 启动服务
echo ""
echo "================================"
echo "启动服务..."
echo "================================"
echo ""
echo "访问 http://localhost:8000/docs 查看 API 文档"
echo ""

python -m uvicorn app.main:app --reload --port 8000