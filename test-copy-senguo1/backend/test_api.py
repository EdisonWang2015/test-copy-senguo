"""
后端单元测试 - 采购单接口测试
使用 pytest 框架
"""
import pytest
import json
import sys
import os

# 添加后端路径
sys.path.insert(0, os.path.dirname(__file__))

from app import app, PURCHASE_ORDERS


@pytest.fixture
def client():
    """创建测试客户端"""
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client
    # 清空测试数据
    PURCHASE_ORDERS.clear()


@pytest.fixture
def sample_order_data():
    """示例采购单数据"""
    return {
        'supplier_name': '测试供应商',
        'product_name': '苹果',
        'quantity': 100,
        'unit_price': 5.5,
        'category': '水果',
        'remark': '测试备注'
    }


class TestHealthCheck:
    """健康检查测试"""
    
    def test_health_check(self, client):
        """测试健康检查接口"""
        response = client.get('/api/health')
        assert response.status_code == 200
        
        data = json.loads(response.data)
        assert data['code'] == 200
        assert 'timestamp' in data


class TestCreatePurchaseOrder:
    """创建采购单测试"""
    
    def test_create_purchase_order_success(self, client, sample_order_data):
        """测试成功创建采购单"""
        response = client.post(
            '/api/purchase/create',
            data=json.dumps(sample_order_data),
            content_type='application/json'
        )
        
        assert response.status_code == 201
        data = json.loads(response.data)
        assert data['code'] == 200
        assert data['message'] == '采购单创建成功'
        assert 'id' in data['data']
        assert data['data']['supplier_name'] == '测试供应商'
        assert data['data']['product_name'] == '苹果'
        assert data['data']['quantity'] == 100
        assert data['data']['unit_price'] == 5.5
        assert data['data']['total_amount'] == 550.0
        assert data['data']['status'] == '待审批'
    
    def test_create_purchase_order_missing_fields(self, client):
        """测试缺少必需字段"""
        incomplete_data = {
            'supplier_name': '测试供应商',
            'product_name': '苹果'
            # 缺少 quantity, unit_price, category
        }
        
        response = client.post(
            '/api/purchase/create',
            data=json.dumps(incomplete_data),
            content_type='application/json'
        )
        
        assert response.status_code == 400
        data = json.loads(response.data)
        assert data['code'] == 400
        assert '缺少必需字段' in data['message']
    
    def test_create_purchase_order_invalid_quantity(self, client, sample_order_data):
        """测试无效的数量"""
        sample_order_data['quantity'] = -10
        
        response = client.post(
            '/api/purchase/create',
            data=json.dumps(sample_order_data),
            content_type='application/json'
        )
        
        assert response.status_code == 400
        data = json.loads(response.data)
        assert data['code'] == 400
    
    def test_create_purchase_order_invalid_price(self, client, sample_order_data):
        """测试无效的单价"""
        sample_order_data['unit_price'] = 'invalid'
        
        response = client.post(
            '/api/purchase/create',
            data=json.dumps(sample_order_data),
            content_type='application/json'
        )
        
        assert response.status_code == 400
        data = json.loads(response.data)
        assert data['code'] == 400
    
    def test_create_purchase_order_empty_body(self, client):
        """测试空请求体"""
        response = client.post(
            '/api/purchase/create',
            data=json.dumps({}),
            content_type='application/json'
        )
        
        # 空对象应该被当作缺少必需字段处理
        assert response.status_code == 400


class TestGetPurchaseOrders:
    """获取采购单列表测试"""
    
    def test_get_purchase_orders_empty(self, client):
        """测试获取空列表"""
        response = client.get('/api/purchase/list')
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['code'] == 200
        assert data['data']['total'] == 0
        assert data['data']['orders'] == []
    
    def test_get_purchase_orders_with_data(self, client, sample_order_data):
        """测试获取有数据的列表"""
        # 创建几个采购单
        client.post(
            '/api/purchase/create',
            data=json.dumps(sample_order_data),
            content_type='application/json'
        )
        
        sample_order_data['product_name'] = '香蕉'
        client.post(
            '/api/purchase/create',
            data=json.dumps(sample_order_data),
            content_type='application/json'
        )
        
        response = client.get('/api/purchase/list')
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['code'] == 200
        assert data['data']['total'] == 2
    
    def test_get_purchase_orders_filter_by_category(self, client, sample_order_data):
        """测试按分类筛选"""
        client.post(
            '/api/purchase/create',
            data=json.dumps(sample_order_data),
            content_type='application/json'
        )
        
        sample_order_data['category'] = '蔬菜'
        sample_order_data['product_name'] = '白菜'
        client.post(
            '/api/purchase/create',
            data=json.dumps(sample_order_data),
            content_type='application/json'
        )
        
        response = client.get('/api/purchase/list?category=蔬菜')
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['data']['total'] == 1
        assert data['data']['orders'][0]['category'] == '蔬菜'


class TestGetSingleOrder:
    """获取单个采购单详情测试"""
    
    def test_get_single_order_success(self, client, sample_order_data):
        """测试成功获取采购单详情"""
        # 先创建一个采购单
        create_response = client.post(
            '/api/purchase/create',
            data=json.dumps(sample_order_data),
            content_type='application/json'
        )
        
        order_id = json.loads(create_response.data)['data']['id']
        
        # 获取详情
        response = client.get(f'/api/purchase/{order_id}')
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['code'] == 200
        assert data['data']['id'] == order_id
    
    def test_get_nonexistent_order(self, client):
        """测试获取不存在的采购单"""
        response = client.get('/api/purchase/PO99999')
        
        assert response.status_code == 404
        data = json.loads(response.data)
        assert data['code'] == 404


class TestUpdateOrder:
    """更新采购单测试"""
    
    def test_update_order_status(self, client, sample_order_data):
        """测试更新采购单状态"""
        # 创建采购单
        create_response = client.post(
            '/api/purchase/create',
            data=json.dumps(sample_order_data),
            content_type='application/json'
        )
        
        order_id = json.loads(create_response.data)['data']['id']
        
        # 更新状态
        update_data = {'status': '已批准'}
        response = client.put(
            f'/api/purchase/{order_id}',
            data=json.dumps(update_data),
            content_type='application/json'
        )
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['code'] == 200
        assert data['data']['status'] == '已批准'


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
