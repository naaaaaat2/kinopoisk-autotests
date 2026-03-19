"""
Базовый класс для Page Object
"""

import allure
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, ElementClickInterceptedException
from config.settings import settings


class BasePage:
    """Базовый класс для всех страниц"""
    
    def __init__(self, driver):
        self.driver = driver
        self.base_url = settings.BASE_URL
        self.timeout = settings.DEFAULT_TIMEOUT
    
    def find_element(self, locator, timeout=None):
        """Поиск элемента с ожиданием"""
        if timeout is None:
            timeout = self.timeout
        return WebDriverWait(self.driver, timeout).until(
            EC.presence_of_element_located(locator)
        )
    
    def find_elements(self, locator, timeout=None):
        """Поиск нескольких элементов"""
        if timeout is None:
            timeout = self.timeout
        return WebDriverWait(self.driver, timeout).until(
            EC.presence_of_all_elements_located(locator)
        )
    
    def wait_for_page_load(self, timeout=None):
        """Ожидание загрузки страницы"""
        if timeout is None:
            timeout = self.timeout
        WebDriverWait(self.driver, timeout).until(
            lambda d: d.execute_script("return document.readyState") == "complete"
        )
    
    def scroll_to_element(self, element):
        """Прокрутка страницы до элемента"""
        self.driver.execute_script("arguments[0].scrollIntoView(true);", element)
    
    def safe_click(self, element):
        """Безопасный клик по элементу (обычный или через JavaScript)"""
        try:
            element.click()
        except ElementClickInterceptedException:
            self.driver.execute_script("arguments[0].click();", element)
    
    def is_captcha_page(self):
        """Проверка, не попали ли мы на капчу"""
        try:
            return "showcaptcha" in self.driver.current_url or "captcha" in self.driver.current_url
        except:
            return False
