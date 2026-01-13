"""
新建采购单 UI 自动化测试用例
使用 Selenium + pytest 测试完整的新建采购单流程
"""

import pytest
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains
import time


class TestPurchaseCreationUI:
    """新建采购单 UI 自动化测试类"""

    @pytest.mark.smoke
    def test_create_purchase_order_complete_flow(self, driver, base_url, page_helper, test_data):
        """测试完整的新建采购单流程 - 主流程测试"""
        # 1. 打开新建采购单页面
        page_helper.open_page('purchase-create.html')

        # 2. 选择加工厂
        factory_element = page_helper.wait.until(
            EC.presence_of_element_located((By.ID, 'factoryText'))
        )
        factory_element.find_element(By.XPATH, '..').click()

        # 等待模态框出现
        page_helper.wait.until(
            EC.presence_of_element_located((By.ID, 'factoryModal'))
        )
        factory_option = (By.XPATH, f'//div[contains(., "{test_data["factory"]["name"]}")]')
        page_helper.click_element(factory_option)

        # 3. 选择类目
        category_element = driver.find_element(By.ID, 'categoryText')
        category_element.find_element(By.XPATH, '..').click()

        page_helper.wait.until(
            EC.presence_of_element_located((By.ID, 'categoryModal'))
        )
        category_option = (By.XPATH, f'//div[contains(., "{test_data["category"]["name"]}")]')
        page_helper.click_element(category_option)

        # 4. 选择农户
        farmer_element = driver.find_element(By.ID, 'farmerText')
        farmer_element.find_element(By.XPATH, '..').click()

        page_helper.wait.until(
            EC.presence_of_element_located((By.ID, 'farmerModal'))
        )
        farmer_option = (By.XPATH, f'//div[contains(., "{test_data["farmer"]["name"]}")]')
        page_helper.click_element(farmer_option)

        # 5. 添加货品
        add_product_btn = (By.CSS_SELECTOR, 'button.add-product-btn')
        page_helper.click_element(add_product_btn)

        # 等待货品模态框
        page_helper.wait.until(
            EC.presence_of_element_located((By.ID, 'productModal'))
        )

        # 选择货品规格
        product_spec_tag = (By.XPATH, f'//span[contains(text(), "{test_data["product"]["spec"]}")]/ancestor::div[@class="product-modal-specs"]//span[contains(text(), "{test_data["product"]["spec"]}")]')
        spec_tags = driver.find_elements(By.CLASS_NAME, 'product-modal-spec-tag')
        if spec_tags:
            spec_tags[0].click()

        # 等待规格详情模态框
        page_helper.wait.until(
            EC.presence_of_element_located((By.ID, 'specDetailModal'))
        )

        # 6. 填写规格详情（使用数字键盘）
        self._input_number_via_keyboard(driver, page_helper, 'quantity', test_data['spec_detail']['quantity'])
        self._input_number_via_keyboard(driver, page_helper, 'grossWeight', test_data['spec_detail']['gross_weight'])
        self._input_number_via_keyboard(driver, page_helper, 'boxWeight', test_data['spec_detail']['box_weight'])
        self._input_number_via_keyboard(driver, page_helper, 'unitPrice', test_data['spec_detail']['unit_price'])

        # 点击"确认"按钮
        confirm_btn = (By.XPATH, '//div[contains(@class, "keyboard-key action-primary")]')
        page_helper.click_element(confirm_btn)

        # 7. 点击"去结算"按钮
        submit_btn = page_helper.wait.until(
            EC.element_to_be_clickable((By.ID, 'submitBtn'))
        )
        submit_btn.click()

        # 8. 等待页面跳转
        page_helper.wait.until(
            lambda d: 'purchase-list.html' in d.current_url
        )

        # 9. 验证跳转到采购单列表页面
        current_url = driver.current_url
        assert 'purchase-list.html' in current_url, "未跳转到采购单列表页面"

    @pytest.mark.ui
    def test_create_purchase_order_validation(self, driver, base_url, page_helper):
        """测试表单验证 - 未填写必填项时提交按钮应禁用"""
        page_helper.open_page('purchase-create.html')

        # 检查初始状态下提交按钮是否禁用
        submit_btn = driver.find_element(By.ID, 'submitBtn')
        assert submit_btn.get_attribute('disabled') == 'true', "初始状态下提交按钮应该是禁用的"

        # 只填写部分信息
        factory_element = driver.find_element(By.ID, 'factoryText')
        factory_element.find_element(By.XPATH, '..').click()

        page_helper.wait.until(
            EC.presence_of_element_located((By.ID, 'factoryModal'))
        )
        factory_option = (By.XPATH, '//div[contains(text(), "第一加工厂")]')
        page_helper.click_element(factory_option)

        # 验证提交按钮仍然禁用
        submit_btn = driver.find_element(By.ID, 'submitBtn')
        assert submit_btn.get_attribute('disabled') == 'true', "只填写部分信息时提交按钮应该是禁用的"

    @pytest.mark.ui
    def test_factory_modal_open_and_close(self, driver, base_url, page_helper):
        """测试加工厂模态框的打开和关闭"""
        page_helper.open_page('purchase-create.html')

        # 点击加工厂选择框
        factory_element = driver.find_element(By.ID, 'factoryText')
        factory_element.find_element(By.XPATH, '..').click()

        # 验证模态框打开
        page_helper.wait.until(
            EC.presence_of_element_located((By.ID, 'factoryModal'))
        )
        modal = driver.find_element(By.ID, 'factoryModal')
        assert 'show' in modal.get_attribute('class'), "模态框应该显示"

        # 点击关闭按钮
        close_btn = driver.find_element(By.XPATH, '//div[@id="factoryModal"]//div[@class="modal-close"]')
        close_btn.click()

        # 等待模态框关闭
        time.sleep(0.5)
        modal = driver.find_element(By.ID, 'factoryModal')
        assert 'show' not in modal.get_attribute('class'), "模态框应该关闭"

    @pytest.mark.regression
    def test_category_selection(self, driver, base_url, page_helper):
        """测试类目选择功能"""
        page_helper.open_page('purchase-create.html')

        # 打开类目选择
        category_element = driver.find_element(By.ID, 'categoryText')
        category_element.find_element(By.XPATH, '..').click()

        # 等待模态框
        page_helper.wait.until(
            EC.presence_of_element_located((By.ID, 'categoryModal'))
        )

        # 选择"水果"
        fruit_option = (By.XPATH, '//div[contains(., "水果")]')
        page_helper.click_element(fruit_option)

        # 等待模态框关闭和文本更新
        page_helper.wait.until(
            lambda d: 'show' not in d.find_element(By.ID, 'categoryModal').get_attribute('class')
        )

        # 验证选择结果 - 使用显式等待
        page_helper.wait.until(
            lambda d: '水果' in d.find_element(By.ID, 'categoryText').text
        )

    @pytest.mark.ui
    def test_farmer_selection(self, driver, base_url, page_helper, test_data):
        """测试农户选择功能"""
        page_helper.open_page('purchase-create.html')

        # 打开农户选择
        farmer_element = driver.find_element(By.ID, 'farmerText')
        farmer_element.find_element(By.XPATH, '..').click()

        # 等待模态框
        page_helper.wait.until(
            EC.presence_of_element_located((By.ID, 'farmerModal'))
        )

        # 选择农户
        farmer_option = (By.XPATH, f'//div[contains(., "{test_data["farmer"]["name"]}")]')
        page_helper.click_element(farmer_option)

        # 等待模态框关闭和文本更新
        page_helper.wait.until(
            lambda d: 'show' not in d.find_element(By.ID, 'farmerModal').get_attribute('class')
        )

        # 验证选择结果 - 使用显式等待
        page_helper.wait.until(
            lambda d: test_data['farmer']['name'] in d.find_element(By.ID, 'farmerText').text
        )

    @pytest.mark.ui
    def test_date_input_default_value(self, driver, base_url, page_helper):
        """测试日期输入框默认为今天"""
        page_helper.open_page('purchase-create.html')

        # 获取今天的日期
        today = time.strftime("%Y-%m-%d")

        # 验证日期输入框的值
        date_input = driver.find_element(By.ID, 'harvestDate')
        assert date_input.get_attribute('value') == today, "日期应该默认为今天"

    @pytest.mark.ui
    def test_product_modal_requires_category(self, driver, base_url, page_helper):
        """测试必须先选择类目才能添加货品"""
        page_helper.open_page('purchase-create.html')

        # 直接点击添加货品按钮（未选择类目）
        add_product_btn = (By.CSS_SELECTOR, 'button.add-product-btn')
        page_helper.click_element(add_product_btn)

        # 等待一下看是否有toast提示
        time.sleep(1)

        # 验证产品模态框未打开
        product_modal = driver.find_element(By.ID, 'productModal')
        assert 'show' not in product_modal.get_attribute('class'), "未选择类目时不应打开货品模态框"

    @pytest.mark.ui
    def test_spec_detail_modal_elements(self, driver, base_url, page_helper, test_data):
        """测试规格详情模态框的元素显示"""
        page_helper.open_page('purchase-create.html')

        # 先完成基本选择
        factory_element = driver.find_element(By.ID, 'factoryText')
        factory_element.find_element(By.XPATH, '..').click()
        page_helper.wait.until(EC.presence_of_element_located((By.ID, 'factoryModal')))
        page_helper.click_element((By.XPATH, '//div[contains(., "第一加工厂")]'))

        category_element = driver.find_element(By.ID, 'categoryText')
        category_element.find_element(By.XPATH, '..').click()
        page_helper.wait.until(EC.presence_of_element_located((By.ID, 'categoryModal')))
        page_helper.click_element((By.XPATH, '//div[contains(., "水果")]'))

        farmer_element = driver.find_element(By.ID, 'farmerText')
        farmer_element.find_element(By.XPATH, '..').click()
        page_helper.wait.until(EC.presence_of_element_located((By.ID, 'farmerModal')))
        page_helper.click_element((By.XPATH, '//div[contains(., "张三农场")]'))

        # 添加货品
        add_product_btn = (By.CSS_SELECTOR, 'button.add-product-btn')
        page_helper.click_element(add_product_btn)
        page_helper.wait.until(EC.presence_of_element_located((By.ID, 'productModal')))

        # 点击第一个规格
        spec_tags = driver.find_elements(By.CLASS_NAME, 'product-modal-spec-tag')
        spec_tags[0].click()

        # 等待规格详情模态框
        page_helper.wait.until(EC.presence_of_element_located((By.ID, 'specDetailModal')))

        # 验证模态框包含必要的输入字段
        assert driver.find_element(By.ID, 'quantityValue').is_displayed(), "应该显示数量输入框"
        assert driver.find_element(By.ID, 'grossWeightValue').is_displayed(), "应该显示毛重输入框"
        assert driver.find_element(By.ID, 'boxWeightValue').is_displayed(), "应该显示箱框皮重输入框"
        assert driver.find_element(By.ID, 'unitPriceValue').is_displayed(), "应该显示单价输入框"
        assert driver.find_element(By.ID, 'discountAmountValue').is_displayed(), "应该显示折扣金额输入框"
        assert driver.find_element(By.ID, 'totalAmountValue').is_displayed(), "应该显示采购金额显示框"

    # ==================== 辅助方法 ====================

    def _input_number_via_keyboard(self, driver, page_helper, field_name, value):
        """通过数字键盘输入数值

        Args:
            driver: WebDriver 实例
            page_helper: PageHelper 实例
            field_name: 字段名称 (quantity, grossWeight, boxWeight, unitPrice, discountAmount)
            value: 要输入的数值
        """
        # 找到对应的值元素的 ID
        value_id_map = {
            'quantity': 'quantityValue',
            'grossWeight': 'grossWeightValue',
            'boxWeight': 'boxWeightValue',
            'unitPrice': 'unitPriceValue',
            'discountAmount': 'discountAmountValue'
        }

        value_id = value_id_map.get(field_name)
        if not value_id:
            return

        # 找到值元素，然后点击其父 div
        value_element = driver.find_element(By.ID, value_id)
        input_box = value_element.find_element(By.XPATH, '..')
        input_box.click()

        # 等待键盘激活
        time.sleep(0.3)

        # 输入数字
        value_str = str(value)
        for digit in value_str:
            if digit == '.':
                key = (By.XPATH, '//div[contains(@class, "keyboard-key") and text()="."]')
            else:
                key = (By.XPATH, f'//div[contains(@class, "keyboard-key") and text()="{digit}"]')
            page_helper.click_element(key)
            time.sleep(0.1)

        # 点击确认保存当前输入
        confirm_btn = (By.XPATH, '//div[contains(@class, "keyboard-key action-primary") and text()="确认"]')
        page_helper.click_element(confirm_btn)
        time.sleep(0.2)

    def _fill_basic_info(self, page_helper, test_data):
        """填写基本信息"""
        # 选择加工厂
        factory_element = page_helper.driver.find_element(By.ID, 'factoryText')
        factory_element.find_element(By.XPATH, '..').click()
        page_helper.wait.until(EC.presence_of_element_located((By.ID, 'factoryModal')))
        factory_option = (By.XPATH, f'//div[contains(., "{test_data["factory"]["name"]}")]')
        page_helper.click_element(factory_option)

        # 选择类目
        category_element = page_helper.driver.find_element(By.ID, 'categoryText')
        category_element.find_element(By.XPATH, '..').click()
        page_helper.wait.until(EC.presence_of_element_located((By.ID, 'categoryModal')))
        category_option = (By.XPATH, f'//div[contains(., "{test_data["category"]["name"]}")]')
        page_helper.click_element(category_option)

        # 选择农户
        farmer_element = page_helper.driver.find_element(By.ID, 'farmerText')
        farmer_element.find_element(By.XPATH, '..').click()
        page_helper.wait.until(EC.presence_of_element_located((By.ID, 'farmerModal')))
        farmer_option = (By.XPATH, f'//div[contains(., "{test_data["farmer"]["name"]}")]')
        page_helper.click_element(farmer_option)
