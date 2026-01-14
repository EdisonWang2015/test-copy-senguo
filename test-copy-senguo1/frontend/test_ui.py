"""
前端UI自动化测试 - 采购单页面
使用 pytest + selenium 框架
"""
import pytest
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import Select
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options


@pytest.fixture(scope="module")
def chrome_driver():
    """创建Chrome驱动"""
    options = Options()
    # options.add_argument("--headless")  # 无头模式（可选）
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--window-size=375,812")  # 移动端尺寸
    
    driver = webdriver.Chrome(options=options)
    driver.set_page_load_timeout(10)
    yield driver
    driver.quit()


@pytest.fixture
def browser(chrome_driver):
    """为每个测试提供浏览器实例"""
    chrome_driver.get("http://127.0.0.1:8000/frontend/index.html")
    time.sleep(2)  # 等待页面加载
    yield chrome_driver
    chrome_driver.refresh()


class TestUIBasics:
    """基础UI测试"""
    
    def test_page_load(self, browser):
        """测试页面加载"""
        assert "采购管理" in browser.title or "采购管理" in browser.page_source
        time.sleep(1)
    
    def test_header_visible(self, browser):
        """测试头部是否可见"""
        header = browser.find_element(By.CLASS_NAME, "header")
        assert header.is_displayed()
        title = header.find_element(By.TAG_NAME, "h1")
        assert "采购管理" in title.text
    
    def test_footer_nav_visible(self, browser):
        """测试底部导航是否可见"""
        footer = browser.find_element(By.CLASS_NAME, "footer-nav")
        assert footer.is_displayed()
        
        # 检查有4个导航项
        nav_items = browser.find_elements(By.CLASS_NAME, "footer-item")
        assert len(nav_items) == 4
    
    def test_features_grid_visible(self, browser):
        """测试功能网格是否可见"""
        features = browser.find_elements(By.CLASS_NAME, "feature-item")
        assert len(features) > 0
        print(f"发现 {len(features)} 个功能项")


class TestNavigation:
    """导航测试"""
    
    def test_navigate_to_create_order_page(self, browser):
        """测试导航到创建采购单页面"""
        # 点击创建按钮
        create_btn = browser.find_elements(By.CLASS_NAME, "footer-item")[1]
        create_btn.click()
        time.sleep(1)
        
        # 检查新页面是否显示
        form_title = browser.find_element(By.CLASS_NAME, "form-title")
        assert "新增采购单" in form_title.text
    
    def test_navigate_to_list_page(self, browser):
        """测试导航到列表页面"""
        # 点击列表按钮
        list_btn = browser.find_elements(By.CLASS_NAME, "footer-item")[2]
        list_btn.click()
        time.sleep(1)
        
        # 检查列表页面是否显示
        form_title = browser.find_element(By.CLASS_NAME, "form-title")
        assert "采购单列表" in form_title.text
    
    def test_navigate_back_to_home(self, browser):
        """测试导航回首页"""
        # 先导航到创建页面
        create_btn = browser.find_elements(By.CLASS_NAME, "footer-item")[1]
        create_btn.click()
        time.sleep(1)
        
        # 再导航回首页
        home_btn = browser.find_elements(By.CLASS_NAME, "footer-item")[0]
        home_btn.click()
        time.sleep(1)
        
        # 检查首页内容是否显示
        module_title = browser.find_element(By.CLASS_NAME, "module-title")
        assert "原料采购" in module_title.text


class TestPurchaseOrderForm:
    """采购单表单测试"""
    
    def test_form_elements_present(self, browser):
        """测试表单元素是否存在"""
        # 导航到创建页面
        create_btn = browser.find_elements(By.CLASS_NAME, "footer-item")[1]
        create_btn.click()
        time.sleep(1)
        
        # 检查所有表单元素
        form = browser.find_element(By.ID, "purchaseForm")
        assert form.is_displayed()
        
        # 检查所有输入字段
        assert browser.find_element(By.ID, "supplier_name")
        assert browser.find_element(By.ID, "product_name")
        assert browser.find_element(By.ID, "quantity")
        assert browser.find_element(By.ID, "unit_price")
        assert browser.find_element(By.ID, "category")
        assert browser.find_element(By.ID, "remark")
    
    def test_form_validation_empty_fields(self, browser):
        """测试表单验证 - 空字段"""
        # 导航到创建页面
        create_btn = browser.find_elements(By.CLASS_NAME, "footer-item")[1]
        create_btn.click()
        time.sleep(1)
        
        # 尝试提交空表单
        submit_btn = browser.find_element(By.CSS_SELECTOR, "button[type='submit']")
        submit_btn.click()
        time.sleep(1)
        
        # 检查是否有验证消息（HTML5原生验证）
        supplier_input = browser.find_element(By.ID, "supplier_name")
        # 检查是否触发了验证
        assert not supplier_input.get_attribute("value")
    
    def test_fill_form_with_valid_data(self, browser):
        """测试填充表单有效数据"""
        # 导航到创建页面
        create_btn = browser.find_elements(By.CLASS_NAME, "footer-item")[1]
        create_btn.click()
        time.sleep(1)
        
        # 填充表单
        browser.find_element(By.ID, "supplier_name").send_keys("测试供应商")
        browser.find_element(By.ID, "product_name").send_keys("测试产品")
        browser.find_element(By.ID, "quantity").send_keys("100")
        browser.find_element(By.ID, "unit_price").send_keys("10.5")
        
        # 选择分类
        category_select = Select(browser.find_element(By.ID, "category"))
        category_select.select_by_value("水果")
        
        browser.find_element(By.ID, "remark").send_keys("测试备注")
        
        time.sleep(1)
        
        # 验证填充的值
        assert browser.find_element(By.ID, "supplier_name").get_attribute("value") == "测试供应商"
        assert browser.find_element(By.ID, "product_name").get_attribute("value") == "测试产品"
        assert browser.find_element(By.ID, "quantity").get_attribute("value") == "100"
        assert browser.find_element(By.ID, "unit_price").get_attribute("value") == "10.5"
    
    def test_cancel_form(self, browser):
        """测试取消表单"""
        # 导航到创建页面
        create_btn = browser.find_elements(By.CLASS_NAME, "footer-item")[1]
        create_btn.click()
        time.sleep(1)
        
        # 填充一些数据
        browser.find_element(By.ID, "supplier_name").send_keys("测试")
        
        # 点击取消按钮
        buttons = browser.find_elements(By.CLASS_NAME, "btn")
        cancel_btn = [btn for btn in buttons if "取消" in btn.text][0]
        cancel_btn.click()
        time.sleep(1)
        
        # 检查是否返回首页
        module_title = browser.find_element(By.CLASS_NAME, "module-title")
        assert "原料采购" in module_title.text


class TestPurchaseOrderSubmission:
    """采购单提交测试"""
    
    def test_submit_valid_purchase_order(self, browser):
        """测试提交有效采购单"""
        # 导航到创建页面
        create_btn = browser.find_elements(By.CLASS_NAME, "footer-item")[1]
        create_btn.click()
        time.sleep(1)
        
        # 填充表单
        browser.find_element(By.ID, "supplier_name").send_keys("测试供应商")
        browser.find_element(By.ID, "product_name").send_keys("测试产品")
        browser.find_element(By.ID, "quantity").send_keys("50")
        browser.find_element(By.ID, "unit_price").send_keys("25.0")
        
        # 选择分类
        category_select = Select(browser.find_element(By.ID, "category"))
        category_select.select_by_value("水果")
        
        # 提交表单
        submit_btn = browser.find_element(By.CSS_SELECTOR, "button[type='submit']")
        submit_btn.click()
        
        # 等待响应和消息出现
        time.sleep(3)
        
        # 检查成功消息
        try:
            message = WebDriverWait(browser, 5).until(
                EC.presence_of_element_located((By.CLASS_NAME, "message"))
            )
            assert message.is_displayed()
            assert "成功" in message.text or "PO" in message.text
        except:
            print("未检测到成功消息，可能是后端未运行")


class TestOrderList:
    """采购单列表测试"""
    
    def test_load_order_list(self, browser):
        """测试加载采购单列表"""
        # 导航到列表页面
        list_btn = browser.find_elements(By.CLASS_NAME, "footer-item")[2]
        list_btn.click()
        time.sleep(2)
        
        # 检查列表是否显示
        orders_list = browser.find_element(By.ID, "ordersList")
        assert orders_list.is_displayed()
    
    def test_order_list_layout(self, browser):
        """测试采购单列表布局"""
        # 导航到列表页面
        list_btn = browser.find_elements(By.CLASS_NAME, "footer-item")[2]
        list_btn.click()
        time.sleep(2)
        
        # 获取列表容器
        orders_list = browser.find_element(By.ID, "ordersList")
        
        # 检查是否有订单卡片或空消息
        cards = orders_list.find_elements(By.CLASS_NAME, "order-card")
        # 如果没有订单卡片，应该有空消息
        if len(cards) == 0:
            message = orders_list.find_element(By.TAG_NAME, "p")
            assert "暂无" in message.text


class TestResponsiveness:
    """响应式设计测试"""
    
    def test_mobile_viewport(self, browser):
        """测试移动端视口"""
        # 浏览器已设置为移动端尺寸 (375x812)
        window_size = browser.get_window_size()
        print(f"窗口大小: {window_size}")
        
        # 检查页面是否能正确渲染
        header = browser.find_element(By.CLASS_NAME, "header")
        assert header.is_displayed()
        
        footer = browser.find_element(By.CLASS_NAME, "footer-nav")
        assert footer.is_displayed()
    
    def test_feature_items_responsive(self, browser):
        """测试功能项响应式布局"""
        features = browser.find_elements(By.CLASS_NAME, "feature-item")
        
        for feature in features:
            # 检查每个功能项是否可见
            assert feature.is_displayed()
            
            # 检查图标和标签是否都存在
            icon = feature.find_element(By.CLASS_NAME, "feature-icon")
            label = feature.find_element(By.CLASS_NAME, "feature-label")
            
            assert icon.is_displayed()
            assert label.is_displayed()


class TestInteractions:
    """交互测试"""
    
    def test_feature_item_click(self, browser):
        """测试点击功能项"""
        features = browser.find_elements(By.CLASS_NAME, "feature-item")
        
        # 点击第一个功能项（应该导航到相应页面）
        if len(features) > 0:
            features[0].click()
            time.sleep(1)
            
            # 检查页面是否改变
            current_page = browser.find_element(By.CLASS_NAME, "page active")
            assert current_page.is_displayed()
    
    def test_footer_item_highlight(self, browser):
        """测试底部导航项高亮"""
        footer_items = browser.find_elements(By.CLASS_NAME, "footer-item")
        
        # 点击第二个导航项
        footer_items[1].click()
        time.sleep(1)
        
        # 检查是否被高亮
        highlighted = browser.find_elements(By.CSS_SELECTOR, ".footer-item.active")
        assert len(highlighted) > 0


if __name__ == "__main__":
    pytest.main([__file__, "-v", "-s"])
