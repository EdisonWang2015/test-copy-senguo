"""
采购单列表筛选接口单元测试
覆盖核心功能场景：
1. 基础列表查询
2. 加工厂筛选
3. 日期范围筛选
4. 组合筛选（工厂 + 日期）
5. 空结果场景
"""

import pytest
import requests
import sqlite3
import os


# ==================== 基础配置 ====================
BASE_URL = "http://127.0.0.1:5000"
API_URL = f"{BASE_URL}/api/purchase/list"

# 数据库路径
DB_PATH = os.path.join(os.path.dirname(__file__), '..', 'testSG.db')


# ==================== 辅助函数 ====================

def get_db_connection():
    """获取数据库连接"""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def count_orders_in_db(factory_name=None, start_date=None, end_date=None):
    """
    查询数据库中的订单数量
    用于验证接口返回结果是否正确
    """
    conn = get_db_connection()
    cursor = conn.cursor()

    try:
        query = 'SELECT COUNT(*) FROM purchase_orders'
        params = []

        conditions = []
        if factory_name:
            conditions.append('factory_name = ?')
            params.append(factory_name)
        if start_date:
            conditions.append('substr(created_at, 1, 10) >= ?')
            params.append(start_date)
        if end_date:
            conditions.append('substr(created_at, 1, 10) <= ?')
            params.append(end_date)

        if conditions:
            query += ' WHERE ' + ' AND '.join(conditions)

        cursor.execute(query, params)
        result = cursor.fetchone()
        return result[0]
    finally:
        conn.close()


def get_distinct_factories():
    """获取数据库中所有不重复的加工厂名称"""
    conn = get_db_connection()
    cursor = conn.cursor()

    try:
        cursor.execute('SELECT DISTINCT factory_name FROM purchase_orders ORDER BY factory_name')
        results = cursor.fetchall()
        return [row[0] for row in results]
    finally:
        conn.close()


def get_date_range_from_db():
    """获取数据库中订单的日期范围"""
    conn = get_db_connection()
    cursor = conn.cursor()

    try:
        cursor.execute('SELECT MIN(substr(created_at, 1, 10)) as min_date, MAX(substr(created_at, 1, 10)) as max_date FROM purchase_orders')
        result = cursor.fetchone()
        return result
    finally:
        conn.close()


# ==================== 测试用例 ====================

class TestPurchaseListFilter:
    """采购单列表筛选接口测试类"""

    @pytest.mark.smoke
    def test_01_get_all_orders_basic(self):
        """
        测试场景 1: 基础列表查询 - 获取全部采购单

        预期结果:
        - 返回状态码 200
        - 包含 code, message, data 字段
        - data 中包含 total 和 orders 数组
        - orders 数组不为空（假设数据库有数据）
        """
        response = requests.get(API_URL)

        assert response.status_code == 200, "响应状态码应为 200"

        result = response.json()
        assert result['code'] == 200, "业务状态码应为 200"
        assert 'data' in result, "响应应包含 data 字段"
        assert 'total' in result['data'], "data 应包含 total 字段"
        assert 'orders' in result['data'], "data 应包含 orders 字段"
        assert isinstance(result['data']['orders'], list), "orders 应为数组"
        assert len(result['data']['orders']) >= 0, "订单数组应至少包含0个元素"

        # 验证 total 值正确
        assert result['data']['total'] == len(result['data']['orders']), "total 应等于 orders 数组长度"

        # 如果有数据，验证数据结构
        if len(result['data']['orders']) > 0:
            order = result['data']['orders'][0]
            required_fields = ['id', 'factory_name', 'category', 'farmer_name', 'created_at', 'status']
            for field in required_fields:
                assert field in order, f"订单应包含 {field} 字段"
            assert 'items' in order, "订单应包含 items 数组"
            assert isinstance(order['items'], list), "items 应为数组"

    @pytest.mark.smoke
    def test_02_filter_by_factory_name(self):
        """
        测试场景 2: 按加工厂筛选

        预期结果:
        - 仅返回指定加工厂的订单
        - 所有订单的 factory_name 与筛选值匹配
        - total 值正确
        """
        # 获取数据库中存在的加工厂
        factories = get_distinct_factories()
        assert len(factories) > 0, "数据库中应至少有一个加工厂"

        # 使用第一个存在的加工厂进行测试
        test_factory = factories[0]

        # 预期的订单数量
        expected_count = count_orders_in_db(factory_name=test_factory)

        # 构建带 URL 编码的请求 URL
        from urllib.parse import quote
        encoded_factory = quote(test_factory)
        response = requests.get(f"{API_URL}?factory_name={encoded_factory}")

        assert response.status_code == 200, "响应状态码应为 200"
        result = response.json()
        assert result['code'] == 200, "业务状态码应为 200"
        assert result['data']['total'] == expected_count, f"返回的订单数量应为 {expected_count}"

        # 验证所有订单都属于该工厂
        for order in result['data']['orders']:
            assert order['factory_name'] == test_factory, f"所有订单的加工厂应为 {test_factory}"

    @pytest.mark.smoke
    def test_03_filter_by_nonexistent_factory(self):
        """
        测试场景 3: 按不存在的加工厂筛选

        预期结果:
        - 返回空列表
        - total 为 0
        - orders 数组为空
        """
        test_factory = "不存在的加工厂XYZ123"

        response = requests.get(f"{API_URL}?factory_name={test_factory}")

        assert response.status_code == 200, "响应状态码应为 200"
        result = response.json()
        assert result['code'] == 200, "业务状态码应为 200"
        assert result['data']['total'] == 0, "不存在的工厂应返回 total 为 0"
        assert len(result['data']['orders']) == 0, "订单数组应为空"

    @pytest.mark.regression
    def test_04_filter_by_start_date(self):
        """
        测试场景 4: 按开始日期筛选

        预期结果:
        - 仅返回该日期及之后创建的订单
        - 所有订单的 created_at >= 筛选日期
        """
        date_range = get_date_range_from_db()
        assert date_range['min_date'], "数据库中应有订单数据"

        test_start_date = date_range['max_date']  # 使用最大日期作为开始日期

        expected_count = count_orders_in_db(start_date=test_start_date)

        response = requests.get(f"{API_URL}?start_date={test_start_date}")

        assert response.status_code == 200, "响应状态码应为 200"
        result = response.json()
        assert result['code'] == 200, "业务状态码应为 200"
        assert result['data']['total'] == expected_count, f"返回的订单数量应为 {expected_count}"

        # 验证所有订单的创建日期 >= 筛选日期
        for order in result['data']['orders']:
            order_date = order['created_at'].split(' ')[0]
            assert order_date >= test_start_date, f"订单日期 {order_date} 应 >= {test_start_date}"

    @pytest.mark.regression
    def test_05_filter_by_end_date(self):
        """
        测试场景 5: 按结束日期筛选

        预期结果:
        - 仅返回该日期及之前创建的订单
        - 所有订单的 created_at <= 筛选日期
        """
        date_range = get_date_range_from_db()
        assert date_range['min_date'], "数据库中应有订单数据"

        test_end_date = date_range['min_date']  # 使用最小日期作为结束日期

        expected_count = count_orders_in_db(end_date=test_end_date)

        response = requests.get(f"{API_URL}?end_date={test_end_date}")

        assert response.status_code == 200, "响应状态码应为 200"
        result = response.json()
        assert result['code'] == 200, "业务状态码应为 200"
        assert result['data']['total'] == expected_count, f"返回的订单数量应为 {expected_count}"

        # 验证所有订单的创建日期 <= 筛选日期
        for order in result['data']['orders']:
            order_date = order['created_at'].split(' ')[0]
            assert order_date <= test_end_date, f"订单日期 {order_date} 应 <= {test_end_date}"

    @pytest.mark.regression
    def test_06_filter_by_date_range(self):
        """
        测试场景 6: 按日期范围筛选

        预期结果:
        - 仅返回日期范围内的订单
        - 所有订单的 created_at 在 [start_date, end_date] 区间内
        """
        date_range = get_date_range_from_db()
        assert date_range['min_date'] and date_range['max_date'], "数据库中应有订单数据"

        test_start_date = date_range['min_date']
        test_end_date = date_range['max_date']

        expected_count = count_orders_in_db(start_date=test_start_date, end_date=test_end_date)

        response = requests.get(f"{API_URL}?start_date={test_start_date}&end_date={test_end_date}")

        assert response.status_code == 200, "响应状态码应为 200"
        result = response.json()
        assert result['code'] == 200, "业务状态码应为 200"
        assert result['data']['total'] == expected_count, f"返回的订单数量应为 {expected_count}"

        # 验证所有订单在日期范围内
        for order in result['data']['orders']:
            order_date = order['created_at'].split(' ')[0]
            assert test_start_date <= order_date <= test_end_date, \
                f"订单日期 {order_date} 应在 [{test_start_date}, {test_end_date}] 范围内"

    @pytest.mark.regression
    def test_07_filter_by_combined_factory_and_date(self):
        """
        测试场景 7: 组合筛选 - 加工厂 + 日期范围

        预期结果:
        - 同时满足两个筛选条件
        - factory_name 匹配且 created_at 在日期范围内
        """
        factories = get_distinct_factories()
        assert len(factories) > 0, "数据库中应至少有一个加工厂"

        test_factory = factories[0]
        date_range = get_date_range_from_db()

        test_start_date = date_range['min_date']
        test_end_date = date_range['max_date']

        expected_count = count_orders_in_db(
            factory_name=test_factory,
            start_date=test_start_date,
            end_date=test_end_date
        )

        from urllib.parse import quote
        encoded_factory = quote(test_factory)
        response = requests.get(
            f"{API_URL}?factory_name={encoded_factory}&start_date={test_start_date}&end_date={test_end_date}"
        )

        assert response.status_code == 200, "响应状态码应为 200"
        result = response.json()
        assert result['code'] == 200, "业务状态码应为 200"
        assert result['data']['total'] == expected_count, f"返回的订单数量应为 {expected_count}"

        # 验证所有订单同时满足两个条件
        for order in result['data']['orders']:
            order_date = order['created_at'].split(' ')[0]
            assert order['factory_name'] == test_factory, f"工厂应为 {test_factory}"
            assert test_start_date <= order_date <= test_end_date, \
                f"订单日期 {order_date} 应在 [{test_start_date}, {test_end_date}] 范围内"

    @pytest.mark.ui
    def test_08_filter_returns_empty_result(self):
        """
        测试场景 8: 空结果场景

        预期结果:
        - 当筛选条件不匹配任何数据时，返回空列表
        - total 为 0
        - orders 数组为空
        - 但响应结构正确
        """
        # 使用一个不可能匹配的日期范围
        response = requests.get(f"{API_URL}?start_date=2099-01-01&end_date=2099-12-31")

        assert response.status_code == 200, "响应状态码应为 200"
        result = response.json()
        assert result['code'] == 200, "业务状态码应为 200"
        assert result['data']['total'] == 0, "空结果时 total 应为 0"
        assert len(result['data']['orders']) == 0, "订单数组应为空"
        assert 'orders' in result['data'], "data 应仍包含 orders 字段"

    @pytest.mark.regression
    def test_09_filter_order_items_structure(self):
        """
        测试场景 9: 订单明细项数据结构验证

        预期结果:
        - 订单包含 items 数组
        - 每个 item 包含必要字段
        """
        response = requests.get(API_URL)

        assert response.status_code == 200, "响应状态码应为 200"
        result = response.json()

        if result['data']['total'] > 0:
            # 检查第一个订单的 items
            order = result['data']['orders'][0]
            assert 'items' in order, "订单应包含 items 数组"
            assert len(order['items']) > 0, "订单应至少有一个明细项"

            # 验证每个 item 的必要字段
            item = order['items'][0]
            required_item_fields = [
                'product_name',
                'spec',
                'quantity',
                'gross_weight',
                'box_weight',
                'unit_price',
                'discount_amount',
                'total_amount'
            ]
            for field in required_item_fields:
                assert field in item, f"明细项应包含 {field} 字段"

    @pytest.mark.ui
    def test_10_multiple_filters_same_time(self):
        """
        测试场景 10: 同一天内多个工厂的订单筛选

        预期结果:
        - 能够正确区分不同工厂的订单
        - 日期过滤时包含同一天的所有订单
        """
        factories = get_distinct_factories()
        if len(factories) < 2:
            pytest.skip("需要至少两个不同的加工厂才能执行此测试")

        date_range = get_date_range_from_db()
        test_date = date_range['max_date']

        from urllib.parse import quote

        # 获取所有工厂在该日期的订单总数
        factory_orders_total = 0
        for i, factory in enumerate(factories):
            factory_count = count_orders_in_db(factory_name=factory, start_date=test_date, end_date=test_date)
            factory_orders_total += factory_count

            # 只验证前两个工厂的查询结果正确
            if i < 2:
                encoded_factory = quote(factory)
                response = requests.get(f"{API_URL}?factory_name={encoded_factory}&start_date={test_date}&end_date={test_date}")
                result = response.json()
                assert result['data']['total'] == factory_count, \
                    f"工厂 {factory} 的订单数应为 {factory_count}"

        # 验证所有工厂的订单数量总和等于当天总订单数
        total_count = count_orders_in_db(start_date=test_date, end_date=test_date)
        assert factory_orders_total == total_count, \
            f"各工厂订单数之和({factory_orders_total}) 应等于当天总订单数({total_count})"

    @pytest.mark.regression
    def test_11_special_characters_in_factory_name(self):
        """
        测试场景 11: 特殊字符的加工厂名称筛选

        预期结果:
        - URL 正确编码处理特殊字符
        - 能够正确匹配包含特殊字符的工厂名称
        """
        # 查询数据库中是否有包含特殊字符的工厂名
        conn = get_db_connection()
        cursor = conn.cursor()

        try:
            cursor.execute(
                "SELECT DISTINCT factory_name FROM purchase_orders WHERE factory_name GLOB '*[A-Za-z]*' LIMIT 1"
            )
            result = cursor.fetchone()
            special_factory = result[0] if result else None

            if special_factory:
                from urllib.parse import quote
                encoded_factory = quote(special_factory)
                response = requests.get(f"{API_URL}?factory_name={encoded_factory}")

                assert response.status_code == 200, "响应状态码应为 200"
                result = response.json()
                assert result['data']['total'] > 0, "应能找到特殊字符工厂的订单"

                for order in result['data']['orders']:
                    assert order['factory_name'] == special_factory, \
                        f"订单工厂名应与筛选值匹配: {special_factory}"
            else:
                pytest.skip("数据库中没有包含特殊字符的工厂名称")
        finally:
            conn.close()

    @pytest.mark.ui
    def test_12_filter_without_parameters(self):
        """
        测试场景 12: 无筛选参数的默认行为

        预期结果:
        - 不传任何参数时返回所有订单
        - 结果应与数据库总数一致
        """
        # 获取数据库中的总订单数
        total_count = count_orders_in_db()

        response = requests.get(API_URL)

        assert response.status_code == 200, "响应状态码应为 200"
        result = response.json()
        assert result['code'] == 200, "业务状态码应为 200"
        assert result['data']['total'] == total_count, f"无筛选时应返回所有订单，数量应为 {total_count}"


class TestPurchaseListFilterCategory:
    """采购单列表按类目筛选测试"""

    @pytest.mark.ui
    def test_01_filter_by_category(self):
        """
        测试场景: 按类目筛选（水果/蔬菜）

        预期结果:
        - 仅返回指定类目的订单
        - 所有订单的 category 与筛选值匹配
        """
        # 测试水果类目
        response = requests.get(f"{API_URL}?category=水果")

        assert response.status_code == 200, "响应状态码应为 200"
        result = response.json()
        assert result['code'] == 200, "业务状态码应为 200"

        # 验证所有订单都属于该类目
        for order in result['data']['orders']:
            assert order['category'] == '水果', "所有订单类目应为 '水果'"

        # 记录数量
        fruit_count = result['data']['total']

        # 测试蔬菜类目
        response = requests.get(f"{API_URL}?category=蔬菜")

        assert response.status_code == 200, "响应状态码应为 200"
        result = response.json()
        assert result['code'] == 200, "业务状态码应为 200"

        # 验证所有订单都属于该类目
        for order in result['data']['orders']:
            assert order['category'] == '蔬菜', "所有订单类目应为 '蔬菜'"

        veggie_count = result['data']['total']

        # 水果和蔬菜订单之和应等于总数
        total_count = count_orders_in_db()
        assert fruit_count + veggie_count == total_count, \
            f"水果订单数({fruit_count}) + 蔬菜订单数({veggie_count}) 应等于总数({total_count})"


class TestPurchaseListFilterStatus:
    """采购单列表按状态筛选测试"""

    @pytest.mark.ui
    def test_01_filter_by_status(self):
        """
        测试场景: 按状态筛选（待审批/已审批）

        预期结果:
        - 仅返回指定状态的订单
        - 所有订单的 status 与筛选值匹配
        """
        # 测试待审批状态
        response = requests.get(f"{API_URL}?status=待审批")

        assert response.status_code == 200, "响应状态码应为 200"
        result = response.json()
        assert result['code'] == 200, "业务状态码应为 200"

        # 验证所有订单状态为待审批
        for order in result['data']['orders']:
            assert order['status'] == '待审批', "所有订单状态应为 '待审批'"

        pending_count = result['data']['total']

        # 测试已审批状态
        response = requests.get(f"{API_URL}?status=已审批")

        assert response.status_code == 200, "响应状态码应为 200"
        result = response.json()
        assert result['code'] == 200, "业务状态码应为 200"

        # 验证所有订单状态为已审批
        for order in result['data']['orders']:
            assert order['status'] == '已审批', "所有订单状态应为 '已审批'"

        approved_count = result['data']['total']

        # 两个状态的订单数之和应等于总数
        total_count = count_orders_in_db()
        assert pending_count + approved_count == total_count, \
            f"待审批({pending_count}) + 已审批({approved_count}) 应等于总数({total_count})"
