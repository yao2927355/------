#!/bin/bash

# 李会计凭证识别系统 - 一键启动脚本

set -e

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# 打印带颜色的消息
print_info() {
    echo -e "${BLUE}ℹ${NC} $1"
}

print_success() {
    echo -e "${GREEN}✓${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}⚠${NC} $1"
}

print_error() {
    echo -e "${RED}✗${NC} $1"
}

print_header() {
    echo ""
    echo -e "${GREEN}========================================${NC}"
    echo -e "${GREEN}  李会计凭证识别系统 - 一键启动${NC}"
    echo -e "${GREEN}========================================${NC}"
    echo ""
}

# 清理函数
cleanup() {
    print_info "正在停止服务..."
    if [ ! -z "$BACKEND_PID" ]; then
        kill $BACKEND_PID 2>/dev/null || true
    fi
    if [ ! -z "$FRONTEND_PID" ]; then
        kill $FRONTEND_PID 2>/dev/null || true
    fi
    exit 0
}

# 注册清理函数
trap cleanup SIGINT SIGTERM

print_header

# 检查Python
print_info "检查Python环境..."
if ! command -v python3 &> /dev/null; then
    print_error "未找到 Python 3，请先安装 Python 3.11+"
    exit 1
fi
PYTHON_VERSION=$(python3 --version | cut -d' ' -f2)
print_success "Python版本: $PYTHON_VERSION"

# 检查Node.js
print_info "检查Node.js环境..."
if ! command -v node &> /dev/null; then
    print_error "未找到 Node.js，请先安装 Node.js 18+"
    exit 1
fi
NODE_VERSION=$(node --version)
print_success "Node.js版本: $NODE_VERSION"

# 检查npm
if ! command -v npm &> /dev/null; then
    print_error "未找到 npm"
    exit 1
fi

echo ""

# ============ 后端启动 ============
print_info "准备后端服务..."

cd backend

# 创建虚拟环境
if [ ! -d "venv" ]; then
    print_info "创建Python虚拟环境..."
    python3 -m venv venv
    print_success "虚拟环境创建成功"
fi

# 激活虚拟环境
print_info "激活虚拟环境..."
source venv/bin/activate

# 安装依赖
if [ ! -f "venv/.deps_installed" ]; then
    print_info "安装Python依赖（首次运行，可能需要几分钟）..."
    pip install --upgrade pip -q
    pip install -r requirements.txt -q
    touch venv/.deps_installed
    print_success "依赖安装完成"
else
    print_info "检查依赖更新..."
    pip install -r requirements.txt -q --upgrade
fi

# 创建上传目录
mkdir -p uploads

# 启动后端
print_info "启动后端服务 (端口: 8000)..."
uvicorn app.main:app --host 0.0.0.0 --port 8000 > ../backend.log 2>&1 &
BACKEND_PID=$!

# 等待后端启动
print_info "等待后端服务启动..."
for i in {1..30}; do
    if curl -s http://localhost:8000/api/health > /dev/null 2>&1; then
        print_success "后端服务启动成功！"
        break
    fi
    if [ $i -eq 30 ]; then
        print_error "后端服务启动超时，请检查 backend.log"
        exit 1
    fi
    sleep 1
done

cd ..

# ============ 前端启动 ============
print_info "准备前端服务..."

cd frontend

# 安装依赖
if [ ! -d "node_modules" ]; then
    print_info "安装Node.js依赖（首次运行，可能需要几分钟）..."
    npm install
    print_success "依赖安装完成"
else
    print_info "检查依赖更新..."
    npm install
fi

# 启动前端
print_info "启动前端服务 (端口: 3000)..."
npm run dev > ../frontend.log 2>&1 &
FRONTEND_PID=$!

cd ..

# 等待前端启动
print_info "等待前端服务启动..."
sleep 5

# ============ 显示结果 ============
echo ""
print_header
print_success "所有服务已启动！"
echo ""
echo -e "  ${GREEN}🌐 前端地址:${NC} http://localhost:3000"
echo -e "  ${GREEN}🔧 后端地址:${NC} http://localhost:8000"
echo -e "  ${GREEN}📚 API文档:${NC} http://localhost:8000/api/docs"
echo ""
print_warning "提示：首次使用请先访问前端页面，在「API配置」中配置OCR和大模型服务"
echo ""
print_info "日志文件："
echo "  - 后端日志: backend.log"
echo "  - 前端日志: frontend.log"
echo ""
print_info "按 Ctrl+C 停止所有服务"
echo ""

# 等待用户中断
wait

