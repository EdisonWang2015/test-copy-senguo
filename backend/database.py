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
                supplier_name TEXT NOT NULL,
                product_name TEXT NOT NULL,
                quantity INTEGER NOT NULL,
                unit_price REAL NOT NULL,
                total_amount REAL NOT NULL,
                category TEXT NOT NULL,
                status TEXT NOT NULL DEFAULT '待审批',
                created_at TEXT NOT NULL,
                created_by TEXT NOT NULL DEFAULT '系统',
                remark TEXT DEFAULT ''
            )
        ''')

        # 创建采购单明细表（用于存储多个采购项）
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS purchase_items (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                order_id TEXT NOT NULL,
                item_name TEXT NOT NULL,
                spec TEXT NOT NULL,
                price REAL NOT NULL,
                amount REAL NOT NULL,
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
        cursor.execute('''
            INSERT INTO purchase_orders
            (id, supplier_name, product_name, quantity, unit_price, total_amount, category, status, created_at, created_by, remark)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            order_data['id'],
            order_data['supplier_name'],
            order_data['product_name'],
            order_data['quantity'],
            order_data['unit_price'],
            order_data['total_amount'],
            order_data['category'],
            order_data['status'],
            order_data['created_at'],
            order_data['created_by'],
            order_data['remark']
        ))

        # 如果有明细项，插入明细表
        if 'items' in order_data and order_data['items']:
            for item in order_data['items']:
                cursor.execute('''
                    INSERT INTO purchase_items (order_id, item_name, spec, price, amount)
                    VALUES (?, ?, ?, ?, ?)
                ''', (
                    order_data['id'],
                    item['name'],
                    item['spec'],
                    item['price'],
                    item['amount']
                ))

        conn.commit()
        return order_data['id']

    except sqlite3.Error as e:
        conn.rollback()
        raise e
    finally:
        conn.close()


def get_orders(category=None, status=None):
    """获取采购单列表"""
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

        if conditions:
            query += ' WHERE ' + ' AND '.join(conditions)

        query += ' ORDER BY created_at DESC'

        cursor.execute(query, params)
        rows = cursor.fetchall()

        orders = []
        for row in rows:
            order = dict(row)
            # 获取明细项
            cursor.execute('SELECT item_name as name, spec, price, amount FROM purchase_items WHERE order_id = ?', (order['id'],))
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
            cursor.execute('SELECT item_name as name, spec, price, amount FROM purchase_items WHERE order_id = ?', (order_id,))
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
