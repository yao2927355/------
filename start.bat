@echo off
chcp 65001 >nul
setlocal enabledelayedexpansion

REM 李会计凭证识别系统 - Windows一键启动脚本

echo.
echo ========================================
echo   李会计凭证识别系统 - 一键启动
echo ========================================
echo.

REM 检查Python
echo [检查] Python环境...
python --version >nul 2>&1
if errorlevel 1 (
    echo [错误] 未找到 Python，请先安装 Python 3.11+
    pause
    exit /b 1
)
for /f "tokens=2" %%i in ('python --version 2^>^&1') do set PYTHON_VERSION=%%i
echo [成功] Python版本: %PYTHON_VERSION%

REM 检查Node.js
echo [检查] Node.js环境...
node --version >nul 2>&1
if errorlevel 1 (
    echo [错误] 未找到 Node.js，请先安装 Node.js 18+
    pause
    exit /b 1
)
for /f %%i in ('node --version') do set NODE_VERSION=%%i
echo [成功] Node.js版本: %NODE_VERSION%

REM 检查npm
npm --version >nul 2>&1
if errorlevel 1 (
    echo [错误] 未找到 npm
    pause
    exit /b 1
)

echo.

REM ============ 后端启动 ============
echo [准备] 后端服务...

cd backend

REM 创建虚拟环境
if not exist "venv" (
    echo [创建] Python虚拟环境...
    python -m venv venv
    echo [成功] 虚拟环境创建成功
)

REM 激活虚拟环境
echo [激活] 虚拟环境...
call venv\Scripts\activate.bat

REM 安装依赖
if not exist "venv\.deps_installed" (
    echo [安装] Python依赖（首次运行，可能需要几分钟）...
    python -m pip install --upgrade pip -q
    pip install -r requirements.txt -q
    type nul > venv\.deps_installed
    echo [成功] 依赖安装完成
) else (
    echo [检查] 依赖更新...
    pip install -r requirements.txt -q --upgrade
)

REM 创建上传目录
if not exist "uploads" mkdir uploads

REM 启动后端
echo [启动] 后端服务 (端口: 8000)...
start "后端服务" cmd /c "uvicorn app.main:app --host 0.0.0.0 --port 8000"

REM 等待后端启动
echo [等待] 后端服务启动...
timeout /t 5 /nobreak >nul

cd ..

REM ============ 前端启动 ============
echo [准备] 前端服务...

cd frontend

REM 安装依赖
if not exist "node_modules" (
    echo [安装] Node.js依赖（首次运行，可能需要几分钟）...
    call npm install
    echo [成功] 依赖安装完成
) else (
    echo [检查] 依赖更新...
    call npm install
)

REM 启动前端
echo [启动] 前端服务 (端口: 3000)...
start "前端服务" cmd /c "npm run dev"

cd ..

REM ============ 显示结果 ============
echo.
echo ========================================
echo   所有服务已启动！
echo ========================================
echo.
echo   🌐 前端地址: http://localhost:3000
echo   🔧 后端地址: http://localhost:8000
echo   📚 API文档: http://localhost:8000/api/docs
echo.
echo [提示] 首次使用请先访问前端页面，在「API配置」中配置OCR和大模型服务
echo.
echo [说明] 服务已在独立窗口中运行，关闭窗口即可停止对应服务
echo.
pause

