#!/bin/bash
# 测试运行脚本

echo "================================"
echo "运行测试用例"
echo "================================"
echo ""

# 检查虚拟环境
if [ ! -d "venv" ]; then
    echo "📦 创建虚拟环境..."
    python3 -m venv venv
fi

source venv/bin/activate

echo "📚 安装依赖..."
pip install -q -r requirements.txt

echo ""
echo "================================"
echo "运行后端单元测试"
echo "================================"
cd backend
echo "测试接口功能..."
python -m pytest test_api.py -v --tb=short

echo ""
echo "================================"
echo "后端测试完成！"
echo "================================"
echo ""
echo "如需运行UI自动化测试，请确保："
echo "1. 后端服务运行在 http://127.0.0.1:5000"
echo "2. 前端服务运行在 http://127.0.0.1:8000"
echo "3. 已安装 ChromeDriver"
echo ""
echo "运行UI测试命令:"
echo "  cd frontend && python -m pytest test_ui.py -v -s"
echo ""
