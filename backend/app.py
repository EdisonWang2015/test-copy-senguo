"""
水果蔬菜采购管理系统 - 后端主文件
"""
from flask import Flask, request, jsonify
from flask_cors import CORS
from datetime import datetime
import json

app = Flask(__name__)
CORS(app)

# ==================== 模拟数据 ====================
PURCHASE_ORDERS = []
ORDER_COUNTER = 1000


# ==================== API 路由 ====================

@app.route('/api/purchase/create', methods=['POST'])
def create_purchase_order():
    """
    创建采购单接口
    Request Body:
    {
        "supplier_name": "供应商名称",
        "product_name": "产品名称",
        "quantity": 100,
        "unit_price": 10.5,
        "category": "蔬菜" or "水果"
    }
    """
    try:
        global ORDER_COUNTER
        
        data = request.get_json()
        
        # 数据验证
        if not data:
            return jsonify({
                'code': 400,
                'message': '请求体不能为空',
                'data': None
            }), 400
        
        required_fields = ['supplier_name', 'product_name', 'quantity', 'unit_price', 'category']
        missing_fields = [field for field in required_fields if field not in data or data[field] is None]
        
        if missing_fields:
            return jsonify({
                'code': 400,
                'message': f'缺少必需字段: {", ".join(missing_fields)}',
                'data': None
            }), 400
        
        # 参数验证
        try:
            quantity = int(data['quantity'])
            unit_price = float(data['unit_price'])
            
            if quantity <= 0:
                raise ValueError('数量必须大于0')
            if unit_price < 0:
                raise ValueError('单价不能为负数')
        except (ValueError, TypeError) as e:
            return jsonify({
                'code': 400,
                'message': f'参数验证失败: {str(e)}',
                'data': None
            }), 400
        
        # 创建采购单
        ORDER_COUNTER += 1
        order_id = f"PO{ORDER_COUNTER}"
        total_amount = quantity * unit_price
        
        purchase_order = {
            'id': order_id,
            'supplier_name': data['supplier_name'],
            'product_name': data['product_name'],
            'quantity': quantity,
            'unit_price': unit_price,
            'total_amount': round(total_amount, 2),
            'category': data['category'],
            'status': '待审批',
            'created_at': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'created_by': data.get('created_by', '系统'),
            'remark': data.get('remark', '')
        }
        
        PURCHASE_ORDERS.append(purchase_order)
        
        return jsonify({
            'code': 200,
            'message': '采购单创建成功',
            'data': purchase_order
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
        
        filtered_orders = PURCHASE_ORDERS
        
        if category:
            filtered_orders = [order for order in filtered_orders if order['category'] == category]
        
        if status:
            filtered_orders = [order for order in filtered_orders if order['status'] == status]
        
        return jsonify({
            'code': 200,
            'message': '获取成功',
            'data': {
                'total': len(filtered_orders),
                'orders': filtered_orders
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
        order = next((o for o in PURCHASE_ORDERS if o['id'] == order_id), None)
        
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
        
        order = next((o for o in PURCHASE_ORDERS if o['id'] == order_id), None)
        if not order:
            return jsonify({
                'code': 404,
                'message': '采购单不存在',
                'data': None
            }), 404
        
        if 'status' in data:
            order['status'] = data['status']
        if 'remark' in data:
            order['remark'] = data['remark']
        
        return jsonify({
            'code': 200,
            'message': '更新成功',
            'data': order
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
        'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
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


if __name__ == '__main__':
    print("=" * 50)
    print("水果蔬菜采购管理系统 - 后端服务")
    print("=" * 50)
    print("API 文档:")
    print("  POST   /api/purchase/create  - 创建采购单")
    print("  GET    /api/purchase/list    - 获取采购单列表")
    print("  GET    /api/purchase/<id>    - 获取采购单详情")
    print("  PUT    /api/purchase/<id>    - 更新采购单")
    print("  GET    /api/health           - 健康检查")
    print("=" * 50)
    print("启动服务: http://127.0.0.1:5000")
    print("=" * 50)
    app.run(debug=True, host='127.0.0.1', port=5000)
