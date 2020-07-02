from appium import webdriver
import os
import time
from selenium.webdriver.support.ui import WebDriverWait
from selenium.common.exceptions import NoSuchElementException
from selenium.common.exceptions import TimeoutException

import logging


class Page(object):
    """页面基本操作"""
    def __init__(self, driver: webdriver.Remote):
        self.driver = driver

    def find_text(self, text):
        """使用text定位元素"""
        text = text.strip()
        if not text:
            raise ValueError
        return self.driver.find_element_by_android_uiautomator('new UiSelector().text("{}")'.format(text))
    
    def find_id(self, resource_id):
        """使用id定位元素"""
        if not resource_id:
            raise ValueError("resource_id参数不能为空")
        return self.driver.find_element_by_id(resource_id)
    
    def find_predicate(self, predicate_value):
        """ios_predicate定位"""
        if not predicate_value:
            raise ValueError("predicate参数不能为空")
        return self.driver.find_element_by_ios_predicate(predicate_value)
    
    def find_predicates(self, *loc):
        """ios_predicate多属性定位"""
        if len(loc) < 2:
            raise ValueError("ios_predicate多属性定位参数不能为空")
        else:
            return self.driver.find_element_by_ios_predicate(loc[0] and loc[1])
    
    def find_element(self, *loc):
        """定位元素，支持id,class_name, xpath, text, msg，accessibility id"""
        if len(loc) != 2:
            raise ValueError("参数定位器长度不为2")
        if loc[0].lower() in ('id', 'class_name', 'xpath', 'accessibility id'):
            return self.driver.find_element(*loc)
        elif loc[0].lower() == 'text':
            return self.find_text(loc[1])
        elif loc[0].lower() == 'msg':
            # return self.wait_toast(loc[1])
            return self.driver.find_element_by_xpath('//*[@text="{}"]'.format(loc[1]))
        else:
            raise ValueError("不支持该种定位方式")
    
    def find(self, *loc):
        """定位元素，找不到则截图，并报错"""
        try:
            return self.find_element(*loc)
        except NoSuchElementException:
            time.sleep(1)  # todo check
            self.screenshot('NotFound_{}'.format('_'.join(loc)))
            logging.error("定位元素: {} 失败".format(loc))
            raise
    
    def try_find_element(self, *args):
        """尝试定位元素，找不到不报错"""
        try:
            return self.find_element(*args)
        except NoSuchElementException:
            logging.debug("元素: {} 未被定位到".format(args))
    
    def is_element_exist(self, *args):
        """判断元素是否存在"""
        try:
            self.find_element(*args)
        except NoSuchElementException:
            logging.debug("元素: {} 未被定位到".format(args))
            return False
        return True
    
    def find_elements(self, *loc):
        """定位一组元素，只支持id, class name, xpath"""
        if len(loc) != 2:
            raise ValueError
        return self.driver.find_elements(*loc)
    
    def wait_element(self, *loc):
        """等待并检测元素，定位不到元素报超时错误"""
        try:
            wait = WebDriverWait(self.driver, 10, 0.01)
            return wait.until(lambda _: self.find_element(*loc))
        except TimeoutException:
            self.screenshot('NotFound_{}'.format('_'.join(loc)))
            logging.error("元素 {} 超时未定位到".format(loc))
            raise
    
    def wait_text(self, text):
        """等待并检测指定text元素，定位不到报超时错误"""
        try:
            wait = WebDriverWait(self.driver, self.TIME_OUT)
            return wait.until(lambda _: self.find_text(text))
        except TimeoutException:
            self.screenshot('NotFound_text_{}'.format(text))
            logging.error("文本 {} 超时未定位到".format(text))
            raise
    
    def wait_toast(self, msg):
        """等待并检测toast消息，定位不到报超时错误"""
        try:
            return self.wait_element('xpath', '//*[@text="{}"]'.format(msg))
        except TimeoutException:
            self.screenshot('NotFound_msg_{}'.format(msg))
            logging.error("提示消息 {} 超时未定位到".format(msg))
            raise
    
    def wait_predicate(self, predicate_value):
        """等待并检测指定predicate元素，定位不到报超时错误"""
        try:
            wait = WebDriverWait(self.driver, self.TIME_OUT)
            return wait.until(lambda _: self.find_predicate(predicate_value))
        except TimeoutException:
            self.screenshot('NotFound_predicate_{}'.format(predicate_value))
            logging.error("predicate {} 超时未定位到".format(predicate_value))
            raise
    
    def wait_predicates(self, *loc):
        """等待并检测指定predicate多元素，定位不到报超时错误"""
        try:
            wait = WebDriverWait(self.driver, self.TIME_OUT)
            return wait.until(lambda _: self.find_predicates(*loc))
        except TimeoutException:
            self.screenshot('NotFound_predicates_{0}{1}'.format(loc[0], loc[1]))
            logging.error("predicates {0}{1} 超时未定位到".format(loc[1], loc[1]))
            raise
    # 元素操作 -------------------------------------------------------------------
    
    def click_text(self, *args):
        """点击指定文本元素"""
        logging.debug("点击文本: {}".format(args))
        self.find_text(*args).click()
    
    def click_id(self, *args):
        """点击指定resource_id元素"""
        logging.debug("点击指定id: {} 元素".format(args))
        self.find_id(*args).click()
    
    def click_predicate(self, predicate_value):
        """点击指定predicate元素"""
        logging.debug("点击predicate: {}".format(predicate_value))
        self.find_predicate(predicate_value).click()
    
    def click_predicates(self, *loc):
        """点击指定predicate多元素"""
        logging.debug("点击predicate: {0}{1}".format(loc[0], loc[1]))
        self.find_predicates(*loc).click()
    
    def click(self, *args):
        """点击元素，支持id,class name,xpath, text, msg, 点击不到则截图并报错"""
        logging.debug("点击: {}".format(args))
        self.find(*args).click()
    
    def wait_click(self, *args):
        """等待并点击元素，定位不到报超时错误"""
        logging.debug("等待点击: {}".format(args))
        self.wait_element(*args).click()
    
    def try_click_text(self, text):
        """尝试点击指定文本，定位不到不报错"""
        logging.debug("尝试点击文本: {}".format(text))
        try:
            self.find_text(text).click()
            return True
        except NoSuchElementException:
            logging.debug("文本: {} 未被定位到".format(text))
    
    def try_click_id(self, resource_id):
        """尝试点击指定resource_id元素，定位不到不报错"""
        logging.debug("尝试点击指定id: {} 元素".format(resource_id))
        try:
            self.find_id(resource_id).click()
            return True
        except NoSuchElementException:
            logging.debug("指定id: {} 元素 未被定位到".format(resource_id))
    
    def try_click_predicate(self, predicate_value):
        """尝试点击指定predicate的元素，定位不到不报错"""
        logging.debug("尝试点击指定predicate: {0} 元素".format(predicate_value))
        try:
            self.find_predicate(predicate_value).click()
            return True
        except NoSuchElementException:
            logging.debug("指定predicate: {0} 元素 未被定位到".format(predicate_value))
    
    def try_click_predicates(self, *loc):
        """尝试点击指定predicate多属性的元素，定位不到不报错"""
        logging.debug("尝试点击指定predicate: {0}{1} 元素".format(loc[0], loc[1]))
        try:
            self.find_predicates(*loc).click()
            return True
        except NoSuchElementException:
            logging.debug("指定predicates: {0}{1} 元素 未被定位到".format(loc[0], loc[1]))
    
    def try_click(self, *args):
        """尝试点击指定元素，定位不到不报错"""
        logging.debug("尝试点击: {}".format(args))
        try:
            self.find_element(*args).click()
            return True
        except NoSuchElementException:
            logging.debug("元素: {} 未被定位到".format(args))
    
    def type(self, *args, text=''):
        """输入，args为元素定位符，支持id，class name, xpath, text, msg"""
        logging.debug("元素: {} 输入: {}".format(args, text))
        text = text.strip()
        if not text:
            logging.warning("type() text参数为空!")
        input = self.find_element(*args)
        input.clear()
        input.send_keys(text)
    
    def type_and_enter(self, *args, text=''):
        """输入并按回车键"""
        self.type(*args, text=text)
        logging.debug("按回车键")
        self.driver.keyevent(66)
    
    def type_and_search(self, *args, text=''):
        """输入并按搜索键"""
        self.type(*args, text=text)
        logging.info("按搜索键")
        self.driver.execute_script('mobile: performEditorAction', {'action': 'search'})
    # page action --------------------------------------------------------------
    
    def long_touch(self):  # todo complete
        """长按"""
        pass
    
    def get_screen_size(self):
        """获取屏幕尺寸"""
        size = self.driver.get_window_size()
        return (size['width'], size['height'])
    
    def swipe_left(self, from_top=0.5):
        """左划，from_top默认为距离顶部0.5个屏幕(屏幕中间)"""
        if not isinstance(from_top, int) and not isinstance(from_top, float):
            raise ValueError("from_top参数不为数字")
        logging.debug("左滑")
        l = self.get_screen_size()
        y1 = int(l[1] * from_top)
        x1 = int(l[0] * 0.95)
        x2 = int(l[0] * 0.25)
        self.driver.swipe(x1, y1, x2, y1, 1000)
    
    def swipe_right(self, from_top=0.5):
        """右划，from_top默认为距离顶部0.5个屏幕(屏幕中间)"""
        if not isinstance(from_top, int) and not isinstance(from_top, float):
            raise ValueError("from_top参数不为数字")
        logging.debug("右滑")
        l = self.get_screen_size()
        y1 = int(l[1] * from_top)
        x1 = int(l[0] * 0.25)
        x2 = int(l[0] * 0.95)
        self.driver.swipe(x1, y1, x2, y1, 1000)
    
    def swipe_up(self, from_left=0.5):
        """上划，from_left默认为距离左侧0.5个屏幕(屏幕中间)"""
        if not isinstance(from_left, int) and not isinstance(from_left, float):
            raise ValueError("from_left参数不为数字")
        logging.debug("上滑")
        l = self.get_screen_size()
        x1 = int(l[1] * from_left)
        y1 = int(l[0] * 0.95)
        y2 = int(l[0] * 0.25)
        self.driver.swipe(x1, y1, x1, y2, 1000)
    
    def swipe_up_to_location(self, *args, from_left=0.5):
        """上划至指定位置，from_left默认为距离左侧0.5个屏幕(屏幕中间)"""
        if not isinstance(from_left, int) and not isinstance(from_left, float):
            raise ValueError("from_left参数不为数字")
        logging.debug("上滑")
        l = self.get_screen_size()
        x1 = int(l[1] * from_left)
        y1 = int(l[0] * 0.95)
        y2 = int(l[0] * 0.25)
        i = 0
        while i < 10:
            try:
                elm = self.find_element(*args)  # 查找元素
            except NoSuchElementException:
                self.driver.swipe(x1, y1, x1, y2, 1000)
                i = i + 1
            else:
                elm.click()
                break
    
    def swipe_down(self, from_left=0.5):
        """下划，from_left默认为距离左侧0.5个屏幕(屏幕中间)"""
        if not isinstance(from_left, int) and not isinstance(from_left, float):
            raise ValueError("from_left参数不为数字")
        logging.debug("下滑")
        l = self.get_screen_size()
        x1 = int(l[1] * from_left)
        y1 = int(l[0] * 0.25)
        y2 = int(l[0] * 0.95)
        self.driver.swipe(x1, y1, x1, y2, 1000)
    
    def screenshot(self, module):
        snapshot_dir = Config.task_dir or os.path.join(PROJECT_ROOT, 'report/snapshot')
        now = time.strftime("%Y-%m-%d %H_%M_%S")
        image_file = os.path.join(snapshot_dir, "{}_{}.png".format(module, now))
        logging.debug("获取 {} 模块屏幕截图".format(module))
        logging.debug("截图文件路径: {}".format(image_file))
        self.driver.get_screenshot_as_file(image_file)
    # 按键 ---------------------------------------------------------------------
    def press_back(self):
        """按返回键"""
        self.driver.keyevent(4)
    
    def press_home(self):
        """按Home键"""
        self.driver.keyevent(3)
    
    def press_search(self):
        """按键盘搜索键"""
        self.driver.execute_script('mobile: performEditorAction', {'action': 'search'})

    # 选择框
    def check_checkbox(self, *loc):
        """判断选择框是否选中"""
        return self.find_element(*loc).is_selected()

