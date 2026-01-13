"""
水果蔬菜采购管理系统 - 后端主文件
"""
from flask import Flask, request, jsonify
from flask_cors import CORS
from datetime import datetime
from database import init_database, get_next_order_id, create_order, get_orders, get_order_by_id, update_order, delete_order

app = Flask(__name__)
CORS(app)


# ==================== 启动时初始化数据库 ====================
def initialize_app():
    """应用启动时初始化数据库"""
    try:
        init_database()
        print("=" * 50)
        print("水果蔬菜采购管理系统 - 后端服务")
        print("=" * 50)
        print("数据库: SQLite (testSG.db)")
        print("=" * 50)
    except Exception as e:
        print(f"数据库初始化失败: {e}")


# ==================== API 路由 ====================

@app.route('/api/purchase/create', methods=['POST'])
def create_purchase_order():
    """
    创建采购单接口
    Request Body:
    {
        "factory_name": "加工厂名称",
        "category": "蔬菜" or "水果",
        "farmer_name": "农户名称",
        "harvest_date": "2024-01-15",
        "items": [
            {
                "product_name": "产品名",
                "spec": "规格",
                "quantity": 10,
                "gross_weight": 50,
                "box_weight": 5,
                "unit_price": 22,
                "discount_amount": 0,
                "total_amount": 220
            }
        ],
        "remark": "备注"  // 可选
    }
    """
    try:
        data = request.get_json()

        # 数据验证
        if not data:
            return jsonify({
                'code': 400,
                'message': '请求体不能为空',
                'data': None
            }), 400

        required_fields = ['factory_name', 'category', 'farmer_name', 'harvest_date', 'items']
        missing_fields = [field for field in required_fields if field not in data or data[field] is None]

        if missing_fields:
            return jsonify({
                'code': 400,
                'message': f'缺少必需字段: {", ".join(missing_fields)}',
                'data': None
            }), 400

        # 验证 items 不为空
        items = data.get('items', [])
        if not items or len(items) == 0:
            return jsonify({
                'code': 400,
                'message': '至少需要添加一个货品',
                'data': None
            }), 400

        # 验证每个货品的必需字段
        for idx, item in enumerate(items):
            item_required = ['product_name', 'spec', 'quantity', 'gross_weight', 'box_weight', 'unit_price', 'total_amount']
            item_missing = [f for f in item_required if f not in item or item[f] is None]
            if item_missing:
                return jsonify({
                    'code': 400,
                    'message': f'第{idx + 1}个货品缺少字段: {", ".join(item_missing)}',
                    'data': None
                }), 400

        # 生成订单ID
        order_id = get_next_order_id()

        # 创建采购单数据
        purchase_order = {
            'id': order_id,
            'factory_name': data['factory_name'],
            'category': data['category'],
            'farmer_name': data['farmer_name'],
            'harvest_date': data['harvest_date'],
            'status': '待审批',
            'created_at': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'created_by': data.get('created_by', '系统'),
            'remark': data.get('remark', ''),
            'items': items
        }

        # 保存到数据库
        create_order(purchase_order)

        return jsonify({
            'code': 200,
            'message': '采购单创建成功',
            'data': {
                'order_id': order_id,
                'redirect_url': '/frontend/purchase-list.html'
            }
        }), 201

    except Exception as e:
        return jsonify({
            'code': 500,
            'message': f'服务器错误: {str(e)}',
            'data': None
        }), 500


@app.route('/api/purchase/list', methods=['GET'])
def get_purchase_orders():
    """
    获取采购单列表
    Query Parameters:
    - category: 分类筛选 (可选)
    - status: 状态筛选 (可选)
    """
    try:
        category = request.args.get('category')
        status = request.args.get('status')

        orders = get_orders(category=category, status=status)

        return jsonify({
            'code': 200,
            'message': '获取成功',
            'data': {
                'total': len(orders),
                'orders': orders
            }
        }), 200

    except Exception as e:
        return jsonify({
            'code': 500,
            'message': f'服务器错误: {str(e)}',
            'data': None
        }), 500


@app.route('/api/purchase/<order_id>', methods=['GET'])
def get_purchase_order(order_id):
    """获取单个采购单详情"""
    try:
        order = get_order_by_id(order_id)

        if not order:
            return jsonify({
                'code': 404,
                'message': '采购单不存在',
                'data': None
            }), 404

        return jsonify({
            'code': 200,
            'message': '获取成功',
            'data': order
        }), 200

    except Exception as e:
        return jsonify({
            'code': 500,
            'message': f'服务器错误: {str(e)}',
            'data': None
        }), 500


@app.route('/api/purchase/<order_id>', methods=['PUT'])
def update_purchase_order(order_id):
    """更新采购单状态"""
    try:
        data = request.get_json()

        # 检查订单是否存在
        existing_order = get_order_by_id(order_id)
        if not existing_order:
            return jsonify({
                'code': 404,
                'message': '采购单不存在',
                'data': None
            }), 404

        # 更新订单
        status = data.get('status')
        remark = data.get('remark')

        updated_order = update_order(order_id, status=status, remark=remark)

        return jsonify({
            'code': 200,
            'message': '更新成功',
            'data': updated_order
        }), 200

    except Exception as e:
        return jsonify({
            'code': 500,
            'message': f'服务器错误: {str(e)}',
            'data': None
        }), 500


@app.route('/api/purchase/<order_id>', methods=['DELETE'])
def delete_purchase_order(order_id):
    """删除采购单"""
    try:
        # 检查订单是否存在
        existing_order = get_order_by_id(order_id)
        if not existing_order:
            return jsonify({
                'code': 404,
                'message': '采购单不存在',
                'data': None
            }), 404

        # 删除订单
        delete_order(order_id)

        return jsonify({
            'code': 200,
            'message': '删除成功',
            'data': None
        }), 200

    except Exception as e:
        return jsonify({
            'code': 500,
            'message': f'服务器错误: {str(e)}',
            'data': None
        }), 500


@app.route('/api/health', methods=['GET'])
def health_check():
    """健康检查接口"""
    return jsonify({
        'code': 200,
        'message': 'Service is running',
        'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        'database': 'SQLite'
    }), 200


# ==================== 错误处理 ====================

@app.errorhandler(404)
def not_found(error):
    return jsonify({
        'code': 404,
        'message': '接口不存在',
        'data': None
    }), 404


@app.errorhandler(500)
def internal_error(error):
    return jsonify({
        'code': 500,
        'message': '服务器内部错误',
        'data': None
    }), 500


# ==================== 启动应用 ====================
if __name__ == '__main__':
    # 初始化数据库
    initialize_app()

    print("API 文档:")
    print("  POST   /api/purchase/create  - 创建采购单")
    print("  GET    /api/purchase/list    - 获取采购单列表")
    print("  GET    /api/purchase/<id>    - 获取采购单详情")
    print("  PUT    /api/purchase/<id>    - 更新采购单")
    print("  DELETE /api/purchase/<id>    - 删除采购单")
    print("  GET    /api/health           - 健康检查")
    print("=" * 50)
    print("启动服务: http://127.0.0.1:5000")
    print("=" * 50)

    app.run(debug=True, host='127.0.0.1', port=5000)
