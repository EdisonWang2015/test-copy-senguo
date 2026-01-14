#!/bin/bash
# 前端启动脚本 - 使用Python简易HTTP服务器

echo "================================"
echo "启动前端服务..."
echo "================================"
echo "前端地址: http://127.0.0.1:8000"
echo "按 Ctrl+C 停止服务"
echo ""

cd frontend
python3 -m http.server 8000 --bind 127.0.0.1
