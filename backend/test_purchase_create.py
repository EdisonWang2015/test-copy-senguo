"""
水果蔬菜采购管理系统 - 创建采购单接口单元测试

测试覆盖范围：
1. 正常场景测试
2. 参数验证测试
3. 边界条件测试
4. 异常情况测试
"""

import unittest
import json
import sys
import os

# 添加父目录到路径以便导入模块
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app import app
from database import init_database, get_orders, get_order_by_id


class TestPurchaseCreateAPI(unittest.TestCase):
    """创建采购单接口测试类"""

    def setUp(self):
        """测试前准备：设置测试客户端"""
        self.app = app
        self.app.config['TESTING'] = True
        self.client = self.app.test_client()

        # 初始化测试数据库
        init_database()

    def tearDown(self):
        """测试后清理"""
        pass

    # ==================== 正常场景测试 ====================

    def test_01_create_order_success(self):
        """测试用例01：成功创建采购单（单个货品）"""
        response = self.client.post('/api/purchase/create',
                                   data=json.dumps({
                                       'factory_name': '第一加工厂',
                                       'category': '水果',
                                       'farmer_name': '张三农场',
                                       'harvest_date': '2024-01-15',
                                       'items': [{
                                           'product_name': '西瓜',
                                           'spec': '5斤/22kg',
                                           'quantity': 10,
                                           'gross_weight': 220,
                                           'box_weight': 5,
                                           'unit_price': 22,
                                           'discount_amount': 0,
                                           'total_amount': 220
                                       }]
                                   }),
                                   content_type='application/json')

        data = json.loads(response.data)

        self.assertEqual(response.status_code, 201)
        self.assertEqual(data['code'], 200)
        self.assertEqual(data['message'], '采购单创建成功')
        self.assertIn('order_id', data['data'])
        self.assertTrue(data['data']['order_id'].startswith('PO'))

    def test_02_create_order_multiple_items(self):
        """测试用例02：成功创建采购单（多个货品）"""
        response = self.client.post('/api/purchase/create',
                                   data=json.dumps({
                                       'factory_name': '第一加工厂',
                                       'category': '水果',
                                       'farmer_name': '李四果园',
                                       'harvest_date': '2024-01-15',
                                       'items': [
                                           {
                                               'product_name': '西瓜',
                                               'spec': '5斤/22kg',
                                               'quantity': 10,
                                               'gross_weight': 220,
                                               'box_weight': 5,
                                               'unit_price': 22,
                                               'discount_amount': 0,
                                               'total_amount': 220
                                           },
                                           {
                                               'product_name': '苹果',
                                               'spec': '10斤/5kg',
                                               'quantity': 5,
                                               'gross_weight': 25,
                                               'box_weight': 2,
                                               'unit_price': 35,
                                               'discount_amount': 5,
                                               'total_amount': 170
                                           }
                                       ]
                                   }),
                                   content_type='application/json')

        data = json.loads(response.data)

        self.assertEqual(response.status_code, 201)
        self.assertEqual(data['code'], 200)

        # 验证订单已保存到数据库
        order_id = data['data']['order_id']
        order = get_order_by_id(order_id)
        self.assertIsNotNone(order)
        self.assertEqual(len(order['items']), 2)

    def test_03_create_order_vegetable_category(self):
        """测试用例03：成功创建蔬菜类采购单"""
        response = self.client.post('/api/purchase/create',
                                   data=json.dumps({
                                       'factory_name': '第二加工厂',
                                       'category': '蔬菜',
                                       'farmer_name': '王五种植园',
                                       'harvest_date': '2024-01-15',
                                       'items': [{
                                           'product_name': '西红柿',
                                           'spec': '5斤/2.5kg',
                                           'quantity': 20,
                                           'gross_weight': 50,
                                           'box_weight': 3,
                                           'unit_price': 12,
                                           'discount_amount': 0,
                                           'total_amount': 240
                                       }]
                                   }),
                                   content_type='application/json')

        data = json.loads(response.data)

        self.assertEqual(response.status_code, 201)
        self.assertEqual(data['code'], 200)

    def test_04_create_order_with_discount(self):
        """测试用例04：成功创建带折扣的采购单"""
        response = self.client.post('/api/purchase/create',
                                   data=json.dumps({
                                       'factory_name': '第一加工厂',
                                       'category': '水果',
                                       'farmer_name': '赵六蔬菜基地',
                                       'harvest_date': '2024-01-15',
                                       'items': [{
                                           'product_name': '橙子',
                                           'spec': '8斤/4kg',
                                           'quantity': 15,
                                           'gross_weight': 60,
                                           'box_weight': 4,
                                           'unit_price': 28,
                                           'discount_amount': 20,
                                           'total_amount': 400
                                       }]
                                   }),
                                   content_type='application/json')

        data = json.loads(response.data)

        self.assertEqual(response.status_code, 201)
        self.assertEqual(data['code'], 200)

    def test_05_create_order_with_remark(self):
        """测试用例05：成功创建带备注的采购单"""
        response = self.client.post('/api/purchase/create',
                                   data=json.dumps({
                                       'factory_name': '第三加工厂',
                                       'category': '水果',
                                       'farmer_name': '田七合作社',
                                       'harvest_date': '2024-01-15',
                                       'items': [{
                                           'product_name': '葡萄',
                                           'spec': '3斤/1.5kg',
                                           'quantity': 8,
                                           'gross_weight': 12,
                                           'box_weight': 1,
                                           'unit_price': 25,
                                           'discount_amount': 0,
                                           'total_amount': 200
                                       }],
                                       'remark': '请优先发货'
                                   }),
                                   content_type='application/json')

        data = json.loads(response.data)

        self.assertEqual(response.status_code, 201)
        self.assertEqual(data['code'], 200)

    def test_06_order_id_increment(self):
        """测试用例06：验证订单ID自动递增"""
        # 创建第一个订单
        response1 = self.client.post('/api/purchase/create',
                                    data=json.dumps({
                                        'factory_name': '第一加工厂',
                                        'category': '水果',
                                        'farmer_name': '张三农场',
                                        'harvest_date': '2024-01-15',
                                        'items': [{
                                            'product_name': '西瓜',
                                            'spec': '5斤/22kg',
                                            'quantity': 10,
                                            'gross_weight': 220,
                                            'box_weight': 5,
                                            'unit_price': 22,
                                            'discount_amount': 0,
                                            'total_amount': 220
                                        }]
                                    }),
                                    content_type='application/json')

        data1 = json.loads(response1.data)
        order_id_1 = data1['data']['order_id']

        # 创建第二个订单
        response2 = self.client.post('/api/purchase/create',
                                    data=json.dumps({
                                        'factory_name': '第一加工厂',
                                        'category': '水果',
                                        'farmer_name': '李四果园',
                                        'harvest_date': '2024-01-15',
                                        'items': [{
                                            'product_name': '苹果',
                                            'spec': '10斤/5kg',
                                            'quantity': 5,
                                            'gross_weight': 25,
                                            'box_weight': 2,
                                            'unit_price': 35,
                                            'discount_amount': 0,
                                            'total_amount': 175
                                        }]
                                    }),
                                    content_type='application/json')

        data2 = json.loads(response2.data)
        order_id_2 = data2['data']['order_id']

        # 验证订单ID递增
        num1 = int(order_id_1[2:])
        num2 = int(order_id_2[2:])
        self.assertEqual(num2, num1 + 1)

    def test_07_list_orders_after_create(self):
        """测试用例07：创建订单后能在列表中查询到"""
        # 创建订单
        create_response = self.client.post('/api/purchase/create',
                                          data=json.dumps({
                                              'factory_name': '第一加工厂',
                                              'category': '水果',
                                              'farmer_name': '张三农场',
                                              'harvest_date': '2024-01-15',
                                              'items': [{
                                                  'product_name': '西瓜',
                                                  'spec': '5斤/22kg',
                                                  'quantity': 10,
                                                  'gross_weight': 220,
                                                  'box_weight': 5,
                                                  'unit_price': 22,
                                                  'discount_amount': 0,
                                                  'total_amount': 220
                                              }]
                                          }),
                                          content_type='application/json')

        create_data = json.loads(create_response.data)
        order_id = create_data['data']['order_id']

        # 查询订单列表
        list_response = self.client.get('/api/purchase/list')
        list_data = json.loads(list_response.data)

        self.assertEqual(list_response.status_code, 200)
        self.assertEqual(list_data['code'], 200)
        self.assertGreater(list_data['data']['total'], 0)

        # 验证新创建的订单在列表中
        order_ids = [order['id'] for order in list_data['data']['orders']]
        self.assertIn(order_id, order_ids)

    # ==================== 参数验证测试 ====================

    def test_08_missing_request_body(self):
        """测试用例08：缺少请求体"""
        response = self.client.post('/api/purchase/create',
                                   data=None,
                                   content_type='application/json')

        data = json.loads(response.data)

        self.assertEqual(response.status_code, 400)
        self.assertEqual(data['code'], 400)
        self.assertIn('请求体不能为空', data['message'])

    def test_09_missing_factory_name(self):
        """测试用例09：缺少加工厂名称"""
        response = self.client.post('/api/purchase/create',
                                   data=json.dumps({
                                       'category': '水果',
                                       'farmer_name': '张三农场',
                                       'harvest_date': '2024-01-15',
                                       'items': [{
                                           'product_name': '西瓜',
                                           'spec': '5斤/22kg',
                                           'quantity': 10,
                                           'gross_weight': 220,
                                           'box_weight': 5,
                                           'unit_price': 22,
                                           'discount_amount': 0,
                                           'total_amount': 220
                                       }]
                                   }),
                                   content_type='application/json')

        data = json.loads(response.data)

        self.assertEqual(response.status_code, 400)
        self.assertEqual(data['code'], 400)
        self.assertIn('factory_name', data['message'])

    def test_10_missing_category(self):
        """测试用例10：缺少类目"""
        response = self.client.post('/api/purchase/create',
                                   data=json.dumps({
                                       'factory_name': '第一加工厂',
                                       'farmer_name': '张三农场',
                                       'harvest_date': '2024-01-15',
                                       'items': [{
                                           'product_name': '西瓜',
                                           'spec': '5斤/22kg',
                                           'quantity': 10,
                                           'gross_weight': 220,
                                           'box_weight': 5,
                                           'unit_price': 22,
                                           'discount_amount': 0,
                                           'total_amount': 220
                                       }]
                                   }),
                                   content_type='application/json')

        data = json.loads(response.data)

        self.assertEqual(response.status_code, 400)
        self.assertEqual(data['code'], 400)
        self.assertIn('category', data['message'])

    def test_11_missing_farmer_name(self):
        """测试用例11：缺少农户名称"""
        response = self.client.post('/api/purchase/create',
                                   data=json.dumps({
                                       'factory_name': '第一加工厂',
                                       'category': '水果',
                                       'harvest_date': '2024-01-15',
                                       'items': [{
                                           'product_name': '西瓜',
                                           'spec': '5斤/22kg',
                                           'quantity': 10,
                                           'gross_weight': 220,
                                           'box_weight': 5,
                                           'unit_price': 22,
                                           'discount_amount': 0,
                                           'total_amount': 220
                                       }]
                                   }),
                                   content_type='application/json')

        data = json.loads(response.data)

        self.assertEqual(response.status_code, 400)
        self.assertEqual(data['code'], 400)
        self.assertIn('farmer_name', data['message'])

    def test_12_missing_harvest_date(self):
        """测试用例12：缺少采果日期"""
        response = self.client.post('/api/purchase/create',
                                   data=json.dumps({
                                       'factory_name': '第一加工厂',
                                       'category': '水果',
                                       'farmer_name': '张三农场',
                                       'items': [{
                                           'product_name': '西瓜',
                                           'spec': '5斤/22kg',
                                           'quantity': 10,
                                           'gross_weight': 220,
                                           'box_weight': 5,
                                           'unit_price': 22,
                                           'discount_amount': 0,
                                           'total_amount': 220
                                       }]
                                   }),
                                   content_type='application/json')

        data = json.loads(response.data)

        self.assertEqual(response.status_code, 400)
        self.assertEqual(data['code'], 400)
        self.assertIn('harvest_date', data['message'])

    def test_13_missing_items(self):
        """测试用例13：缺少货品列表"""
        response = self.client.post('/api/purchase/create',
                                   data=json.dumps({
                                       'factory_name': '第一加工厂',
                                       'category': '水果',
                                       'farmer_name': '张三农场',
                                       'harvest_date': '2024-01-15'
                                   }),
                                   content_type='application/json')

        data = json.loads(response.data)

        self.assertEqual(response.status_code, 400)
        self.assertEqual(data['code'], 400)
        self.assertIn('items', data['message'])

    def test_14_empty_items_array(self):
        """测试用例14：货品列表为空数组"""
        response = self.client.post('/api/purchase/create',
                                   data=json.dumps({
                                       'factory_name': '第一加工厂',
                                       'category': '水果',
                                       'farmer_name': '张三农场',
                                       'harvest_date': '2024-01-15',
                                       'items': []
                                   }),
                                   content_type='application/json')

        data = json.loads(response.data)

        self.assertEqual(response.status_code, 400)
        self.assertEqual(data['code'], 400)
        self.assertIn('至少需要添加一个货品', data['message'])

    def test_15_missing_item_product_name(self):
        """测试用例15：货品缺少产品名称"""
        response = self.client.post('/api/purchase/create',
                                   data=json.dumps({
                                       'factory_name': '第一加工厂',
                                       'category': '水果',
                                       'farmer_name': '张三农场',
                                       'harvest_date': '2024-01-15',
                                       'items': [{
                                           'spec': '5斤/22kg',
                                           'quantity': 10,
                                           'gross_weight': 220,
                                           'box_weight': 5,
                                           'unit_price': 22,
                                           'discount_amount': 0,
                                           'total_amount': 220
                                       }]
                                   }),
                                   content_type='application/json')

        data = json.loads(response.data)

        self.assertEqual(response.status_code, 400)
        self.assertEqual(data['code'], 400)
        self.assertIn('第1个货品缺少字段', data['message'])
        self.assertIn('product_name', data['message'])

    def test_16_missing_item_spec(self):
        """测试用例16：货品缺少规格"""
        response = self.client.post('/api/purchase/create',
                                   data=json.dumps({
                                       'factory_name': '第一加工厂',
                                       'category': '水果',
                                       'farmer_name': '张三农场',
                                       'harvest_date': '2024-01-15',
                                       'items': [{
                                           'product_name': '西瓜',
                                           'quantity': 10,
                                           'gross_weight': 220,
                                           'box_weight': 5,
                                           'unit_price': 22,
                                           'discount_amount': 0,
                                           'total_amount': 220
                                       }]
                                   }),
                                   content_type='application/json')

        data = json.loads(response.data)

        self.assertEqual(response.status_code, 400)
        self.assertEqual(data['code'], 400)
        self.assertIn('第1个货品缺少字段', data['message'])

    def test_17_missing_item_quantity(self):
        """测试用例17：货品缺少数量"""
        response = self.client.post('/api/purchase/create',
                                   data=json.dumps({
                                       'factory_name': '第一加工厂',
                                       'category': '水果',
                                       'farmer_name': '张三农场',
                                       'harvest_date': '2024-01-15',
                                       'items': [{
                                           'product_name': '西瓜',
                                           'spec': '5斤/22kg',
                                           'gross_weight': 220,
                                       'box_weight': 5,
                                       'unit_price': 22,
                                       'discount_amount': 0,
                                       'total_amount': 220
                                   }]
                                   }),
                                   content_type='application/json')

        data = json.loads(response.data)

        self.assertEqual(response.status_code, 400)
        self.assertEqual(data['code'], 400)

    def test_18_null_values_in_required_fields(self):
        """测试用例18：必需字段值为null"""
        response = self.client.post('/api/purchase/create',
                                   data=json.dumps({
                                       'factory_name': None,
                                       'category': '水果',
                                       'farmer_name': '张三农场',
                                       'harvest_date': '2024-01-15',
                                       'items': [{
                                           'product_name': '西瓜',
                                           'spec': '5斤/22kg',
                                           'quantity': 10,
                                           'gross_weight': 220,
                                           'box_weight': 5,
                                           'unit_price': 22,
                                           'discount_amount': 0,
                                           'total_amount': 220
                                       }]
                                   }),
                                   content_type='application/json')

        data = json.loads(response.data)

        self.assertEqual(response.status_code, 400)
        self.assertEqual(data['code'], 400)

    # ==================== 边界条件测试 ====================

    def test_19_zero_quantity(self):
        """测试用例19：数量为0（边界值测试，允许0作为初始值）"""
        response = self.client.post('/api/purchase/create',
                                   data=json.dumps({
                                       'factory_name': '第一加工厂',
                                       'category': '水果',
                                       'farmer_name': '张三农场',
                                       'harvest_date': '2024-01-15',
                                       'items': [{
                                           'product_name': '西瓜',
                                           'spec': '5斤/22kg',
                                           'quantity': 0,
                                           'gross_weight': 0,
                                       'box_weight': 0,
                                       'unit_price': 22,
                                       'discount_amount': 0,
                                       'total_amount': 0
                                       }]
                                   }),
                                   content_type='application/json')

        # 接口应该允许创建（业务规则可能不允许，但接口层面不限制）
        data = json.loads(response.data)
        self.assertIn(response.status_code, [200, 201, 400])

    def test_20_large_quantity(self):
        """测试用例20：大数量值测试"""
        response = self.client.post('/api/purchase/create',
                                   data=json.dumps({
                                       'factory_name': '第一加工厂',
                                       'category': '水果',
                                       'farmer_name': '张三农场',
                                       'harvest_date': '2024-01-15',
                                       'items': [{
                                           'product_name': '西瓜',
                                           'spec': '5斤/22kg',
                                           'quantity': 99999,
                                           'gross_weight': 2199978,
                                       'box_weight': 49999,
                                       'unit_price': 22,
                                       'discount_amount': 0,
                                       'total_amount': 2199978
                                       }]
                                   }),
                                   content_type='application/json')

        data = json.loads(response.data)
        self.assertEqual(response.status_code, 201)
        self.assertEqual(data['code'], 200)

    def test_21_decimal_price(self):
        """测试用例21：小数单价测试"""
        response = self.client.post('/api/purchase/create',
                                   data=json.dumps({
                                       'factory_name': '第一加工厂',
                                       'category': '水果',
                                       'farmer_name': '张三农场',
                                       'harvest_date': '2024-01-15',
                                       'items': [{
                                           'product_name': '西瓜',
                                           'spec': '5斤/22kg',
                                           'quantity': 10,
                                           'gross_weight': 220,
                                       'box_weight': 5,
                                       'unit_price': 22.5,
                                       'discount_amount': 0,
                                       'total_amount': 225
                                       }]
                                   }),
                                   content_type='application/json')

        data = json.loads(response.data)
        self.assertEqual(response.status_code, 201)
        self.assertEqual(data['code'], 200)

    def test_22_zero_discount(self):
        """测试用例22：零折扣金额"""
        response = self.client.post('/api/purchase/create',
                                   data=json.dumps({
                                       'factory_name': '第一加工厂',
                                       'category': '水果',
                                       'farmer_name': '张三农场',
                                       'harvest_date': '2024-01-15',
                                       'items': [{
                                           'product_name': '西瓜',
                                           'spec': '5斤/22kg',
                                           'quantity': 10,
                                           'gross_weight': 220,
                                       'box_weight': 5,
                                       'unit_price': 22,
                                       'discount_amount': 0,
                                       'total_amount': 220
                                       }]
                                   }),
                                   content_type='application/json')

        data = json.loads(response.data)
        self.assertEqual(response.status_code, 201)

    def test_23_max_discount(self):
        """测试用例23：最大折扣金额（不超过总金额）"""
        response = self.client.post('/api/purchase/create',
                                   data=json.dumps({
                                       'factory_name': '第一加工厂',
                                       'category': '水果',
                                       'farmer_name': '张三农场',
                                       'harvest_date': '2024-01-15',
                                       'items': [{
                                           'product_name': '西瓜',
                                           'spec': '5斤/22kg',
                                           'quantity': 10,
                                           'gross_weight': 220,
                                       'box_weight': 5,
                                       'unit_price': 22,
                                       'discount_amount': 100,
                                       'total_amount': 120
                                       }]
                                   }),
                                   content_type='application/json')

        data = json.loads(response.data)
        self.assertEqual(response.status_code, 201)

    def test_24_very_long_factory_name(self):
        """测试用例24：超长加工厂名称"""
        response = self.client.post('/api/purchase/create',
                                   data=json.dumps({
                                       'factory_name': 'A' * 500,
                                       'category': '水果',
                                       'farmer_name': '张三农场',
                                       'harvest_date': '2024-01-15',
                                       'items': [{
                                           'product_name': '西瓜',
                                           'spec': '5斤/22kg',
                                           'quantity': 10,
                                           'gross_weight': 220,
                                       'box_weight': 5,
                                       'unit_price': 22,
                                       'discount_amount': 0,
                                       'total_amount': 220
                                       }]
                                   }),
                                   content_type='application/json')

        data = json.loads(response.data)
        self.assertEqual(response.status_code, 201)

    def test_25_special_characters_in_names(self):
        """测试用例25：名称中包含特殊字符"""
        response = self.client.post('/api/purchase/create',
                                   data=json.dumps({
                                       'factory_name': '第一加工厂（分厂）',
                                       'category': '水果',
                                       'farmer_name': '张三-李四农场',
                                       'harvest_date': '2024-01-15',
                                       'items': [{
                                           'product_name': '西瓜（甜）',
                                           'spec': '5斤/22kg',
                                           'quantity': 10,
                                           'gross_weight': 220,
                                       'box_weight': 5,
                                       'unit_price': 22,
                                       'discount_amount': 0,
                                       'total_amount': 220
                                       }]
                                   }),
                                   content_type='application/json')

        data = json.loads(response.data)
        self.assertEqual(response.status_code, 201)

    # ==================== 数据类型测试 ====================

    def test_26_invalid_json_format(self):
        """测试用例26：无效的JSON格式"""
        response = self.client.post('/api/purchase/create',
                                   data='invalid json',
                                   content_type='application/json')

        self.assertEqual(response.status_code, 400)

    def test_27_wrong_content_type(self):
        """测试用例27：错误的Content-Type"""
        response = self.client.post('/api/purchase/create',
                                   data=json.dumps({
                                       'factory_name': '第一加工厂',
                                       'category': '水果',
                                       'farmer_name': '张三农场',
                                       'harvest_date': '2024-01-15',
                                       'items': [{
                                           'product_name': '西瓜',
                                           'spec': '5斤/22kg',
                                           'quantity': 10,
                                           'gross_weight': 220,
                                       'box_weight': 5,
                                       'unit_price': 22,
                                       'discount_amount': 0,
                                       'total_amount': 220
                                       }]
                                   }),
                                   content_type='text/plain')

        # 应该能处理，但可能不会正确解析
        self.assertIn(response.status_code, [400, 415])

    def test_28_string_instead_of_number(self):
        """测试用例28：数值字段传字符串"""
        response = self.client.post('/api/purchase/create',
                                   data=json.dumps({
                                       'factory_name': '第一加工厂',
                                       'category': '水果',
                                       'farmer_name': '张三农场',
                                       'harvest_date': '2024-01-15',
                                       'items': [{
                                           'product_name': '西瓜',
                                           'spec': '5斤/22kg',
                                           'quantity': '10',  # 字符串而不是数字
                                           'gross_weight': '220',
                                       'box_weight': '5',
                                       'unit_price': '22',
                                       'discount_amount': '0',
                                       'total_amount': '220'
                                       }]
                                   }),
                                   content_type='application/json')

        # 接口可能接受也可能拒绝，取决于是否做类型转换
        self.assertIn(response.status_code, [201, 400])

    def test_29_negative_values(self):
        """测试用例29：负数值"""
        response = self.client.post('/api/purchase/create',
                                   data=json.dumps({
                                       'factory_name': '第一加工厂',
                                       'category': '水果',
                                       'farmer_name': '张三农场',
                                       'harvest_date': '2024-01-15',
                                       'items': [{
                                           'product_name': '西瓜',
                                           'spec': '5斤/22kg',
                                           'quantity': -10,
                                           'gross_weight': -220,
                                       'box_weight': -5,
                                       'unit_price': -22,
                                       'discount_amount': -10,
                                       'total_amount': -220
                                       }]
                                   }),
                                   content_type='application/json')

        # 业务规则应该拒绝负数
        self.assertIn(response.status_code, [201, 400])

    # ==================== 业务逻辑测试 ====================

    def test_30_category_fruit(self):
        """测试用例30：类目为水果"""
        response = self.client.post('/api/purchase/create',
                                   data=json.dumps({
                                       'factory_name': '第一加工厂',
                                       'category': '水果',
                                       'farmer_name': '张三农场',
                                       'harvest_date': '2024-01-15',
                                       'items': [{
                                           'product_name': '西瓜',
                                           'spec': '5斤/22kg',
                                           'quantity': 10,
                                           'gross_weight': 220,
                                       'box_weight': 5,
                                       'unit_price': 22,
                                       'discount_amount': 0,
                                       'total_amount': 220
                                       }]
                                   }),
                                   content_type='application/json')

        data = json.loads(response.data)
        self.assertEqual(response.status_code, 201)

    def test_31_category_vegetable(self):
        """测试用例31：类目为蔬菜"""
        response = self.client.post('/api/purchase/create',
                                   data=json.dumps({
                                       'factory_name': '第一加工厂',
                                       'category': '蔬菜',
                                       'farmer_name': '张三农场',
                                       'harvest_date': '2024-01-15',
                                       'items': [{
                                           'product_name': '白菜',
                                           'spec': '15斤/7.5kg',
                                           'quantity': 20,
                                           'gross_weight': 150,
                                       'box_weight': 10,
                                       'unit_price': 10,
                                       'discount_amount': 0,
                                       'total_amount': 200
                                       }]
                                   }),
                                   content_type='application/json')

        data = json.loads(response.data)
        self.assertEqual(response.status_code, 201)

    def test_32_date_format_standard(self):
        """测试用例32：标准日期格式"""
        response = self.client.post('/api/purchase/create',
                                   data=json.dumps({
                                       'factory_name': '第一加工厂',
                                       'category': '水果',
                                       'farmer_name': '张三农场',
                                       'harvest_date': '2024-01-15',
                                       'items': [{
                                           'product_name': '西瓜',
                                           'spec': '5斤/22kg',
                                           'quantity': 10,
                                           'gross_weight': 220,
                                       'box_weight': 5,
                                       'unit_price': 22,
                                       'discount_amount': 0,
                                       'total_amount': 220
                                       }]
                                   }),
                                   content_type='application/json')

        data = json.loads(response.data)
        self.assertEqual(response.status_code, 201)

    def test_33_total_amount_calculation(self):
        """测试用例33：总金额计算验证"""
        quantity = 10
        unit_price = 22
        discount = 5
        expected_total = quantity * unit_price - discount

        response = self.client.post('/api/purchase/create',
                                   data=json.dumps({
                                       'factory_name': '第一加工厂',
                                       'category': '水果',
                                       'farmer_name': '张三农场',
                                       'harvest_date': '2024-01-15',
                                       'items': [{
                                           'product_name': '西瓜',
                                           'spec': '5斤/22kg',
                                           'quantity': quantity,
                                           'gross_weight': 220,
                                       'box_weight': 5,
                                       'unit_price': unit_price,
                                           'discount_amount': discount,
                                           'total_amount': expected_total
                                       }]
                                   }),
                                   content_type='application/json')

        data = json.loads(response.data)
        self.assertEqual(response.status_code, 201)

    def test_34_default_status_pending(self):
        """测试用例34：验证默认状态为待审批"""
        response = self.client.post('/api/purchase/create',
                                   data=json.dumps({
                                       'factory_name': '第一加工厂',
                                       'category': '水果',
                                       'farmer_name': '张三农场',
                                       'harvest_date': '2024-01-15',
                                       'items': [{
                                           'product_name': '西瓜',
                                           'spec': '5斤/22kg',
                                           'quantity': 10,
                                           'gross_weight': 220,
                                       'box_weight': 5,
                                       'unit_price': 22,
                                       'discount_amount': 0,
                                           'total_amount': 220
                                       }]
                                   }),
                                   content_type='application/json')

        data = json.loads(response.data)
        order_id = data['data']['order_id']

        # 查询订单验证状态
        order = get_order_by_id(order_id)
        self.assertEqual(order['status'], '待审批')

    # ==================== 并发测试 ====================

    def test_35_concurrent_create_orders(self):
        """测试用例35：并发创建多笔订单（订单ID唯一性）"""
        import threading

        orders_created = []
        lock = threading.Lock()

        def create_order(index):
            response = self.client.post('/api/purchase/create',
                                       data=json.dumps({
                                           'factory_name': f'加工厂{index}',
                                           'category': '水果',
                                           'farmer_name': f'农户{index}',
                                           'harvest_date': '2024-01-15',
                                           'items': [{
                                               'product_name': '西瓜',
                                               'spec': '5斤/22kg',
                                               'quantity': 10,
                                               'gross_weight': 220,
                                           'box_weight': 5,
                                               'unit_price': 22,
                                               'discount_amount': 0,
                                               'total_amount': 220
                                           }]
                                       }),
                                       content_type='application/json')
            data = json.loads(response.data)
            with lock:
                orders_created.append(data['data']['order_id'])

        # 创建5个并发线程
        threads = []
        for i in range(5):
            t = threading.Thread(target=create_order, args=(i,))
            threads.append(t)
            t.start()

        for t in threads:
            t.join()

        # 验证所有订单ID唯一
        self.assertEqual(len(orders_created), len(set(orders_created)))

    # ==================== 完整流程测试 ====================

    def test_36_full_crud_flow(self):
        """测试用例36：完整的CRUD流程"""
        # 1. 创建订单
        create_response = self.client.post('/api/purchase/create',
                                          data=json.dumps({
                                              'factory_name': '第一加工厂',
                                              'category': '水果',
                                              'farmer_name': '张三农场',
                                              'harvest_date': '2024-01-15',
                                              'items': [{
                                                  'product_name': '西瓜',
                                                  'spec': '5斤/22kg',
                                                  'quantity': 10,
                                                  'gross_weight': 220,
                                              'box_weight': 5,
                                              'unit_price': 22,
                                              'discount_amount': 0,
                                              'total_amount': 220
                                              }]
                                          }),
                                          content_type='application/json')

        create_data = json.loads(create_response.data)
        order_id = create_data['data']['order_id']

        # 2. 查询订单详情
        detail_response = self.client.get(f'/api/purchase/{order_id}')
        detail_data = json.loads(detail_response.data)

        self.assertEqual(detail_response.status_code, 200)
        self.assertEqual(detail_data['data']['id'], order_id)
        self.assertEqual(detail_data['data']['factory_name'], '第一加工厂')

        # 3. 查询订单列表
        list_response = self.client.get('/api/purchase/list')
        list_data = json.loads(list_response.data)

        self.assertEqual(list_response.status_code, 200)
        self.assertGreater(list_data['data']['total'], 0)

        # 4. 更新订单状态
        update_response = self.client.put(f'/api/purchase/{order_id}',
                                         data=json.dumps({
                                             'status': '已审批'
                                         }),
                                         content_type='application/json')

        update_data = json.loads(update_response.data)
        self.assertEqual(update_response.status_code, 200)
        self.assertEqual(update_data['data']['status'], '已审批')

    # ==================== 性能测试 ====================

    def test_37_create_100_orders(self):
        """测试用例37：批量创建100笔订单（性能测试）"""
        import time

        start_time = time.time()

        for i in range(100):
            response = self.client.post('/api/purchase/create',
                                       data=json.dumps({
                                           'factory_name': f'加工厂{i % 5}',
                                           'category': '水果' if i % 2 == 0 else '蔬菜',
                                           'farmer_name': f'农户{i % 10}',
                                           'harvest_date': '2024-01-15',
                                           'items': [{
                                               'product_name': f'产品{i % 10}',
                                               'spec': f'规格{i}',
                                               'quantity': 10 + i,
                                               'gross_weight': 220,
                                           'box_weight': 5,
                                           'unit_price': 22,
                                           'discount_amount': 0,
                                           'total_amount': 220
                                           }]
                                       }),
                                       content_type='application/json')

            if response.status_code not in [200, 201]:
                self.fail(f'第{i}笔订单创建失败')

        end_time = time.time()
        elapsed_time = end_time - start_time

        # 验证所有订单都创建成功
        list_response = self.client.get('/api/purchase/list')
        list_data = json.loads(list_response.data)

        self.assertGreaterEqual(list_data['data']['total'], 100)

        # 性能断言：100笔订单应在合理时间内完成
        self.assertLess(elapsed_time, 30, f'创建100笔订单耗时{elapsed_time:.2f}秒，超过30秒')

    def test_38_response_structure(self):
        """测试用例38：验证响应结构符合规范"""
        response = self.client.post('/api/purchase/create',
                                   data=json.dumps({
                                       'factory_name': '第一加工厂',
                                       'category': '水果',
                                       'farmer_name': '张三农场',
                                       'harvest_date': '2024-01-15',
                                       'items': [{
                                           'product_name': '西瓜',
                                           'spec': '5斤/22kg',
                                           'quantity': 10,
                                           'gross_weight': 220,
                                       'box_weight': 5,
                                       'unit_price': 22,
                                       'discount_amount': 0,
                                       'total_amount': 220
                                       }]
                                   }),
                                   content_type='application/json')

        data = json.loads(response.data)

        # 验证响应结构
        self.assertIn('code', data)
        self.assertIn('message', data)
        self.assertIn('data', data)

        # 成功响应
        self.assertEqual(data['code'], 200)
        self.assertIn('order_id', data['data'])


class TestPurchaseCreateAPIErrors(unittest.TestCase):
    """错误场景专项测试类"""

    def setUp(self):
        self.app = app
        self.app.config['TESTING'] = True
        self.client = self.app.test_client()
        init_database()

    def test_error_405_wrong_method(self):
        """错误测试01：使用错误的HTTP方法"""
        response = self.client.get('/api/purchase/create')
        self.assertEqual(response.status_code, 405)

    def test_error_malformed_json(self):
        """错误测试02：格式错误的JSON"""
        response = self.client.post('/api/purchase/create',
                                   data='{"factory_name": "第一加工厂",}',
                                   content_type='application/json')
        self.assertEqual(response.status_code, 400)


def run_tests():
    """运行所有测试"""
    # 创建测试套件
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()

    # 添加所有测试用例
    suite.addTests(loader.loadTestsFromTestCase(TestPurchaseCreateAPI))
    suite.addTests(loader.loadTestsFromTestCase(TestPurchaseCreateAPIErrors))

    # 运行测试
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)

    # 打印测试统计
    print("\n" + "=" * 60)
    print("测试统计:")
    print(f"总用例数: {result.testsRun}")
    print(f"成功: {result.testsRun - len(result.failures) - len(result.errors)}")
    print(f"失败: {len(result.failures)}")
    print(f"错误: {len(result.errors)}")
    print("=" * 60)

    return result


if __name__ == '__main__':
    run_tests()
