#!/bin/bash
# 一键启动脚本 - 水果蔬菜采购管理系统

echo "================================"
echo "水果蔬菜采购管理系统"
echo "================================"
echo ""

# 检查Python
if ! command -v python3 &> /dev/null; then
    echo "❌ 错误: 未找到Python3"
    exit 1
fi

echo "✓ Python版本: $(python3 --version)"
echo ""

# 创建虚拟环境（如果不存在）
if [ ! -d "venv" ]; then
    echo "📦 创建虚拟环境..."
    python3 -m venv venv
fi

# 激活虚拟环境
echo "🔧 激活虚拟环境..."
source venv/bin/activate

# 安装依赖
echo "📚 安装依赖..."
pip install -q -r requirements.txt

echo ""
echo "================================"
echo "启动后端服务..."
echo "================================"
echo "后端地址: http://127.0.0.1:5000"
echo "前端地址: http://127.0.0.1:8000 (需要单独启动)"
echo "按 Ctrl+C 停止服务"
echo ""

# 启动后端
cd backend
python app.py
