#!/bin/bash

# 李会计凭证识别系统 - 开发环境启动脚本

echo "========================================="
echo "  李会计凭证识别系统 - 开发环境启动"
echo "========================================="

# 检查Python是否安装
if ! command -v python3 &> /dev/null; then
    echo "❌ 请先安装 Python 3.11+"
    exit 1
fi

# 检查Node.js是否安装
if ! command -v node &> /dev/null; then
    echo "❌ 请先安装 Node.js 18+"
    exit 1
fi

# 启动后端
echo ""
echo "📦 启动后端服务..."
cd backend

# 创建虚拟环境（如果不存在）
if [ ! -d "venv" ]; then
    echo "创建Python虚拟环境..."
    python3 -m venv venv
fi

# 激活虚拟环境
source venv/bin/activate

# 安装依赖
echo "安装Python依赖..."
pip install -r requirements.txt -q

# 后台启动后端
echo "启动FastAPI后端服务 (端口: 8000)..."
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000 &
BACKEND_PID=$!

cd ..

# 等待后端启动
sleep 3

# 启动前端
echo ""
echo "📦 启动前端服务..."
cd frontend

# 安装依赖（如果node_modules不存在）
if [ ! -d "node_modules" ]; then
    echo "安装Node.js依赖..."
    npm install
fi

# 启动前端
echo "启动Vite开发服务器 (端口: 3000)..."
npm run dev &
FRONTEND_PID=$!

cd ..

echo ""
echo "========================================="
echo "  服务已启动！"
echo "========================================="
echo ""
echo "  🌐 前端: http://localhost:3000"
echo "  🔧 后端: http://localhost:8000"
echo "  📚 API文档: http://localhost:8000/api/docs"
echo ""
echo "  按 Ctrl+C 停止所有服务"
echo ""

# 等待用户中断
trap "kill $BACKEND_PID $FRONTEND_PID 2>/dev/null; exit 0" SIGINT SIGTERM
wait

