"""
pytest 配置文件
用于 UI 自动化测试的 fixture 和配置
"""

import pytest
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager


@pytest.fixture(scope="function")
def driver():
    """
    初始化 WebDriver fixture
    每个测试函数执行前创建，执行后自动关闭
    """
    # Chrome 浏览器配置
    options = webdriver.ChromeOptions()

    # 无头模式（可选，注释掉以便看到执行过程）
    # options.add_argument('--headless')

    # 禁用 GPU 加速
    options.add_argument('--disable-gpu')

    # 窗口大小设置
    options.add_argument('--window-size=480,800')

    # 忽略证书错误
    options.add_argument('--ignore-certificate-errors')

    # 禁用自动化扩展
    options.add_experimental_option('excludeSwitches', ['enable-automation'])
    options.add_experimental_option('useAutomationExtension', False)

    # 创建 driver (使用 webdriver-manager 自动管理 ChromeDriver)
    service = webdriver.chrome.service.Service(ChromeDriverManager().install())
    driver_instance = webdriver.Chrome(service=service, options=options)

    # 隐式等待设置
    driver_instance.implicitly_wait(10)

    yield driver_instance

    # 测试结束后关闭浏览器
    driver_instance.quit()


@pytest.fixture(scope="function")
def base_url():
    """获取基础 URL"""
    return "file:///Users/senguoyun/code/test-copy-senguo/frontend/"


@pytest.fixture(scope="function")
def wait(driver):
    """
    显式等待 fixture
    用于等待元素出现、可点击等条件
    """
    return WebDriverWait(driver, 15)


@pytest.fixture(scope="function", autouse=True)
def screenshot_on_failure(request, driver):
    """
    测试失败时自动截图
    """
    yield

    # 检查测试是否失败（兼容不同 pytest 版本）
    failed = hasattr(request, 'node') and hasattr(request.node, 'rep_call') and request.node.rep_call.failed
    if not failed:
        # 兼容旧版本
        try:
            if hasattr(request.node, 'call_result'):
                failed = request.node.call_result.failed
        except AttributeError:
            pass

    if failed:
        timestamp = time.strftime("%Y%m%d_%H%M%S")
        screenshot_name = f"screenshot_{request.node.name}_{timestamp}.png"
        driver.save_screenshot(screenshot_name)
        print(f"✗ 测试失败，截图已保存: {screenshot_name}")


class PageHelper:
    """页面操作辅助类"""

    def __init__(self, driver, base_url):
        self.driver = driver
        self.base_url = base_url
        self.wait = WebDriverWait(driver, 15)

    def open_page(self, page_name):
        """打开指定页面"""
        url = self.base_url + page_name
        self.driver.get(url)
        self.wait.until(EC.presence_of_element_located((By.TAG_NAME, "body")))

    def click_element(self, locator):
        """点击元素"""
        element = self.wait.until(EC.element_to_be_clickable(locator))
        element.click()
        return element

    def input_text(self, locator, text):
        """输入文本"""
        element = self.wait.until(EC.presence_of_element_located(locator))
        element.clear()
        element.send_keys(text)
        return element

    def select_dropdown(self, trigger_locator, option_text):
        """选择下拉选项"""
        # 点击下拉框
        self.click_element(trigger_locator)

        # 等待选项出现并点击
        option_locator = (By.XPATH, f"//div[contains(text(), '{option_text}')]")
        self.click_element(option_locator)

    def wait_for_element_visible(self, locator):
        """等待元素可见"""
        return self.wait.until(EC.visibility_of_element_located(locator))

    def wait_for_text_present(self, text):
        """等待文本出现在页面中"""
        locator = (By.XPATH, f"//*[contains(text(), '{text}')]")
        return self.wait.until(EC.presence_of_element_located(locator))

    def is_element_present(self, locator):
        """检查元素是否存在"""
        try:
            self.driver.find_element(*locator)
            return True
        except:
            return False

    def get_element_text(self, locator):
        """获取元素文本"""
        element = self.wait.until(EC.presence_of_element_located(locator))
        return element.text

    def switch_to_frame(self, frame_locator):
        """切换到 iframe"""
        self.wait.until(EC.frame_to_be_available_and_switch_to_it(frame_locator))


@pytest.fixture(scope="function")
def page_helper(driver, base_url):
    """PageHelper fixture"""
    return PageHelper(driver, base_url)


# ==================== 测试数据 ====================

@pytest.fixture(scope="function")
def test_data():
    """测试数据 fixture"""
    return {
        'factory': {
            'name': '第一加工厂'
        },
        'category': {
            'name': '水果'
        },
        'farmer': {
            'name': '张三农场'
        },
        'product': {
            'name': '西瓜',
            'spec': '5斤/22kg'
        },
        'spec_detail': {
            'quantity': '10',
            'gross_weight': '220',
            'box_weight': '5',
            'unit_price': '22',
            'discount_amount': '0'
        }
    }


# ==================== pytest 插件配置 ====================

def pytest_configure(config):
    """pytest 配置"""
    config.addinivalue_line(
        "markers", "smoke: 冒烟测试"
    )
    config.addinivalue_line(
        "markers", "regression: 回归测试"
    )
    config.addinivalue_line(
        "markers", "ui: UI自动化测试"
    )
