#!/bin/bash

# 日志查看脚本 - 李会计凭证识别系统

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

LOG_DIR="./backend/logs"

# 检查日志目录是否存在
if [ ! -d "$LOG_DIR" ]; then
    echo -e "${RED}错误: 日志目录不存在 ($LOG_DIR)${NC}"
    echo "请先启动服务以生成日志文件"
    exit 1
fi

# 显示菜单
show_menu() {
    echo ""
    echo -e "${GREEN}========================================${NC}"
    echo -e "${GREEN}  日志查看工具${NC}"
    echo -e "${GREEN}========================================${NC}"
    echo ""
    echo -e "${CYAN}请选择要查看的日志类型:${NC}"
    echo ""
    echo "  1) 所有日志 (app.log)"
    echo "  2) 错误日志 (error.log)"
    echo "  3) 请求日志 (request.log)"
    echo "  4) OCR日志 (ocr.log)"
    echo "  5) LLM日志 (llm.log)"
    echo "  6) 查看所有日志文件"
    echo "  7) 清理旧日志"
    echo "  0) 退出"
    echo ""
}

# 实时查看日志
view_log() {
    local log_file=$1
    local log_name=$2
    
    if [ ! -f "$log_file" ]; then
        echo -e "${YELLOW}日志文件不存在: $log_file${NC}"
        echo "等待日志文件生成..."
        # 等待文件创建
        while [ ! -f "$log_file" ]; do
            sleep 1
        done
    fi
    
    echo ""
    echo -e "${GREEN}正在查看: $log_name${NC}"
    echo -e "${CYAN}按 Ctrl+C 退出${NC}"
    echo ""
    echo "----------------------------------------"
    
    # 显示最后20行，然后实时跟踪
    tail -n 20 "$log_file" 2>/dev/null || echo "文件为空"
    echo "----------------------------------------"
    echo ""
    tail -f "$log_file" 2>/dev/null
}

# 查看所有日志文件
view_all_files() {
    echo ""
    echo -e "${GREEN}日志文件列表:${NC}"
    echo ""
    
    for file in "$LOG_DIR"/*.log; do
        if [ -f "$file" ]; then
            filename=$(basename "$file")
            size=$(du -h "$file" | cut -f1)
            lines=$(wc -l < "$file" 2>/dev/null || echo "0")
            echo -e "  ${CYAN}$filename${NC} - 大小: $size, 行数: $lines"
        fi
    done
    
    echo ""
    read -p "按回车键继续..."
}

# 清理旧日志
clean_logs() {
    echo ""
    echo -e "${YELLOW}警告: 这将删除所有日志文件！${NC}"
    read -p "确定要继续吗？(y/N): " confirm
    
    if [ "$confirm" = "y" ] || [ "$confirm" = "Y" ]; then
        rm -f "$LOG_DIR"/*.log*
        echo -e "${GREEN}日志文件已清理${NC}"
    else
        echo "操作已取消"
    fi
    
    echo ""
    read -p "按回车键继续..."
}

# 主循环
while true; do
    show_menu
    read -p "请选择 [0-7]: " choice
    
    case $choice in
        1)
            view_log "$LOG_DIR/app.log" "所有日志"
            ;;
        2)
            view_log "$LOG_DIR/error.log" "错误日志"
            ;;
        3)
            view_log "$LOG_DIR/request.log" "请求日志"
            ;;
        4)
            view_log "$LOG_DIR/ocr.log" "OCR日志"
            ;;
        5)
            view_log "$LOG_DIR/llm.log" "LLM日志"
            ;;
        6)
            view_all_files
            ;;
        7)
            clean_logs
            ;;
        0)
            echo -e "${GREEN}退出${NC}"
            exit 0
            ;;
        *)
            echo -e "${RED}无效选择，请重试${NC}"
            sleep 1
            ;;
    esac
done

