"""
新建采购单功能 - 综合测试用例
包含：正向测试、边界测试、负向测试、数据验证测试
"""

import pytest
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
import time


class TestPurchaseCreationComprehensive:
    """新建采购单综合测试类"""

    # ==================== 正向测试用例 ====================

    @pytest.mark.smoke
    def test_create_single_product_order(self, driver, base_url, page_helper):
        """测试创建单个货品的采购单"""
        page_helper.open_page('purchase-create.html')

        # 选择加工厂
        self._select_factory(driver, page_helper, '第一加工厂')
        time.sleep(0.5)
        # 选择类目
        self._select_category(driver, page_helper, '水果')
        time.sleep(0.5)
        # 选择农户
        self._select_farmer(driver, page_helper, '张三农场')
        time.sleep(0.5)

        # 验证添加货品按钮可点击
        add_btn = driver.find_element(By.CSS_SELECTOR, 'button.add-product-btn')
        assert add_btn.is_enabled(), "添加货品按钮应该可点击"

        # 添加货品
        self._add_product_with_keyboard(
            driver, page_helper,
            quantity='10',
            gross_weight='220',
            box_weight='5',
            unit_price='22'
        )

        # 验证提交按钮可点击
        submit_btn = driver.find_element(By.ID, 'submitBtn')
        assert submit_btn.get_attribute('disabled') is None, "填写完整信息后提交按钮应该可点击"

    @pytest.mark.regression
    def test_create_multiple_products_order(self, driver, base_url, page_helper):
        """测试创建多个货品的采购单"""
        page_helper.open_page('purchase-create.html')

        # 填写基本信息
        self._select_factory(driver, page_helper, '第一加工厂')
        self._select_category(driver, page_helper, '水果')
        self._select_farmer(driver, page_helper, '张三农场')

        # 添加第一个货品
        self._add_product_with_keyboard(driver, page_helper, '10', '220', '5', '22')

        # 添加第二个货品
        add_btn = driver.find_element(By.CSS_SELECTOR, 'button.add-product-btn')
        add_btn.click()
        page_helper.wait.until(EC.presence_of_element_located((By.ID, 'productModal')))
        spec_tags = driver.find_elements(By.CLASS_NAME, 'product-modal-spec-tag')
        spec_tags[1].click()  # 选择第二个规格
        page_helper.wait.until(EC.presence_of_element_located((By.ID, 'specDetailModal')))
        self._input_via_keyboard(driver, page_helper, 'quantity', '20')
        self._input_via_keyboard(driver, page_helper, 'grossWeight', '100')
        self._input_via_keyboard(driver, page_helper, 'boxWeight', '5')
        self._input_via_keyboard(driver, page_helper, 'unit_price', '15')
        self._click_confirm(driver, page_helper)

        # 验证货品列表中有2个货品
        page_helper.wait.until(EC.presence_of_element_located((By.CLASS_NAME, 'product-card')))
        products = driver.find_elements(By.CLASS_NAME, 'product-item')
        assert len(products) == 2, "应该有2个货品"

    @pytest.mark.ui
    def test_switch_factory_before_submit(self, driver, base_url, page_helper):
        """测试提交前切换加工厂"""
        page_helper.open_page('purchase-create.html')

        # 先选择一个加工厂
        self._select_factory(driver, page_helper, '第一加工厂')
        time.sleep(0.5)
        factory_text = driver.find_element(By.ID, 'factoryText')
        assert '第一加工厂' in factory_text.text

        # 切换到另一个加工厂
        factory_text.find_element(By.XPATH, '..').click()
        page_helper.wait.until(EC.presence_of_element_located((By.ID, 'factoryModal')))
        page_helper.click_element((By.XPATH, '//div[contains(., "第二加工厂")]'))

        # 验证已切换
        page_helper.wait.until(
            lambda d: 'show' not in d.find_element(By.ID, 'factoryModal').get_attribute('class')
        )
        time.sleep(0.5)
        factory_text = driver.find_element(By.ID, 'factoryText')
        assert '第二加工厂' in factory_text.text, "应该切换到第二加工厂"

    @pytest.mark.ui
    def test_change_category_clears_products(self, driver, base_url, page_helper):
        """测试切换类目时清空已选货品"""
        page_helper.open_page('purchase-create.html')

        # 填写基本信息并添加货品
        self._select_factory(driver, page_helper, '第一加工厂')
        self._select_category(driver, page_helper, '水果')
        self._select_farmer(driver, page_helper, '张三农场')
        self._add_product_with_keyboard(driver, page_helper, '10', '220', '5', '22')

        # 验证货品已添加
        products = driver.find_elements(By.CLASS_NAME, 'product-item')
        assert len(products) == 1, "应该有1个货品"

        # 切换到蔬菜类目（需要取消确认对话框，或者直接操作DOM）
        category_text = driver.find_element(By.ID, 'categoryText')
        category_text.find_element(By.XPATH, '..').click()
        page_helper.wait.until(EC.presence_of_element_located((By.ID, 'categoryModal')))
        page_helper.click_element((By.XPATH, '//div[contains(., "蔬菜")]'))

        # 如果弹出确认对话框，点击取消
        try:
            page_helper.wait.until(EC.alert_is_present())
            driver.switch_to.alert.dismiss()
        except:
            pass

    # ==================== 边界值测试 ====================

    @pytest.mark.regression
    def test_minimum_quantity(self, driver, base_url, page_helper):
        """测试最小数量（1）"""
        page_helper.open_page('purchase-create.html')
        self._select_factory(driver, page_helper, '第一加工厂')
        self._select_category(driver, page_helper, '水果')
        self._select_farmer(driver, page_helper, '张三农场')

        # 添加货品，数量为1
        self._add_product_with_keyboard(driver, page_helper, '1', '220', '5', '22')

        # 验证货品数量显示正确
        quantity_input = driver.find_element(By.CSS_SELECTOR, '.quantity-input')
        assert quantity_input.get_attribute('value') == '1', "数量应该是1"

    @pytest.mark.ui
    def test_large_quantity(self, driver, base_url, page_helper):
        """测试大数量（999）"""
        page_helper.open_page('purchase-create.html')
        self._select_factory(driver, page_helper, '第一加工厂')
        self._select_category(driver, page_helper, '水果')
        self._select_farmer(driver, page_helper, '张三农场')

        # 添加货品，数量为999
        self._add_product_with_keyboard(driver, page_helper, '999', '220', '5', '22')

        # 验证货品数量显示正确
        quantity_input = driver.find_element(By.CSS_SELECTOR, '.quantity-input')
        assert quantity_input.get_attribute('value') == '999', "数量应该是999"

    @pytest.mark.ui
    def test_decimal_unit_price(self, driver, base_url, page_helper):
        """测试小数单价"""
        page_helper.open_page('purchase-create.html')
        self._select_factory(driver, page_helper, '第一加工厂')
        self._select_category(driver, page_helper, '水果')
        self._select_farmer(driver, page_helper, '张三农场')

        # 添加货品，单价为22.5
        self._add_product_with_keyboard(driver, page_helper, '10', '220', '5', '22.5')

        # 验证采购金额计算正确: 10 * 22.5 = 225
        total_amount = driver.find_element(By.ID, 'totalAmountValue')
        assert '225' in total_amount.text, "采购金额应该是225"

    @pytest.mark.ui
    def test_zero_discount(self, driver, base_url, page_helper):
        """测试零折扣"""
        page_helper.open_page('purchase-create.html')
        self._select_factory(driver, page_helper, '第一加工厂')
        self._select_category(driver, page_helper, '水果')
        self._select_farmer(driver, page_helper, '张三农场')

        # 添加货品，折扣为0
        add_btn = driver.find_element(By.CSS_SELECTOR, 'button.add-product-btn')
        add_btn.click()
        page_helper.wait.until(EC.presence_of_element_located((By.ID, 'productModal')))
        spec_tags = driver.find_elements(By.CLASS_NAME, 'product-modal-spec-tag')
        spec_tags[0].click()
        page_helper.wait.until(EC.presence_of_element_located((By.ID, 'specDetailModal')))

        self._input_via_keyboard(driver, page_helper, 'quantity', '10')
        self._input_via_keyboard(driver, page_helper, 'gross_weight', '220')
        self._input_via_keyboard(driver, page_helper, 'box_weight', '5')
        self._input_via_keyboard(driver, page_helper, 'unit_price', '22')
        self._input_via_keyboard(driver, page_helper, 'discount_amount', '0')
        self._click_confirm(driver, page_helper)

        # 验证采购金额计算正确: 10 * 22 - 0 = 220
        total_amount = driver.find_element(By.ID, 'totalAmountValue')
        assert '220' in total_amount.text, "采购金额应该是220"

    @pytest.mark.ui
    def test_with_discount(self, driver, base_url, page_helper):
        """测试带折扣"""
        page_helper.open_page('purchase-create.html')
        self._select_factory(driver, page_helper, '第一加工厂')
        self._select_category(driver, page_helper, '水果')
        self._select_farmer(driver, page_helper, '张三农场')

        # 添加货品，有折扣
        add_btn = driver.find_element(By.CSS_SELECTOR, 'button.add-product-btn')
        add_btn.click()
        page_helper.wait.until(EC.presence_of_element_located((By.ID, 'productModal')))
        spec_tags = driver.find_elements(By.CLASS_NAME, 'product-modal-spec-tag')
        spec_tags[0].click()
        page_helper.wait.until(EC.presence_of_element_located((By.ID, 'specDetailModal')))

        self._input_via_keyboard(driver, page_helper, 'quantity', '10')
        self._input_via_keyboard(driver, page_helper, 'gross_weight', '220')
        self._input_via_keyboard(driver, page_helper, 'box_weight', '5')
        self._input_via_keyboard(driver, page_helper, 'unit_price', '22')
        self._input_via_keyboard(driver, page_helper, 'discount_amount', '50')
        self._click_confirm(driver, page_helper)

        # 验证采购金额计算正确: 10 * 22 - 50 = 170
        total_amount = driver.find_element(By.ID, 'totalAmountValue')
        assert '170' in total_amount.text, "采购金额应该是170"

    # ==================== 负向测试用例 ====================

    @pytest.mark.ui
    def test_submit_without_factory(self, driver, base_url, page_helper):
        """测试不选择加工厂时提交按钮禁用"""
        page_helper.open_page('purchase-create.html')
        # 只填写类目和农户
        self._select_category(driver, page_helper, '水果')
        self._select_farmer(driver, page_helper, '张三农场')
        # 验证提交按钮仍然禁用
        submit_btn = driver.find_element(By.ID, 'submitBtn')
        assert submit_btn.get_attribute('disabled') == 'true', "未选择加工厂时提交按钮应该禁用"

    @pytest.mark.ui
    def test_submit_without_category(self, driver, base_url, page_helper):
        """测试不选择类目时提交按钮禁用"""
        page_helper.open_page('purchase-create.html')
        # 只填写加工厂和农户
        self._select_factory(driver, page_helper, '第一加工厂')
        self._select_farmer(driver, page_helper, '张三农场')
        # 验证提交按钮仍然禁用
        submit_btn = driver.find_element(By.ID, 'submitBtn')
        assert submit_btn.get_attribute('disabled') == 'true', "未选择类目时提交按钮应该禁用"

    @pytest.mark.ui
    def test_submit_without_farmer(self, driver, base_url, page_helper):
        """测试不选择农户时提交按钮禁用"""
        page_helper.open_page('purchase-create.html')
        # 只填写加工厂和类目
        self._select_factory(driver, page_helper, '第一加工厂')
        self._select_category(driver, page_helper, '水果')
        # 验证提交按钮仍然禁用
        submit_btn = driver.find_element(By.ID, 'submitBtn')
        assert submit_btn.get_attribute('disabled') == 'true', "未选择农户时提交按钮应该禁用"

    @pytest.mark.ui
    def test_submit_without_products(self, driver, base_url, page_helper):
        """测试不添加货品时提交按钮禁用"""
        page_helper.open_page('purchase-create.html')
        # 填写基本信息但不添加货品
        self._select_factory(driver, page_helper, '第一加工厂')
        self._select_category(driver, page_helper, '水果')
        self._select_farmer(driver, page_helper, '张三农场')
        # 验证提交按钮仍然禁用
        submit_btn = driver.find_element(By.ID, 'submitBtn')
        assert submit_btn.get_attribute('disabled') == 'true', "未添加货品时提交按钮应该禁用"

    @pytest.mark.ui
    def test_add_product_without_category(self, driver, base_url, page_helper):
        """测试不选择类目时添加货品应提示"""
        page_helper.open_page('purchase-create.html')
        # 不选择类目，直接点击添加货品
        add_btn = driver.find_element(By.CSS_SELECTOR, 'button.add-product-btn')
        add_btn.click()
        # 验证产品模态框未打开
        product_modal = driver.find_element(By.ID, 'productModal')
        assert 'show' not in product_modal.get_attribute('class'), "未选择类目时不应打开货品模态框"

    # ==================== 数据验证测试 ====================

    @pytest.mark.ui
    def test_total_amount_calculation(self, driver, base_url, page_helper):
        """测试采购金额自动计算"""
        page_helper.open_page('purchase-create.html')
        self._select_factory(driver, page_helper, '第一加工厂')
        self._select_category(driver, page_helper, '水果')
        self._select_farmer(driver, page_helper, '张三农场')

        # 添加货品
        add_btn = driver.find_element(By.CSS_SELECTOR, 'button.add-product-btn')
        add_btn.click()
        page_helper.wait.until(EC.presence_of_element_located((By.ID, 'productModal')))
        spec_tags = driver.find_elements(By.CLASS_NAME, 'product-modal-spec-tag')
        spec_tags[0].click()
        page_helper.wait.until(EC.presence_of_element_located((By.ID, 'specDetailModal')))

        # 输入单价后验证金额
        self._input_via_keyboard(driver, page_helper, 'quantity', '10')
        self._input_via_keyboard(driver, page_helper, 'unit_price', '22')

        # 等待金额计算
        time.sleep(0.5)
        total_amount = driver.find_element(By.ID, 'totalAmountValue')
        assert '220' in total_amount.text, "采购金额应该自动计算为220"

    @pytest.mark.ui
    def test_spec_detail_farmer_display(self, driver, base_url, page_helper):
        """测试规格详情中显示已选农户"""
        page_helper.open_page('purchase-create.html')
        # 先选择农户
        self._select_farmer(driver, page_helper, '张三农场')

        # 打开货品选择
        self._select_category(driver, page_helper, '水果')
        add_btn = driver.find_element(By.CSS_SELECTOR, 'button.add-product-btn')
        add_btn.click()
        page_helper.wait.until(EC.presence_of_element_located((By.ID, 'productModal')))
        spec_tags = driver.find_elements(By.CLASS_NAME, 'product-modal-spec-tag')
        spec_tags[0].click()
        page_helper.wait.until(EC.presence_of_element_located((By.ID, 'specDetailModal')))

        # 验证显示已选农户
        farmer_name = driver.find_element(By.ID, 'specFarmerName')
        assert '张三农场' in farmer_name.text, "规格详情应显示已选农户"

    @pytest.mark.ui
    def test_delete_product(self, driver, base_url, page_helper):
        """测试删除货品"""
        page_helper.open_page('purchase-create.html')
        self._select_factory(driver, page_helper, '第一加工厂')
        self._select_category(driver, page_helper, '水果')
        self._select_farmer(driver, page_helper, '张三农场')
        self._add_product_with_keyboard(driver, page_helper, '10', '220', '5', '22')

        # 验证货品已添加
        products = driver.find_elements(By.CLASS_NAME, 'product-item')
        assert len(products) == 1

        # 删除货品
        delete_btn = driver.find_element(By.CLASS_NAME, 'product-remove')
        delete_btn.click()

        # 验证货品已删除
        page_helper.wait.until(
            lambda d: len(d.find_elements(By.CLASS_NAME, 'product-item')) == 0
        )
        # 验证提交按钮禁用
        submit_btn = driver.find_element(By.ID, 'submitBtn')
        assert submit_btn.get_attribute('disabled') == 'true', "删除所有货品后提交按钮应该禁用"

    @pytest.mark.ui
    def test_harvest_date_default_today(self, driver, base_url, page_helper):
        """测试采果日期默认为今天"""
        page_helper.open_page('purchase-create.html')
        today = time.strftime("%Y-%m-%d")
        date_input = driver.find_element(By.ID, 'harvestDate')
        assert date_input.get_attribute('value') == today, "采果日期应该默认为今天"

    @pytest.mark.ui
    def test_edit_product_quantity(self, driver, base_url, page_helper):
        """测试修改货品数量"""
        page_helper.open_page('purchase-create.html')
        self._select_factory(driver, page_helper, '第一加工厂')
        self._select_category(driver, page_helper, '水果')
        self._select_farmer(driver, page_helper, '张三农场')
        self._add_product_with_keyboard(driver, page_helper, '10', '220', '5', '22')

        # 修改数量
        quantity_input = driver.find_element(By.CSS_SELECTOR, '.quantity-input')
        quantity_input.clear()
        quantity_input.send_keys('20')

        # 验证数量已更新
        time.sleep(0.5)
        assert quantity_input.get_attribute('value') == '20', "数量应该更新为20"

    # ==================== 辅助方法 ====================

    def _select_factory(self, driver, page_helper, factory_name):
        """选择加工厂"""
        factory_element = driver.find_element(By.ID, 'factoryText')
        factory_element.find_element(By.XPATH, '..').click()
        page_helper.wait.until(EC.presence_of_element_located((By.ID, 'factoryModal')))
        page_helper.click_element((By.XPATH, f'//div[contains(., "{factory_name}")]'))
        # 等待模态框关闭
        time.sleep(0.5)

    def _select_category(self, driver, page_helper, category_name):
        """选择类目"""
        category_element = driver.find_element(By.ID, 'categoryText')
        category_element.find_element(By.XPATH, '..').click()
        page_helper.wait.until(EC.presence_of_element_located((By.ID, 'categoryModal')))
        page_helper.click_element((By.XPATH, f'//div[contains(., "{category_name}")]'))
        # 等待模态框关闭
        time.sleep(0.5)

    def _select_farmer(self, driver, page_helper, farmer_name):
        """选择农户"""
        farmer_element = driver.find_element(By.ID, 'farmerText')
        farmer_element.find_element(By.XPATH, '..').click()
        page_helper.wait.until(EC.presence_of_element_located((By.ID, 'farmerModal')))
        page_helper.click_element((By.XPATH, f'//div[contains(., "{farmer_name}")]'))
        # 等待模态框关闭
        time.sleep(0.5)

    def _add_product_with_keyboard(self, driver, page_helper, quantity, gross_weight, box_weight, unit_price):
        """添加货品（完整流程）"""
        add_btn = driver.find_element(By.CSS_SELECTOR, 'button.add-product-btn')
        add_btn.click()
        # 等待货品模态框显示
        page_helper.wait.until(
            lambda d: 'show' in d.find_element(By.ID, 'productModal').get_attribute('class')
        )
        # 等待货品列表加载 - 增加超时时间
        spec_tags = page_helper.wait.until(
            lambda d: len(d.find_elements(By.CLASS_NAME, 'product-modal-spec-tag')) > 0
        )
        spec_tags = driver.find_elements(By.CLASS_NAME, 'product-modal-spec-tag')
        # 点击第一个规格
        spec_tags[0].click()
        page_helper.wait.until(EC.presence_of_element_located((By.ID, 'specDetailModal')))

        self._input_via_keyboard(driver, page_helper, 'quantity', quantity)
        self._input_via_keyboard(driver, page_helper, 'gross_weight', gross_weight)
        self._input_via_keyboard(driver, page_helper, 'box_weight', box_weight)
        self._input_via_keyboard(driver, page_helper, 'unit_price', unit_price)
        self._click_confirm(driver, page_helper)

    def _input_via_keyboard(self, driver, page_helper, field_name, value):
        """通过数字键盘输入"""
        field_id_map = {
            'quantity': 'quantityValue',
            'gross_weight': 'grossWeightValue',
            'box_weight': 'boxWeightValue',
            'unit_price': 'unitPriceValue',
            'discount_amount': 'discountAmountValue'
        }

        value_id = field_id_map.get(field_name)
        if not value_id:
            return

        value_element = driver.find_element(By.ID, value_id)
        input_box = value_element.find_element(By.XPATH, '..')

        # 使用 JavaScript 点击避免元素遮挡问题
        driver.execute_script("arguments[0].click();", input_box)
        time.sleep(0.2)

        # 输入数字
        for digit in str(value):
            if digit == '.':
                key = (By.XPATH, '//div[contains(@class, "keyboard-key") and text()="."]')
            else:
                key = (By.XPATH, f'//div[contains(@class, "keyboard-key") and text()="{digit}"]')
            page_helper.click_element(key)
            time.sleep(0.05)

        # 点击确认保存当前输入
        confirm_btn = (By.XPATH, '//div[contains(@class, "keyboard-key action-primary") and text()="确认"]')
        page_helper.click_element(confirm_btn)
        time.sleep(0.2)

    def _click_confirm(self, driver, page_helper):
        """点击模态框确认按钮"""
        confirm_btn = (By.XPATH, '//div[contains(@class, "keyboard-key action-primary") and text()="确认"]')
        page_helper.wait.until(EC.element_to_be_clickable(confirm_btn)).click()
        time.sleep(0.3)
