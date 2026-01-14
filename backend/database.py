"""
数据库模块 - SQLite数据库初始化和操作
"""
import sqlite3
import os
from datetime import datetime

# 数据库文件路径
DB_PATH = os.path.join(os.path.dirname(__file__), '..', 'testSG.db')


def get_db_connection():
    """获取数据库连接"""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_database():
    """初始化数据库表"""
    conn = get_db_connection()
    cursor = conn.cursor()

    try:
        # 创建采购单表
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS purchase_orders (
                id TEXT PRIMARY KEY,
                factory_name TEXT NOT NULL,
                category TEXT NOT NULL,
                farmer_name TEXT NOT NULL,
                harvest_date TEXT NOT NULL,
                status TEXT NOT NULL DEFAULT '待审批',
                created_at TEXT NOT NULL,
                created_by TEXT NOT NULL DEFAULT '系统',
                total_amount REAL NOT NULL DEFAULT 0,
                remark TEXT DEFAULT ''
            )
        ''')

        # 创建采购单明细表（用于存储多个采购项）
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS purchase_items (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                order_id TEXT NOT NULL,
                product_name TEXT NOT NULL,
                spec TEXT NOT NULL,
                quantity REAL NOT NULL,
                gross_weight REAL NOT NULL,
                box_weight REAL NOT NULL,
                unit_price REAL NOT NULL,
                discount_amount REAL NOT NULL,
                total_amount REAL NOT NULL,
                FOREIGN KEY (order_id) REFERENCES purchase_orders(id) ON DELETE CASCADE
            )
        ''')

        # 创建索引
        cursor.execute('''
            CREATE INDEX IF NOT EXISTS idx_purchase_orders_category
            ON purchase_orders(category)
        ''')
        cursor.execute('''
            CREATE INDEX IF NOT EXISTS idx_purchase_orders_status
            ON purchase_orders(status)
        ''')
        cursor.execute('''
            CREATE INDEX IF NOT EXISTS idx_purchase_orders_date
            ON purchase_orders(created_at)
        ''')

        conn.commit()
        print("✓ 数据库初始化成功")
        print(f"✓ 数据库位置: {os.path.abspath(DB_PATH)}")

    except sqlite3.Error as e:
        print(f"✗ 数据库初始化失败: {e}")
        raise
    finally:
        conn.close()


def get_next_order_id():
    """获取下一个订单ID"""
    conn = get_db_connection()
    cursor = conn.cursor()

    try:
        cursor.execute('SELECT id FROM purchase_orders ORDER BY id DESC LIMIT 1')
        result = cursor.fetchone()

        if result:
            # 提取数字部分并递增
            last_id = result['id']  # PO1001
            if last_id.startswith('PO'):
                num = int(last_id[2:]) + 1
                return f"PO{num}"
            else:
                return "PO1001"
        else:
            return "PO1001"

    except sqlite3.Error as e:
        print(f"获取订单ID失败: {e}")
        return "PO1001"
    finally:
        conn.close()


# 数据库操作函数
def create_order(order_data):
    """创建采购单"""
    conn = get_db_connection()
    cursor = conn.cursor()

    try:
        # 计算总金额
        total_amount = sum(item.get('total_amount', 0) for item in order_data['items'])

        cursor.execute('''
            INSERT INTO purchase_orders
            (id, factory_name, category, farmer_name, harvest_date, status, created_at, created_by, total_amount, remark)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            order_data['id'],
            order_data['factory_name'],
            order_data['category'],
            order_data['farmer_name'],
            order_data['harvest_date'],
            order_data.get('status', '待审批'),
            order_data['created_at'],
            order_data.get('created_by', '系统'),
            total_amount,
            order_data.get('remark', '')
        ))

        # 插入明细项
        if 'items' in order_data and order_data['items']:
            for item in order_data['items']:
                cursor.execute('''
                    INSERT INTO purchase_items (order_id, product_name, spec, quantity, gross_weight, box_weight, unit_price, discount_amount, total_amount)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', (
                    order_data['id'],
                    item['product_name'],
                    item['spec'],
                    item['quantity'],
                    item['gross_weight'],
                    item['box_weight'],
                    item['unit_price'],
                    item['discount_amount'],
                    item['total_amount']
                ))

        conn.commit()
        return order_data['id']

    except sqlite3.Error as e:
        conn.rollback()
        raise e
    finally:
        conn.close()


def get_orders(category=None, status=None, factory_name=None, start_date=None, end_date=None):
    """
    获取采购单列表
    Args:
        category: 类目筛选 (可选)
        status: 状态筛选 (可选)
        factory_name: 加工厂筛选 (可选)
        start_date: 开始日期 (可选)
        end_date: 结束日期 (可选)
    """
    conn = get_db_connection()
    cursor = conn.cursor()

    try:
        query = 'SELECT * FROM purchase_orders'
        params = []

        conditions = []
        if category:
            conditions.append('category = ?')
            params.append(category)
        if status:
            conditions.append('status = ?')
            params.append(status)
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

        query += ' ORDER BY created_at DESC'

        cursor.execute(query, params)
        rows = cursor.fetchall()

        orders = []
        for row in rows:
            order = dict(row)
            # 获取明细项
            cursor.execute('SELECT product_name, spec, quantity, gross_weight, box_weight, unit_price, discount_amount, total_amount FROM purchase_items WHERE order_id = ?', (order['id'],))
            items = [dict(row) for row in cursor.fetchall()]
            order['items'] = items
            orders.append(order)

        return orders

    except sqlite3.Error as e:
        raise e
    finally:
        conn.close()


def get_order_by_id(order_id):
    """获取单个采购单"""
    conn = get_db_connection()
    cursor = conn.cursor()

    try:
        cursor.execute('SELECT * FROM purchase_orders WHERE id = ?', (order_id,))
        row = cursor.fetchone()

        if row:
            order = dict(row)
            # 获取明细项
            cursor.execute('SELECT product_name, spec, quantity, gross_weight, box_weight, unit_price, discount_amount, total_amount FROM purchase_items WHERE order_id = ?', (order_id,))
            items = [dict(row) for row in cursor.fetchall()]
            order['items'] = items
            return order
        return None

    except sqlite3.Error as e:
        raise e
    finally:
        conn.close()


def update_order(order_id, status=None, remark=None):
    """更新采购单"""
    conn = get_db_connection()
    cursor = conn.cursor()

    try:
        updates = []
        params = []

        if status is not None:
            updates.append('status = ?')
            params.append(status)
        if remark is not None:
            updates.append('remark = ?')
            params.append(remark)

        if updates:
            params.append(order_id)
            cursor.execute(f'''
                UPDATE purchase_orders
                SET {', '.join(updates)}
                WHERE id = ?
            ''', params)
            conn.commit()

        return get_order_by_id(order_id)

    except sqlite3.Error as e:
        conn.rollback()
        raise e
    finally:
        conn.close()


def delete_order(order_id):
    """删除采购单"""
    conn = get_db_connection()
    cursor = conn.cursor()

    try:
        # 先删除明细项
        cursor.execute('DELETE FROM purchase_items WHERE order_id = ?', (order_id,))
        # 再删除主订单
        cursor.execute('DELETE FROM purchase_orders WHERE id = ?', (order_id,))
        conn.commit()
        return True

    except sqlite3.Error as e:
        conn.rollback()
        raise e
    finally:
        conn.close()


if __name__ == '__main__':
    # 测试数据库初始化
    init_database()
