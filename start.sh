#!/bin/bash

# 职业规划导航平台启动脚本

echo "🚀 启动职业规划导航平台..."

# 创建数据目录
mkdir -p data
mkdir -p logs

# 检查Docker是否安装
if ! command -v docker &> /dev/null; then
    echo "❌ Docker未安装，请先安装Docker"
    exit 1
fi

# 检查Docker Compose是否安装
if ! command -v docker compose &> /dev/null; then
    echo "❌ Docker Compose未安装，请先安装Docker Compose"
    exit 1
fi

# 构建并启动服务
echo "📦 构建Docker镜像..."
docker compose build

echo "🚀 启动服务..."
docker compose up -d

echo "⏳ 等待服务启动..."
sleep 5

# 检查服务状态
if docker compose ps | grep -q "Up"; then
    echo "✅ 服务启动成功！"
    echo "🌐 前端地址: http://localhost"
    echo "🔧 后端API地址: http://localhost:8000"
    echo "📊 API文档: http://localhost:8000/docs"
    echo ""
    echo "📋 常用命令:"
    echo "  查看日志: docker-compose logs -f"
    echo "  停止服务: docker-compose down"
    echo "  重启服务: docker-compose restart"
else
    echo "❌ 服务启动失败，请检查日志:"
    docker-compose logs
fi